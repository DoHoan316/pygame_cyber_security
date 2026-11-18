"""Async REST client for desktop Pygame-CE and browser Pygbag runtime."""
import asyncio
import json
import os
import sys


class APIError(Exception):
    def __init__(self, message, status=0):
        super().__init__(message)
        self.status = status


class CyberSafeAPI:
    def __init__(self):
        self.base_url = os.getenv("CYBERSAFE_API_URL", "http://127.0.0.1:8000/api").rstrip("/")
        self.token = None
        self.timeout = 12
        self._session = None
        self.token = self._load_browser_token()

    def _load_browser_token(self):
        if sys.platform != "emscripten":
            return None
        try:
            import platform
            return platform.window.localStorage.getItem("cybersafe_access_token") or None
        except Exception:
            return None

    def _save_browser_token(self):
        if sys.platform == "emscripten":
            try:
                import platform
                if self.token:
                    platform.window.localStorage.setItem("cybersafe_access_token", self.token)
                else:
                    platform.window.localStorage.removeItem("cybersafe_access_token")
            except Exception:
                pass

    async def close(self):
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def _request_browser(self, method, url, payload, headers):
        # Pygbag runs on Emscripten; use the browser Fetch API rather than a
        # CPython HTTP package that may not have a compatible WASM wheel.
        import platform
        options = {"method": method, "headers": headers}
        if payload is not None:
            options["body"] = json.dumps(payload, ensure_ascii=False)
        js_options = platform.window.JSON.parse(json.dumps(options))
        response = await platform.window.fetch(url, js_options)
        status = int(response.status)
        raw = await response.text()
        try:
            body = json.loads(str(raw))
        except Exception:
            body = {"message": str(raw)}
        return status, body

    async def _request_desktop(self, method, url, payload, headers):
        try:
            import aiohttp
        except ImportError as exc:
            raise APIError("Thiếu aiohttp. Hãy cài requirements.txt") from exc
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        async with self._session.request(method, url, json=payload, headers=headers) as response:
            try:
                body = await response.json(content_type=None)
            except Exception:
                body = {"message": await response.text()}
            return response.status, body

    async def request(self, method, path, payload=None, auth=True):
        headers = {"Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        url = f"{self.base_url}{path}"
        try:
            if sys.platform == "emscripten":
                status, body = await self._request_browser(method, url, payload, headers)
            else:
                status, body = await self._request_desktop(method, url, payload, headers)
        except APIError:
            raise
        except asyncio.TimeoutError as exc:
            raise APIError("Máy chủ phản hồi quá thời gian") from exc
        except Exception as exc:
            raise APIError(f"Không thể kết nối máy chủ: {exc}") from exc
        if status == 401 and auth:
            self.token = None
            self._save_browser_token()
        if status >= 400 or body.get("success") is False:
            message = body.get("message") or body.get("detail") or f"HTTP {status}"
            raise APIError(message, status)
        return body.get("data", body)

    async def login(self, email, password):
        data = await self.request("POST", "/auth/login", {"email": email, "password": password}, auth=False)
        self.token = data["access_token"]
        self._save_browser_token()
        return data["user"]

    async def register(self, email, password, display_name):
        data = await self.request("POST", "/auth/register", {"email": email, "password": password, "display_name": display_name}, auth=False)
        self.token = data["access_token"]
        self._save_browser_token()
        return data["user"]

    async def me(self): return await self.request("GET", "/auth/me")
    async def campaigns(self): return await self.request("GET", "/campaigns")
    async def dashboard(self): return await self.request("GET", "/me/dashboard")
    async def history(self): return await self.request("GET", "/me/history")
    async def errors(self): return await self.request("GET", "/me/errors")
    async def leaderboard(self, campaign_id): return await self.request("GET", f"/leaderboard/{campaign_id}")
    async def start_session(self, campaign_id): return await self.request("POST", "/game/sessions", {"campaign_id": campaign_id})
    async def get_session(self, session_id): return await self.request("GET", f"/game/sessions/{session_id}")
    async def choose(self, session_id, scenario_id, choice_id):
        return await self.request("POST", f"/game/sessions/{session_id}/choices", {"scenario_id": scenario_id, "choice_id": choice_id})
    async def continue_session(self, session_id): return await self.request("POST", f"/game/sessions/{session_id}/continue", {})
    async def result(self, session_id): return await self.request("GET", f"/game/sessions/{session_id}/result")
