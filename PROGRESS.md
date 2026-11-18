# Tiến độ CyberSafe V3

Cập nhật: 17/11/2026

## Đã triển khai
- [x] Giữ source V2, font và nội dung 30 tình huống gốc.
- [x] Chuyển 30 tình huống/120 lựa chọn thành seed data; tổ chức 4 chiến dịch.
- [x] Validator kiểm tra start node, lựa chọn, nhánh nội bộ, khả năng tiếp cận và vòng lặp.
- [x] FastAPI V3, JWT, Argon2 password hash, Player/Admin, trạng thái tài khoản.
- [x] Campaign/session/choice/continue/result APIs; backend quyết định nhánh và tính điểm.
- [x] Session states, feedback resume, lịch sử, dashboard, error groups, leaderboard, Admin APIs.
- [x] Web Player/Admin UI kết nối API.
- [x] Alembic migration; SQLite local; URL PostgreSQL/Supabase được chuẩn hóa sang psycopg 3.
- [x] Pygame-CE V3 client được triển khai: login/register, home, campaigns, gameplay, feedback, result, dashboard, history, errors, leaderboard (10 trạng thái/màn hình).
- [x] Pygame V3 gọi API session; không tính điểm hoặc chọn nhánh ở client.
- [x] Pygbag browser networking dùng Fetch API khi chạy trên Emscripten; JWT có thể lưu/khôi phục qua localStorage.
- [x] Giữ Pygame V2 cũ ở `game_client/main_legacy_v2.py` để tham khảo.
- [x] Sửa PowerShell scripts thành ASCII để tránh lỗi mã hóa trên Windows PowerShell 5.1.
- [x] README, API contract, deployment handoff, decision log.

## Đã kiểm thử trong môi trường phát triển
- [x] `python -m backend.app.validate_seed`: 4 campaigns, 30 scenarios, 120 choices.
- [x] `python -m pytest -q`: 2 passed.
- [x] Python compile check cho Pygame V3/API client/backend/migration.
- [x] `node --check admin_web/js/app.js`.
- [x] Alembic migration chạy thành công trên SQLite ở checkpoint trước.
- [x] API smoke chạy lại trên SQLite DB mới sau migration: health, register, campaigns, session, choice, feedback resume, completion, result, Player/Admin RBAC.
- [x] Luồng hoàn chỉnh 4 chiến dịch đã chạy qua TestClient ở checkpoint trước.
- [x] `/app/` trả HTTP 200 trong môi trường checkpoint trước.

## Chưa thể đánh dấu hoàn tất nếu chưa chạy trên máy/hosting thật
- [ ] Chạy Pygame V3 trên Windows thật sau khi cài `pygame-ce` và `aiohttp`.
- [ ] Cài/chạy Pygbag build và xác minh game chạy trên Chrome. Môi trường build hiện tại không có pygame-ce/pygbag và không truy cập được PyPI để cài; browser Fetch integration mới được kiểm tra cú pháp, chưa chạy thực tế.
- [ ] Kiểm thử CORS và HTTPS với URL API công khai.
- [ ] Chạy Alembic/API trên một project Supabase PostgreSQL thật; hiện chỉ có cấu hình driver/URL, chưa có credentials/instance để xác minh.
- [ ] Kiểm thử giao diện thủ công trên Chrome ở nhiều kích thước màn hình.
- [ ] Rà soát nội dung nhánh và công thức SafetyScore/RiskScore với nhóm/giảng viên.
- [ ] Deploy online; cần tài khoản/secret/hosting của nhóm.

Không ghi Pass cho các mục chưa thực thi. Xem `docs/DECISIONS.md` và `docs/DEPLOYMENT_HANDOFF.md` để biết các quyết định và điều kiện cần cho nghiệm thu.
