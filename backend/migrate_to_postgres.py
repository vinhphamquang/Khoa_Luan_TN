import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'food_recognition.db')
POSTGRES_URL = os.environ.get("DATABASE_URL")

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS NguoiDung (
    MaNguoiDung SERIAL PRIMARY KEY,
    TenNguoiDung TEXT NOT NULL,
    Email TEXT UNIQUE,
    MatKhau TEXT NOT NULL,
    NgayDangKy DATE,
    VaiTro TEXT
);

CREATE TABLE IF NOT EXISTS MonAn (
    MaMonAn SERIAL PRIMARY KEY,
    TenMonAn TEXT NOT NULL,
    MoTa TEXT,
    PhanLoai TEXT,
    NgayTao DATE,
    IsDeleted INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS DinhDuong (
    MaDinhDuong SERIAL PRIMARY KEY,
    MaMonAn INTEGER,
    Calo REAL,
    Protein REAL,
    ChatBeo REAL,
    Carbohydrate REAL,
    Vitamin TEXT,
    FOREIGN KEY (MaMonAn) REFERENCES MonAn(MaMonAn) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CongThuc (
    MaCongThuc SERIAL PRIMARY KEY,
    MaMonAn INTEGER,
    HuongDan TEXT,
    ThoiGianNau INTEGER,
    KhauPhan INTEGER,
    FOREIGN KEY (MaMonAn) REFERENCES MonAn(MaMonAn) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS NguyenLieu (
    MaNguyenLieu SERIAL PRIMARY KEY,
    TenNguyenLieu TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ChiTietNguyenLieu (
    MaCongThuc INTEGER,
    MaNguyenLieu INTEGER,
    SoLuong TEXT,
    PRIMARY KEY (MaCongThuc, MaNguyenLieu),
    FOREIGN KEY (MaCongThuc) REFERENCES CongThuc(MaCongThuc) ON DELETE CASCADE,
    FOREIGN KEY (MaNguyenLieu) REFERENCES NguyenLieu(MaNguyenLieu) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS LichSuNhanDien (
    MaLichSu SERIAL PRIMARY KEY,
    MaNguoiDung INTEGER,
    HinhAnh TEXT,
    KetQuaNhanDien TEXT,
    ThoiGianNhanDien TIMESTAMP,
    DoChinhXac REAL,
    FOREIGN KEY (MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS FeedbackNhanDien (
    MaFeedback SERIAL PRIMARY KEY,
    MaNguoiDung INTEGER,
    TenMonNhanDien TEXT NOT NULL,
    DoChinhXac REAL,
    DanhGia TEXT CHECK(DanhGia IN ('accurate', 'inaccurate')),
    TenMonDung TEXT,
    ThoiGian TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS HoSoSucKhoe (
    MaHoSo SERIAL PRIMARY KEY,
    MaNguoiDung INTEGER UNIQUE,
    Tuoi INTEGER,
    ChieuCao REAL,
    CanNang REAL,
    GioiTinh TEXT,
    MucTieu TEXT,
    FOREIGN KEY(MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung) ON DELETE CASCADE
);
"""

def migrate():
    print("Connecting to SQLite...")
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    print(f"Connecting to PostgreSQL... URL: {POSTGRES_URL}")
    pg_conn = psycopg2.connect(POSTGRES_URL)
    pg_cur = pg_conn.cursor()

    # Create tables
    print("Creating tables in PostgreSQL...")
    pg_cur.execute(CREATE_TABLES_SQL)
    pg_conn.commit()

    tables = [
        ("NguoiDung", "MaNguoiDung"),
        ("MonAn", "MaMonAn"),
        ("DinhDuong", "MaDinhDuong"),
        ("CongThuc", "MaCongThuc"),
        ("NguyenLieu", "MaNguyenLieu"),
        ("ChiTietNguyenLieu", None), # No serial sequence
        ("LichSuNhanDien", "MaLichSu"),
        ("FeedbackNhanDien", "MaFeedback"),
        ("HoSoSucKhoe", "MaHoSo"),
    ]

    for table, pk in tables:
        print(f"Migrating table {table}...")
        
        # Check if table already has data
        pg_cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = pg_cur.fetchone()[0]
        if count > 0:
            print(f"Table {table} already has {count} rows. Skipping...")
            continue
            
        sqlite_cur.execute(f"SELECT * FROM {table}")
        rows = sqlite_cur.fetchall()
        
        if not rows:
            print(f"Table {table} is empty. Skipping...")
            continue
            
        # Get column names
        cols = rows[0].keys()
        col_names = ", ".join(cols)
        placeholders = ", ".join(["%s"] * len(cols))
        
        insert_query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
        
        # Insert rows
        data_to_insert = [tuple(row[col] for col in cols) for row in rows]
        
        # Handle orphan records due to SQLite lack of FK enforcement
        if table == "DinhDuong" or table == "CongThuc":
            pg_cur.execute("SELECT MaMonAn FROM MonAn")
            valid_mamonan = set(r[0] for r in pg_cur.fetchall())
            data_to_insert = [d for d in data_to_insert if d[list(cols).index('MaMonAn')] in valid_mamonan]
            
        if table == "ChiTietNguyenLieu":
            pg_cur.execute("SELECT MaCongThuc FROM CongThuc")
            valid_macongthuc = set(r[0] for r in pg_cur.fetchall())
            pg_cur.execute("SELECT MaNguyenLieu FROM NguyenLieu")
            valid_manguyenlieu = set(r[0] for r in pg_cur.fetchall())
            data_to_insert = [d for d in data_to_insert if d[list(cols).index('MaCongThuc')] in valid_macongthuc and d[list(cols).index('MaNguyenLieu')] in valid_manguyenlieu]
            
        if table == "LichSuNhanDien" or table == "FeedbackNhanDien" or table == "HoSoSucKhoe":
            pg_cur.execute("SELECT MaNguoiDung FROM NguoiDung")
            valid_manguoidung = set(r[0] for r in pg_cur.fetchall())
            mnd_idx = list(cols).index('MaNguoiDung')
            data_to_insert = [d for d in data_to_insert if d[mnd_idx] is None or d[mnd_idx] in valid_manguoidung]
            
        pg_cur.executemany(insert_query, data_to_insert)
        
        print(f"Inserted {len(data_to_insert)} rows into {table} (filtered out {len(rows) - len(data_to_insert)} invalid FKs).")
        
        # Update sequence
        if pk:
            print(f"Updating sequence for {table}...")
            pg_cur.execute(f"SELECT setval('{table}_{pk}_seq', (SELECT MAX({pk}) FROM {table}))")
            
    pg_conn.commit()
    print("Migration completed successfully!")
    
    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    migrate()
