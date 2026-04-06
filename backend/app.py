from flask import Flask, request, jsonify, send_from_directory, send_file
import os
from external_api import analyze_image
from db_queries import search_food_by_name, insert_lich_su

app = Flask(__name__, static_folder="../frontend")

@app.route("/")
def index():
    return send_file(os.path.join(app.static_folder, "index.html"))

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
        
    image_bytes = file.read()
    
    # 1. Gọi API nhận diện ngoại
    food_name, confidence = analyze_image(image_bytes)
    
    if not food_name:
        return jsonify({
            "success": False,
            "message": "Không thể nhận diện hình ảnh qua API."
        })
        
    # 2. Truy vấn Database dựa trên tên món ăn
    food_data = search_food_by_name(food_name)
    
    # 3. Format Kết quả
    confidence_pct = round(confidence * 100, 2) if confidence else 0
    
    response_data = {
        "success": True,
        "predicted_class_name": food_name,
        "confidence": confidence_pct,
        "food_data": None,
        "message": ""
    }
    
    if food_data:
        # Map properties cho Frontend
        dinh_duong = food_data.get("DinhDuong") or {}
        cong_thuc = food_data.get("CongThuc") or {}
        nguyen_lieu = cong_thuc.get("NguyenLieu") or []
        
        response_data["food_data"] = {
            "name": food_data.get("TenMonAn", food_name),
            "description": food_data.get("MoTa", ""),
            "calories": dinh_duong.get("Calo", "--"),
            "proteins": dinh_duong.get("Protein", "--"),
            "carbs": dinh_duong.get("Carbohydrate", "--"),
            "fats": dinh_duong.get("ChatBeo", "--"),
            "recipe_instructions": cong_thuc.get("HuongDan", ""),
            "recipe_time": cong_thuc.get("ThoiGianNau", ""),
            "ingredients": nguyen_lieu
        }
    else:
        response_data["message"] = f"[Cảnh Báo] API nhận diện ra '{food_name}' nhưng trên SQLite chưa có dữ liệu món này."

    # (Tùy chọn) Ghi log lịch sử nếu có user_id (hiện tại hardcode = 1)
    # try:
    #     insert_lich_su(1, file.filename, food_name, confidence_pct)
    # except Exception as e:
    #     pass

    return jsonify(response_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
