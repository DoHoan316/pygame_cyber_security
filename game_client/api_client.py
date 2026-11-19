"""Async REST client for desktop Pygame-CE and browser Pygbag runtime.

Desktop: aiohttp with a bounded request timeout.
Pygbag/WebAssembly: browser Fetch API with AbortController and timeout.
"""

import asyncio
import json
import os
import sys


class APIError(Exception):
    """A readable API/network error suitable for showing in the game UI."""

    def __init__(self, message: str, status: int = 0):
        super().__init__(message)
        self.status = status


class CyberSafeAPI:
    def __init__(self):
        default_url = (
            "https://pygame-cyber-security.onrender.com/api"
        )
        self.base_url = os.getenv(
            "CYBERSAFE_API_URL",
            default_url,
        ).strip().rstrip("/")

        self.token = None
        self.timeout = float(os.getenv("CYBERSAFE_API_TIMEOUT", "15"))
        self._session = None
        self.token = self._load_browser_token()

    # -----------------------------------------------------
    # TOKEN STORAGE
    # -----------------------------------------------------

    def _load_browser_token(self):
        if sys.platform != "emscripten":
            return None

        try:
            import platform

            token = platform.window.localStorage.getItem(
                "cybersafe_access_token"
            )
            return str(token) if token else None
        except Exception:
            return None

    def _save_browser_token(self):
        if sys.platform != "emscripten":
            return

        try:
            import platform

            storage = platform.window.localStorage

            if self.token:
                storage.setItem(
                    "cybersafe_access_token",
                    self.token,
                )
            else:
                storage.removeItem("cybersafe_access_token")
        except Exception:
            # Storage can be blocked by browser privacy settings.
            # The current in-memory token remains usable.
            pass

    def logout(self):
        self.token = None
        self._save_browser_token()

    async def close(self):
        if self._session is not None and not self._session.closed:
            await self._session.close()
        self._session = None

    # -----------------------------------------------------
    # URL / RESPONSE HELPERS
    # -----------------------------------------------------

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            raise APIError("Chưa cấu hình CYBERSAFE_API_URL")

        normalized_path = "/" + str(path).lstrip("/")
        return self.base_url + normalized_path

    @staticmethod
    def _decode_body(raw_text):
        try:
            return json.loads(str(raw_text))
        except (TypeError, ValueError):
            text = str(raw_text).strip()
            return {"message": text or "Máy chủ trả về dữ liệu không hợp lệ"}

    @staticmethod
    def _error_message(body, status):
        if isinstance(body, dict):
            message = (
                body.get("message")
                or body.get("detail")
                or body.get("error")
            )

            # FastAPI validation errors can contain a structured detail.
            if isinstance(message, list):
                message = "; ".join(
                    str(item.get("msg", item))
                    if isinstance(item, dict)
                    else str(item)
                    for item in message
                )

            if message:
                return str(message)

        return f"Lỗi máy chủ (HTTP {status})"

    # -----------------------------------------------------
    # PYGBAG / BROWSER FETCH
    # -----------------------------------------------------

    async def _request_browser(self, method, url, payload, headers):
        """Send a request using the browser Fetch API.

        AbortController stops the underlying fetch when the timeout expires.
        This avoids leaving the Pygbag game waiting forever on a pending
        browser request.
        """
        import platform

        window = platform.window
        controller = None

        options = {
            "method": method.upper(),
            "mode": "cors",
            "cache": "no-store",
            "credentials": "omit",
            "redirect": "follow",
            "headers": headers,
        }

        if payload is not None:
            options["body"] = json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
            )

        js_options = window.JSON.parse(json.dumps(options))

        try:
            controller = window.AbortController.new()
            js_options.signal = controller.signal
        except Exception:
            # Older browser runtimes may not expose AbortController.
            controller = None

        try:
            fetch_promise = window.fetch(url, js_options)
            response = await asyncio.wait_for(
                fetch_promise,
                timeout=self.timeout,
            )

            status = int(response.status)

            # response.text() is also asynchronous in the browser.
            raw_text = await asyncio.wait_for(
                response.text(),
                timeout=self.timeout,
            )

            body = self._decode_body(raw_text)
            return status, body

        except asyncio.TimeoutError as exc:
            if controller is not None:
                try:
                    controller.abort()
                except Exception:
                    pass

            raise APIError(
                f"Máy chủ không phản hồi sau {self.timeout:g} giây. "
                "Hãy kiểm tra kết nối hoặc thử lại."
            ) from exc

        except APIError:
            raise

        except Exception as exc:
            error_text = str(exc)

            if "AbortError" in error_text:
                raise APIError(
                    "Yêu cầu đã bị hủy do quá thời gian chờ."
                ) from exc

            # Fetch commonly reports CORS, DNS and TLS failures as TypeError.
            raise APIError(
                "Không thể kết nối API từ trình duyệt. "
                "Kiểm tra CORS trên Render, URL API và kết nối mạng. "
                f"Chi tiết: {error_text[:180]}"
            ) from exc

    # -----------------------------------------------------
    # DESKTOP HTTP
    # -----------------------------------------------------

    async def _request_desktop(self, method, url, payload, headers):
        try:
            import aiohttp
        except ImportError as exc:
            raise APIError(
                "Thiếu aiohttp. Hãy cài thư viện trong requirements.txt."
            ) from exc

        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)

        try:
            async with self._session.request(
                method.upper(),
                url,
                json=payload,
                headers=headers,
            ) as response:
                raw_text = await response.text()
                body = self._decode_body(raw_text)
                return response.status, body

        except asyncio.TimeoutError as exc:
            raise APIError(
                f"Máy chủ không phản hồi sau {self.timeout:g} giây."
            ) from exc

        except APIError:
            raise

        except Exception as exc:
            raise APIError(
                f"Không thể kết nối máy chủ: {str(exc)[:180]}"
            ) from exc

    # -----------------------------------------------------
    # COMMON REQUEST
    # -----------------------------------------------------

    async def request(
        self,
        method,
        path,
        payload=None,
        auth=True,
    ):
        method = str(method).upper()
        url = self._build_url(path)

        headers = {
            "Accept": "application/json",
        }

        if payload is not None:
            headers["Content-Type"] = "application/json"

        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

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
            body = {"data": body}

        if status == 401 and auth:
            self.logout()

        if status >= 400 or body.get("success") is False:
            raise APIError(
                self._error_message(body, status),
                status,
            )

        # Current backend wraps successful responses as:
        # {"success": true, "message": "...", "data": ...}
        if "data" in body:
            return body["data"]

        # Keep compatibility with endpoints returning raw JSON.
        return body

    # -----------------------------------------------------
    # AUTH
    # -----------------------------------------------------

    async def login(self, email, password):
        data = await self.request(
            "POST",
            "/auth/login",
            {
                "email": email.strip(),
                "password": password,
            },
            auth=False,
        )

        token = data.get("access_token")
        user = data.get("user")

        if not token or not isinstance(user, dict):
            raise APIError(
                "Đăng nhập phản hồi không đầy đủ từ máy chủ."
            )

        self.token = str(token)
        self._save_browser_token()
        return user

    async def register(self, email, password, display_name):
        data = await self.request(
            "POST",
            "/auth/register",
            {
                "email": email.strip(),
                "password": password,
                "display_name": display_name.strip(),
            },
            auth=False,
        )

        token = data.get("access_token")
        user = data.get("user")

        if not token or not isinstance(user, dict):
            raise APIError(
                "Đăng ký phản hồi không đầy đủ từ máy chủ."
            )

        self.token = str(token)
        self._save_browser_token()
        return user

    async def me(self):
        return await self.request("GET", "/auth/me")

    # -----------------------------------------------------
    # CAMPAIGNS / PLAYER
    # -----------------------------------------------------

    async def campaigns(self):
        return await self.request("GET", "/campaigns")

    async def dashboard(self):
        return await self.request("GET", "/me/dashboard")

    async def history(self):
        return await self.request("GET", "/me/history")

    async def errors(self):
        return await self.request("GET", "/me/errors")

    async def leaderboard(self, campaign_id):
        return await self.request(
            "GET",
            f"/leaderboard/{campaign_id}",
        )

    # -----------------------------------------------------
    # GAME
    # -----------------------------------------------------

    async def start_session(self, campaign_id):
        return await self.request(
            "POST",
            "/game/sessions",
            {"campaign_id": campaign_id},
        )

    async def get_session(self, session_id):
        return await self.request(
            "GET",
            f"/game/sessions/{session_id}",
        )

    async def choose(self, session_id, scenario_id, choice_id):
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
