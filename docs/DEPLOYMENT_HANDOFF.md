# Deployment handoff — chưa triển khai

## Backend
1. Tạo PostgreSQL project (ví dụ Supabase) và lấy connection string dạng SQLAlchemy PostgreSQL.
2. Cấu hình `DATABASE_URL`, `JWT_SECRET_KEY` (random >=32 chars), `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `CORS_ORIGINS` trong environment variables của host.
3. Cài dependencies từ `requirements.txt`.
4. Chạy `alembic upgrade head` trong thư mục dự án để áp dụng migration.
5. Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` (điều chỉnh cú pháp biến PORT theo nền tảng).
6. Kiểm tra `/api/health`, `/docs`, đăng ký Player, đăng nhập Admin và kiểm tra 403 khi Player gọi API Admin.

## Web
- Web tĩnh được FastAPI phục vụ tại `/app/`; khi dùng chung origin không cần cấu hình CORS thêm.
- Nếu tách frontend, cập nhật `API` trong `admin_web/js/app.js` và CORS allowlist.

## Pygbag
- Chưa có build WebAssembly được xác minh trong gói này.
- Trước deploy phải hoàn tất tích hợp Pygame client với API session v3, chạy `pygbag game_client` theo đúng cấu trúc entrypoint được kiểm thử, kiểm tra asset/font, token và HTTPS/CORS trên URL thật.

## Release gate
Không công bố URL là nghiệm thu cho đến khi kiểm thử end-to-end từ đăng ký/đăng nhập, chơi một chiến dịch, reload ở FEEDBACK, hoàn tất, dashboard, leaderboard và quyền Admin. Lưu log/ảnh bằng chứng; không đánh dấu PASS nếu chưa thực thi.
