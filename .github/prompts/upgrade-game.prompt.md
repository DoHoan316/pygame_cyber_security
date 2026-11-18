---
description: 'Nâng cấp và mở rộng Game Mô Phỏng An Toàn Thông Tin (Pygame + FastAPI)'
agent: 'agent'
---
Bạn là Senior Python Game Developer & Cybersecurity Specialist. Hãy kiểm tra toàn bộ workspace hiện tại trước khi chỉnh sửa.

## Quy tắc bắt buộc (Strict Constraints)
1. **Tiếng Việt có dấu chuẩn UTF-8**: Mọi chuỗi hiển thị trên UI phải dùng tiếng Việt có dấu tự nhiên. Luôn load font từ `game_client/assets/fonts/font_regular.ttf` và `font_bold.ttf` (không dùng `SysFont` mặc định vì sẽ lỗi font khi build WebAssembly/Pygbag).
2. **Tương thích Pygbag (WebAssembly)**: Vòng lặp game trong `game_client/main.py` bắt buộc chạy bất đồng bộ (`async def run()`) và có `await asyncio.sleep(0)` ở mỗi frame. Không dùng thư viện chặn luồng (blocking) bên trong vòng lặp render.
3. **Cấu trúc câu hỏi**: Mỗi tình huống trong `game_client/data/scenarios.py` phải có đúng **4 lựa chọn (A, B, C, D)**, gắn với trụ cột CIA (Confidentiality, Integrity, Availability), có `score_delta`, `risk`, `mistake_tag` và `feedback` giải thích chi tiết.
4. **Kiến trúc Cầu nối (`GameBridgeService`)**: Mọi thao tác lưu điểm, đăng nhập, lấy bảng xếp hạng phải đi qua `game_client/services/api_service.py` để đảm bảo tự động fallback về JSON local khi offline.
5. **Kiểm thử sau khi sửa**: Sau khi chỉnh sửa code, hãy chạy kiểm tra cú pháp (`python -m py_compile`) trên tất cả các file `.py` đã thay đổi để đảm bảo không có lỗi runtime.
