import re

with open('db_queries.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports and Connection
imports = """import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("DATABASE_URL")

COLUMN_MAP = {
    'manguoidung': 'MaNguoiDung', 'tennguoidung': 'TenNguoiDung', 'email': 'Email',
    'matkhau': 'MatKhau', 'ngaydangky': 'NgayDangKy', 'vaitro': 'VaiTro',
    'mamonan': 'MaMonAn', 'tenmonan': 'TenMonAn', 'mota': 'MoTa',
    'phanloai': 'PhanLoai', 'ngaytao': 'NgayTao', 'isdeleted': 'IsDeleted',
    'madinhduong': 'MaDinhDuong', 'calo': 'Calo', 'protein': 'Protein',
    'chatbeo': 'ChatBeo', 'carbohydrate': 'Carbohydrate', 'vitamin': 'Vitamin',
    'macongthuc': 'MaCongThuc', 'huongdan': 'HuongDan', 'thoigiannau': 'ThoiGianNau',
    'khauphan': 'KhauPhan', 'manguyenlieu': 'MaNguyenLieu', 'tennguyenlieu': 'TenNguyenLieu',
    'soluong': 'SoLuong', 'malichsu': 'MaLichSu', 'hinhanh': 'HinhAnh',
    'ketquanhandien': 'KetQuaNhanDien', 'thoigiannhandien': 'ThoiGianNhanDien',
    'dochinhxac': 'DoChinhXac', 'mafeedback': 'MaFeedback', 'tenmonnhandien': 'TenMonNhanDien',
    'danhgia': 'DanhGia', 'tenmondung': 'TenMonDung', 'thoigian': 'ThoiGian',
    'mahoso': 'MaHoSo', 'tuoi': 'Tuoi', 'chieucao': 'ChieuCao', 'cannang': 'CanNang',
    'gioitinh': 'GioiTinh', 'muctieu': 'MucTieu'
}

def map_row(row):
    if not row: return row
    return {COLUMN_MAP.get(k, k): v for k, v in row.items()}

class PascalCaseCursor(psycopg2.extras.RealDictCursor):
    def fetchone(self):
        row = super().fetchone()
        return map_row(row) if row else None
    def fetchall(self):
        rows = super().fetchall()
        return [map_row(row) for row in rows]

def get_db_connection():
    conn = psycopg2.connect(DB_URL, cursor_factory=PascalCaseCursor)
    return conn
"""

content = re.sub(r'import sqlite3\nimport os\n\nDB_PATH = .*?\n\ndef get_db_connection\(\):\n    conn = sqlite3\.connect\(DB_PATH\)\n    conn\.row_factory = sqlite3\.Row\n    return conn\n', imports, content, flags=re.DOTALL)

# 2. SQLite specific syntax replacements
content = content.replace("sqlite3.IntegrityError", "psycopg2.IntegrityError")
content = content.replace("datetime('now', 'localtime')", "CURRENT_TIMESTAMP")
content = content.replace("date('now', 'localtime')", "CURRENT_DATE")
content = content.replace("date('now')", "CURRENT_DATE")
content = content.replace("datetime.date.today().strftime('%Y-%m-%d')", "CURRENT_DATE")

# 3. Parameter placeholders
content = content.replace("?", "%s")

# 4. lastrowid replacements
# NguoiDung
content = content.replace(
    "VALUES (%s, %s, %s, CURRENT_DATE, 'user')\n        \", (name, email, hashed_password))\n        user_id = cursor.lastrowid",
    "VALUES (%s, %s, %s, CURRENT_DATE, 'user') RETURNING MaNguoiDung\n        \", (name, email, hashed_password))\n        user_id = cursor.fetchone()['MaNguoiDung']"
)

# insert_generated_food_data
content = content.replace(
    "VALUES (%s, %s, %s, CURRENT_DATE)\n        \", (data.get('TenMonAn', food_name_english), mo_ta, data.get('PhanLoai', '')))\n        ma_mon_an = cursor.lastrowid",
    "VALUES (%s, %s, %s, CURRENT_DATE) RETURNING MaMonAn\n        \", (data.get('TenMonAn', food_name_english), mo_ta, data.get('PhanLoai', '')))\n        ma_mon_an = cursor.fetchone()['MaMonAn']"
)
content = content.replace(
    "VALUES (%s, %s, %s, %s)\n        \", (\n            ma_mon_an,\n            cong_thuc.get('HuongDan', ''),\n            cong_thuc.get('ThoiGianNau', 0),\n            cong_thuc.get('KhauPhan', 1)\n        ))\n        ma_cong_thuc = cursor.lastrowid",
    "VALUES (%s, %s, %s, %s) RETURNING MaCongThuc\n        \", (\n            ma_mon_an,\n            cong_thuc.get('HuongDan', ''),\n            cong_thuc.get('ThoiGianNau', 0),\n            cong_thuc.get('KhauPhan', 1)\n        ))\n        ma_cong_thuc = cursor.fetchone()['MaCongThuc']"
)
content = content.replace(
    "cursor.execute(\"INSERT INTO NguyenLieu (TenNguyenLieu) VALUES (%s)\", (ten_nl,))\n                ma_nl = cursor.lastrowid",
    "cursor.execute(\"INSERT INTO NguyenLieu (TenNguyenLieu) VALUES (%s) RETURNING MaNguyenLieu\", (ten_nl,))\n                ma_nl = cursor.fetchone()['MaNguyenLieu']"
)

# insert_food_full
content = content.replace(
    "VALUES (%s, %s, %s, CURRENT_DATE, 0)\n        \", (data.get('TenMonAn'), data.get('MoTa'), data.get('PhanLoai')))\n        food_id = cursor.lastrowid",
    "VALUES (%s, %s, %s, CURRENT_DATE, 0) RETURNING MaMonAn\n        \", (data.get('TenMonAn'), data.get('MoTa'), data.get('PhanLoai')))\n        food_id = cursor.fetchone()['MaMonAn']"
)
content = content.replace(
    "VALUES (%s, %s, %s, %s)\n        \", (food_id, cong_thuc.get('HuongDan'), cong_thuc.get('ThoiGianNau'), cong_thuc.get('KhauPhan')))\n        ct_id = cursor.lastrowid",
    "VALUES (%s, %s, %s, %s) RETURNING MaCongThuc\n        \", (food_id, cong_thuc.get('HuongDan'), cong_thuc.get('ThoiGianNau'), cong_thuc.get('KhauPhan')))\n        ct_id = cursor.fetchone()['MaCongThuc']"
)

# update_food_full
content = content.replace(
    "VALUES (%s, %s, %s, %s)\n            \", (food_id, cong_thuc.get('HuongDan'), cong_thuc.get('ThoiGianNau'), cong_thuc.get('KhauPhan')))\n            ct_id = cursor.lastrowid",
    "VALUES (%s, %s, %s, %s) RETURNING MaCongThuc\n            \", (food_id, cong_thuc.get('HuongDan'), cong_thuc.get('ThoiGianNau'), cong_thuc.get('KhauPhan')))\n            ct_id = cursor.fetchone()['MaCongThuc']"
)

# 5. Fix boolean integers
content = content.replace("IsDeleted = 0", "IsDeleted = 0") # Postgres can auto cast int to smallint if we use INTEGER, wait we defined IsDeleted as INTEGER DEFAULT 0 in postgres, so it's fine!

# Ensure SQLite AUTOINCREMENT creation is skipped
content = re.sub(r'def create_health_profile_table\(\):.*?conn\.commit\(\)\n    conn\.close\(\)', '', content, flags=re.DOTALL)
content = content.replace('create_health_profile_table()', 'pass')

with open('db_queries.py', 'w', encoding='utf-8') as f:
    f.write(content)
