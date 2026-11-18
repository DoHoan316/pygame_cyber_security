# Quyết định triển khai và khác biệt so với tài liệu phân công

1. **Giữ 30 tình huống V2:** theo lựa chọn đã xác nhận của chủ dự án, không cắt về 16 tình huống trong quy mô đề xuất của tài liệu phân công. Bốn chiến dịch là cách tổ chức lại nội dung; toàn bộ 30 mã `SCEN_01`–`SCEN_30` được giữ.
2. **Bốn chiến dịch:** Phishing và lừa đảo trực tuyến (5); Wi-Fi, thiết bị và an toàn kết nối (6); Tài khoản, mật khẩu và kiểm soát truy cập (8); Bảo vệ dữ liệu và ứng phó social engineering (11).
3. **Lựa chọn gốc:** mỗi tình huống V2 giữ 4 lựa chọn để không mất nội dung. Tài liệu phân công V1 đề xuất 2–3 lựa chọn cho 16 tình huống; quyết định giữ nguyên V2 được ưu tiên theo xác nhận mới nhất.
4. **Nhánh:** seed hiện tại có nhánh hội tụ/đi tắt dựa trên lựa chọn; mọi cạnh nằm trong cùng chiến dịch, tiến về trước và có đường kết thúc. Nhánh được sinh theo quy tắc kỹ thuật ban đầu và cần được nhóm rà soát nội dung trước nghiệm thu.
5. **Scoring:** `score_delta` dương của V2 chuyển thành `safety_points`; âm chuyển thành `risk_points` dương. SafetyScore/RiskScore chuẩn hóa theo tổng điểm hai loại. Tài liệu phân công yêu cầu chuẩn hóa nhưng không nêu công thức số cụ thể, vì vậy đây là quyết định triển khai cần nhóm xác nhận.
6. **Giao diện:** có web Player/Admin để kiểm thử API và trải nghiệm end-to-end ở trình duyệt. Pygame gốc được giữ nguyên nhưng chưa được chuyển đổi sang API session mới; Pygbag build chưa được xác minh.
7. **Database:** SQLite dùng local; Alembic quản lý schema. Có thể chuyển sang PostgreSQL/Supabase qua `DATABASE_URL`; chưa xác minh trên instance Supabase thật.
