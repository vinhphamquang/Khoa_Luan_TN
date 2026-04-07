# Hướng Dẫn Sử Dụng Chức Năng Đăng Nhập/Đăng Ký

## Tính Năng Mới

Ứng dụng Smart Food Analysis đã được bổ sung chức năng đăng nhập và đăng ký tài khoản người dùng.

## Các Tính Năng

### 1. Đăng Ký Tài Khoản
- Truy cập trang đăng ký qua nút "Đăng Ký" trên thanh navigation
- Điền thông tin:
  - Tên đăng nhập (bắt buộc)
  - Họ và tên (tùy chọn)
  - Email (tùy chọn)
  - Mật khẩu (bắt buộc, tối thiểu 6 ký tự)
- Nhấn "Đăng Ký" để tạo tài khoản

### 2. Đăng Nhập
- Truy cập trang đăng nhập qua nút "Đăng Nhập" trên thanh navigation
- Nhập tên đăng nhập và mật khẩu
- Nhấn "Đăng Nhập"
- Sau khi đăng nhập thành công, tên người dùng sẽ hiển thị trên thanh navigation

### 3. Đăng Xuất
- Khi đã đăng nhập, nhấn nút "Đăng Xuất" trên thanh navigation

### 4. Lưu Lịch Sử Phân Tích
- Khi đã đăng nhập, mỗi lần phân tích món ăn sẽ được tự động lưu vào lịch sử
- Lịch sử bao gồm: hình ảnh, kết quả nhận diện, độ chính xác, thời gian

## API Endpoints

### POST /api/register
Đăng ký tài khoản mới

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string (optional)",
  "fullname": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Đăng ký thành công",
  "user_id": 1
}
```

### POST /api/login
Đăng nhập

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "fullname": "testuser"
  }
}
```

### POST /api/logout
Đăng xuất

**Response:**
```json
{
  "success": true,
  "message": "Đăng xuất thành công"
}
```

### GET /api/me
Lấy thông tin người dùng hiện tại

**Response:**
```json
{
  "success": true,
  "user": {
    "MaNguoiDung": 1,
    "TenNguoiDung": "testuser",
    "Email": "test@example.com",
    "NgayDangKy": "2026-04-07 08:45:15",
    "VaiTro": "user"
  }
}
```

## Bảo Mật

- Mật khẩu được hash bằng SHA256 trước khi lưu vào database
- Session được quản lý bằng Flask session với SECRET_KEY
- CORS được cấu hình với `supports_credentials=True` để hỗ trợ cookie

## Cấu Trúc Database

Bảng `NguoiDung`:
- `MaNguoiDung` (INTEGER, PRIMARY KEY)
- `TenNguoiDung` (TEXT, NOT NULL)
- `Email` (TEXT)
- `MatKhau` (TEXT, NOT NULL)
- `NgayDangKy` (DATE)
- `VaiTro` (TEXT)

Bảng `LichSuNhanDien`:
- `MaLichSu` (INTEGER, PRIMARY KEY)
- `MaNguoiDung` (INTEGER, FOREIGN KEY)
- `HinhAnh` (TEXT)
- `KetQuaNhanDien` (TEXT)
- `DoChinhXac` (REAL)
- `ThoiGianNhanDien` (DATETIME)

## Test

Chạy file `test_auth.py` để test các chức năng:
```bash
python test_auth.py
```

## Lưu Ý

- Đảm bảo file `.env` có biến `SECRET_KEY` được cấu hình
- Chức năng lưu lịch sử chỉ hoạt động khi người dùng đã đăng nhập
- Nếu chưa đăng nhập, vẫn có thể sử dụng chức năng phân tích món ăn bình thường
