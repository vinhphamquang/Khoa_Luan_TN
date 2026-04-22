"""
Database Queries for PostgreSQL
Thay thế SQLite bằng PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Kết nối PostgreSQL"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def get_db_cursor(conn):
    """Lấy cursor với RealDictCursor để trả về dict"""
    return conn.cursor(cursor_factory=RealDictCursor)

# ============================================
# USER MANAGEMENT
# ============================================

def create_user(name, email, hashed_password):
    """Tạo user mới"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            INSERT INTO NguoiDung (TenNguoiDung, Email, MatKhau, VaiTro)
            VALUES (%s, %s, %s, 'user')
            RETURNING MaNguoiDung
        """, (name, email, hashed_password))
        
        user_id = cursor.fetchone()['manguoidung']
        conn.commit()
        conn.close()
        
        return True, f"Đăng ký thành công! User ID: {user_id}"
    except psycopg2.IntegrityError:
        return False, "Email đã tồn tại"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"

def get_user_by_email(email):
    """Lấy thông tin user theo email"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT MaNguoiDung, TenNguoiDung, Email, MatKhau, VaiTro
            FROM NguoiDung
            WHERE Email = %s
        """, (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'MaNguoiDung': user['manguoidung'],
                'TenNguoiDung': user['tennguoidung'],
                'Email': user['email'],
                'MatKhau': user['matkhau'],
                'VaiTro': user['vaitro']
            }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_user_by_id(user_id):
    """Lấy thông tin user theo ID"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT MaNguoiDung, TenNguoiDung, Email, MatKhau, VaiTro
            FROM NguoiDung
            WHERE MaNguoiDung = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'MaNguoiDung': user['manguoidung'],
                'TenNguoiDung': user['tennguoidung'],
                'Email': user['email'],
                'MatKhau': user['matkhau'],
                'VaiTro': user['vaitro']
            }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def update_password(user_id, new_hashed_password):
    """Cập nhật mật khẩu"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE NguoiDung
            SET MatKhau = %s
            WHERE MaNguoiDung = %s
        """, (new_hashed_password, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# ============================================
# FOOD MANAGEMENT
# ============================================

def search_food_by_name(food_name):
    """Tìm món ăn theo tên (hỗ trợ tiếng Việt)"""
    try:
        from food_translator import get_search_variants
        from unicode_utils import normalize_for_search
    except ImportError:
        from backend.food_translator import get_search_variants
        from backend.unicode_utils import normalize_for_search
    
    search_variants = get_search_variants(food_name)
    print(f"[SEARCH] Searching for: '{food_name}'")
    print(f"[SEARCH] Variants: {search_variants}")
    
    conn = get_db_connection()
    cursor = get_db_cursor(conn)
    
    try:
        # Priority 1: Exact match
        for variant in search_variants:
            cursor.execute("""
                SELECT * FROM MonAn 
                WHERE LOWER(TenMonAn) = LOWER(%s) AND IsDeleted = 0
                LIMIT 1
            """, (variant,))
            
            mon_an = cursor.fetchone()
            if mon_an:
                print(f"[SEARCH] ✅ Exact match: '{variant}'")
                result = format_food_data(mon_an, cursor, conn)
                conn.close()
                return result
        
        # Priority 2: Partial match
        for variant in search_variants:
            cursor.execute("""
                SELECT * FROM MonAn 
                WHERE LOWER(TenMonAn) LIKE LOWER(%s) AND IsDeleted = 0
                LIMIT 1
            """, (f'%{variant}%',))
            
            mon_an = cursor.fetchone()
            if mon_an:
                print(f"[SEARCH] ⚠️ Partial match: '{variant}'")
                result = format_food_data(mon_an, cursor, conn)
                conn.close()
                return result
        
        print(f"[SEARCH] ❌ No match found")
        conn.close()
        return None
    except Exception as e:
        print(f"[SEARCH ERROR] {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return None

def format_food_data(mon_an, cursor, conn):
    """Format dữ liệu món ăn với dinh dưỡng, công thức, nguyên liệu"""
    ma_mon_an = mon_an['mamonan']
    
    # Get nutrition
    cursor.execute("SELECT * FROM DinhDuong WHERE MaMonAn = %s", (ma_mon_an,))
    dinh_duong = cursor.fetchone()
    
    # Get recipe
    cursor.execute("SELECT * FROM CongThuc WHERE MaMonAn = %s", (ma_mon_an,))
    cong_thuc = cursor.fetchone()
    
    # Get ingredients
    nguyen_lieu = []
    if cong_thuc:
        ma_cong_thuc = cong_thuc['macongthuc']
        cursor.execute("""
            SELECT nl.TenNguyenLieu, ctnl.SoLuong 
            FROM ChiTietNguyenLieu ctnl
            JOIN NguyenLieu nl ON ctnl.MaNguyenLieu = nl.MaNguyenLieu
            WHERE ctnl.MaCongThuc = %s
        """, (ma_cong_thuc,))
        
        ingredients = cursor.fetchall()
        nguyen_lieu = [
            {
                'TenNguyenLieu': ing['tennguyenlieu'],
                'SoLuong': ing['soluong']
            }
            for ing in ingredients
        ]
    
    # Don't close connection here - let caller handle it
    
    result = {
        'MaMonAn': ma_mon_an,
        'TenMonAn': mon_an['tenmonan'],
        'MoTa': mon_an['mota'] or '',
        'PhanLoai': mon_an['phanloai'] or '',
        'IsDeleted': mon_an.get('isdeleted', False),
        'DinhDuong': {
            'Calo': float(dinh_duong['calo']) if dinh_duong and dinh_duong['calo'] else 0,
            'Protein': float(dinh_duong['protein']) if dinh_duong and dinh_duong['protein'] else 0,
            'ChatBeo': float(dinh_duong['chatbeo']) if dinh_duong and dinh_duong['chatbeo'] else 0,
            'Carbohydrate': float(dinh_duong['carbohydrate']) if dinh_duong and dinh_duong['carbohydrate'] else 0,
            'Vitamin': dinh_duong['vitamin'] if dinh_duong else ''
        } if dinh_duong else {
            'Calo': 0,
            'Protein': 0,
            'ChatBeo': 0,
            'Carbohydrate': 0,
            'Vitamin': ''
        },
        'CongThuc': {
            'HuongDan': cong_thuc['huongdan'] if cong_thuc else '',
            'ThoiGianNau': cong_thuc['thoigiannau'] if cong_thuc else 0,
            'KhauPhan': cong_thuc['khauphan'] if cong_thuc else 0,
            'NguyenLieu': nguyen_lieu
        } if cong_thuc else {
            'HuongDan': '',
            'ThoiGianNau': 0,
            'KhauPhan': 0,
            'NguyenLieu': []
        }
    }
    
    return result

def insert_food_full(food_data):
    """Thêm món ăn mới với đầy đủ thông tin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert MonAn
        cursor.execute("""
            INSERT INTO MonAn (TenMonAn, MoTa, PhanLoai)
            VALUES (%s, %s, %s)
            RETURNING MaMonAn
        """, (
            food_data['TenMonAn'],
            food_data.get('MoTa', ''),
            food_data.get('PhanLoai', 'Món ăn')
        ))
        
        ma_mon_an = cursor.fetchone()[0]
        
        # Insert DinhDuong
        if 'DinhDuong' in food_data:
            dd = food_data['DinhDuong']
            cursor.execute("""
                INSERT INTO DinhDuong (MaMonAn, Calo, Protein, ChatBeo, Carbohydrate, Vitamin)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                ma_mon_an,
                dd.get('Calo', 0),
                dd.get('Protein', 0),
                dd.get('ChatBeo', 0),
                dd.get('Carbohydrate', 0),
                dd.get('Vitamin', '')
            ))
        
        # Insert CongThuc
        if 'CongThuc' in food_data:
            ct = food_data['CongThuc']
            cursor.execute("""
                INSERT INTO CongThuc (MaMonAn, HuongDan, ThoiGianNau, KhauPhan)
                VALUES (%s, %s, %s, %s)
                RETURNING MaCongThuc
            """, (
                ma_mon_an,
                ct.get('HuongDan', ''),
                ct.get('ThoiGianNau', 30),
                ct.get('KhauPhan', 1)
            ))
            
            ma_cong_thuc = cursor.fetchone()[0]
            
            # Insert NguyenLieu
            if 'NguyenLieu' in ct:
                for nl in ct['NguyenLieu']:
                    # Insert or get NguyenLieu
                    cursor.execute("""
                        INSERT INTO NguyenLieu (TenNguyenLieu)
                        VALUES (%s)
                        ON CONFLICT DO NOTHING
                        RETURNING MaNguyenLieu
                    """, (nl['TenNguyenLieu'],))
                    
                    result = cursor.fetchone()
                    if result:
                        ma_nguyen_lieu = result[0]
                    else:
                        cursor.execute("""
                            SELECT MaNguyenLieu FROM NguyenLieu
                            WHERE TenNguyenLieu = %s
                        """, (nl['TenNguyenLieu'],))
                        ma_nguyen_lieu = cursor.fetchone()[0]
                    
                    # Insert ChiTietNguyenLieu
                    cursor.execute("""
                        INSERT INTO ChiTietNguyenLieu (MaCongThuc, MaNguyenLieu, SoLuong)
                        VALUES (%s, %s, %s)
                    """, (ma_cong_thuc, ma_nguyen_lieu, nl['SoLuong']))
        
        conn.commit()
        conn.close()
        
        print(f"[SUCCESS] Đã thêm món '{food_data['TenMonAn']}' vào database")
        return True
        
    except Exception as e:
        print(f"[ERROR] Lỗi khi thêm món ăn: {e}")
        return False

# ============================================
# HISTORY
# ============================================

def insert_lich_su(user_id, image_path, food_name, accuracy):
    """Lưu lịch sử nhận diện"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO LichSu (MaNguoiDung, DuongDanAnh, TenMonAn, DoChinhXac)
            VALUES (%s, %s, %s, %s)
        """, (user_id, image_path, food_name, accuracy))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_user_history(user_id):
    """Lấy lịch sử nhận diện của user"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT MaLichSu, TenMonAn, DoChinhXac, ThoiGian
            FROM LichSu
            WHERE MaNguoiDung = %s
            ORDER BY ThoiGian DESC
            LIMIT 50
        """, (user_id,))
        
        history = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': h['malichsu'],
                'food_name': h['tenmonan'],
                'accuracy': float(h['dochinhxac']) if h['dochinhxac'] else 0,
                'time': h['thoigian'].strftime('%Y-%m-%d %H:%M:%S') if h['thoigian'] else ''
            }
            for h in history
        ]
    except Exception as e:
        print(f"Error getting user history: {e}")
        import traceback
        traceback.print_exc()
        return []

# ============================================
# ADMIN FUNCTIONS
# ============================================

def get_all_users():
    """Lấy danh sách tất cả users"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT MaNguoiDung, TenNguoiDung, Email, VaiTro, NgayDangKy
            FROM NguoiDung
            ORDER BY NgayDangKy DESC
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': u['manguoidung'],
                'name': u['tennguoidung'],
                'email': u['email'],
                'role': u['vaitro'],
                'created_at': u['ngaydangky'].strftime('%Y-%m-%d') if u['ngaydangky'] else ''
            }
            for u in users
        ]
    except Exception as e:
        print(f"Error getting users: {e}")
        import traceback
        traceback.print_exc()
        return []

def delete_user(user_id):
    """Xóa user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM NguoiDung WHERE MaNguoiDung = %s", (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_system_stats():
    """Lấy thống kê hệ thống"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        # Count users
        cursor.execute("SELECT COUNT(*) as count FROM NguoiDung")
        total_users = cursor.fetchone()['count']
        
        # Count foods
        cursor.execute("SELECT COUNT(*) as count FROM MonAn WHERE IsDeleted = 0")
        total_foods = cursor.fetchone()['count']
        
        # Count history
        cursor.execute("SELECT COUNT(*) as count FROM LichSu")
        total_scans = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_foods': total_foods,
            'total_scans': total_scans
        }
    except Exception as e:
        print(f"Error: {e}")
        return {'total_users': 0, 'total_foods': 0, 'total_scans': 0}

def get_all_history_admin():
    """Lấy tất cả lịch sử (admin)"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT l.MaLichSu, n.TenNguoiDung, l.TenMonAn, l.DoChinhXac, l.ThoiGian
            FROM LichSu l
            LEFT JOIN NguoiDung n ON l.MaNguoiDung = n.MaNguoiDung
            ORDER BY l.ThoiGian DESC
            LIMIT 100
        """)
        
        history = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': h['malichsu'],
                'user_name': h['tennguoidung'] or 'Guest',
                'food_name': h['tenmonan'],
                'accuracy': float(h['dochinhxac']) if h['dochinhxac'] else 0,
                'time': h['thoigian'].strftime('%Y-%m-%d %H:%M:%S') if h['thoigian'] else ''
            }
            for h in history
        ]
    except Exception as e:
        print(f"Error getting history: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_all_foods_admin():
    """Lấy tất cả món ăn (admin)"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT m.MaMonAn, m.TenMonAn, m.PhanLoai, m.IsDeleted,
                   d.Calo, d.Protein
            FROM MonAn m
            LEFT JOIN DinhDuong d ON m.MaMonAn = d.MaMonAn
            ORDER BY m.MaMonAn DESC
        """)
        
        foods = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': f['mamonan'],
                'name': f['tenmonan'],
                'category': f['phanloai'],
                'calories': float(f['calo']) if f['calo'] else 0,
                'protein': float(f['protein']) if f['protein'] else 0,
                'is_deleted': f['isdeleted']
            }
            for f in foods
        ]
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_food_detail_admin(food_id):
    """Lấy chi tiết món ăn (admin)"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        cursor.execute("SELECT * FROM MonAn WHERE MaMonAn = %s", (food_id,))
        mon_an = cursor.fetchone()
        
        if not mon_an:
            conn.close()
            return None
        
        result = format_food_data(mon_an, cursor, conn)
        conn.close()
        return result
    except Exception as e:
        print(f"Error getting food detail: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_food_full(food_id, food_data):
    """Cập nhật món ăn"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update MonAn
        cursor.execute("""
            UPDATE MonAn
            SET TenMonAn = %s, MoTa = %s, PhanLoai = %s, IsDeleted = %s
            WHERE MaMonAn = %s
        """, (
            food_data['TenMonAn'],
            food_data.get('MoTa', ''),
            food_data.get('PhanLoai', ''),
            food_data.get('IsDeleted', False),
            food_id
        ))
        
        # Update or insert DinhDuong
        if 'DinhDuong' in food_data:
            dd = food_data['DinhDuong']
            cursor.execute("""
                INSERT INTO DinhDuong (MaMonAn, Calo, Protein, ChatBeo, Carbohydrate, Vitamin)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (MaMonAn) DO UPDATE
                SET Calo = EXCLUDED.Calo,
                    Protein = EXCLUDED.Protein,
                    ChatBeo = EXCLUDED.ChatBeo,
                    Carbohydrate = EXCLUDED.Carbohydrate,
                    Vitamin = EXCLUDED.Vitamin
            """, (
                food_id,
                dd.get('Calo', 0),
                dd.get('Protein', 0),
                dd.get('ChatBeo', 0),
                dd.get('Carbohydrate', 0),
                dd.get('Vitamin', '')
            ))
        
        # Update or insert CongThuc
        if 'CongThuc' in food_data:
            ct = food_data['CongThuc']
            
            # Check if recipe exists
            cursor.execute("SELECT MaCongThuc FROM CongThuc WHERE MaMonAn = %s", (food_id,))
            existing_recipe = cursor.fetchone()
            
            if existing_recipe:
                ma_cong_thuc = existing_recipe[0]
                cursor.execute("""
                    UPDATE CongThuc
                    SET HuongDan = %s, ThoiGianNau = %s, KhauPhan = %s
                    WHERE MaCongThuc = %s
                """, (
                    ct.get('HuongDan', ''),
                    ct.get('ThoiGianNau', 30),
                    ct.get('KhauPhan', 1),
                    ma_cong_thuc
                ))
                
                # Delete old ingredients
                cursor.execute("DELETE FROM ChiTietNguyenLieu WHERE MaCongThuc = %s", (ma_cong_thuc,))
            else:
                cursor.execute("""
                    INSERT INTO CongThuc (MaMonAn, HuongDan, ThoiGianNau, KhauPhan)
                    VALUES (%s, %s, %s, %s)
                    RETURNING MaCongThuc
                """, (
                    food_id,
                    ct.get('HuongDan', ''),
                    ct.get('ThoiGianNau', 30),
                    ct.get('KhauPhan', 1)
                ))
                ma_cong_thuc = cursor.fetchone()[0]
            
            # Insert new ingredients
            if 'NguyenLieu' in ct:
                for nl in ct['NguyenLieu']:
                    if not nl.get('TenNguyenLieu'):
                        continue
                        
                    # Insert or get NguyenLieu
                    cursor.execute("""
                        INSERT INTO NguyenLieu (TenNguyenLieu)
                        VALUES (%s)
                        ON CONFLICT (TenNguyenLieu) DO NOTHING
                        RETURNING MaNguyenLieu
                    """, (nl['TenNguyenLieu'],))
                    
                    result = cursor.fetchone()
                    if result:
                        ma_nguyen_lieu = result[0]
                    else:
                        cursor.execute("""
                            SELECT MaNguyenLieu FROM NguyenLieu
                            WHERE TenNguyenLieu = %s
                        """, (nl['TenNguyenLieu'],))
                        ma_nguyen_lieu = cursor.fetchone()[0]
                    
                    # Insert ChiTietNguyenLieu
                    cursor.execute("""
                        INSERT INTO ChiTietNguyenLieu (MaCongThuc, MaNguyenLieu, SoLuong)
                        VALUES (%s, %s, %s)
                    """, (ma_cong_thuc, ma_nguyen_lieu, nl.get('SoLuong', '')))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating food: {e}")
        import traceback
        traceback.print_exc()
        return False

def delete_food_soft(food_id):
    """Soft delete món ăn"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE MonAn
            SET IsDeleted = 1
            WHERE MaMonAn = %s
        """, (food_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting food: {e}")
        import traceback
        traceback.print_exc()
        return False

def restore_food_soft(food_id):
    """Khôi phục món ăn"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE MonAn
            SET IsDeleted = 0
            WHERE MaMonAn = %s
        """, (food_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error restoring food: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================
# HEALTH PROFILE MANAGEMENT
# ============================================

def get_health_profile(user_id):
    """Lấy hồ sơ sức khỏe của user"""
    try:
        conn = get_db_connection()
        cursor = get_db_cursor(conn)
        
        cursor.execute("""
            SELECT MaHoSo, MaNguoiDung, CanNang, ChieuCao, Tuoi, GioiTinh, 
                   MucDoVanDong, MucTieu, BMR, TDEE, CaloDuKien
            FROM HoSoSucKhoe
            WHERE MaNguoiDung = %s
            ORDER BY NgayCapNhat DESC
            LIMIT 1
        """, (user_id,))
        
        profile = cursor.fetchone()
        conn.close()
        
        if profile:
            # Map lowercase column names
            return {
                'MaHoSo': profile.get('mahoso'),
                'MaNguoiDung': profile.get('manguoidung'),
                'CanNang': float(profile.get('cannang')) if profile.get('cannang') else 0,
                'ChieuCao': float(profile.get('chieucao')) if profile.get('chieucao') else 0,
                'Tuoi': profile.get('tuoi'),
                'GioiTinh': profile.get('gioitinh'),
                'MucDoVanDong': profile.get('mucdovandong'),
                'MucTieu': profile.get('muctieu'),
                'BMR': float(profile.get('bmr')) if profile.get('bmr') else 0,
                'TDEE': float(profile.get('tdee')) if profile.get('tdee') else 0,
                'CaloDuKien': float(profile.get('calodukien')) if profile.get('calodukien') else 0
            }
        return None
    except Exception as e:
        print(f"Error getting health profile: {e}")
        import traceback
        traceback.print_exc()
        return None

def upsert_health_profile(user_id, data):
    """Thêm hoặc cập nhật hồ sơ sức khỏe"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate BMR, TDEE, CaloDuKien
        can_nang = float(data.get('CanNang', 0))
        chieu_cao = float(data.get('ChieuCao', 0))
        tuoi = int(data.get('Tuoi', 0))
        gioi_tinh = data.get('GioiTinh', 'Nam')
        muc_do_van_dong = data.get('MucDoVanDong', 'Vừa')
        muc_tieu = data.get('MucTieu', 'Duy trì')
        
        # Calculate BMR (Mifflin-St Jeor)
        if gioi_tinh == 'Nam':
            bmr = 10 * can_nang + 6.25 * chieu_cao - 5 * tuoi + 5
        else:
            bmr = 10 * can_nang + 6.25 * chieu_cao - 5 * tuoi - 161
        
        # Calculate TDEE
        activity_factors = {
            'Ít': 1.2,
            'Vừa': 1.55,
            'Nhiều': 1.725
        }
        tdee = bmr * activity_factors.get(muc_do_van_dong, 1.55)
        
        # Adjust for goal
        goal_adjustments = {
            'Giảm cân': -400,
            'Tăng cân': 400,
            'Duy trì': 0
        }
        calo_du_kien = tdee + goal_adjustments.get(muc_tieu, 0)
        
        # Check if profile exists
        cursor.execute("""
            SELECT MaHoSo FROM HoSoSucKhoe WHERE MaNguoiDung = %s
        """, (user_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update
            cursor.execute("""
                UPDATE HoSoSucKhoe
                SET CanNang = %s, ChieuCao = %s, Tuoi = %s, GioiTinh = %s,
                    MucDoVanDong = %s, MucTieu = %s, BMR = %s, TDEE = %s, CaloDuKien = %s
                WHERE MaNguoiDung = %s
            """, (can_nang, chieu_cao, tuoi, gioi_tinh, muc_do_van_dong, 
                  muc_tieu, bmr, tdee, calo_du_kien, user_id))
        else:
            # Insert
            cursor.execute("""
                INSERT INTO HoSoSucKhoe 
                (MaNguoiDung, CanNang, ChieuCao, Tuoi, GioiTinh, MucDoVanDong, MucTieu, BMR, TDEE, CaloDuKien)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, can_nang, chieu_cao, tuoi, gioi_tinh, muc_do_van_dong,
                  muc_tieu, bmr, tdee, calo_du_kien))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error upserting health profile: {e}")
        import traceback
        traceback.print_exc()
        return False
