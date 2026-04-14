# Cấu Trúc Dự Án Smart Food Analysis

## 📁 Cấu Trúc Thư Mục

```
KLTN/
├── backend/                    # Backend Python Flask
│   ├── __pycache__/           # Python cache (tự động tạo)
│   ├── ai_generator.py        # AI Generator với Gemini
│   ├── app.py                 # Flask application chính
│   ├── db_queries.py          # Database queries
│   └── external_api.py        # External API integrations
│
├── frontend/                   # Frontend HTML/CSS/JS
│   ├── images/                # Hình ảnh
│   │   ├── slide1.jpg         # Banner slider 1
│   │   ├── slide2.jpg         # Banner slider 2
│   │   ├── slide3.jpg         # Banner slider 3
│   │   ├── slide4.jpg         # Banner slider 4
│   │   └── slide5.jpg         # Banner slider 5
│   ├── admin_append.css       # CSS cho trang admin
│   ├── index.html             # Trang chính (SPA)
│   ├── script.js              # JavaScript logic
│   └── style.css              # CSS chính
│
├── .env                        # Environment variables (API keys)
├── .env.example               # Template cho .env
├── .gitignore                 # Git ignore rules
├── DOCS.md                    # Tài liệu tổng hợp
├── food_recognition.db        # SQLite database
├── PROJECT_STRUCTURE.md       # File này
├── README.md                  # Hướng dẫn chính
├── requirements.txt           # Python dependencies
├── schema.sql                 # Database schema
└── seed_db.py                 # Script seed database
```

## 📄 Mô Tả Files

### Backend Files

#### `backend/app.py`
- Flask application chính
- Định nghĩa tất cả API endpoints
- Quản lý routing và static files
- Session management

**API Endpoints:**
- `/api/predict` - Nhận diện món ăn
- `/api/dishes/<name>` - Lấy thông tin món ăn
- `/api/register` - Đăng ký user
- `/api/login` - Đăng nhập
- `/api/logout` - Đăng xuất
- `/api/me` - Thông tin user hiện tại
- `/api/profile/*` - Profile endpoints
- `/api/admin/*` - Admin endpoints

#### `backend/db_queries.py`
- Tất cả database queries
- CRUD operations cho các bảng
- Helper functions cho database

**Functions:**
- User management: `create_user()`, `authenticate_user()`, `get_user_by_id()`
- Food management: `get_all_foods_admin()`, `insert_food_full()`, `update_food_full()`
- Profile: `get_user_history()`, `get_user_stats()`
- Admin: `get_system_stats()`, `get_all_history_admin()`

#### `backend/external_api.py`
- Tích hợp external APIs
- Fallback mechanism
- Error handling

**APIs:**
- Spoonacular (primary)
- Imagga (fallback 1)
- Open Food Facts (fallback 2)

#### `backend/ai_generator.py`
- Google Gemini AI integration
- Generate food descriptions
- Currently disabled (quota exceeded)

### Frontend Files

#### `frontend/index.html`
- Single Page Application (SPA)
- Tất cả pages trong một file
- Responsive design

**Pages:**
- Giới Thiệu (intro)
- Phân Tích (analyze)
- Hồ Sơ (profile)
- Admin (admin)

#### `frontend/script.js`
- SPA routing logic
- API calls
- Form handling
- Image upload & preview
- Admin panel logic
- Food slider logic

#### `frontend/style.css`
- Light theme (trắng + xanh lá)
- Glassmorphism design
- Responsive breakpoints
- Animations & transitions

#### `frontend/admin_append.css`
- Additional styles cho admin panel
- Table styles
- Form styles

### Root Files

#### `.env`
- Chứa API keys (KHÔNG commit lên Git)
- Environment variables

#### `.env.example`
- Template cho `.env`
- Hướng dẫn các biến cần thiết

#### `.gitignore`
- Ignore `.env`
- Ignore `__pycache__`
- Ignore `.venv`

#### `food_recognition.db`
- SQLite database
- Chứa 64 món ăn Việt Nam
- User data, history, recipes

#### `schema.sql`
- Database schema definition
- 7 tables: NguoiDung, MonAn, DinhDuong, CongThuc, NguyenLieu, ChiTietNguyenLieu, LichSuNhanDien

#### `seed_db.py`
- Script để seed database
- Tạo 3 món ăn mẫu ban đầu

#### `requirements.txt`
- Python dependencies
- Flask, requests, google-generativeai, etc.

#### `README.md`
- Hướng dẫn cài đặt và chạy project
- Overview của dự án

#### `DOCS.md`
- Tài liệu chi tiết
- Hướng dẫn sử dụng
- Troubleshooting

## 🚀 Workflow

### 1. Khởi Động
```bash
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python backend/app.py
```

### 2. Truy Cập
- Frontend: `http://localhost:5000`
- API: `http://localhost:5000/api/*`

### 3. Phát Triển
1. Backend: Sửa files trong `backend/`
2. Frontend: Sửa files trong `frontend/`
3. Database: Sửa `schema.sql` và chạy lại seed

## 📊 Database

### Tables
- **NguoiDung**: User accounts
- **MonAn**: Food items (64 món)
- **DinhDuong**: Nutrition info
- **CongThuc**: Recipes
- **NguyenLieu**: Ingredients
- **ChiTietNguyenLieu**: Recipe ingredients
- **LichSuNhanDien**: Recognition history

### Current Data
- 64 món ăn Việt Nam
- 20+ phân loại
- Đầy đủ thông tin dinh dưỡng và công thức

## 🔧 Technologies

### Backend
- Python 3.x
- Flask (Web framework)
- SQLite (Database)
- Google Gemini AI
- Spoonacular API
- Imagga API
- Open Food Facts API

### Frontend
- HTML5
- CSS3 (Glassmorphism)
- Vanilla JavaScript
- Font Awesome icons
- Google Fonts (Outfit)

## 📝 Notes

- Project sử dụng SPA architecture
- Light theme với màu trắng và xanh lá
- Header/Footer màu tối (dark)
- Responsive design cho mobile
- Session-based authentication
- Soft delete cho món ăn (IsDeleted flag)

---

**Cập nhật:** 14/04/2026
