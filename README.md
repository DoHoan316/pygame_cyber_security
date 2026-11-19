# 🛡️ CyberSafe V3 – Game mô phỏng an toàn thông tin

CyberSafe V3 là ứng dụng mô phỏng các tình huống an toàn thông tin dưới hình thức trò chơi tương tác. Người chơi đưa ra quyết định trong từng tình huống, nhận phản hồi về hậu quả và theo dõi mức độ an toàn thông tin thông qua hệ thống điểm.

Dự án sử dụng Pygame-CE cho giao diện game, FastAPI cho xử lý nghiệp vụ và REST API, PostgreSQL (Supabase) để lưu trữ dữ liệu, cùng giao diện Web Admin xây dựng bằng HTML, CSS và JavaScript.

---

## 1. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Game Client | Python, Pygame-CE |
| Chạy game trên trình duyệt | Pygbag, WebAssembly |
| Backend | Python, FastAPI |
| API | REST API, JSON, JWT |
| Cơ sở dữ liệu | PostgreSQL / Supabase |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Xác thực | JWT, Argon2 |
| Web Admin | HTML, CSS, JavaScript |
| Quản lý môi trường | Python Virtual Environment |

## 2. Cấu trúc dự án

```text
cyber_security_game_v3_fix/
│
├── backend/
│   └── app/
│       ├── main.py              # FastAPI application
│       ├── database.py          # Kết nối cơ sở dữ liệu
│       ├── models.py            # Các model dữ liệu
│       └── security.py          # JWT và xác thực mật khẩu
│
├── game_client/
│   ├── main.py                 # Game Client V3
│   ├── main_v3.py              # Mã nguồn game V3
│   ├── main_legacy_v2.py       # Client V2 cũ, chỉ lưu tham khảo
│   ├── api_client.py           # Kết nối Backend API
│   ├── assets/
│   │   └── fonts/              # Font chữ
│   ├── data/                   # Dữ liệu phía game
│   └── services/               # Các dịch vụ phía game
│
├── admin_web/
│   ├── index.html              # Giao diện quản trị
│   ├── login.html              # Trang đăng nhập
│   ├── css/                    # Giao diện CSS
│   ├── js/                     # JavaScript và API helper
│   └── assets/                 # Tài nguyên giao diện
│
├── seed_data/
│   └── campaigns.json          # Dữ liệu chiến dịch và tình huống
│
├── archives/                   # Tài nguyên phục vụ Pygbag
│
├── docs/                       # Tài liệu kỹ thuật
│
├── requirements.txt            # Danh sách thư viện Python
├── .env.example                # Mẫu cấu hình môi trường
├── .gitignore
└── README.md
```

## 3. Kiến trúc hoạt động

Hệ thống gồm ba thành phần chính:

**Game Client – Pygame-CE**

- Hiển thị giao diện và các màn hình chơi.
- Cho phép người chơi đăng ký, đăng nhập và lựa chọn chiến dịch.
- Gửi lựa chọn của người chơi đến Backend.
- Hiển thị hậu quả, giải thích và kết quả do Backend trả về.

**Backend – FastAPI**

- Tiếp nhận và xử lý các yêu cầu từ Game Client và Web Admin.
- Quản lý tài khoản, phân quyền Player/Admin.
- Quản lý chiến dịch, tình huống và phiên chơi.
- Xử lý nhánh lựa chọn và tính điểm.
- Lưu lịch sử chơi, thống kê và dữ liệu bảng xếp hạng.

**Web Admin – HTML/CSS/JavaScript**

- Cung cấp giao diện quản trị trên trình duyệt.
- Hỗ trợ đăng nhập tài khoản Admin.
- Quản lý người dùng và trạng thái tài khoản.
- Hiển thị dữ liệu thống kê và tổng quan hoạt động.

Luồng tổng quát:

```text
                 Người chơi / Quản trị viên
                           |
             +-------------+-------------+
             |                           |
        Pygame Client                Web Admin
             |                     HTML/CSS/JS
             |                           |
             +-------------+-------------+
                           |
                       REST API
                           |
                     FastAPI Backend
                           |
                 SQLAlchemy / ORM
                           |
                  PostgreSQL Database
                       (Supabase)
```

## 4. Yêu cầu môi trường

- Windows 10/11 hoặc hệ điều hành hỗ trợ Python.
- Python tương thích với các thư viện trong `requirements.txt`.
- Git (nếu tải dự án từ GitHub).
- Trình duyệt Chrome, Edge hoặc Firefox.
- Kết nối Internet khi sử dụng cơ sở dữ liệu Supabase.

## 5. Cài đặt dự án

Mở PowerShell tại thư mục gốc của dự án.

### Bước 1: Tạo môi trường ảo

```powershell
python -m venv .venv
```

Nếu máy đã có môi trường `.venv` thì không cần tạo lại.

### Bước 2: Kích hoạt môi trường ảo

```powershell
.\.venv\Scripts\Activate.ps1
```

### Bước 3: Cài đặt thư viện

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Bước 4: Tạo file cấu hình

Sao chép `.env.example` thành `.env` tại thư mục gốc.

Cấu hình các biến môi trường cần thiết:

```env
DATABASE_URL=your_postgresql_connection_string
JWT_SECRET_KEY=your_random_secret_key
ACCESS_TOKEN_MINUTES=720
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:8001,http://127.0.0.1:8001
ADMIN_EMAIL=your_admin_email
ADMIN_PASSWORD=your_admin_password
```

Lưu ý:

- `DATABASE_URL`: chuỗi kết nối PostgreSQL/Supabase.
- `JWT_SECRET_KEY`: khóa bí mật dùng để ký JWT.
- `ACCESS_TOKEN_MINUTES`: thời hạn của access token.
- `CORS_ORIGINS`: danh sách các địa chỉ được phép gọi API.
- `ADMIN_EMAIL`, `ADMIN_PASSWORD`: thông tin dùng để tạo tài khoản Admin nếu tài khoản đó chưa tồn tại.

Không đưa file `.env`, mật khẩu hoặc khóa bí mật lên GitHub.

## 6. HƯỚNG DẪN MỞ VÀ CHẠY DỰ ÁN

Đây là phần hướng dẫn nhanh để mở đúng thành phần khi trình diễn hoặc kiểm tra dự án.

### 6.1. Mở Backend – FastAPI

**Mục đích:** Khởi động máy chủ xử lý API và kết nối cơ sở dữ liệu.

Mở Terminal số 1 tại thư mục gốc dự án:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --env-file .env
```

Khi Backend khởi động thành công, có thể kiểm tra:

| Địa chỉ | Chức năng |
|---|---|
| http://127.0.0.1:8000/ | Thông tin ứng dụng |
| http://127.0.0.1:8000/api/health | Kiểm tra trạng thái Backend và Database |
| http://127.0.0.1:8000/docs | Tài liệu API Swagger |
| http://127.0.0.1:8000/app/ | Giao diện Web Admin |

Giữ Terminal này hoạt động trong suốt quá trình sử dụng game và Web Admin.

### 6.2. Mở game Pygame trên máy tính

**Mục đích:** Chạy game trực tiếp bằng Python trên Windows.

Điều kiện: Backend phải đang chạy ở cổng 8000.

Mở Terminal số 2 tại thư mục gốc dự án:

```powershell
$env:CYBERSAFE_API_URL = "http://127.0.0.1:8000/api"
.\.venv\Scripts\python.exe game_client\main.py
```

Game sẽ mở thành cửa sổ riêng trên máy tính.

Đây là cách phù hợp để trình diễn bản Pygame Desktop.

### 6.3. Mở game trên trình duyệt bằng Pygbag

**Mục đích:** Chạy game Pygame dưới dạng ứng dụng WebAssembly trong trình duyệt.

Điều kiện:

- Backend đang chạy.
- Đã cài Pygbag theo `requirements.txt`.
- Cấu hình API và CORS phù hợp với địa chỉ trình duyệt.

Mở Terminal mới tại thư mục gốc:

```powershell
.\.venv\Scripts\python.exe -m pygbag --port 8666 .\game_client
```

Sau khi máy chủ Pygbag khởi động, mở trình duyệt:

```text
http://localhost:8666
```

Lưu ý: Pygbag đóng gói ứng dụng Pygame thành nội dung chạy trên trình duyệt bằng WebAssembly. Cần kiểm tra thực tế việc tải game, font, tài nguyên, đăng nhập và gọi API từ trình duyệt trước khi xác nhận bản Web đã hoạt động hoàn chỉnh.

Khi triển khai online, Game Client phải gọi API bằng địa chỉ HTTPS công khai của Backend; CORS phải cho phép origin của trang game.

### 6.4. Mở giao diện Web Admin bằng HTML

Web Admin được xây dựng bằng HTML, CSS và JavaScript.

Trong cấu hình hiện tại, FastAPI phục vụ thư mục `admin_web` tại đường dẫn:

```text
http://127.0.0.1:8000/app/
```

Cách mở:

1. Khởi động Backend theo mục 6.1.
2. Mở Chrome hoặc Edge.
3. Truy cập `http://127.0.0.1:8000/app/`.
4. Đăng nhập bằng tài khoản có quyền Admin.

Không cần chạy riêng Live Server hoặc mở trực tiếp file HTML khi muốn kiểm tra luồng API tích hợp. Mở thông qua Backend giúp giao diện gọi API trên cùng origin.

### 6.5. Mở tài liệu API

Khi cần kiểm tra các API hoặc trình diễn phần Backend:

1. Đảm bảo FastAPI đang chạy.
2. Truy cập:

```text
http://127.0.0.1:8000/docs
```

Tại đây có thể xem các endpoint, phương thức HTTP, tham số đầu vào và phản hồi JSON.

### 6.6. Mở phiên bản online sau khi triển khai

Sau khi hoàn tất triển khai:

- **Web Admin:** Truy cập đường dẫn `/app/` trên domain Backend.
- **API:** Truy cập `/docs` để xem tài liệu API.
- **Health Check:** Truy cập `/api/health`.
- **Game Web:** Truy cập URL của trang game được triển khai bằng Pygbag.

Ví dụ cấu trúc địa chỉ:

```text
https://your-backend-domain.onrender.com/app/
https://your-backend-domain.onrender.com/docs
https://your-backend-domain.onrender.com/api/health

https://your-game-domain/
```

Các địa chỉ trên là ví dụ minh họa. Thay bằng URL thực tế sau khi triển khai.

## 7. Các API chính

| Nhóm chức năng | Endpoint |
|---|---|
| Đăng ký | `POST /api/auth/register` |
| Đăng nhập | `POST /api/auth/login` |
| Thông tin tài khoản | `GET /api/auth/me` |
| Danh sách chiến dịch | `GET /api/campaigns` |
| Chi tiết chiến dịch | `GET /api/campaigns/{id}` |
| Tạo phiên chơi | `POST /api/game/sessions` |
| Lấy thông tin phiên | `GET /api/game/sessions/{id}` |
| Gửi lựa chọn | `POST /api/game/sessions/{id}/choices` |
| Tiếp tục phiên | `POST /api/game/sessions/{id}/continue` |
| Kết quả phiên chơi | `GET /api/game/sessions/{id}/result` |
| Dashboard người chơi | `GET /api/me/dashboard` |
| Lịch sử chơi | `GET /api/me/history` |
| Nhóm lỗi đã gặp | `GET /api/me/errors` |
| Bảng xếp hạng | `GET /api/leaderboard/{campaign_id}` |
| Danh sách người dùng | `GET /api/admin/users` |
| Thống kê Admin | `GET /api/admin/analytics/overview` |

Các API nghiệp vụ yêu cầu xác thực bằng Bearer JWT. API quản trị yêu cầu tài khoản có quyền Admin.

## 8. Cơ sở dữ liệu và bảo mật

- SQLAlchemy được sử dụng để thao tác với dữ liệu.
- PostgreSQL/Supabase là cơ sở dữ liệu sử dụng khi triển khai.
- JWT được dùng để xác thực các yêu cầu.
- Argon2 được sử dụng để băm mật khẩu.
- Backend kiểm tra quyền Admin trước khi cho phép thực hiện chức năng quản trị.
- Điểm số và kết quả phiên chơi được xử lý ở Backend, không tin dữ liệu điểm do Client tự gửi lên.

Không công khai thông tin kết nối cơ sở dữ liệu, mật khẩu Admin hoặc JWT secret.

## 9. Một số lỗi thường gặp

| Vấn đề | Hướng xử lý |
|---|---|
| Không tìm thấy Python | Kiểm tra Python đã cài và sử dụng đúng đường dẫn Python |
| Thiếu thư viện | Chạy lại lệnh cài `requirements.txt` |
| Không kết nối được API | Kiểm tra Backend có đang chạy ở cổng 8000 không |
| Database không kết nối | Kiểm tra `DATABASE_URL` trong `.env` |
| Đăng nhập thất bại | Kiểm tra email, mật khẩu và trạng thái tài khoản |
| Lỗi CORS | Kiểm tra `CORS_ORIGINS` và origin của trang đang chạy |
| Pygbag không tải được game | Kiểm tra Terminal Pygbag, thư mục `game_client` và tài nguyên build |
| Token không hợp lệ | Đăng nhập lại để lấy access token mới |

---

## 10. GHI NHỚ NHANH KHI TRÌNH DIỄN

| Muốn mở phần nào? | Cách mở |
|---|---|
| Pygame Desktop | Chạy `game_client\main.py` bằng Python |
| Game trên trình duyệt | Chạy Pygbag ở cổng 8001 |
| Web Admin / HTML | Mở `/app/` trên Backend |
| Backend | Chạy Uvicorn ở cổng 8000 |
| API Swagger | Mở `/docs` |
| Kiểm tra hệ thống | Mở `/api/health` |
| Bản online | Truy cập URL công khai sau khi deploy |

**Thứ tự chạy local khuyến nghị:**

1. Mở Backend trước.
2. Mở Pygame Desktop hoặc Pygbag tùy hình thức trình diễn.
3. Mở Web Admin bằng trình duyệt nếu cần trình diễn phần quản trị.
4. Kiểm tra API và trạng thái Database qua Swagger hoặc Health Check.

**Lưu ý:** Không cần chạy đồng thời Pygame Desktop và Pygbag nếu chỉ trình diễn một phiên bản game. Web Admin được phục vụ trực tiếp bởi FastAPI nên không cần một máy chủ frontend riêng trong cấu hình hiện tại.

## 11. Triển khai và kiểm thử

Trước khi công bố phiên bản online, cần kiểm tra:

- Backend khởi động thành công trên máy chủ.
- Kết nối PostgreSQL/Supabase ổn định.
- Đăng ký và đăng nhập Player.
- Đăng nhập Admin và kiểm tra phân quyền.
- Chọn chiến dịch, chơi và nhận phản hồi.
- Dữ liệu phiên chơi được lưu và khôi phục khi tải lại.
- Dashboard, lịch sử và bảng xếp hạng trả dữ liệu chính xác.
- Game Pygbag gọi được API qua HTTPS.
- Web Admin hoạt động trên domain triển khai.

---