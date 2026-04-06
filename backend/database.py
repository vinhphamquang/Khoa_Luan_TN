from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# LƯU Ý CHO USER: Cập nhật "root" và "password" thành thông tin MySQL thực tế của bạn. 
# Ví dụ: "mysql+pymysql://root:123456@localhost:3306/food_recognition_db"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:VINH%4084tv@localhost:3306/nhan_dien_mon_an"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
