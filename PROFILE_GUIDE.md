# Hướng Dẫn Trang Hồ Sơ Cá Nhân

## Tính Năng

Trang hồ sơ cá nhân cho phép người dùng xem thông tin tài khoản, lịch sử phân tích món ăn và thống kê sử dụng.

## Các Thành Phần

### 1. Thông Tin Tài Khoản
- Avatar người dùng
- Tên đăng nhập
- Email
- Ngày tham gia

### 2. Thống Kê
- **Tổng số lần phân tích**: Số lần người dùng đã phân tích món ăn
- **Món ăn khác nhau**: Số lượng món ăn unique đã phân tích
- **Độ chính xác trung bình**: Độ chính xác trung bình của các lần phân tích

### 3. Lịch Sử Phân Tích
- Danh sách các lần phân tích món ăn gần đây (20 bản ghi mới nhất)
- Hiển thị: Tên món ăn, thời gian, độ chính xác
- Nút xóa toàn bộ lịch sử

## API Endpoints

### GET /api/profile/history
Lấy lịch sử phân tích của người dùng

**Query Parameters:**
- `limit` (optional): Số lượng bản ghi tối đa (mặc định: 20)

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "MaLichSu": 1,
      "HinhAnh": "image_hash",
      "KetQuaNhanDien": "Pho",
      "DoChinhXac": 95.5,
      "ThoiGianNhanDien": "2026-04-07 16:00:56"
    }
  ]
}
```

### GET /api/profile/stats
Lấy thống kê của người dùng

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_scans": 5,
    "unique_foods": 3,
    "avg_confidence": 91.74
  }
}
```

### DELETE /api/profile/history
Xóa toàn bộ lịch sử phân tích

**Response:**
```json
{
  "success": true,
  "message": "Đã xóa 5 bản ghi lịch sử"
}
```

## Cách Sử Dụng

1. **Truy cập trang hồ sơ:**
   - Đăng nhập vào tài khoản
   - Click vào "Hồ Sơ" trên thanh navigation
   - Hoặc truy cập: `http://localhost:5000#profile`

2. **Xem lịch sử:**
   - Lịch sử phân tích sẽ tự động hiển thị
   - Mỗi bản ghi hiển thị tên món ăn, thời gian và độ chính xác

3. **Xóa lịch sử:**
   - Click nút "Xóa Lịch Sử"
   - Xác nhận trong hộp thoại
   - Toàn bộ lịch sử sẽ bị xóa

## Bảo Mật

- Chỉ người dùng đã đăng nhập mới có thể truy cập trang hồ sơ
- Mỗi người dùng chỉ xem được lịch sử và thống kê của chính mình
- Session được kiểm tra cho mọi request API

## Database Schema

### Bảng LichSuNhanDien
```sql
CREATE TABLE LichSuNhanDien (
    MaLichSu INTEGER PRIMARY KEY AUTOINCREMENT,
    MaNguoiDung INTEGER NOT NULL,
    HinhAnh TEXT,
    KetQuaNhanDien TEXT,
    DoChinhXac REAL,
    ThoiGianNhanDien DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung)
);
```

## Test

Chạy file test để tạo dữ liệu mẫu:
```bash
python test_profile.py
```

## Giao Diện

- Thiết kế glassmorphism đồng nhất với toàn bộ ứng dụng
- Responsive trên mobile và tablet
- Animation mượt mà khi load dữ liệu
- Icon và màu sắc trực quan

## Tính Năng Tương Lai

- Export lịch sử ra CSV/PDF
- Biểu đồ thống kê theo thời gian
- Lọc lịch sử theo món ăn
- Chia sẻ kết quả phân tích
- Đánh giá và nhận xét món ăn
