from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base

class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    class_index = Column(Integer, unique=True, index=True) # Nhãn tương ứng với Model Output (vd: 0 -> Phở, 1 -> Bún chả)
    name = Column(String(255), unique=True, index=True)
    calories = Column(Float, default=0.0) # calo (kcal)
    proteins = Column(Float, default=0.0) # đạm (g)
    carbs = Column(Float, default=0.0) # tinh bột (g)
    fats = Column(Float, default=0.0) # chất béo (g)
    description = Column(Text) # Bổ sung thêm mô tả nếu cần
