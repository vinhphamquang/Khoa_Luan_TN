from fastapi import FastAPI, Depends, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from . import models, database, crud
from ml_core.predict import predict_image

app = FastAPI(title="Hệ Thống Nhận Diện Món Ăn Bằng Hình Ảnh")

# Tự động tạo bảng CSDL dựa theo cấu trúc models.py nếu CSDL chưa có bảng đó
models.Base.metadata.create_all(bind=database.engine)

# Mount thư mục tĩnh cho Frontend (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/predict")
async def analyze_food(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    """
    API Nhận diện món ăn.
    Luồng hoạt động:
    1. Lấy byte ảnh
    2. Model predict -> ra index nhãn dự đoán (VD: 0)
    3. Tìm trong CSDL MySQL món ăn có class_index = 0
    """
    contents = await file.read()
    
    predicted_class_idx, confidence = predict_image(contents)
    
    # Tìm nhanh thông tin món ăn 
    food_info = crud.get_food_by_class_index(db, class_index=predicted_class_idx)
    
    if food_info is None:
        return {
            "success": True,
            "predicted_class_index": predicted_class_idx,
            "confidence": round(confidence * 100, 2),
            "food_data": None,
            "message": f"[Cảnh Báo] Nhận diện nhãn lớp {predicted_class_idx} nhưng trên database chưa khai báo món."
        }
        
    return {
        "success": True,
        "predicted_class_index": predicted_class_idx,
        "confidence": round(confidence * 100, 2),
        "food_data": {
            "name": food_info.name,
            "calories": food_info.calories,
            "proteins": food_info.proteins,
            "carbs": food_info.carbs,
            "fats": food_info.fats,
            "description": food_info.description
        }
    }

@app.get("/api/foods")
def list_foods(db: Session = Depends(database.get_db)):
    return crud.get_all_foods(db)
