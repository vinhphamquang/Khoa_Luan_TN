from sqlalchemy.orm import Session
from . import models

def get_food_by_class_index(db: Session, class_index: int):
    """
    Tìm món ăn dựa vào kết quả index dự đoán được từ ML Model.
    """
    return db.query(models.Food).filter(models.Food.class_index == class_index).first()

def get_all_foods(db: Session):
    return db.query(models.Food).all()
