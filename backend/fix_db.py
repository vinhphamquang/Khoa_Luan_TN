import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
if 'sslmode' not in db_url:
    db_url += '?sslmode=require'

conn = psycopg2.connect(db_url)
cursor = conn.cursor()
cursor.execute("""
    UPDATE NguoiDung 
    SET NgayHetHanPremium = COALESCE(NgayNangCap, CURRENT_TIMESTAMP) + INTERVAL '30 days' 
    WHERE LoaiTaiKhoan = 'premium' AND NgayHetHanPremium IS NULL
""")
conn.commit()
print("Updated", cursor.rowcount, "users")
conn.close()
