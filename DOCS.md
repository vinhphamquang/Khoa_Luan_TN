# Tài Liệu Hệ Thống Smart Food Analysis

## 📚 Mục Lục

1. [Bảo Mật API Key](#bảo-mật-api-key)
2. [Hướng Dẫn Đăng Nhập/Đăng Ký](#hướng-dẫn-đăng-nhập-đăng-ký)
3. [Hướng Dẫn Hồ Sơ Cá Nhân](#hướng-dẫn-hồ-sơ-cá-nhân)
4. [Hướng Dẫn Slider Banner](#hướng-dẫn-slider-banner)
5. [Khắc Phục Sự Cố](#khắc-phục-sự-cố)
6. [Database](#database)

---

## 🔐 Bảo Mật API Key

### Vấn Đề
API keys bị leak lên GitHub có thể bị lạm dụng và bị khóa bởi nhà cung cấp.

### Giải Pháp
1. **Lưu API keys trong file `.env`**
2. **Thêm `.env` vào `.gitignore`**
3. **Sử dụng `.env.example` làm template**

### Cấu Trúc File .env
```env
GOOGLE_VISION_API_KEY=your_google_vision_key_here
GEMINI_API_KEY=your_gemini_key_here
SPOONACULAR_API_KEY=your_spoonacular_key_here
IMAGGA_API_KEY=your_imagga_key_here
IMAGGA_API_SECRET=your_imagga_secret_here
```

### Lưu Ý
- ❌ KHÔNG commit file `.env` lên Git
- ✅ Chỉ commit file `.env.example`
- ✅ Tạo API key mới nếu bị leak
- ✅ Kiểm tra `.gitignore` trước khi commit

---

## 👤 Hướng Dẫn Đăng Nhập/Đăng Ký

### Đăng Ký Tài Khoản Mới
1. Click nút "Đăng Ký" trên navbar
2. Điền thông tin:
   - Họ tên
   - Email (unique)
   - Mật khẩu (tối thiểu 4 ký tự)
3. Click "Đăng Ký"
4. Tự động đăng nhập sau khi đăng ký thành công

### Đăng Nhập
1. Click nút "Đăng Nhập"
2. Nhập email và mật khẩu
3. Click "Đăng Nhập"
4. Session được lưu, không cần đăng nhập lại

### Đăng Xuất
- Click vào tên người dùng → "Đăng Xuất"

### Bảo Mật
- Mật khẩu được hash bằng SHA256
- Session được quản lý bởi Flask
- Chỉ admin mới truy cập được trang Admin

---

## 📊 Hướng Dẫn Hồ Sơ Cá Nhân

### Truy Cập
- Click vào tên người dùng trên navbar
- Hoặc vào menu → "Hồ Sơ"

### Tính Năng

#### 1. Thông Tin Cá Nhân
- Avatar (icon)
- Tên người dùng
- Email

#### 2. Thống Kê
- Tổng số lần phân tích
- Số món ăn khác nhau đã phân tích
- Độ chính xác trung bình

#### 3. Lịch Sử Tra Cứu
- Danh sách các món ăn đã phân tích
- Thời gian phân tích
- Độ chính xác
- Xóa lịch sử (từng món hoặc toàn bộ)

#### 4. Đổi Mật Khẩu
- Nhập mật khẩu cũ
- Nhập mật khẩu mới
- Xác nhận thay đổi

---

## 🎨 Hướng Dẫn Slider Banner

### Thêm Ảnh Của Bạn

#### Bước 1: Chuẩn Bị Ảnh
- Kích thước: 1200x500px (tỷ lệ 2.4:1)
- Định dạng: JPG, PNG, WebP
- Dung lượng: < 500KB

#### Bước 2: Đặt Tên File
```
frontend/images/slide1.jpg
frontend/images/slide2.jpg
frontend/images/slide3.jpg
frontend/images/slide4.jpg
frontend/images/slide5.jpg
```

#### Bước 3: Cập Nhật Tiêu Đề
Mở `frontend/index.html` và tìm:
```html
<div class="slide-info">
    <h3>Tên Món Ăn</h3>
    <p>Mô tả món ăn</p>
</div>
```

### Tính Năng Slider
- ✅ Tự động chuyển slide mỗi 5 giây
- ✅ Nút Previous/Next
- ✅ Dots indicator
- ✅ Pause khi hover
- ✅ Responsive mobile

---

## 🔧 Khắc Phục Sự Cố

### Lỗi API Timeout
**Triệu chứng:** API không phản hồi sau 15-30 giây

**Giải pháp:**
1. Sử dụng Demo Mode (nút 🍜 Phở, 🥖 Bánh Mì, 🍖 Bún Chả)
2. Hệ thống tự động fallback: Spoonacular → Imagga → Open Food Facts
3. Kiểm tra kết nối internet

### Lỗi API Key
**Triệu chứng:** 403 Forbidden hoặc 401 Unauthorized

**Giải pháp:**
1. Kiểm tra file `.env` có đúng API key không
2. Tạo API key mới nếu bị khóa
3. Restart backend server

### Database Không Hiển Thị
**Triệu chứng:** Không thấy dữ liệu trong SQLite

**Giải pháp:**
```bash
# Kiểm tra database
sqlite3 food_recognition.db ".tables"

# Xem dữ liệu
sqlite3 food_recognition.db "SELECT * FROM MonAn;"

# Seed lại database
python seed_db.py
```

### Admin Không Lưu Dữ Liệu
**Triệu chứng:** Thêm món ăn nhưng không lưu vào database

**Giải pháp:**
- Đã fix: Thêm cột `IsDeleted` vào bảng `MonAn`
- Nếu vẫn lỗi, chạy:
```sql
ALTER TABLE MonAn ADD COLUMN IsDeleted INTEGER DEFAULT 0;
```

---

## 💾 Database

### Cấu Trúc

#### Bảng NguoiDung
- MaNguoiDung (PK)
- TenNguoiDung
- Email (Unique)
- MatKhau (SHA256)
- NgayDangKy
- VaiTro (user/admin)

#### Bảng MonAn
- MaMonAn (PK)
- TenMonAn
- MoTa
- PhanLoai
- NgayTao
- IsDeleted (Soft delete)

#### Bảng DinhDuong
- MaDinhDuong (PK)
- MaMonAn (FK)
- Calo, Protein, ChatBeo, Carbohydrate, Vitamin

#### Bảng CongThuc
- MaCongThuc (PK)
- MaMonAn (FK)
- HuongDan
- ThoiGianNau
- KhauPhan

#### Bảng NguyenLieu
- MaNguyenLieu (PK)
- TenNguyenLieu

#### Bảng ChiTietNguyenLieu
- MaCongThuc (FK)
- MaNguyenLieu (FK)
- SoLuong

#### Bảng LichSuNhanDien
- MaLichSu (PK)
- MaNguoiDung (FK)
- HinhAnh
- KetQuaNhanDien
- ThoiGianNhanDien
- DoChinhXac

### Thống Kê Hiện Tại
- **64 món ăn** Việt Nam
- **20+ phân loại** khác nhau
- **Đầy đủ thông tin** dinh dưỡng và công thức

### Truy Vấn Hữu Ích

```sql
-- Xem tất cả món ăn
SELECT * FROM MonAn WHERE IsDeleted = 0;

-- Thống kê theo phân loại
SELECT PhanLoai, COUNT(*) FROM MonAn 
WHERE IsDeleted = 0 
GROUP BY PhanLoai;

-- Xem món ăn với dinh dưỡng
SELECT m.TenMonAn, d.Calo, d.Protein 
FROM MonAn m 
JOIN DinhDuong d ON m.MaMonAn = d.MaMonAn;

-- Lịch sử người dùng
SELECT n.TenNguoiDung, COUNT(l.MaLichSu) as SoLan
FROM NguoiDung n
LEFT JOIN LichSuNhanDien l ON n.MaNguoiDung = l.MaNguoiDung
GROUP BY n.MaNguoiDung;
```

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề, kiểm tra:
1. Backend server đang chạy (`python backend/app.py`)
2. File `.env` có đầy đủ API keys
3. Database `food_recognition.db` tồn tại
4. Các dependencies đã cài đặt (`pip install -r requirements.txt`)

---

**Cập nhật:** 14/04/2026
