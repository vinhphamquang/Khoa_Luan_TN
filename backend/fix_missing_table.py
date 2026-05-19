import os, sys, psycopg2
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if 'sslmode' not in DATABASE_URL:
    DATABASE_URL += ('&' if '?' in DATABASE_URL else '?') + 'sslmode=require'

conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS KeHoachDinhDuong (
        MaKeHoach SERIAL PRIMARY KEY,
        MaNguoiDung INTEGER REFERENCES NguoiDung(MaNguoiDung) ON DELETE CASCADE,
        NgayLuu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CaloDuKien DECIMAL(10,2) DEFAULT 0,
        TongCaloChon DECIMAL(10,2) DEFAULT 0,
        BuaSang TEXT DEFAULT '',
        BuaSangCalo DECIMAL(10,2) DEFAULT 0,
        BuaTrua TEXT DEFAULT '',
        BuaTruaCalo DECIMAL(10,2) DEFAULT 0,
        BuaToi TEXT DEFAULT '',
        BuaToiCalo DECIMAL(10,2) DEFAULT 0,
        BuaPhu TEXT DEFAULT '',
        BuaPhuCalo DECIMAL(10,2) DEFAULT 0
    )
""")
conn.commit()
print("[OK] Da tao bang KeHoachDinhDuong")

c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
tables = c.fetchall()
print(f"Tong: {len(tables)} bang")
for t in tables:
    print(f"  - {t[0]}")
conn.close()
