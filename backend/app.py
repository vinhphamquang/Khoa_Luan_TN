import sys
import os
sys.path.append(os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from external_api import analyze_image
from db_queries import (
    search_food_by_name, insert_lich_su, get_db_connection,
    create_user, get_user_by_email, get_user_history, get_user_by_id, update_password,
    get_all_users, delete_user, get_system_stats, get_all_history_admin, 
    get_all_foods_admin, get_food_detail_admin, insert_food_full, update_food_full, 
    delete_food_soft, restore_food_soft, get_health_profile, upsert_health_profile
)
from ai_generator import generate_food_data_vietnamese
from food_translator import translate_food_name, get_search_variants
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder="../frontend")
CORS(app)

@app.route("/")
def index():
    return send_file(os.path.join(app.static_folder, "index.html"))

@app.route("/admin")
def admin_page():
    return send_file(os.path.join(app.static_folder, "admin.html"))

@app.route("/nutrition")
def nutrition_page():
    return send_file(os.path.join(app.static_folder, "nutrition.html"))

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
    try:
        conn = get_db_connection()
        from psycopg2.extras import RealDictCursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT m.MaMonAn, m.TenMonAn, m.MoTa, m.PhanLoai,
                   d.Calo, d.Protein, d.ChatBeo, d.Carbohydrate
            FROM MonAn m
            LEFT JOIN DinhDuong d ON m.MaMonAn = d.MaMonAn
            WHERE m.IsDeleted = 0
            ORDER BY m.MaMonAn
        """)
        
        rows = cursor.fetchall()
        dishes = []
        for row in rows:
            dishes.append({
                "id": row.get("mamonan"),
                "name": row.get("tenmonan", ""),
                "description": row.get("mota", ""),
                "category": row.get("phanloai", ""),
                "calories": float(row.get("calo", 0)) if row.get("calo") else 0,
                "protein": float(row.get("protein", 0)) if row.get("protein") else 0,
                "fats": float(row.get("chatbeo", 0)) if row.get("chatbeo") else 0,
                "carbs": float(row.get("carbohydrate", 0)) if row.get("carbohydrate") else 0,
            })
        
        conn.close()
        return jsonify({"dishes": dishes, "total": len(dishes)})
    except Exception as e:
        print(f"[ERROR] get_dishes: {e}")
        return jsonify({"dishes": [], "total": 0, "error": str(e)})

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    if not data or not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"success": False, "message": "Vui lòng điền đầy đủ thông tin"}), 400
    
    hashed_password = generate_password_hash(data["password"])
    success, message, user_id = create_user(data["name"], data["email"], hashed_password)
    
    if success and user_id:
        # Nếu có thông tin sức khỏe thì lưu luôn
        tuoi = data.get("hp_age")
        chieu_cao = data.get("hp_height")
        can_nang = data.get("hp_weight")
        if tuoi and chieu_cao and can_nang:
            hp_data = {
                "Tuoi": tuoi,
                "ChieuCao": chieu_cao,
                "CanNang": can_nang,
                "GioiTinh": data.get("hp_gender", "Nam"),
                "MucTieu": data.get("hp_goal", "giu_dang")
            }
            upsert_health_profile(user_id, hp_data)
            
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 400

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"success": False, "message": "Vui lòng nhập Email và Mật khẩu"}), 400
        
    user = get_user_by_email(data["email"])
    if not user or not check_password_hash(user["MatKhau"], data["password"]):
        return jsonify({"success": False, "message": "Email hoặc mật khẩu không đúng"}), 401
        
    return jsonify({
        "success": True,
        "message": "Đăng nhập thành công",
        "user": {
            "id": user["MaNguoiDung"],
            "name": user["TenNguoiDung"],
            "email": user["Email"],
            "role": user["VaiTro"]
        }
    })

@app.route("/api/history/<int:user_id>")
def get_user_history_api(user_id):
    history = get_user_history(user_id)
    return jsonify({"success": True, "history": history})

@app.route("/api/change-password", methods=["POST"])
def change_password():
    data = request.json
    user_id = data.get("user_id")
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    if not user_id or not old_password or not new_password:
        return jsonify({"success": False, "message": "Vui lòng nhập đủ thông tin"}), 400
        
    user = get_user_by_id(user_id)
    if not user or not check_password_hash(user["MatKhau"], old_password):
        return jsonify({"success": False, "message": "Mật khẩu cũ không chính xác"}), 400
        
    if update_password(user_id, generate_password_hash(new_password)):
        return jsonify({"success": True, "message": "Đổi mật khẩu thành công"})
    else:
        return jsonify({"success": False, "message": "Có lỗi xảy ra, vui lòng thử lại"}), 500

@app.route("/api/health-profile/<int:user_id>", methods=["GET"])
def get_user_health_profile(user_id):
    profile = get_health_profile(user_id)
    if profile:
        return jsonify({"success": True, "profile": profile})
    return jsonify({"success": False, "message": "Chưa có hồ sơ sức khỏe"}), 404

@app.route("/api/health-profile/<int:user_id>", methods=["POST"])
def update_user_health_profile(user_id):
    data = request.json
    if upsert_health_profile(user_id, data):
        return jsonify({"success": True, "message": "Cập nhật hồ sơ sức khỏe thành công"})
    return jsonify({"success": False, "message": "Lỗi khi cập nhật hồ sơ"}), 500

@app.route("/api/meal-suggestions", methods=["GET"])
def get_meal_suggestions():
    """API đề xuất món ăn theo bữa và calo mục tiêu - lấy từ CSDL"""
    meal_type = request.args.get('meal_type', 'breakfast')
    target_calo = float(request.args.get('target_calo', 500))
    
    try:
        conn = get_db_connection()
        from psycopg2.extras import RealDictCursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Mapping bữa ăn -> categories thực tế trong CSDL
        meal_categories = {
            'breakfast': [
                'Ăn sáng', 'Món ăn sáng', 'Món hấp', 'Ăn nhẹ', 
                'Bánh', 'Khai vị', 'Breakfast'
            ],
            'lunch': [
                'Món chính', 'Món cơm', 'Món nước', 'Món mặn', 'Món bún',
                'Bún trộn', 'Cơm', 'Lunch', 'Canh'
            ],
            'dinner': [
                'Món chính', 'Món cơm', 'Món mặn', 'Món nước', 'Món bún',
                'Thức ăn nhanh', 'Ăn nhanh', 'Cơm', 'Canh'
            ],
            'snack': [
                'Ăn nhẹ', 'Ăn chơi', 'Món ăn chơi', 'Khai vị', 
                'Tráng miệng', 'Ăn nhanh', 'Antipasti', 'Snack'
            ]
        }
        
        categories = meal_categories.get(meal_type, [])
        
        # Khoảng calo phù hợp (mở rộng để có nhiều kết quả hơn)
        min_calo = target_calo * 0.3
        max_calo = target_calo * 2.0
        
        suggestions = []
        seen_ids = set()
        seen_names = set()
        
        # Bước 1: Tìm món ăn theo category phù hợp với bữa ăn
        if categories:
            category_conditions = ' OR '.join(['m.PhanLoai ILIKE %s' for _ in categories])
            category_params = [f'%{cat}%' for cat in categories]
            
            query_category = f"""
                SELECT m.MaMonAn, m.TenMonAn, m.MoTa, m.PhanLoai,
                       d.Calo, d.Protein, d.ChatBeo, d.Carbohydrate
                FROM MonAn m
                JOIN DinhDuong d ON m.MaMonAn = d.MaMonAn
                WHERE m.IsDeleted = 0
                AND d.Calo IS NOT NULL
                AND d.Calo BETWEEN %s AND %s
                AND ({category_conditions})
                ORDER BY ABS(d.Calo - %s)
                LIMIT 12
            """
            
            params = [min_calo, max_calo] + category_params + [target_calo]
            cursor.execute(query_category, params)
            
            for food in cursor.fetchall():
                food_id = food['mamonan']
                food_name = food['tenmonan'].strip().lower()
                if food_id not in seen_ids and food_name not in seen_names:
                    seen_ids.add(food_id)
                    seen_names.add(food_name)
                    suggestions.append(_format_food_suggestion(food))
        
        # Bước 2: Nếu chưa đủ 6 món, bổ sung từ tất cả món ăn (sắp xếp theo calo gần nhất)
        if len(suggestions) < 6:
            remaining = 12 - len(suggestions)
            exclude_clause = ""
            exclude_params = []
            
            if seen_ids:
                placeholders = ', '.join(['%s'] * len(seen_ids))
                exclude_clause = f"AND m.MaMonAn NOT IN ({placeholders})"
                exclude_params = list(seen_ids)
            
            query_fallback = f"""
                SELECT m.MaMonAn, m.TenMonAn, m.MoTa, m.PhanLoai,
                       d.Calo, d.Protein, d.ChatBeo, d.Carbohydrate
                FROM MonAn m
                JOIN DinhDuong d ON m.MaMonAn = d.MaMonAn
                WHERE m.IsDeleted = 0
                AND d.Calo IS NOT NULL
                AND d.Calo > 0
                {exclude_clause}
                ORDER BY ABS(d.Calo - %s)
                LIMIT %s
            """
            
            params_fallback = exclude_params + [target_calo, remaining]
            cursor.execute(query_fallback, params_fallback)
            
            for food in cursor.fetchall():
                food_id = food['mamonan']
                food_name = food['tenmonan'].strip().lower()
                if food_id not in seen_ids and food_name not in seen_names:
                    seen_ids.add(food_id)
                    seen_names.add(food_name)
                    suggestions.append(_format_food_suggestion(food))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'meal_type': meal_type,
            'target_calo': target_calo
        })
        
    except Exception as e:
        print(f"[ERROR] get_meal_suggestions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


def _format_food_suggestion(food):
    """Format một dòng dữ liệu món ăn thành dict cho API response"""
    return {
        'id': food['mamonan'],
        'name': food['tenmonan'],
        'description': food['mota'] or '',
        'category': food['phanloai'] or '',
        'calories': float(food['calo']) if food['calo'] else 0,
        'protein': float(food['protein']) if food['protein'] else 0,
        'carbs': float(food['carbohydrate']) if food['carbohydrate'] else 0,
        'fats': float(food['chatbeo']) if food['chatbeo'] else 0
    }

# ============================================
# MEAL PLAN SAVE & HISTORY
# ============================================

@app.route("/api/meal-plans/<int:user_id>", methods=["POST"])
def save_meal_plan(user_id):
    """Lưu kế hoạch dinh dưỡng trong ngày"""
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO KeHoachDinhDuong 
            (MaNguoiDung, CaloDuKien, TongCaloChon, BuaSang, BuaSangCalo, BuaTrua, BuaTruaCalo, BuaToi, BuaToiCalo, BuaPhu, BuaPhuCalo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            data.get('caloDuKien', 0),
            data.get('tongCaloChon', 0),
            data.get('buaSang', ''),
            data.get('buaSangCalo', 0),
            data.get('buaTrua', ''),
            data.get('buaTruaCalo', 0),
            data.get('buaToi', ''),
            data.get('buaToiCalo', 0),
            data.get('buaPhu', ''),
            data.get('buaPhuCalo', 0)
        ))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Đã lưu kế hoạch dinh dưỡng!'})
        
    except Exception as e:
        print(f"[ERROR] save_meal_plan: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/api/meal-plans/<int:user_id>", methods=["GET"])
def get_meal_plans(user_id):
    """Lấy lịch sử kế hoạch dinh dưỡng"""
    try:
        from psycopg2.extras import RealDictCursor
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT MaKeHoach, NgayLuu, CaloDuKien, TongCaloChon,
                   BuaSang, BuaSangCalo, BuaTrua, BuaTruaCalo,
                   BuaToi, BuaToiCalo, BuaPhu, BuaPhuCalo
            FROM KeHoachDinhDuong
            WHERE MaNguoiDung = %s
            ORDER BY NgayLuu DESC
            LIMIT 100
        """, (user_id,))
        
        plans = cursor.fetchall()
        conn.close()
        
        result = []
        for p in plans:
            result.append({
                'id': p['makehoach'],
                'date': p['ngayluu'].strftime('%Y-%m-%d %H:%M') if p['ngayluu'] else '',
                'month': p['ngayluu'].strftime('%Y-%m') if p['ngayluu'] else '',
                'caloDuKien': float(p['calodukien']) if p['calodukien'] else 0,
                'tongCaloChon': float(p['tongcalochon']) if p['tongcalochon'] else 0,
                'buaSang': p['buasang'] or '',
                'buaSangCalo': float(p['buasangcalo']) if p['buasangcalo'] else 0,
                'buaTrua': p['buatrua'] or '',
                'buaTruaCalo': float(p['buatruacalo']) if p['buatruacalo'] else 0,
                'buaToi': p['buatoi'] or '',
                'buaToiCalo': float(p['buatoicalo']) if p['buatoicalo'] else 0,
                'buaPhu': p['buaphu'] or '',
                'buaPhuCalo': float(p['buaphucalo']) if p['buaphucalo'] else 0
            })
        
        return jsonify({'success': True, 'plans': result})
        
    except Exception as e:
        print(f"[ERROR] get_meal_plans: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/api/admin/users", methods=["GET"])
def api_admin_get_users():
    return jsonify({"success": True, "users": get_all_users()})

@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
def api_admin_delete_user(user_id):
    if delete_user(user_id): return jsonify({"success": True, "message": "Xóa người dùng thành công"})
    return jsonify({"success": False, "message": "Lỗi khi xóa người dùng"}), 500

@app.route("/api/admin/stats", methods=["GET"])
def api_admin_get_stats():
    return jsonify({"success": True, "stats": get_system_stats()})

@app.route("/api/admin/history", methods=["GET"])
def api_admin_get_history():
    return jsonify({"success": True, "history": get_all_history_admin()})

@app.route("/api/admin/foods", methods=["GET"])
def api_admin_get_foods():
    return jsonify({"success": True, "foods": get_all_foods_admin()})

@app.route("/api/admin/foods/<int:food_id>", methods=["GET"])
def api_admin_get_food(food_id):
    data = get_food_detail_admin(food_id)
    if data: return jsonify({"success": True, "food": data})
    return jsonify({"success": False, "message": "Không tìm thấy món ăn"}), 404

@app.route("/api/admin/foods", methods=["POST"])
def api_admin_add_food():
    data = request.json
    if not data or not data.get("TenMonAn"):
        return jsonify({"success": False, "message": "Thiếu thông tin tên món ăn"}), 400
    if insert_food_full(data):
        return jsonify({"success": True, "message": "Thêm món ăn thành công"})
    return jsonify({"success": False, "message": "Lỗi khi thêm món ăn"}), 500

@app.route("/api/admin/foods/<int:food_id>", methods=["PUT"])
def api_admin_update_food(food_id):
    data = request.json
    if not data or not data.get("TenMonAn"):
        return jsonify({"success": False, "message": "Thiếu thông tin tên món ăn"}), 400
    if update_food_full(food_id, data):
        return jsonify({"success": True, "message": "Cập nhật món ăn thành công"})
    return jsonify({"success": False, "message": "Lỗi khi cập nhật món ăn"}), 500

@app.route("/api/admin/foods/<int:food_id>", methods=["DELETE"])
def api_admin_delete_food(food_id):
    if delete_food_soft(food_id):
        return jsonify({"success": True, "message": "Đã chuyển món ăn vào thùng rác (Soft Delete) thành công"})
    return jsonify({"success": False, "message": "Lỗi khi xóa món ăn"}), 500

@app.route("/api/admin/foods/<int:food_id>/restore", methods=["PUT"])
def api_admin_restore_food(food_id):
    if restore_food_soft(food_id):
        return jsonify({"success": True, "message": "Đã khôi phục món ăn từ thùng rác thành công"})
    return jsonify({"success": False, "message": "Lỗi khi khôi phục món ăn"}), 500

def get_recommendation(user_id, calories):
    if not user_id or str(calories) == '--':
        return None
    
    try:
        calories = float(calories)
    except:
        return None

    profile = get_health_profile(user_id)
    if not profile:
        return None

    chieu_cao = profile.get('ChieuCao')
    can_nang = profile.get('CanNang')
    muc_tieu = profile.get('MucTieu')

    if not chieu_cao or not can_nang or not muc_tieu:
        return None

    bmi = can_nang / ((chieu_cao / 100) ** 2)
    bmi = round(bmi, 1)

    if bmi < 18.5:
        bmi_category = "Gầy"
    elif 18.5 <= bmi < 25:
        bmi_category = "Bình thường"
    else:
        bmi_category = "Thừa cân"

    threshold = 350
    recommendation = ""
    reason = ""

    # Normalize muc_tieu to lowercase for comparison
    muc_tieu_lower = str(muc_tieu).lower()
    
    if 'giam' in muc_tieu_lower or 'giảm' in muc_tieu_lower:
        # Giảm cân
        if calories > threshold:
            recommendation = "Hạn chế"
            reason = f"Món ăn có lượng calo ({calories} kcal) khá cao, không tốt cho mục tiêu giảm cân."
        else:
            recommendation = "Nên ăn"
            reason = f"Món ăn ít calo ({calories} kcal), phù hợp với mục tiêu giảm cân."
    elif 'tang' in muc_tieu_lower or 'tăng' in muc_tieu_lower:
        # Tăng cân
        if calories > threshold:
            recommendation = "Nên ăn"
            reason = f"Món ăn giàu năng lượng ({calories} kcal), rất tốt cho mục tiêu tăng cân."
        else:
            recommendation = "Ăn vừa phải"
            reason = f"Món ăn ít năng lượng ({calories} kcal), nên ăn kèm các món khác để đủ calo tăng cân."
    else:
        # Duy trì / Giữ dáng
        recommendation = "Ăn cân đối"
        reason = f"Món ăn cung cấp {calories} kcal, ăn uống cân đối để duy trì vóc dáng."

    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "recommendation": recommendation,
        "reason": reason
    }

@app.route("/api/dishes/<food_name>", methods=["GET"])
def get_dish_info(food_name):
    """API lấy thông tin món ăn trực tiếp từ database (cho demo mode)"""
    try:
        food_data = search_food_by_name(food_name)
        
        if not food_data:
            return jsonify({
                "success": False,
                "message": f"Không tìm thấy món ăn '{food_name}' trong database"
            }), 404
        
        # Format giống như predict endpoint
        dinh_duong = food_data.get("DinhDuong") or {}
        cong_thuc = food_data.get("CongThuc") or {}
        nguyen_lieu = cong_thuc.get("NguyenLieu") or []
        
        response_data = {
            "success": True,
            "predicted_class_name": food_name,
            "confidence": 100.0,  # Demo mode = 100% confidence
            "food_data": {
                "name": food_data.get("TenMonAn", food_name),
                "description": food_data.get("MoTa", ""),
                "calories": dinh_duong.get("Calo", "--"),
                "proteins": dinh_duong.get("Protein", "--"),
                "carbs": dinh_duong.get("Carbohydrate", "--"),
                "fats": dinh_duong.get("ChatBeo", "--"),
                "recipe_instructions": cong_thuc.get("HuongDan", ""),
                "recipe_time": cong_thuc.get("ThoiGianNau", ""),
                "ingredients": nguyen_lieu
            },
            "message": "Chế độ demo - Dữ liệu từ database"
        }
        
        user_id = request.args.get("user_id")
        if user_id and str(user_id).isdigit():
            rec = get_recommendation(int(user_id), dinh_duong.get("Calo", "--"))
            if rec:
                response_data["health_recommendation"] = rec

        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[Get Dish Error] {e}")
        return jsonify({
            "success": False,
            "message": f"Lỗi server: {str(e)}"
        }), 500

@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
        
    image_bytes = file.read()
    
    # 1. Gọi API nhận diện món ăn từ hình ảnh (tiếng Anh)
    food_name_english, confidence, error_msg = analyze_image(image_bytes)
    
    if not food_name_english:
        return jsonify({
            "success": False,
            "message": "Không thể nhận diện hình ảnh. API đang gặp sự cố (timeout hoặc quá tải). Vui lòng thử lại sau hoặc chọn ảnh khác.",
            "error_detail": error_msg,
            "suggestion": "Bạn có thể thử upload ảnh Phở, Bánh Mì hoặc Bún Chả để xem demo với dữ liệu có sẵn."
        }), 503  # Service Unavailable
    
    # 2. Dịch tên món ăn sang tiếng Việt
    food_name_vietnamese = translate_food_name(food_name_english)
    print(f"[TRANSLATE] '{food_name_english}' → '{food_name_vietnamese}'")
    
    # 3. Tìm kiếm món ăn trong Database (thử cả tiếng Anh và tiếng Việt)
    print(f"[INFO] Tìm kiếm '{food_name_vietnamese}' trong database...")
    food_data = search_food_by_name(food_name_vietnamese)
    
    # Nếu không tìm thấy bằng tiếng Việt, thử tiếng Anh
    if not food_data and food_name_vietnamese != food_name_english:
        print(f"[INFO] Thử tìm bằng tên tiếng Anh: '{food_name_english}'")
        food_data = search_food_by_name(food_name_english)
    
    is_newly_added = False
    found_in_db = bool(food_data)  # Track if food was found in DB
    
    # 4. Nếu không có trong database, tự động lấy thông tin từ AI (Tiếng Việt) và thêm vào
    if not food_data:
        print(f"[INFO] Không tìm thấy '{food_name_vietnamese}' trong database. Đang tạo thông tin mới bằng AI...")
        try:
            from ai_generator import generate_food_data_vietnamese
            
            ai_data = generate_food_data_vietnamese(food_name_english)
            
            if ai_data:
                print(f"[INFO] Đã tạo thông tin từ AI. Đang thêm vào database...")
                
                # Nếu translation dictionary không có, dùng tên tiếng Việt do AI trả về
                if food_name_vietnamese == food_name_english and "TenMonAn" in ai_data:
                    food_name_vietnamese = ai_data["TenMonAn"]
                
                # Chuẩn bị dữ liệu để insert vào database
                food_to_insert = {
                    "TenMonAn": food_name_vietnamese,
                    "MoTa": ai_data.get("MoTa", f"Món ăn {food_name_vietnamese}"),
                    "PhanLoai": ai_data.get("PhanLoai", "Món ăn"),
                    "DinhDuong": ai_data.get("DinhDuong", {
                        "Calo": 0, "Protein": 0, "ChatBeo": 0, "Carbohydrate": 0, "Vitamin": ""
                    }),
                    "CongThuc": ai_data.get("CongThuc", {
                        "HuongDan": "Chưa có hướng dẫn",
                        "ThoiGianNau": 30,
                        "KhauPhan": 1,
                        "NguyenLieu": []
                    })
                }
                
                # Thêm vào database
                if insert_food_full(food_to_insert):
                    print(f"[SUCCESS] Đã thêm '{food_name_vietnamese}' vào database!")
                    is_newly_added = True
                    
                    # Tìm lại trong database
                    food_data = search_food_by_name(food_name_vietnamese)
                else:
                    print(f"[ERROR] Không thể thêm '{food_name_vietnamese}' vào database")
            else:
                print(f"[WARNING] Không tạo được dữ liệu từ AI cho '{food_name_english}'")
                
        except Exception as e:
            print(f"[ERROR] Lỗi khi tạo dữ liệu từ AI: {e}")
            # Không làm gián đoạn flow nếu external API lỗi

    # 5. Format Kết quả (sử dụng tên tiếng Việt)
    confidence_pct = round(confidence * 100, 2) if confidence else 0
    
    response_data = {
        "success": True,
        "predicted_class_name": food_name_vietnamese,  # Trả về tên tiếng Việt
        "confidence": confidence_pct,
        "food_data": None,
        "message": "",
        "found_in_db": found_in_db,  # NEW: Cho frontend biết món có sẵn hay không
        "is_new": is_newly_added  # NEW: Cho frontend biết món vừa được thêm
    }
    
    if food_data:
        # Map properties cho Frontend
        dinh_duong = food_data.get("DinhDuong") or {}
        cong_thuc = food_data.get("CongThuc") or {}
        nguyen_lieu = cong_thuc.get("NguyenLieu") or []
        
        response_data["food_data"] = {
            "name": food_data.get("TenMonAn", food_name_vietnamese),
            "description": food_data.get("MoTa", ""),
            "calories": dinh_duong.get("Calo", "--"),
            "proteins": dinh_duong.get("Protein", "--"),
            "carbs": dinh_duong.get("Carbohydrate", "--"),
            "fats": dinh_duong.get("ChatBeo", "--"),
            "recipe_instructions": cong_thuc.get("HuongDan", ""),
            "recipe_time": cong_thuc.get("ThoiGianNau", ""),
            "ingredients": nguyen_lieu
        }
        
        if is_newly_added:
            response_data["message"] = f"✨ Món ăn '{food_name_vietnamese}' vừa được thêm vào cơ sở dữ liệu!"
        else:
            response_data["message"] = f"✅ Đã tìm thấy thông tin món '{food_name_vietnamese}' trong cơ sở dữ liệu"
    else:
        response_data["message"] = f"⚠️ Nhận diện được '{food_name_vietnamese}' nhưng chưa có đầy đủ thông tin. Vui lòng thử lại sau."


    user_id = request.form.get("user_id")
    if user_id and str(user_id).isdigit():
        try:
            # Lưu lịch sử với tên tiếng Việt
            insert_lich_su(int(user_id), "", food_name_vietnamese, confidence_pct)
        except Exception as e:
            print(f"Error saving history: {e}")

        # Tính toán lời khuyên sức khỏe
        if food_data and food_data.get("DinhDuong"):
            calo = food_data["DinhDuong"].get("Calo", "--")
            rec = get_recommendation(int(user_id), calo)
            if rec:
                response_data["health_recommendation"] = rec

    return jsonify(response_data)

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """API để user đánh giá kết quả nhận diện"""
    data = request.json
    
    user_id = data.get("user_id")
    food_name = data.get("food_name")
    confidence = data.get("confidence", 0)
    rating = data.get("rating")  # 'accurate' hoặc 'inaccurate'
    correct_name = data.get("correct_name")  # Tên đúng nếu user sửa
    
    if not food_name or not rating:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO FeedbackNhanDien (MaNguoiDung, TenMonNhanDien, DoChinhXac, DanhGia, TenMonDung)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, food_name, confidence, rating, correct_name))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Cảm ơn bạn đã đánh giá!"
        })
    except Exception as e:
        print(f"[ERROR] Lỗi khi lưu feedback: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/retry-recognition", methods=["POST"])
def retry_recognition():
    """API để nhận diện lại với các API khác"""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
    
    # Lấy kết quả cũ để skip API đó
    skip_api = request.form.get("skip_api", "")
    
    image_bytes = file.read()
    
    print(f"[RETRY] Nhận diện lại, skip API: {skip_api}")
    
    # Gọi API nhận diện với logic retry
    from external_api import analyze_image_with_retry
    food_name_english, confidence, error_msg = analyze_image_with_retry(image_bytes, skip_api)
    
    if not food_name_english:
        return jsonify({
            "success": False,
            "message": "Vẫn không thể nhận diện. Vui lòng thử ảnh khác hoặc chọn món thủ công.",
            "error_detail": error_msg
        }), 503
    
    # Dịch sang tiếng Việt
    food_name_vietnamese = translate_food_name(food_name_english)
    print(f"[RETRY TRANSLATE] '{food_name_english}' → '{food_name_vietnamese}'")
    
    # Tìm trong database
    food_data = search_food_by_name(food_name_vietnamese)
    
    if not food_data and food_name_vietnamese != food_name_english:
        food_data = search_food_by_name(food_name_english)
    
    # Tự động thêm nếu chưa có
    is_newly_added = False
    if not food_data:
        try:
            from ai_generator import generate_food_data_vietnamese
            
            ai_data = generate_food_data_vietnamese(food_name_english)
            
            if ai_data:
                if food_name_vietnamese == food_name_english and "TenMonAn" in ai_data:
                    food_name_vietnamese = ai_data["TenMonAn"]
                
                food_to_insert = {
                    "TenMonAn": food_name_vietnamese,
                    "MoTa": ai_data.get("MoTa", f"Món ăn {food_name_vietnamese}"),
                    "PhanLoai": ai_data.get("PhanLoai", "Món ăn"),
                    "DinhDuong": ai_data.get("DinhDuong", {
                        "Calo": 0, "Protein": 0, "ChatBeo": 0, "Carbohydrate": 0, "Vitamin": ""
                    }),
                    "CongThuc": ai_data.get("CongThuc", {
                        "HuongDan": "Chưa có hướng dẫn",
                        "ThoiGianNau": 30,
                        "KhauPhan": 1,
                        "NguyenLieu": []
                    })
                }
                
                if insert_food_full(food_to_insert):
                    is_newly_added = True
                    food_data = search_food_by_name(food_name_vietnamese)
        except Exception as e:
            print(f"[ERROR] Lỗi khi thêm món: {e}")
    
    # Format response
    confidence_pct = round(confidence * 100, 2) if confidence else 0
    
    response_data = {
        "success": True,
        "predicted_class_name": food_name_vietnamese,
        "confidence": confidence_pct,
        "food_data": None,
        "message": ""
    }
    
    if food_data:
        dinh_duong = food_data.get("DinhDuong") or {}
        cong_thuc = food_data.get("CongThuc") or {}
        nguyen_lieu = cong_thuc.get("NguyenLieu") or []
        
        response_data["food_data"] = {
            "name": food_data.get("TenMonAn", food_name_vietnamese),
            "description": food_data.get("MoTa", ""),
            "calories": dinh_duong.get("Calo", "--"),
            "proteins": dinh_duong.get("Protein", "--"),
            "carbs": dinh_duong.get("Carbohydrate", "--"),
            "fats": dinh_duong.get("ChatBeo", "--"),
            "recipe_instructions": cong_thuc.get("HuongDan", ""),
            "recipe_time": cong_thuc.get("ThoiGianNau", ""),
            "ingredients": nguyen_lieu
        }
        
        if is_newly_added:
            response_data["message"] = f"✨ Nhận diện lại thành công! Món '{food_name_vietnamese}' vừa được thêm vào."
        else:
            response_data["message"] = f"✅ Nhận diện lại thành công: '{food_name_vietnamese}'"
    
    # Lưu lịch sử
    user_id = request.form.get("user_id")
    if user_id and str(user_id).isdigit():
        try:
            insert_lich_su(int(user_id), "", food_name_vietnamese, confidence_pct)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
