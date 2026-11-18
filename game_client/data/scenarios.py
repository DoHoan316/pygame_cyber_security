# -*- coding: utf-8 -*-
# Bộ 30 tình huống mô phỏng An toàn thông tin đa dạng chủ đề (Mỗi câu 4 đáp án A, B, C, D)

SCENARIOS = [
    {
        "id": "SCEN_01",
        "category": "Email Phishing",
        "title": "Câu 1: Email thông báo khóa tài khoản ngân hàng",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn nhận email từ 'support@vietcombank-verify-security.com' báo tài khoản sẽ bị khóa sau 2 giờ nếu không bấm vào liên kết để xác thực mật khẩu và mã OTP.",
        "choices": [
            {"text": "A. Bấm ngay vào liên kết và nhập mật khẩu cùng mã OTP để tránh bị khóa.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Click link Phishing & Lộ mã OTP", "feedback": "Sai lầm! Tên miền giả mạo tinh vi. Ngân hàng không bao giờ yêu cầu nhập OTP qua liên kết email."},
            {"text": "B. Kiểm tra kỹ địa chỉ người gửi, xóa email và tự mở ứng dụng ngân hàng chính thức để kiểm tra.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chính xác! Luôn truy cập qua ứng dụng hoặc website chính thức thay vì bấm link lạ."},
            {"text": "C. Trả lời lại email để hỏi nhân viên ngân hàng xem thông báo này có thật không.", "score_delta": -20, "risk": "RỦI RO TRUNG BÌNH", "mistake_tag": "Tương tác với địa chỉ email lừa đảo", "feedback": "Không nên! Việc phản hồi giúp kẻ gian xác nhận email của bạn đang hoạt động để tiếp tục tấn công."},
            {"text": "D. Chuyển tiếp email này vào nhóm chat công ty để mọi người cùng bấm thử xem sao.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Phát tán liên kết độc hại cho người khác", "feedback": "Rất nguy hiểm! Bạn có thể vô tình khiến đồng nghiệp sập bẫy lừa đảo."}
        ]
    },
    {
        "id": "SCEN_02",
        "category": "Wi-Fi Công Cộng",
        "title": "Câu 2: Điểm phát Wi-Fi miễn phí tại quán cà phê",
        "cia_pillar": "Integrity & Confidentiality",
        "description": "Tại quán cà phê, bạn thấy 2 mạng Wi-Fi không mật khẩu: 'Cafe_Free_Wifi' và 'Cafe_Free_5G_VIP'. Bạn đang cần chuyển khoản gấp cho đối tác.",
        "choices": [
            {"text": "A. Kết nối ngay vào 'Cafe_Free_5G_VIP' vì tốc độ cao và thực hiện chuyển khoản.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Dính bẫy Wi-Fi giả mạo (Evil Twin)", "feedback": "Nguy hiểm! Tin tặc thường lập điểm phát Wi-Fi giả (Evil Twin) để nghe lén lưu lượng (MITM)."},
            {"text": "B. Tắt Wi-Fi, chuyển sang dùng dữ liệu di động 4G/5G cá nhân để giao dịch ngân hàng.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Tuyệt vời! Mạng di động 4G/5G có cơ chế mã hóa riêng, an toàn hơn nhiều so với Wi-Fi công cộng."},
            {"text": "C. Kết nối thử cả hai mạng xem mạng nào vào được web nhanh hơn thì dùng.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Kết nối bừa bãi vào mạng không mã hóa", "feedback": "Không an toàn! Thiết bị của bạn có thể bị quét cổng hoặc đánh cắp cookie phiên đăng nhập."},
            {"text": "D. Dùng Wi-Fi miễn phí nhưng mở trình duyệt ẩn danh (Incognito) để chuyển khoản.", "score_delta": -20, "risk": "RỦI RO TRUNG BÌNH", "mistake_tag": "Hiểu nhầm tác dụng của chế độ ẩn danh", "feedback": "Sai lầm! Chế độ ẩn danh chỉ không lưu lịch sử trên máy, không mã hóa dữ liệu truyền qua Wi-Fi."}
        ]
    },
    {
        "id": "SCEN_03",
        "category": "Social Engineering",
        "title": "Câu 3: Cuộc gọi giả danh cán bộ Công an điều tra",
        "cia_pillar": "Availability & Confidentiality",
        "description": "Một số lạ gọi đến tự xưng là Công an, thông báo bạn liên quan đến đường dây rửa tiền và yêu cầu cài ứng dụng 'DichVuCong_BoCongAn.apk' ngoài Google Play để xác minh.",
        "choices": [
            {"text": "A. Lo sợ, tải file .apk về cài đặt và cấp quyền Trợ năng (Accessibility) theo hướng dẫn.", "score_delta": -80, "risk": "THẢM HỌA", "mistake_tag": "Cài file APK lạ chiếm quyền điều khiển điện thoại", "feedback": "Mất quyền kiểm soát! Mã độc qua quyền Accessibility sẽ đọc trộm OTP và tự động rút sạch tiền."},
            {"text": "B. Cúp máy ngay lập tức, tuyệt đối không cài file lạ và báo cáo cho cơ quan công an địa phương.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Xuất sắc! Cơ quan nhà nước không làm việc qua điện thoại và không bao giờ yêu cầu cài file APK."},
            {"text": "C. Đọc số CCCD và số tài khoản ngân hàng qua điện thoại để họ kiểm tra giúp cho nhanh.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Tiết lộ thông tin định danh nhạy cảm qua điện thoại", "feedback": "Sai lầm! Kẻ gian sẽ dùng thông tin này để mạo danh hoặc mở tài khoản/vay tín dụng trái phép."},
            {"text": "D. Tải file .apk về máy tính trước để mở thử xem bên trong có gì.", "score_delta": -10, "risk": "RỦI RO THẤP", "mistake_tag": "Tải tệp tin không rõ nguồn gốc về thiết bị", "feedback": "Không cần thiết và tiềm ẩn rủi ro nếu vô tình kích hoạt trên trình giả lập."}
        ]
    },
    {
        "id": "SCEN_04",
        "category": "Quản Lý Mật Khẩu",
        "title": "Câu 4: Sử dụng lại mật khẩu cho nhiều tài khoản",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn vừa được cấp tài khoản hệ thống nội bộ công ty. Để dễ nhớ, bạn định dùng lại mật khẩu đang sử dụng cho Facebook và Gmail cá nhân.",
        "choices": [
            {"text": "A. Dùng chung một mật khẩu cho tất cả tài khoản để khỏi phải ghi nhớ nhiều.", "score_delta": -40, "risk": "RỦI RO CAO", "mistake_tag": "Dùng chung mật khẩu (Credential Stuffing)", "feedback": "Rủi ro lớn! Nếu một dịch vụ bị rò rỉ dữ liệu, tin tặc sẽ dùng mật khẩu đó để chiếm toàn bộ tài khoản khác."},
            {"text": "B. Tạo mật khẩu mạnh độc nhất, lưu vào Trình quản lý mật khẩu và bật xác thực 2 lớp (2FA).", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chuẩn bảo mật! Mật khẩu riêng biệt kết hợp 2FA ngăn chặn gần như tuyệt đối nguy cơ chiếm đoạt."},
            {"text": "C. Dùng mật khẩu cũ nhưng thêm số '123' hoặc năm sinh vào cuối cho khác đi.", "score_delta": -20, "risk": "RỦI RO TRUNG BÌNH", "mistake_tag": "Đặt mật khẩu theo quy luật dễ đoán", "feedback": "Quá yếu! Các công cụ dò mật khẩu tự động dễ dàng đoán ra các biến thể thêm số đơn giản."},
            {"text": "D. Ghi mật khẩu ra giấy nhớ (Sticky Note) rồi dán ngay lên cạnh màn hình máy tính.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Lộ mật khẩu vật lý nơi công cộng", "feedback": "Mất an toàn vật lý! Bất kỳ ai đi ngang qua bàn làm việc cũng có thể nhìn thấy mật khẩu của bạn."}
        ]
    },
    {
        "id": "SCEN_05",
        "category": "Bảo Mật Vật Lý & USB",
        "title": "Câu 5: Nhặt được USB lạ ở bãi đỗ xe công ty",
        "cia_pillar": "Integrity & Availability",
        "description": "Trên đường đi làm vào văn phòng, bạn nhặt được một chiếc USB có dán nhãn 'Bảng Lương Thưởng Quý 4'.",
        "choices": [
            {"text": "A. Cắm ngay vào máy tính công ty để xem bên trong có danh sách lương không.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Dính bẫy USB Drop Attack / Mã độc BadUSB", "feedback": "Sập bẫy kinh điển! Tin tặc cố tình thả USB chứa mã độc (BadUSB/Ransomware) để xâm nhập mạng nội bộ."},
            {"text": "B. Tuyệt đối không cắm vào bất kỳ máy nào, bàn giao ngay cho bộ phận IT / An ninh thông tin.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chính xác! Bộ phận IT có môi trường cách ly (Sandbox) chuyên dụng để xử lý thiết bị lạ."},
            {"text": "C. Mang về nhà cắm vào máy tính cá nhân của mình để kiểm tra trước cho an toàn.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Cắm thiết bị lạ vào máy tính cá nhân", "feedback": "Vẫn rất nguy hiểm! Máy cá nhân của bạn sẽ bị nhiễm mã độc đánh cắp dữ liệu hoặc tống tiền."},
            {"text": "D. Cắm vào máy tính của đồng nghiệp ngồi bên cạnh để nhờ mở giúp.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Gây nguy hiểm cho thiết bị của đồng nghiệp", "feedback": "Hành động này sẽ lây nhiễm mã độc sang máy đồng nghiệp và lan ra toàn mạng nội bộ."}
        ]
    },
    {
        "id": "SCEN_06",
        "category": "Mã Độc Tống Tiền",
        "title": "Câu 6: Tệp đính kèm hóa đơn dạng .zip / .exe",
        "cia_pillar": "Availability (Tính Sẵn Sàng)",
        "description": "Một khách hàng lạ gửi email đính kèm tệp 'HoaDon_ThanhToan.pdf.exe' và giục bạn mở ngay để đối chiếu công nợ.",
        "choices": [
            {"text": "A. Nhấp đúp mở tệp ngay vì thấy có chữ '.pdf' ở tên tệp.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Mở tệp thực thi giả mạo đuôi kép (.pdf.exe)", "feedback": "Nguy hiểm! Đuôi thật của tệp là '.exe' (chương trình chạy), thường chứa Ransomware mã hóa toàn bộ ổ cứng."},
            {"text": "B. Không mở tệp, kiểm tra định dạng đuôi tệp và liên hệ xác nhận với khách hàng qua kênh chính thức.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Rất tỉnh táo! Phát hiện đuôi tệp thực thi bất thường giúp ngăn chặn mã độc tống tiền."},
            {"text": "C. Tắt phần mềm diệt virus trên máy vì sợ nó chặn nhầm tệp hóa đơn của khách.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Tắt lá chắn bảo vệ Antivirus", "feedback": "Sai lầm nghiêm trọng! Không bao giờ tắt phần mềm diệt virus để mở tệp từ nguồn không tin cậy."},
            {"text": "D. Đổi tên tệp xóa chữ '.exe' đi rồi mở bằng trình đọc PDF.", "score_delta": -10, "risk": "RỦI RO THẤP", "mistake_tag": "Xử lý thủ công tệp nghi chứa mã độc", "feedback": "Tệp không mở được vì bản chất nó là file thực thi, nhưng bạn nên xóa hẳn nó thay vì giữ lại."}
        ]
    },
    {
        "id": "SCEN_07",
        "category": "Xác Thực 2 Lớp (2FA)",
        "title": "Câu 7: Nhận thông báo duyệt đăng nhập lạ (MFA Fatigue)",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Lúc 1 giờ sáng, điện thoại bạn liên tục hiện thông báo yêu cầu bấm 'Chấp thuận' (Approve) đăng nhập tài khoản công ty dù bạn đang ngủ.",
        "choices": [
            {"text": "A. Bấm 'Chấp thuận' cho đỡ phiền để tắt tiếng chuông thông báo.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Sập bẫy tấn công dội bom xác thực (MFA Fatigue)", "feedback": "Mắc bẫy! Kẻ gian đã có mật khẩu của bạn và đang spam thông báo chờ bạn bấm nhầm chấp thuận."},
            {"text": "B. Bấm 'Từ chối' (Deny), đổi ngay mật khẩu tài khoản và báo cáo sự cố cho bộ phận IT.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Xử lý chuẩn xác! Thông báo lạ chứng tỏ mật khẩu của bạn đã bị lộ và cần đổi ngay lập tức."},
            {"text": "C. Tắt nguồn điện thoại đi ngủ tiếp, sáng mai tính sau.", "score_delta": -20, "risk": "RỦI RO TRUNG BÌNH", "mistake_tag": "Chậm trễ xử lý khi mật khẩu đã bị lộ", "feedback": "Chưa đủ an toàn! Kẻ gian vẫn đang nắm mật khẩu của bạn và có thể tiếp tục tìm cách tấn công."},
            {"text": "D. Gỡ bỏ ứng dụng xác thực 2FA để không bị làm phiền vào ban đêm.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Gỡ bỏ lớp bảo vệ 2FA", "feedback": "Tự mở cửa cho kẻ trộm! Gỡ 2FA sẽ khiến kẻ gian đăng nhập thẳng vào tài khoản bằng mật khẩu đã lộ."}
        ]
    },
    {
        "id": "SCEN_08",
        "category": "Bảo Mật Mạng Xã Hội",
        "title": "Câu 8: Tin nhắn mượn tiền từ tài khoản Facebook người thân",
        "cia_pillar": "Confidentiality & Integrity",
        "description": "Tài khoản Facebook của người thân nhắn tin hỏi mượn gấp 5 triệu đồng và gửi số tài khoản ngân hàng mang tên một người lạ.",
        "choices": [
            {"text": "A. Chuyển khoản ngay vì nghĩ người thân đang gặp chuyện khẩn cấp.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Chuyển tiền cho tài khoản mạng xã hội bị chiếm quyền", "feedback": "Mất tiền oan! Kẻ gian thường chiếm quyền Facebook rồi nhắn tin mượn tiền hàng loạt danh sách bạn bè."},
            {"text": "B. Gọi điện thoại trực tiếp qua số di động (không gọi qua Messenger) để xác nhận giọng nói.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chính xác! Xác minh qua cuộc gọi di động truyền thống là cách chắc chắn nhất."},
            {"text": "C. Nhắn tin hỏi lại trên chính khung chat Messenger đó: 'Có đúng là bạn không?'.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Xác minh trên chính kênh đang bị chiếm quyền", "feedback": "Vô ích! Kẻ gian đang cầm tài khoản đó nên chắc chắn sẽ trả lời 'Đúng là mình đây'."},
            {"text": "D. Chuyển trước 1 triệu đồng xem họ có nhận được không rồi mới chuyển tiếp.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Chuyển tiền thử nghiệm cho kẻ lừa đảo", "feedback": "Vẫn mất 1 triệu đồng! Không chuyển bất kỳ khoản nào khi chưa xác minh qua kênh độc lập."}
        ]
    },
    {
        "id": "SCEN_09",
        "category": "Mã QR Độc Hại (Quishing)",
        "title": "Câu 9: Quét mã QR dán đè ở trạm sạc / bãi gửi xe",
        "cia_pillar": "Confidentiality & Integrity",
        "description": "Tại bãi giữ xe công cộng, bạn thấy một mã QR thanh toán được in trên giấy dán đè lên biển bảng gốc, dẫn tới một trang web lạ yêu cầu nhập thông tin thẻ.",
        "choices": [
            {"text": "A. Quét mã và nhập số thẻ tín dụng cùng mã CVV để thanh toán nhanh.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Dính bẫy tấn công mã QR giả mạo (Quishing)", "feedback": "Sập bẫy Quishing! Kẻ gian thường dán đè mã QR giả để dẫn nạn nhân tới trang web đánh cắp thẻ."},
            {"text": "B. Kiểm tra bề mặt tem dán, xem kỹ đường link hiện ra trước khi mở và hỏi nhân viên quản lý.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Rất cẩn trọng! Luôn kiểm tra tên miền đích của mã QR trước khi thực hiện giao dịch."},
            {"text": "C. Quét thử bằng camera điện thoại rồi bấm mở mọi đường link hiện ra để xem giao diện.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Mở liên kết không rõ nguồn gốc từ mã QR", "feedback": "Rủi ro! Trang web độc hại có thể tự động tải mã độc hoặc khai thác lỗ hổng trình duyệt."},
            {"text": "D. Dùng tài khoản ngân hàng phụ nhưng vẫn nhập mật khẩu ngân hàng vào trang web đó.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Nhập thông tin đăng nhập vào trang web giả mạo", "feedback": "Kẻ gian sẽ lấy được thông tin đăng nhập của bạn ngay khi bạn gõ vào trang giả mạo."}
        ]
    },
    {
        "id": "SCEN_10",
        "category": "Sao Lưu Dữ Liệu",
        "title": "Câu 10: Chiến lược sao lưu dữ liệu quan trọng (Backup)",
        "cia_pillar": "Availability (Tính Sẵn Sàng)",
        "description": "Bạn đang lưu trữ khóa luận tốt nghiệp và toàn bộ dữ liệu dự án quan trọng chỉ trên duy nhất ổ cứng laptop cá nhân.",
        "choices": [
            {"text": "A. Không cần sao lưu vì laptop mới mua rất bền, khó hỏng.", "score_delta": -40, "risk": "RỦI RO CAO", "mistake_tag": "Không có bản sao lưu dữ liệu (Single Point of Failure)", "feedback": "Rất rủi ro! Ổ cứng có thể hỏng bất ngờ, mất máy hoặc bị mã độc tống tiền khóa toàn bộ."},
            {"text": "B. Áp dụng quy tắc 3-2-1: Lưu 3 bản sao, trên 2 loại phương tiện khác nhau và 1 bản trên Cloud.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chuẩn mực vàng! Quy tắc 3-2-1 đảm bảo bạn luôn khôi phục được dữ liệu trong mọi thảm họa."},
            {"text": "C. Copy thêm 1 thư mục nữa ngay trên cùng ổ đĩa C của laptop đó.", "score_delta": -20, "risk": "RỦI RO TRUNG BÌNH", "mistake_tag": "Sao lưu trên cùng một ổ cứng vật lý", "feedback": "Không hiệu quả! Nếu ổ cứng hỏng hoặc dính Ransomware, cả hai thư mục đều mất sạch."},
            {"text": "D. Gửi toàn bộ dữ liệu mật của công ty lên một trang web chia sẻ công khai không đặt mật khẩu.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Làm rò rỉ dữ liệu lên nền tảng công khai", "feedback": "Vi phạm bảo mật! Dữ liệu nhạy cảm phải được mã hóa và phân quyền truy cập chặt chẽ."}
        ]
    },
    {
        "id": "SCEN_11",
        "category": "Cập Nhật Phần Mềm",
        "title": "Câu 11: Thông báo cập nhật bản vá bảo mật hệ điều hành",
        "cia_pillar": "Integrity & Availability",
        "description": "Windows / macOS thông báo có bản cập nhật bảo mật quan trọng (Security Patch), nhưng bạn đang bận làm việc.",
        "choices": [
            {"text": "A. Tắt vĩnh viễn dịch vụ cập nhật (Windows Update) để máy không bao giờ khởi động lại.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Vô hiệu hóa bản vá lỗ hổng bảo mật", "feedback": "Cực kỳ nguy hiểm! Tin tặc thường khai thác các lỗ hổng đã công bố trên những máy chưa cập nhật."},
            {"text": "B. Hẹn giờ cập nhật vào cuối ngày làm việc (ngoài giờ) và tiến hành khởi động lại để vá lỗi.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Hợp lý và an toàn! Vừa không gián đoạn công việc, vừa đảm bảo hệ thống được vá lỗi kịp thời."},
            {"text": "C. Bấm 'Nhắc lại sau' liên tục trong suốt 6 tháng liền.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Trì hoãn cập nhật bảo mật quá lâu", "feedback": "Thiết bị của bạn sẽ tồn tại hàng loạt lỗ hổng đã biết (Known Vulnerabilities)."},
            {"text": "D. Tải các bản 'Crack / Patch' trôi nổi trên mạng về chạy thay cho cập nhật chính hãng.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Cài đặt công cụ bẻ khóa chứa mã độc", "feedback": "Phần lớn công cụ crack đều được cấy sẵn Trojan hoặc phần mềm đào tiền ảo ngầm."}
        ]
    },
    {
        "id": "SCEN_12",
        "category": "Quyền Riêng Tư & AI",
        "title": "Câu 12: Nhập mã nguồn và dữ liệu khách hàng vào AI công cộng",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn muốn nhờ một công cụ AI trực tuyến miễn phí sửa lỗi đoạn code có chứa API Key thật và danh sách email khách hàng của công ty.",
        "choices": [
            {"text": "A. Dán nguyên văn toàn bộ đoạn code kèm API Key và dữ liệu khách hàng lên AI để sửa cho nhanh.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Rò rỉ bí mật kinh doanh & API Key lên AI công cộng", "feedback": "Vi phạm nghiêm trọng! Dữ liệu nhập vào bản miễn phí có thể được dùng để huấn luyện mô hình."},
            {"text": "B. Xóa hoặc thay thế toàn bộ API Key và dữ liệu thật bằng dữ liệu giả (Mock data) trước khi hỏi AI.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Tuyệt vời! Ẩn danh hóa dữ liệu (Data Masking) giúp tận dụng AI mà vẫn bảo mật tuyệt đối."},
            {"text": "C. Chỉ xóa tên khách hàng nhưng vẫn giữ nguyên API Key thật vì nghĩ AI không biết dùng.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Làm lộ khóa truy cập hệ thống (API Key)", "feedback": "API Key là chìa khóa truy cập thẳng vào dịch vụ/database, tuyệt đối không đưa lên mạng."},
            {"text": "D. Đăng tải cả file cấu hình `.env` lên diễn đàn hỏi đáp công cộng.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Công khai tệp cấu hình chứa thông tin nhạy cảm", "feedback": "Bot quét tự động của hacker sẽ thu thập `.env` chỉ trong vài giây sau khi bạn đăng."}
        ]
    },
    {
        "id": "SCEN_13",
        "category": "Bảo Mật Nơi Làm Việc",
        "title": "Câu 13: Rời khỏi bàn làm việc đi ăn trưa",
        "cia_pillar": "Confidentiality & Integrity",
        "description": "Đến giờ nghỉ trưa, bạn rời bàn làm việc trong 45 phút. Trên màn hình laptop đang mở sẵn email công ty và hệ thống quản trị.",
        "choices": [
            {"text": "A. Cứ để nguyên màn hình như vậy vì xung quanh toàn đồng nghiệp thân thiết.", "score_delta": -40, "risk": "RỦI RO CAO", "mistake_tag": "Không khóa màn hình khi rời khỏi vị trí", "feedback": "Vi phạm chính sách Clean Desk! Người lạ hoặc kẻ xấu có thể tranh thủ thao tác trên máy bạn."},
            {"text": "B. Nhấn tổ hợp phím khóa màn hình ngay lập tức (Windows + L hoặc Cmd + Ctrl + Q) trước khi đứng dậy.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Thói quen vàng! Khóa màn hình mất 1 giây nhưng bảo vệ toàn bộ phiên làm việc của bạn."},
            {"text": "C. Chỉ thu nhỏ cửa sổ trình duyệt xuống thanh Taskbar rồi đi ăn.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Thu nhỏ cửa sổ thay vì khóa phiên đăng nhập", "feedback": "Bất kỳ ai chỉ cần bấm chuột vào thanh Taskbar là mở lại được toàn bộ dữ liệu."},
            {"text": "D. Nhờ một thực tập sinh mới vào ngồi trông máy hộ.", "score_delta": -20, "risk": "RỦI RO TRUNG BÌNH", "mistake_tag": "Giao quyền truy cập tài khoản cá nhân cho người khác", "feedback": "Mỗi nhân viên phải tự chịu trách nhiệm với tài khoản của mình, không nhờ người khác trông hộ."}
        ]
    },
    {
        "id": "SCEN_14",
        "category": "SMS Phishing (Smishing)",
        "title": "Câu 14: Tin nhắn SMS brandname giả mạo thông báo trúng thưởng / phạt nguội",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn nhận tin nhắn SMS nằm chung luồng tin nhắn ngân hàng với nội dung: 'Ban co bien ban phat nguoi, truy cap http://csgt-vn-tra-cuu.xyz de xem chi tiet'.",
        "choices": [
            {"text": "A. Bấm ngay vào đường link vì thấy tin nhắn nằm chung mục với tin nhắn thật.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Mắc bẫy trạm phát sóng giả (Fake BTS / Smishing)", "feedback": "Cảnh giác! Kẻ gian dùng trạm BTS giả để phát tán SMS giả mạo brandname, tên miền '.xyz' là giả."},
            {"text": "B. Không bấm link, tự mở trình duyệt truy cập cổng thông tin chính thức của Cục CSGT (.gov.vn).", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chính xác! Trang web cơ quan nhà nước Việt Nam luôn dùng tên miền '.gov.vn'."},
            {"text": "C. Nhập biển số xe và số thẻ ngân hàng lên trang web đó để nộp phạt cho nhanh.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Nộp tiền và lộ thông tin thẻ trên web giả mạo", "feedback": "Bạn sẽ mất toàn bộ số tiền trong thẻ ngân hàng ngay lập tức."},
            {"text": "D. Gửi tin nhắn SMS phản hồi lại số điện thoại đó để chửi kẻ lừa đảo.", "score_delta": -10, "risk": "RỦI RO THẤP", "mistake_tag": "Phản hồi tin nhắn rác/lừa đảo", "feedback": "Không nên tương tác; hãy báo cáo tin nhắn rác tới tổng đài 156 hoặc 5656."}
        ]
    },
    {
        "id": "SCEN_15",
        "category": "An Toàn Trình Duyệt",
        "title": "Câu 15: Cảnh báo chứng chỉ bảo mật SSL/HTTPS không hợp lệ",
        "cia_pillar": "Integrity & Confidentiality",
        "description": "Khi truy cập một trang web giao dịch, trình duyệt hiện màn hình đỏ cảnh báo: 'Kết nối của bạn không phải là kết nối riêng tư (NET::ERR_CERT_AUTHORITY_INVALID)'.",
        "choices": [
            {"text": "A. Bấm 'Nâng cao -> Tiếp tục truy cập (không an toàn)' để vào trang web bằng được.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Bỏ qua cảnh báo chứng chỉ bảo mật HTTPS/SSL", "feedback": "Nguy hiểm! Cảnh báo này thường xuất hiện khi bạn đang bị tấn công xen giữa (MITM) hoặc web giả."},
            {"text": "B. Dừng truy cập ngay lập tức, kiểm tra lại đường truyền mạng và tên miền trang web.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Đúng đắn! Không bao giờ vượt qua cảnh báo chứng chỉ bảo mật trên các trang yêu cầu đăng nhập."},
            {"text": "C. Tắt tường lửa (Firewall) trên máy tính để trình duyệt không hiện cảnh báo nữa.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Tắt tường lửa bảo vệ hệ thống", "feedback": "Sai hoàn toàn! Tắt tường lửa khiến máy tính phơi bày trước mọi cuộc tấn công mạng."},
            {"text": "D. Đổi sang trình duyệt khác cũ hơn để không bị chặn cảnh báo.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Dùng trình duyệt lỗi thời để né cơ chế bảo vệ", "feedback": "Trình duyệt cũ thiếu các cơ chế bảo vệ hiện đại, khiến bạn dễ bị khai thác lỗ hổng hơn."}
        ]
    },
    {
        "id": "SCEN_16",
        "category": "Quản Lý Quyền Ứng Dụng",
        "title": "Câu 16: Ứng dụng chỉnh sửa ảnh đòi quyền đọc tin nhắn SMS & Danh bạ",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn vừa cài một ứng dụng ghép ảnh miễn phí trên điện thoại. Khi mở lên, ứng dụng yêu cầu cấp quyền truy cập Tin nhắn SMS, Nhật ký cuộc gọi và Danh bạ.",
        "choices": [
            {"text": "A. Bấm 'Cho phép tất cả' cho nhanh để vào chỉnh ảnh.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Cấp quyền quá mức cho ứng dụng (Over-privileged App)", "feedback": "Rủi ro lớn! Ứng dụng chỉnh ảnh không cần đọc SMS (nơi chứa mã OTP) hay danh bạ của bạn."},
            {"text": "B. Từ chối các quyền vô lý này, chỉ cấp quyền truy cập Ảnh/Thư viện hoặc gỡ bỏ ứng dụng.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chuẩn nguyên tắc đặc quyền tối thiểu (Least Privilege)! Chỉ cấp đúng quyền cần thiết."},
            {"text": "C. Cho phép tạm thời rồi để nguyên như vậy dùng hàng tháng trời.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Quên thu hồi quyền truy cập nhạy cảm", "feedback": "Trong thời gian đó ứng dụng có thể âm thầm thu thập toàn bộ danh bạ và tin nhắn gửi về máy chủ lạ."},
            {"text": "D. Cấp quyền Quản trị thiết bị (Device Admin) cho ứng dụng chỉnh ảnh.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Cấp quyền quản trị thiết bị cho ứng dụng không rõ nguồn gốc", "feedback": "Cấp quyền Device Admin sẽ khiến bạn không thể gỡ cài đặt ứng dụng nếu nó là mã độc."}
        ]
    },
    {
        "id": "SCEN_17",
        "category": "An Toàn Email Công Việc",
        "title": "Câu 17: Gửi danh sách khách hàng cho nhiều đối tác cùng lúc",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn cần gửi email thông báo sự kiện tới 200 khách hàng VIP bên ngoài công ty.",
        "choices": [
            {"text": "A. Nhập toàn bộ 200 địa chỉ email vào ô 'To' hoặc 'CC' rồi bấm gửi.", "score_delta": -40, "risk": "RỦI RO CAO", "mistake_tag": "Lộ danh sách email khách hàng do dùng CC thay vì BCC", "feedback": "Lỗi bảo mật phổ biến! Tất cả 200 khách hàng sẽ nhìn thấy email của nhau và dễ bị spam."},
            {"text": "B. Đặt toàn bộ danh sách khách hàng vào ô 'BCC' (hoặc dùng công cụ Email Marketing chuyên dụng).", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chính xác! Dùng BCC giúp ẩn danh sách người nhận, bảo vệ quyền riêng tư của khách hàng."},
            {"text": "C. Đính kèm file Excel chứa đầy đủ SĐT, Email và địa chỉ của 200 khách hàng vào email gửi chung.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Phát tán dữ liệu cá nhân (PII) hàng loạt", "feedback": "Vi phạm nghiêm trọng quy định bảo vệ dữ liệu cá nhân (PDPD/GDPR)!"},
            {"text": "D. Dùng email cá nhân miễn phí để gửi thay vì email tên miền công ty.", "score_delta": -20, "risk": "RỦI RO TRUNG BÌNH", "mistake_tag": "Dùng email cá nhân cho giao dịch công việc", "feedback": "Thiếu chuyên nghiệp, dễ rơi vào hòm thư rác (Spam) và không kiểm soát được dữ liệu công ty."}
        ]
    },
    {
        "id": "SCEN_18",
        "category": "Bảo Mật Thiết Bị Di Động",
        "title": "Câu 18: Sạc pin điện thoại qua cổng USB công cộng ở sân bay",
        "cia_pillar": "Confidentiality & Integrity",
        "description": "Điện thoại sắp hết pin ở sân bay, bạn thấy một trụ sạc chỉ có sẵn đầu dây cáp USB (không có ổ cắm điện 220V).",
        "choices": [
            {"text": "A. Cắm thẳng cáp USB đó vào điện thoại và bấm 'Tin cậy máy tính này' (Trust) khi màn hình hỏi.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Dính tấn công truyền mã độc qua cáp sạc (Juice Jacking)", "feedback": "Sập bẫy Juice Jacking! Cáp USB vừa truyền điện vừa truyền dữ liệu, có thể cài mã độc vào máy."},
            {"text": "B. Dùng pin sạc dự phòng cá nhân, hoặc dùng củ sạc riêng cắm vào ổ điện 220V (hoặc USB Data Blocker).", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "An toàn tuyệt đối! Tách biệt đường truyền dữ liệu giúp ngăn chặn mọi rủi ro qua cổng sạc."},
            {"text": "C. Cắm vào dây cáp USB công cộng và mở khóa màn hình suốt quá trình sạc.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Mở khóa thiết bị khi kết nối cổng USB lạ", "feedback": "Khi màn hình mở khóa, cổng USB có quyền truy cập trực tiếp vào hệ thống tệp của điện thoại."},
            {"text": "D. Mượn laptop của một người lạ ngồi cạnh để cắm nhờ sạc qua cổng USB.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Kết nối thiết bị cá nhân với máy tính người lạ", "feedback": "Máy tính của người lạ có thể tự động sao lưu ảnh hoặc cài phần mềm gián điệp sang máy bạn."}
        ]
    },
    {
        "id": "SCEN_19",
        "category": "Social Engineering (Vishing)",
        "title": "Câu 19: Nhân viên 'Bộ phận IT' gọi điện xin mật khẩu để nâng cấp hệ thống",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Có người gọi tới bàn làm việc tự xưng là nhân viên IT mới, nói cần mật khẩu đăng nhập máy tính của bạn để cài phần mềm từ xa.",
        "choices": [
            {"text": "A. Đọc ngay mật khẩu cho họ vì nghĩ nhân viên IT có quyền biết mật khẩu mọi người.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Chia sẻ mật khẩu cho người tự xưng là IT", "feedback": "Nguyên tắc bất di bất dịch: Nhân viên IT thật KHÔNG BAO GIỜ hỏi mật khẩu của người dùng."},
            {"text": "B. Từ chối cung cấp mật khẩu, yêu cầu họ tạo phiếu hỗ trợ (Ticket) chính thức và xác minh lại với trưởng phòng IT.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chính xác! Đây là kỹ thuật mạo danh nội bộ (Pretexting) rất phổ biến của tin tặc."},
            {"text": "C. Nhắn tin mật khẩu qua Zalo cho họ thay vì đọc qua điện thoại cho đỡ bị nghe lén.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Gửi mật khẩu dạng văn bản rõ (Plaintext) qua chat", "feedback": "Dù gửi qua kênh nào thì việc tiết lộ mật khẩu cá nhân đều là sai lầm nghiêm trọng."},
            {"text": "D. Đổi mật khẩu thành '123456' rồi đưa cho họ dùng tạm.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Hạ cấp mật khẩu và giao quyền tài khoản", "feedback": "Kẻ gian sẽ chiếm quyền tài khoản của bạn ngay lập tức và thực hiện hành vi phá hoại."}
        ]
    },
    {
        "id": "SCEN_20",
        "category": "Thanh Toán Trực Tuyến",
        "title": "Câu 20: Lưu thông tin thẻ tín dụng trên trình duyệt và các web mua sắm lạ",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn mua hàng trên một website bán đồ giảm giá mới tìm thấy trên mạng xã hội. Trình duyệt hỏi có muốn lưu thông tin thẻ thanh toán không.",
        "choices": [
            {"text": "A. Lưu thông tin thẻ trên mọi website và bật tự động điền (Autofill) trên máy tính dùng chung.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Lưu thông tin thẻ thanh toán trên thiết bị/web không tin cậy", "feedback": "Rủi ro mất tiền rất cao nếu máy tính bị nhiễm mã độc đánh cắp dữ liệu trình duyệt (Infostealer)."},
            {"text": "B. Dùng thẻ ảo (Virtual Card) có giới hạn hạn mức, không lưu thẻ trên web lạ và bật thông báo biến động số dư.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Quá chuyên nghiệp! Thẻ ảo giới hạn hạn mức giúp khoanh vùng thiệt hại bằng 0 nếu web bị hack."},
            {"text": "C. Chụp ảnh hai mặt thẻ tín dụng lưu trong album ảnh điện thoại cho tiện gõ số khi mua hàng.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Lưu ảnh chụp thẻ tín dụng (cả mã CVV) trong thư viện ảnh", "feedback": "Nếu điện thoại bị mất hoặc đồng bộ ảnh lên đám mây bị lộ, kẻ gian có đủ thông tin để quẹt thẻ."},
            {"text": "D. Nhờ người bán hàng thanh toán hộ bằng cách gửi số thẻ và mã CVV qua tin nhắn.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Cung cấp mã bảo mật CVV cho người khác", "feedback": "Mã CVV là bí mật tuyệt đối, đưa cho người khác đồng nghĩa với việc trao ví tiền của bạn cho họ."}
        ]
    },
    {
        "id": "SCEN_21",
        "category": "An Toàn Dữ Liệu Cloud",
        "title": "Câu 21: Chia sẻ thư mục Google Drive chứa tài liệu nội bộ",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn cần gửi tài liệu báo cáo tài chính cho 3 thành viên trong ban giám đốc qua Google Drive.",
        "choices": [
            {"text": "A. Bật chế độ 'Bất kỳ ai có đường liên kết đều có thể chỉnh sửa' rồi gửi link vào nhóm.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Mở quyền truy cập công khai (Public Link) cho tài liệu mật", "feedback": "Rất nguy hiểm! Link này có thể bị lộ ra ngoài hoặc bị công cụ tìm kiếm lập chỉ mục."},
            {"text": "B. Giới hạn quyền truy cập (Restricted), chỉ thêm đích danh 3 địa chỉ email của người nhận và tắt quyền tải xuống nếu cần.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chuẩn mực kiểm soát truy cập! Chỉ đúng người được chỉ định mới có thể mở tệp."},
            {"text": "C. Để chế độ 'Bất kỳ ai có liên kết đều có thể xem' vì nghĩ chỉ xem thì không sao.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Công khai quyền xem tài liệu nhạy cảm", "feedback": "Báo cáo tài chính là dữ liệu mật, chỉ cần bị xem trộm cũng đã gây thiệt hại lớn."},
            {"text": "D. Đăng tải tệp lên một nhóm Facebook công khai rồi gắn thẻ (tag) 3 người đó vào.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Đăng tải tài liệu nội bộ lên mạng xã hội công cộng", "feedback": "Toàn bộ người dùng Internet đều có thể tải về báo cáo tài chính của công ty bạn."}
        ]
    },
    {
        "id": "SCEN_22",
        "category": "Phát Hiện Giả Mạo Deepfake",
        "title": "Câu 22: Cuộc gọi video từ 'Sếp' yêu cầu chuyển tiền gấp",
        "cia_pillar": "Integrity & Confidentiality",
        "description": "Bạn nhận cuộc gọi video ngắn (hình ảnh hơi mờ, giật lag) từ tài khoản của Giám đốc yêu cầu chuyển khoản gấp cho hợp đồng mật và dặn không được nói với ai.",
        "choices": [
            {"text": "A. Chuyển tiền ngay theo quy trình khẩn cấp vì đã nhìn thấy khuôn mặt Giám đốc trên video.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Sập bẫy lừa đảo video giả mạo (AI Deepfake)", "feedback": "Cảnh giác với Deepfake! Kẻ gian dùng AI ghép mặt và giọng nói để lừa đảo chuyển tiền."},
            {"text": "B. Tuân thủ quy trình phê duyệt tài chính của công ty, gọi lại qua số nội bộ/di động để xác nhận chéo.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Xuất sắc! Không một lệnh chuyển tiền nào được phép bỏ qua quy trình xác minh đa bước."},
            {"text": "C. Nhắn tin hỏi lại trên chính ứng dụng vừa gọi video để xác nhận.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Xác minh trên cùng nền tảng đang bị giả mạo", "feedback": "Tài khoản đó đang do kẻ gian kiểm soát, việc nhắn lại không có giá trị xác thực."},
            {"text": "D. Chuyển trước 50% số tiền để giữ uy tín với Sếp.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Thỏa hiệp quy trình bảo mật trước áp lực tâm lý", "feedback": "Kẻ gian luôn tạo áp lực khẩn cấp và bí mật để nạn nhân tự phá vỡ quy trình an toàn."}
        ]
    },
    {
        "id": "SCEN_23",
        "category": "Bảo Mật Mạng Gia Đình",
        "title": "Câu 23: Cấu hình bộ phát Wi-Fi (Router) mới mua tại nhà",
        "cia_pillar": "Confidentiality & Availability",
        "description": "Nhà mạng vừa lắp đặt cho bạn một bộ phát Wi-Fi mới. Mật khẩu quản trị trang cấu hình (192.168.1.1) đang là 'admin / admin'.",
        "choices": [
            {"text": "A. Giữ nguyên tài khoản 'admin / admin' để sau này dễ nhớ khi cần cài đặt lại.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Để mật khẩu mặc định của nhà sản xuất (Default Credentials)", "feedback": "Rất nguy hiểm! Bất kỳ ai kết nối vào Wi-Fi nhà bạn đều có thể chiếm quyền điều khiển Router và đổi DNS."},
            {"text": "B. Đổi ngay mật khẩu quản trị Router thành mật khẩu mạnh, bật chuẩn mã hóa WPA2/WPA3 cho Wi-Fi.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chính xác! Bảo vệ lớp mạng biên (Router) giúp toàn bộ thiết bị trong nhà an toàn hơn."},
            {"text": "C. Tắt mật khẩu Wi-Fi để hàng xóm dùng chung cho vui và khỏi phải nhập mật khẩu.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Mở mạng Wi-Fi không mật khẩu (Open Network)", "feedback": "Nếu người khác dùng Wi-Fi nhà bạn để thực hiện hành vi phạm pháp, bạn sẽ là người liên đới đầu tiên."},
            {"text": "D. Sử dụng chuẩn mã hóa cũ WEP vì thấy nó có chữ cái ngắn gọn.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Sử dụng giao thức mã hóa Wi-Fi lỗi thời (WEP)", "feedback": "Chuẩn WEP đã lỗi thời từ lâu và có thể bị bẻ khóa chỉ trong chưa đầy 1 phút."}
        ]
    },
    {
        "id": "SCEN_24",
        "category": "Quản Lý Thiết Bị Cũ",
        "title": "Câu 24: Bán hoặc thanh lý điện thoại / laptop cũ",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn chuẩn bị bán lại chiếc điện thoại cũ cho một cửa hàng thu mua điện thoại.",
        "choices": [
            {"text": "A. Chỉ xóa thủ công các bức ảnh nhạy cảm trong album rồi đem đi bán luôn.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Không xóa sạch dữ liệu (Factory Reset) trước khi thanh lý", "feedback": "Rất dễ bị khôi phục! Các phần mềm phục hồi dữ liệu có thể lấy lại ảnh và tin nhắn đã xóa."},
            {"text": "B. Sao lưu dữ liệu, đăng xuất toàn bộ tài khoản (iCloud/Google), mã hóa và Khôi phục cài đặt gốc (Factory Reset).", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Hoàn hảo! Quy trình xóa sạch đúng chuẩn đảm bảo dữ liệu cũ không thể bị khôi phục."},
            {"text": "C. Quên tháo thẻ SIM và thẻ nhớ microSD bên trong máy trước khi giao cho cửa hàng.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Để quên thẻ SIM (nơi nhận mã OTP ngân hàng) trong máy cũ", "feedback": "Cực kỳ nguy hiểm! Người giữ SIM của bạn có thể chiếm đoạt hàng loạt tài khoản qua OTP SMS."},
            {"text": "D. Chỉ cần đổi hình nền và xóa ứng dụng ngân hàng là đủ an toàn.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Vẫn giữ phiên đăng nhập email và mạng xã hội trên máy cũ", "feedback": "Người mua máy vẫn truy cập được vào Gmail của bạn để đặt lại mật khẩu ngân hàng."}
        ]
    },
    {
        "id": "SCEN_25",
        "category": "Tiện Ích Mở Rộng Trình Duyệt",
        "title": "Câu 25: Cài đặt Extension tải video miễn phí trên Chrome",
        "cia_pillar": "Confidentiality & Integrity",
        "description": "Bạn muốn tải video từ một trang web nên tìm kiếm và định cài một Extension không rõ tác giả, có rất ít lượt tải và yêu cầu quyền 'Đọc và thay đổi tất cả dữ liệu của bạn trên mọi trang web'.",
        "choices": [
            {"text": "A. Cài đặt ngay và bấm chấp nhận mọi quyền truy cập.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Cài tiện ích mở rộng (Extension) độc hại đánh cắp Cookie", "feedback": "Rất nguy hiểm! Extension độc hại có thể đọc trộm Cookie phiên đăng nhập Facebook/Email mà không cần mật khẩu."},
            {"text": "B. Không cài các Extension lạ ít đánh giá; chỉ dùng tiện ích từ nhà phát triển uy tín và rà soát quyền định kỳ.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chính xác! Tiện ích mở rộng trình duyệt có quyền rất sâu nên cần chọn lọc cực kỳ kỹ."},
            {"text": "C. Cài cùng lúc 10 Extension khác nhau xem cái nào tải được thì giữ lại hết.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Cài đặt tràn lan tiện ích không kiểm soát", "feedback": "Mỗi Extension là một bề mặt tấn công tiềm ẩn, cài tràn lan làm tăng nguy cơ rò rỉ dữ liệu."},
            {"text": "D. Tải tệp `.crx` trôi nổi từ một blog lạ rồi bật chế độ Nhà phát triển (Developer Mode) để cài ép.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Cài đặt tiện ích ngoài cửa hàng chính thức (Sideloading)", "feedback": "Các gói `.crx` ngoài cửa hàng không qua kiểm duyệt bảo mật của Google, rất dễ chứa mã độc."}
        ]
    },
    {
        "id": "SCEN_26",
        "category": "Phát Triển Phần Mềm An Toàn",
        "title": "Câu 26: Đẩy mã nguồn dự án lên GitHub công khai (Public Repo)",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn vừa hoàn thành bài tập lớn kết nối cơ sở dữ liệu và chuẩn bị dùng `git push` đẩy code lên kho lưu trữ GitHub Public.",
        "choices": [
            {"text": "A. Đẩy toàn bộ thư mục dự án lên, bao gồm cả chuỗi kết nối Database và mật khẩu viết cứng (Hardcode) trong code.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Hardcode mật khẩu/khóa bí mật lên GitHub Public", "feedback": "Lỗ hổng kinh điển! Các bot quét tự động trên GitHub sẽ tìm thấy mật khẩu của bạn trong vòng vài giây."},
            {"text": "B. Tách toàn bộ thông tin nhạy cảm vào file `.env`, thêm `.env` vào `.gitignore` và kiểm tra kỹ `git diff` trước khi push.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chuẩn quy trình DevSecOps! Luôn tách biệt cấu hình bí mật khỏi mã nguồn."},
            {"text": "C. Lỡ push mật khẩu lên rồi thì chỉ cần tạo commit mới xóa dòng đó đi là xong.", "score_delta": -40, "risk": "NGUY HIỂM CAO", "mistake_tag": "Để sót thông tin bí mật trong lịch sử Git (Git History)", "feedback": "Chưa đủ! Mật khẩu vẫn nằm nguyên trong lịch sử Commit cũ; bạn bắt buộc phải thu hồi (Revoke) và đổi khóa mới."},
            {"text": "D. Mã hóa mật khẩu bằng Base64 rồi dán vào code công khai cho an toàn.", "score_delta": -30, "risk": "RỦI RO CAO", "mistake_tag": "Nhầm lẫn giữa mã hóa (Encryption) và encoding Base64", "feedback": "Base64 chỉ là định dạng biểu diễn dữ liệu, ai cũng có thể giải mã ngược lại trong 1 giây."}
        ]
    },
    {
        "id": "SCEN_27",
        "category": "Chống Lừa Đảo Tuyển Dụng",
        "title": "Câu 27: Tin nhắn tuyển dụng việc nhẹ lương cao làm nhiệm vụ online",
        "cia_pillar": "Confidentiality & Integrity",
        "description": "Một người tự xưng là nhân sự sàn thương mại điện tử mời bạn làm cộng tác viên tại nhà: chỉ cần bấm thích sản phẩm và chuyển tiền nạp nhiệm vụ để nhận hoa hồng 20%.",
        "choices": [
            {"text": "A. Chuyển thử số tiền nhỏ làm nhiệm vụ đầu tiên vì thấy họ trả hoa hồng thật.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Dính bẫy lừa đảo cộng tác viên nạp tiền làm nhiệm vụ", "feedback": "Kịch bản quen thuộc! Kẻ gian thả mồi ở các nhiệm vụ nhỏ rồi chiếm đoạt số tiền lớn ở các nhiệm vụ sau."},
            {"text": "B. Nhận diện đây là kịch bản lừa đảo đa cấp/nhiệm vụ, chặn liên hệ và tuyệt đối không chuyển tiền.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Tỉnh táo! Không có công việc hợp pháp nào yêu cầu người lao động phải nạp tiền trước để nhận lương."},
            {"text": "C. Tải ứng dụng đầu tư riêng do họ gửi link để rút tiền hoa hồng.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Cài đặt ứng dụng sàn giao dịch giả mạo", "feedback": "Ứng dụng giả mạo do kẻ gian tự lập trình để hiển thị số dư ảo và cài mã độc vào điện thoại."},
            {"text": "D. Cung cấp ảnh chụp hai mặt CCCD và ảnh chân dung để họ 'tạo hồ sơ nhận lương'.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Rò rỉ dữ liệu sinh trắc học & CCCD cho kẻ lừa đảo", "feedback": "Dữ liệu này sẽ bị dùng để vượt qua bước xác thực eKYC mở tài khoản ngân hàng mạo danh bạn."}
        ]
    },
    {
        "id": "SCEN_28",
        "category": "Bảo Mật Dữ Liệu Nhạy Cảm",
        "title": "Câu 28: Xử lý tài liệu giấy in chứa thông tin mật sau khi dùng xong",
        "cia_pillar": "Confidentiality (Tính Bảo Mật)",
        "description": "Bạn vừa in nhầm một bản danh sách lương nhân viên và hợp đồng có thông tin cá nhân khách hàng.",
        "choices": [
            {"text": "A. Vò sơ qua rồi ném thẳng vào thùng rác công cộng dưới hành lang.", "score_delta": -40, "risk": "RỦI RO CAO", "mistake_tag": "Vứt tài liệu mật nguyên vẹn vào thùng rác (Dumpster Diving)", "feedback": "Kỹ thuật 'Bới rác' (Dumpster Diving) giúp kẻ gian thu thập được rất nhiều thông tin nội bộ giá trị."},
            {"text": "B. Đưa tài liệu vào máy hủy giấy (Paper Shredder) cắt vụn trước khi bỏ đi.", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Chính xác! Hủy vật lý tài liệu giấy là bước bắt buộc đối với hồ sơ chứa dữ liệu nhạy cảm."},
            {"text": "C. Tận dụng mặt sau của tờ giấy in nhầm đó để làm giấy nháp phát cho mọi người.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Tái sử dụng giấy in chứa thông tin bảo mật", "feedback": "Tuyệt đối không tái sử dụng giấy in nhầm có chứa bảng lương hay dữ liệu khách hàng."},
            {"text": "D. Để chồng giấy đó ngay trên khay máy in dùng chung của văn phòng.", "score_delta": -40, "risk": "RỦI RO CAO", "mistake_tag": "Bỏ quên tài liệu mật tại máy in dùng chung", "feedback": "Bất kỳ ai đến lấy tài liệu in sau bạn đều có thể đọc được toàn bộ thông tin trên đó."}
        ]
    },
    {
        "id": "SCEN_29",
        "category": "An Toàn Khi Làm Việc Từ Xa",
        "title": "Câu 29: Truy cập hệ thống nội bộ công ty khi đang đi du lịch",
        "cia_pillar": "Confidentiality & Integrity",
        "description": "Bạn đang đi công tác ở khách sạn và cần truy cập vào máy chủ cơ sở dữ liệu nội bộ của công ty để kiểm tra báo cáo.",
        "choices": [
            {"text": "A. Yêu cầu IT mở thẳng cổng Database (Port 3306/5432) ra ngoài Internet công cộng để kết nối cho tiện.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Mở cổng Database trực tiếp ra Internet công cộng", "feedback": "Cực kỳ nguy hiểm! Cơ sở dữ liệu mở công khai sẽ bị tấn công dò mật khẩu và đánh cắp toàn bộ dữ liệu."},
            {"text": "B. Kết nối thông qua mạng riêng ảo của công ty (Corporate VPN) có xác thực đa yếu tố (MFA).", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Đúng quy chuẩn! VPN tạo đường hầm mã hóa an toàn giữa thiết bị của bạn và mạng nội bộ công ty."},
            {"text": "C. Dùng Wi-Fi khách sạn không mật khẩu và truy cập qua đường dẫn HTTP không mã hóa.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Truyền dữ liệu nội bộ qua giao thức HTTP không mã hóa", "feedback": "Mọi dữ liệu và mật khẩu truyền qua HTTP đều ở dạng văn bản rõ, dễ dàng bị bắt gói tin."},
            {"text": "D. Gửi tài khoản đăng nhập hệ thống cho người nhà ở nhà đăng nhập hộ rồi chụp ảnh màn hình gửi qua.", "score_delta": -50, "risk": "NGUY HIỂM CAO", "mistake_tag": "Chia sẻ tài khoản nội bộ cho người ngoài tổ chức", "feedback": "Vi phạm nghiêm trọng quy định an toàn thông tin của tổ chức."}
        ]
    },
    {
        "id": "SCEN_30",
        "category": "Ứng Phó Sự Cố Bảo Mật",
        "title": "Câu 30: Phát hiện máy tính có dấu hiệu bị nhiễm mã độc",
        "cia_pillar": "Availability & Integrity",
        "description": "Bạn lỡ bấm vào một tệp lạ, sau đó thấy chuột tự di chuyển và các tệp trên màn hình bắt đầu đổi đuôi lạ hàng loạt.",
        "choices": [
            {"text": "A. Cố gắng làm việc tiếp và giấu nhẹm sự việc vì sợ bị cấp trên khiển trách.", "score_delta": -70, "risk": "THẢM HỌA", "mistake_tag": "Che giấu sự cố khiến mã độc lây lan toàn mạng", "feedback": "Hậu quả khôn lường! Mã độc sẽ lan qua mạng nội bộ sang toàn bộ máy chủ khác của công ty."},
            {"text": "B. Ngắt kết nối mạng ngay lập tức (rút dây mạng / tắt Wi-Fi), giữ nguyên trạng thái máy và báo ngay cho đội ứng cứu sự cố (IT/SOC).", "score_delta": 100, "risk": "AN TOÀN", "mistake_tag": None, "feedback": "Xử lý chuẩn mực ứng phó sự cố! Ngắt mạng giúp cô lập mã độc, giữ nguyên máy giúp điều tra dấu vết."},
            {"text": "C. Cắm ngay ổ cứng di động chứa bản sao lưu vào máy để copy dữ liệu ra ngoài.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Cắm ổ sao lưu vào máy đang nhiễm mã độc", "feedback": "Mã độc tống tiền sẽ mã hóa luôn cả ổ cứng di động sao lưu của bạn!"},
            {"text": "D. Gửi tệp mã độc đó qua email cho đồng nghiệp hỏi xem máy họ có bị giống mình không.", "score_delta": -60, "risk": "NGUY HIỂM CAO", "mistake_tag": "Phát tán mẫu mã độc đang hoạt động qua email nội bộ", "feedback": "Tuyệt đối không gửi tệp nghi nhiễm mã độc cho người khác."}
        ]
    }
]
