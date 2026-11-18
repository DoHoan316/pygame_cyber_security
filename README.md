# CyberSafe — Game mô phỏng an toàn thông tin

Dự án nâng cấp từ V2, giữ nguyên game Pygame và toàn bộ 30 tình huống gốc. Nội dung được tổ chức thành 4 chiến dịch: Phishing & lừa đảo; Wi-Fi/thiết bị/kết nối; Tài khoản/mật khẩu; Bảo vệ dữ liệu & social engineering.

## Kiến trúc hiện tại

- `game_client/`: game Pygame gốc được giữ lại, gồm giao diện, font và dữ liệu gốc.
- `backend/app/`: API FastAPI mới: JWT, hash mật khẩu Argon2, Player/Admin, campaign, game session, nhánh, scoring, history, dashboard, leaderboard và admin analytics.
- `seed_data/campaigns.json`: 30 tình huống chuyển đổi từ `game_client/data/scenarios.py`; giữ nguyên mã, mô tả, lựa chọn và phản hồi.
- `admin_web/`: giao diện web responsive Player/Admin dùng REST API.
- `docs/`: API và hướng dẫn kỹ thuật.

**Lưu ý minh bạch:** giao diện web Player/Admin đã được thêm để kiểm thử luồng API trong trình duyệt. Game Pygame gốc vẫn được giữ trong repo; phần chuyển toàn bộ 10 màn hình Pygame sang API session mới và kiểm chứng bản Pygbag WebAssembly là hạng mục tích hợp tiếp theo, chưa được đánh dấu hoàn tất. Nhánh lựa chọn hiện tại là DAG được sinh theo quy tắc tiến về trước; cần rà soát nội dung nhánh trước khi phát hành chính thức.

## 1. Chạy local trên Windows PowerShell

Từ thư mục `cyber_security_game_v2`, chạy lần lượt:

```powershell
.\setup.ps1
```

Mở `.env` và đổi `JWT_SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`. Sau đó chạy:

```powershell
.\run.ps1
```

Mở `.env`, thay `JWT_SECRET_KEY` bằng chuỗi bí mật ngẫu nhiên. Đổi `ADMIN_EMAIL` và `ADMIN_PASSWORD` thành thông tin riêng của nhóm.

Tạo/cập nhật database bằng migration:

```powershell
alembic upgrade head
```

Chạy backend:

```powershell
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 --env-file .env
```

Mở trình duyệt:
- Web Player/Admin: http://127.0.0.1:8001/app/
- Swagger API: http://127.0.0.1:8001/docs
- Health: http://127.0.0.1:8001/api/health

## 2. Database

Mặc định dùng SQLite để chạy local. Schema được quản lý bằng Alembic (`alembic upgrade head`). Khi deploy, đặt `DATABASE_URL` thành connection string PostgreSQL của Supabase và chạy migration trước khi khởi động. Không đưa mật khẩu DB hoặc JWT secret lên Git.

## 3. Tài khoản Admin

Nếu `ADMIN_EMAIL` và `ADMIN_PASSWORD` được đặt trước lần chạy đầu tiên, backend sẽ tạo tài khoản Admin nếu chưa tồn tại. Không dùng mật khẩu mẫu trong môi trường thật.

## 4. API chính

- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/campaigns`, `GET /api/campaigns/{id}`
- `POST /api/game/sessions`, `GET /api/game/sessions/{id}`
- `POST /api/game/sessions/{id}/choices`, `POST /api/game/sessions/{id}/continue`
- `GET /api/game/sessions/{id}/result`
- `GET /api/me/dashboard`, `/api/me/history`, `/api/me/errors`
- `GET /api/leaderboard/{campaign_id}`
- Admin: `/api/admin/users`, `/api/admin/users/{id}`, `/api/admin/users/{id}/status`, `/api/admin/analytics/overview`

Tất cả API nghiệp vụ yêu cầu Bearer JWT; endpoint Admin kiểm tra role ở backend. Điểm không được nhận từ client.

## 5. Pygame gốc

Game V2 vẫn có thể được mở riêng bằng `python game_client/main.py` sau khi cài dependencies. Bản client này đang dùng cầu nối API V2 cũ/offline; chưa dùng API session V3 mới. Không dùng nó làm bằng chứng rằng Pygbag build hoặc kết nối V3 đã đạt.

## 6. Kiểm tra nội dung seed

```powershell
python -m backend.app.validate_seed
```

## 7. Triển khai online

Phần deploy chưa thực hiện trong gói này. Tham khảo `docs/DEPLOYMENT_HANDOFF.md` để cấu hình PostgreSQL, HTTPS, CORS và build Pygbag.

## 8. Pygame-CE Client V3

The V3 Pygame client is now the default entry point. It authenticates with JWT and uses the V3 session endpoints; choices, branching, scoring and results are supplied by the backend. It does not calculate scores or choose the next scenario locally.

Local desktop run (keep the FastAPI server running in another terminal):

```powershell
$env:CYBERSAFE_API_URL = "http://127.0.0.1:8000/api"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe game_client\main.py
```

The previous V2 client is preserved as `game_client/main_legacy_v2.py` for reference only; it uses the retired bridge and should not be used for current demonstrations.

Pygbag build attempt (run from the project root):

```powershell
.\.venv\Scripts\python.exe -m pygbag --port 8001 game_client
```

For local browser testing, keep FastAPI on port 8000 and Pygbag on port 8001, then open `http://localhost:8001?CYBERSAFE_API_URL=http://127.0.0.1:8000/api`. The `.env` CORS allowlist must include `http://localhost:8001`. For a deployed game, pass the public HTTPS API base as `CYBERSAFE_API_URL` and configure the backend CORS allowlist for the game origin. The Pygbag build and browser Fetch API compatibility still require an actual local build/browser test; do not report browser integration as passed until that test succeeds.
