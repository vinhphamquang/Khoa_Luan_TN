from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
from external_api import analyze_image
from db_queries import search_food_by_name, insert_lich_su, get_db_connection, insert_generated_food_data
from ai_generator import generate_food_data_vietnamese

app = Flask(__name__, static_folder="../frontend")
CORS(app)

@app.route("/")
def index():
    return send_file(os.path.join(app.static_folder, "index.html"))

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# SPA catch-all: mọi route không match sẽ trả về index.html
@app.route("/<path:path>")
def catch_all(path):
    # Nếu là file tĩnh thực sự thì serve nó
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    # Ngược lại trả về index.html cho SPA routing
    return send_file(os.path.join(app.static_folder, "index.html"))

@app.route("/api/dishes")
def get_dishes():
    """API trả về danh sách các món ăn được hỗ trợ (cho trang Giới Thiệu)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.MaMonAn, m.TenMonAn, m.MoTa, m.PhanLoai,
               d.Calo, d.Protein, d.ChatBeo, d.Carbohydrate
        FROM MonAn m
        LEFT JOIN DinhDuong d ON m.MaMonAn = d.MaMonAn
        ORDER BY m.MaMonAn
    """)
    
    rows = cursor.fetchall()
    dishes = []
    for row in rows:
        row_dict = dict(row)
        dishes.append({
            "id": row_dict.get("MaMonAn"),
            "name": row_dict.get("TenMonAn", ""),
            "description": row_dict.get("MoTa", ""),
            "category": row_dict.get("PhanLoai", ""),
            "calories": row_dict.get("Calo", 0),
            "protein": row_dict.get("Protein", 0),
            "fats": row_dict.get("ChatBeo", 0),
            "carbs": row_dict.get("Carbohydrate", 0),
        })
    
    conn.close()
    return jsonify({"dishes": dishes, "total": len(dishes)})

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
    
    # KÍCH HOẠT AI TỰ ĐỘNG SINH DỮ LIỆU NẾU KHÔNG TÌM THẤY
    is_newly_generated = False
    if not food_data:
        ai_data = generate_food_data_vietnamese(food_name)
        if ai_data:
            success = insert_generated_food_data(food_name, ai_data)
            if success:
                food_data = search_food_by_name(food_name)
                is_newly_generated = True

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
        if is_newly_generated:
            response_data["message"] = f"Món ăn mới '{food_name}' vừa được AI phân tích và lưu vào cơ sở dữ liệu thành công!"
    else:
        response_data["message"] = f"[Cảnh Báo] API nhận diện ra '{food_name}' nhưng trên SQLite chưa có dữ liệu và AI Generator không hoạt động."

    return jsonify(response_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
