import os
import json
import requests

class GameBridgeService:
    """
    Cầu nối dữ liệu (Adapter Pattern):
    - Khi USE_REMOTE_SERVER = True: Kết nối FastAPI Backend (Localhost hoặc Cloud).
    - Tự động chuyển sang chế độ Offline (lưu JSON cục bộ) nếu không tìm thấy Server.
    """
    def __init__(self):
        self.USE_REMOTE_SERVER = True
        self.API_BASE_URL = os.getenv("GAME_API_URL", "http://127.0.0.1:8000/api")
        self.local_cache_file = "local_save_bridge.json"

        self.current_user = {
            "user_id": 1,
            "username": "SinhVien_IT",
            "total_score": 0,
            "rank": "Tân Binh An Ninh",
            "mistakes": []
        }

    def _load_local_cache(self):
        if os.path.exists(self.local_cache_file):
            try:
                with open(self.local_cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_local_cache(self, data):
        with open(self.local_cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def login(self, username: str, password: str):
        if self.USE_REMOTE_SERVER:
            try:
                resp = requests.post(
                    f"{self.API_BASE_URL}/auth/login",
                    json={"username": username, "password": password},
                    timeout=2.5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.current_user.update({
                        "user_id": data["user_id"],
                        "username": data["username"],
                        "total_score": data["total_score"],
                        "rank": data["rank"]
                    })
                    return True, "Kết nối máy chủ FastAPI thành công!"
                else:
                    return False, resp.json().get("detail", "Lỗi đăng nhập")
            except Exception:
                self.USE_REMOTE_SERVER = False

        cache = self._load_local_cache()
        user_data = cache.get(username, {
            "user_id": 999,
            "username": username,
            "total_score": 0,
            "rank": "Tân Binh (Offline)",
            "mistakes": []
        })
        self.current_user = user_data
        cache[username] = user_data
        self._save_local_cache(cache)
        return True, "Đang chạy chế độ Cục bộ (Offline Bridge)"

    def submit_scenario_result(self, scenario_id: str, score_delta: int, risk: str, mistake_tag: str = None):
        if self.USE_REMOTE_SERVER:
            try:
                resp = requests.post(
                    f"{self.API_BASE_URL}/progress/submit",
                    json={
                        "user_id": self.current_user["user_id"],
                        "scenario_id": scenario_id,
                        "score_earned": score_delta,
                        "risk_level": risk,
                        "mistake_tag": mistake_tag
                    },
                    timeout=2.5
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.current_user["total_score"] = data["total_score"]
                    self.current_user["rank"] = data["rank"]
                    if mistake_tag and mistake_tag not in self.current_user["mistakes"]:
                        self.current_user["mistakes"].append(mistake_tag)
                    return self.current_user
            except Exception:
                pass

        self.current_user["total_score"] = max(0, self.current_user["total_score"] + score_delta)
        if mistake_tag and mistake_tag not in self.current_user["mistakes"]:
            self.current_user["mistakes"].append(mistake_tag)

        cache = self._load_local_cache()
        cache[self.current_user["username"]] = self.current_user
        self._save_local_cache(cache)
        return self.current_user

    def get_leaderboard(self):
        if self.USE_REMOTE_SERVER:
            try:
                resp = requests.get(f"{self.API_BASE_URL}/leaderboard", timeout=2.5)
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        return [
            {"username": self.current_user["username"], "total_score": self.current_user["total_score"], "rank": self.current_user["rank"]},
            {"username": "CyberGuard_VN", "total_score": 1850, "rank": "Chuyên Gia Bảo Mật"},
            {"username": "SecMaster_2026", "total_score": 1200, "rank": "Chiến Binh Phòng Thủ"}
        ]
