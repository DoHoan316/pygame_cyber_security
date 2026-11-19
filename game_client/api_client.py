
"""CyberSafe REST client for desktop Pygame-CE and browser Pygbag."""

import asyncio
import json
import os
import sys
from urllib.parse import urlencode


class APIError(Exception):
    def __init__(self, message, status=0):
        super().__init__(message)
        self.status = status


# Pygbag cannot safely await window.fetch() directly.
# Start Fetch in JavaScript and let platform.jsiter step this generator.
_BROWSER_BRIDGE = r"""
window.CyberSafeAPIRequest = window.CyberSafeAPIRequest || {};

window.CyberSafeAPIRequest.run = function* (
    url, method, headers_json, body_json, timeout_ms
) {
    let result = null;

    const options = {
        method: method,
        headers: JSON.parse(headers_json)
    };

    if (body_json !== "") {
        options.body = body_json;
    }

    const timeout_id = window.setTimeout(function () {
        if (result === null) {
            result = JSON.stringify({
                status: 0,
                body: JSON.stringify({
                    message: "Request timed out"
                })
            });
        }
    }, timeout_ms);

    fetch(url, options)
        .then(function (response) {
            return response.text().then(function (body_text) {
                if (result === null) {
                    window.clearTimeout(timeout_id);

                    result = JSON.stringify({
                        status: response.status,
                        body: body_text
                    });
                }
            });
        })
        .catch(function (error) {
            if (result === null) {
                window.clearTimeout(timeout_id);

                result = JSON.stringify({
                    status: 0,
                    body: JSON.stringify({
                        message: String(error)
                    })
                });
            }
        });

    // Yield control back to the browser until Fetch finishes.
    while (result === null) {
        yield;
    }

    yield result;
};
"""


class CyberSafeAPI:
    def __init__(self):
        self.base_url = self._resolve_base_url().rstrip("/")
        self.timeout = 15
        self.token = self._load_browser_token()

        self._session = None
        self._browser_platform = None
        self._browser_bridge_error = None

        if sys.platform == "emscripten":
            self._install_browser_bridge()

    # --------------------------------------------------------------
    # Configuration
    # --------------------------------------------------------------

    def _resolve_base_url(self):
        configured_url = os.getenv("CYBERSAFE_API_URL")

        if configured_url:
            return configured_url

        if sys.platform == "emscripten":
            try:
                import platform

                hostname = str(
                    platform.window.location.hostname
                )

                if hostname in ("localhost", "127.0.0.1"):
                    return f"http://{hostname}:8000/api"

            except Exception:
                pass

        return "https://pygame-cyber-security.onrender.com/api"

    def _install_browser_bridge(self):
        try:
            import platform

            # Install the JavaScript generator once per game session.
            platform.window.eval(_BROWSER_BRIDGE)

            self._browser_platform = platform

        except Exception as exc:
            self._browser_bridge_error = str(exc)

    # --------------------------------------------------------------
    # Token
    # --------------------------------------------------------------

    def _load_browser_token(self):
        if sys.platform != "emscripten":
            return None

        try:
            import platform

            value = platform.window.localStorage.getItem(
                "cybersafe_access_token"
            )

            return str(value) if value else None

        except Exception:
            return None

    def _save_browser_token(self):
        if sys.platform != "emscripten":
            return

        try:
            import platform

            if self.token:
                platform.window.localStorage.setItem(
                    "cybersafe_access_token",
                    self.token,
                )
            else:
                platform.window.localStorage.removeItem(
                    "cybersafe_access_token"
                )

        except Exception:
            pass

    def clear_token(self):
        self.token = None
        self._save_browser_token()

    # --------------------------------------------------------------
    # Close
    # --------------------------------------------------------------

    async def close(self):
        if self._session is not None and not self._session.closed:
            await self._session.close()

        self._session = None

    # --------------------------------------------------------------
    # Browser request: Pygbag / Emscripten
    # --------------------------------------------------------------

    async def _request_browser(
        self,
        method,
        url,
        payload,
        headers,
    ):
        if self._browser_platform is None:
            detail = (
                self._browser_bridge_error
                or "platform.jsiter is unavailable"
            )

            raise APIError(
                f"Không khởi tạo được cầu nối Pygbag: {detail}"
            )

        platform = self._browser_platform

        body_json = (
            json.dumps(payload, ensure_ascii=False)
            if payload is not None
            else ""
        )

        # Give the browser event loop a turn before starting Fetch.
        await asyncio.sleep(0)

        generator = (
            platform.window.CyberSafeAPIRequest.run(
                url,
                method,
                json.dumps(headers, ensure_ascii=False),
                body_json,
                int(self.timeout * 1000),
            )
        )

        # Do not replace this with:
        # await platform.window.fetch(url, options)
        raw_result = await platform.jsiter(generator)

        try:
            envelope = json.loads(str(raw_result))

            status = int(
                envelope.get("status", 0)
            )

            raw_body = envelope.get("body", "")

        except Exception as exc:
            raise APIError(
                f"Không đọc được phản hồi từ trình duyệt: {exc}"
            ) from exc

        try:
            body = (
                json.loads(raw_body)
                if raw_body
                else {}
            )

        except Exception:
            body = {
                "message": str(raw_body)
            }

        if status == 0:
            message = (
                body.get("message", "Không thể kết nối máy chủ")
                if isinstance(body, dict)
                else str(body)
            )

            raise APIError(str(message), 0)

        return status, body

    # --------------------------------------------------------------
    # Desktop request: Windows / CPython
    # --------------------------------------------------------------

    async def _request_desktop(
        self,
        method,
        url,
        payload,
        headers,
    ):
        try:
            import aiohttp

        except ImportError as exc:
            raise APIError(
                "Thiếu aiohttp. Hãy cài requirements.txt"
            ) from exc

        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(
                total=self.timeout
            )

            self._session = aiohttp.ClientSession(
                timeout=timeout
            )

        try:
            async with self._session.request(
                method,
                url,
                json=payload,
                headers=headers,
            ) as response:

                raw = await response.text()

                try:
                    body = (
                        json.loads(raw)
                        if raw
                        else {}
                    )

                except Exception:
                    body = {
                        "message": raw
                    }

                return response.status, body

        except asyncio.TimeoutError as exc:
            raise APIError(
                "Máy chủ phản hồi quá thời gian"
            ) from exc

        except Exception as exc:
            raise APIError(
                f"Không thể kết nối máy chủ: {exc}"
            ) from exc

    # --------------------------------------------------------------
    # Common request dispatcher
    # --------------------------------------------------------------

    async def request(
        self,
        method,
        path,
        payload=None,
        auth=True,
    ):
        headers = {
            "Accept": "application/json"
        }

        if payload is not None:
            headers["Content-Type"] = "application/json"

        if auth and self.token:
            headers["Authorization"] = (
                f"Bearer {self.token}"
            )

        url = f"{self.base_url}{path}"

        if sys.platform == "emscripten":
            status, body = await self._request_browser(
                method,
                url,
                payload,
                headers,
            )

        else:
            status, body = await self._request_desktop(
                method,
                url,
                payload,
                headers,
            )

        if not isinstance(body, dict):
            body = {
                "data": body
            }

        if status == 401 and auth:
            self.clear_token()

        if status >= 400 or body.get("success") is False:
            message = (
                body.get("message")
                or body.get("detail")
                or f"HTTP {status}"
            )

            raise APIError(
                str(message),
                status,
            )

        return body.get("data", body)

    # --------------------------------------------------------------
    # Authentication
    # --------------------------------------------------------------

    async def login(self, email, password):
        data = await self.request(
            "POST",
            "/auth/login",
            {
                "email": email,
                "password": password,
            },
            auth=False,
        )

        if (
            not isinstance(data, dict)
            or not data.get("access_token")
        ):
            raise APIError(
                "Máy chủ không trả về access_token"
            )

        self.token = data["access_token"]
        self._save_browser_token()

        return data.get("user", {})

    async def register(
        self,
        email,
        password,
        display_name,
    ):
        data = await self.request(
            "POST",
            "/auth/register",
            {
                "email": email,
                "password": password,
                "display_name": display_name,
            },
            auth=False,
        )

        if (
            not isinstance(data, dict)
            or not data.get("access_token")
        ):
            raise APIError(
                "Máy chủ không trả về access_token"
            )

        self.token = data["access_token"]
        self._save_browser_token()

        return data.get("user", {})

    async def me(self):
        return await self.request(
            "GET",
            "/auth/me",
        )

    # --------------------------------------------------------------
    # Player endpoints
    # --------------------------------------------------------------

    async def campaigns(self):
        return await self.request(
            "GET",
            "/campaigns",
        )

    async def dashboard(self):
        return await self.request(
            "GET",
            "/me/dashboard",
        )

    async def history(self):
        return await self.request(
            "GET",
            "/me/history",
        )

    async def errors(self):
        return await self.request(
            "GET",
            "/me/errors",
        )

    async def leaderboard(self, campaign_id):
        return await self.request(
            "GET",
            f"/leaderboard/{campaign_id}",
        )

    async def start_session(self, campaign_id):
        return await self.request(
            "POST",
            "/game/sessions",
            {
                "campaign_id": campaign_id,
            },
        )

    async def get_session(self, session_id):
        return await self.request(
            "GET",
            f"/game/sessions/{session_id}",
        )

    async def choose(
        self,
        session_id,
        scenario_id,
        choice_id,
    ):
        return await self.request(
            "POST",
            f"/game/sessions/{session_id}/choices",
            {
                "scenario_id": scenario_id,
                "choice_id": choice_id,
            },
        )

    async def continue_session(self, session_id):
        return await self.request(
            "POST",
            f"/game/sessions/{session_id}/continue",
            {},
        )

    async def result(self, session_id):
        return await self.request(
            "GET",
            f"/game/sessions/{session_id}/result",
        )

    # --------------------------------------------------------------
    # Admin endpoints
    # --------------------------------------------------------------

    async def admin_overview(self):
        return await self.request(
            "GET",
            "/admin/analytics/overview",
        )

    async def admin_users(
        self,
        query="",
        offset=0,
        limit=50,
    ):
        params = urlencode({
            "q": query,
            "offset": max(0, int(offset)),
            "limit": min(100, max(1, int(limit))),
        })

        return await self.request(
            "GET",
            f"/admin/users?{params}",
        )

    async def admin_set_user_status(
        self,
        user_id,
        is_active,
    ):
        return await self.request(
            "PATCH",
            f"/admin/users/{int(user_id)}/status",
            {
                "is_active": bool(is_active),
            },
        )
