import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'food_recognition.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_mapped_food_name(food_name: str) -> str:
    """
    Ánh xạ tên/nhãn tiếng Anh thường gặp từ API về tên món ăn trong Database.
    CHỈ map những trường hợp rất cụ thể để tránh nhầm lẫn.
    """
    food_lower = food_name.lower().strip()
    
    # CHỈ map những trường hợp RẤT CỤ THỂ
    alias_map = {
        # Phở - chỉ map những tên rất cụ thể
        'pho': 'Phở',
        'pho bo': 'Phở Bò',
        'beef pho': 'Phở Bò',
        'chicken pho': 'Phở Gà',
        'vietnamese noodle soup': 'Phở',
        
        # Bánh Mì - chỉ map tên cụ thể
        'banh mi': 'Bánh Mì',
        'banh my': 'Bánh Mì',
        'vietnamese sandwich': 'Bánh Mì',
        'vietnamese baguette': 'Bánh Mì',
        
        # Bún Chả
        'bun cha': 'Bún Chả',
        'grilled pork with noodles': 'Bún Chả',
        'vietnamese grilled pork': 'Bún Chả',
        
        # Bún Bò Huế
        'bun bo hue': 'Bún Bò Huế',
        'bun bo': 'Bún Bò Huế',
        'hue beef noodle': 'Bún Bò Huế',
        'spicy beef noodle soup': 'Bún Bò Huế',
        
        # Gỏi Cuốn
        'goi cuon': 'Gỏi Cuốn',
        'fresh spring rolls': 'Gỏi Cuốn',
        'summer rolls': 'Gỏi Cuốn',
        'vietnamese spring rolls': 'Gỏi Cuốn',
        
        # Chả Giò
        'cha gio': 'Chả Giò',
        'fried spring rolls': 'Chả Giò',
        'vietnamese egg rolls': 'Chả Giò',
        
        # Cơm Tấm
        'com tam': 'Cơm Tấm',
        'broken rice': 'Cơm Tấm',
        'vietnamese broken rice': 'Cơm Tấm',
    }
    
    return alias_map.get(food_lower, food_name)

def search_food_by_name(food_name: str):
    """
    Search for a food item by name or English translation in the database.
    Uses multiple search variants (Vietnamese, English, case variations) for better matching.
    Priority: Exact match > Normalized match > Partial match
    """
    try:
        from food_translator import get_search_variants
        from unicode_utils import normalize_for_search
    except ImportError:
        from backend.food_translator import get_search_variants
        from backend.unicode_utils import normalize_for_search
    
    # Get all search variants (Vietnamese, English, case variations)
    search_variants = get_search_variants(food_name)
    print(f"[SEARCH] Searching for: '{food_name}'")
    print(f"[SEARCH] Variants: {search_variants}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Try each variant with priority matching
    mon_an = None
    
    # Priority 1: Exact match (case-insensitive)
    for variant in search_variants:
        if mon_an:
            break
            
        mapped_name = get_mapped_food_name(variant)
        
        # Try exact match with mapped name
        cursor.execute("""
            SELECT * FROM MonAn 
            WHERE LOWER(TenMonAn) = LOWER(?) AND IsDeleted = 0
            LIMIT 1
        """, (mapped_name,))
        mon_an = cursor.fetchone()
        
        if mon_an:
            print(f"[SEARCH] ✅ Exact match: '{variant}' = '{dict(mon_an)['TenMonAn']}'")
            break
        
        # Try exact match with original variant
        cursor.execute("""
            SELECT * FROM MonAn 
            WHERE LOWER(TenMonAn) = LOWER(?) AND IsDeleted = 0
            LIMIT 1
        """, (variant,))
        mon_an = cursor.fetchone()
        
        if mon_an:
            print(f"[SEARCH] ✅ Exact match: '{variant}' = '{dict(mon_an)['TenMonAn']}'")
            break
    
    # Priority 2: Normalized match (without accents)
    if not mon_an:
        for variant in search_variants:
            if mon_an:
                break
            
            normalized_search = normalize_for_search(variant)
            
            # Get all foods and compare normalized
            cursor.execute("""
                SELECT * FROM MonAn WHERE IsDeleted = 0
            """)
            all_foods = cursor.fetchall()
            
            for food in all_foods:
                food_dict = dict(food)
                normalized_db = normalize_for_search(food_dict['TenMonAn'])
                
                if normalized_db == normalized_search:
                    mon_an = food
                    print(f"[SEARCH] ✅ Normalized match: '{variant}' ≈ '{food_dict['TenMonAn']}'")
                    break
            
            if mon_an:
                break
    
    # Priority 3: Partial match (only if search term is long enough)
    if not mon_an and len(food_name) >= 4:
        for variant in search_variants:
            if mon_an:
                break
                
            mapped_name = get_mapped_food_name(variant)
            normalized_search = normalize_for_search(variant)
            
            # Get all foods and check if search term is contained
            cursor.execute("""
                SELECT * FROM MonAn WHERE IsDeleted = 0
            """)
            all_foods = cursor.fetchall()
            
            for food in all_foods:
                food_dict = dict(food)
                normalized_db = normalize_for_search(food_dict['TenMonAn'])
                
                # Check if search term is in food name
                if normalized_search in normalized_db or normalized_db in normalized_search:
                    mon_an = food
                    print(f"[SEARCH] ⚠️  Partial match: '{variant}' in '{food_dict['TenMonAn']}'")
                    break
            
            if mon_an:
                break
    
    if not mon_an:
        print(f"[SEARCH] ❌ No match found for '{food_name}'")
        conn.close()
        return None
        
    mon_an_dict = dict(mon_an)
    ma_mon_an = mon_an_dict['MaMonAn']
    
    # 2. Get DinhDuong (Nutrition)
    cursor.execute("SELECT * FROM DinhDuong WHERE MaMonAn = ?", (ma_mon_an,))
    dinh_duong = cursor.fetchone()
    if dinh_duong:
        mon_an_dict['DinhDuong'] = dict(dinh_duong)
    else:
        mon_an_dict['DinhDuong'] = None
        
    # 3. Get CongThuc (Recipe)
    cursor.execute("SELECT * FROM CongThuc WHERE MaMonAn = ?", (ma_mon_an,))
    cong_thuc = cursor.fetchone()
    
    if cong_thuc:
        cong_thuc_dict = dict(cong_thuc)
        ma_cong_thuc = cong_thuc_dict['MaCongThuc']
        
        # 4. Get Ingredients for this recipe
        cursor.execute("""
            SELECT nl.TenNguyenLieu, ctnl.SoLuong 
            FROM ChiTietNguyenLieu ctnl
            JOIN NguyenLieu nl ON ctnl.MaNguyenLieu = nl.MaNguyenLieu
            WHERE ctnl.MaCongThuc = ?
        """, (ma_cong_thuc,))
        nguyen_lieu_list = cursor.fetchall()
        cong_thuc_dict['NguyenLieu'] = [dict(row) for row in nguyen_lieu_list]
        
        mon_an_dict['CongThuc'] = cong_thuc_dict
    else:
        mon_an_dict['CongThuc'] = None
        
    conn.close()
    return mon_an_dict

def insert_lich_su(ma_nguoi_dung, hinh_anh, ket_qua, do_chinh_xac):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO LichSuNhanDien (MaNguoiDung, HinhAnh, KetQuaNhanDien, DoChinhXac, ThoiGianNhanDien)
        VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
    """, (ma_nguoi_dung, hinh_anh, ket_qua, do_chinh_xac))
    conn.commit()
    conn.close()

def create_user(name: str, email: str, hashed_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO NguoiDung (TenNguoiDung, Email, MatKhau, NgayDangKy, VaiTro)
            VALUES (?, ?, ?, date('now', 'localtime'), 'user')
        """, (name, email, hashed_password))
        user_id = cursor.lastrowid
        conn.commit()
        return True, "Đăng ký thành công", user_id
    except sqlite3.IntegrityError:
        return False, "Email đã được sử dụng", None
    except Exception as e:
        return False, str(e), None
    finally:
        conn.close()

def get_user_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM NguoiDung WHERE Email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def get_user_by_id(ma_nguoi_dung: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM NguoiDung WHERE MaNguoiDung = ?", (ma_nguoi_dung,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def update_password(ma_nguoi_dung: int, new_hashed_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE NguoiDung SET MatKhau = ? WHERE MaNguoiDung = ?", (new_hashed_password, ma_nguoi_dung))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        return False
    finally:
        conn.close()

def get_user_history(ma_nguoi_dung: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MaLichSu, HinhAnh, KetQuaNhanDien, DoChinhXac, ThoiGianNhanDien 
        FROM LichSuNhanDien 
        WHERE MaNguoiDung = ? 
        ORDER BY ThoiGianNhanDien DESC
    """, (ma_nguoi_dung,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def create_health_profile_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HoSoSucKhoe (
            MaHoSo INTEGER PRIMARY KEY AUTOINCREMENT,
            MaNguoiDung INTEGER UNIQUE,
            Tuoi INTEGER,
            ChieuCao REAL,
            CanNang REAL,
            GioiTinh TEXT,
            MucTieu TEXT,
            FOREIGN KEY(MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def get_health_profile(ma_nguoi_dung: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM HoSoSucKhoe WHERE MaNguoiDung = ?", (ma_nguoi_dung,))
    profile = cursor.fetchone()
    conn.close()
    if profile:
        return dict(profile)
    return None

def upsert_health_profile(ma_nguoi_dung: int, data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MaHoSo FROM HoSoSucKhoe WHERE MaNguoiDung = ?", (ma_nguoi_dung,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("""
                UPDATE HoSoSucKhoe 
                SET Tuoi = ?, ChieuCao = ?, CanNang = ?, GioiTinh = ?, MucTieu = ?
                WHERE MaNguoiDung = ?
            """, (data.get('Tuoi'), data.get('ChieuCao'), data.get('CanNang'), data.get('GioiTinh'), data.get('MucTieu'), ma_nguoi_dung))
        else:
            cursor.execute("""
                INSERT INTO HoSoSucKhoe (MaNguoiDung, Tuoi, ChieuCao, CanNang, GioiTinh, MucTieu)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ma_nguoi_dung, data.get('Tuoi'), data.get('ChieuCao'), data.get('CanNang'), data.get('GioiTinh'), data.get('MucTieu')))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error upsert_health_profile: {e}")
        return False
    finally:
        conn.close()


import datetime

def insert_generated_food_data(food_name_english: str, data: dict):
    """
    Nhận dữ liệu dạng JSON dict từ Gemini và lưu vào SQLite.
    Bao gồm ghi chú gốc tiếng Anh vào `MoTa` để lần sau `search_food_by_name` có thể match được qua `MoTa LIKE ?`
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Thêm ghi chú Tên Tiếng Anh vào Mô tả để công cụ tìm kiếm qua LIKE tìm được trong tương lai
        mo_ta = data.get('MoTa', '') + f" [AI_Alias: {food_name_english}]"
        
        # 1. Insert MonAn
        cursor.execute("""
            INSERT INTO MonAn (TenMonAn, MoTa, PhanLoai, NgayTao)
            VALUES (?, ?, ?, ?)
        """, (data.get('TenMonAn', food_name_english), mo_ta, data.get('PhanLoai', ''), datetime.date.today().strftime('%Y-%m-%d')))
        ma_mon_an = cursor.lastrowid
        
        dinh_duong = data.get('DinhDuong', {})
        # 2. Insert DinhDuong
        cursor.execute("""
            INSERT INTO DinhDuong (MaMonAn, Calo, Protein, ChatBeo, Carbohydrate, Vitamin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ma_mon_an, 
            dinh_duong.get('Calo', 0), 
            dinh_duong.get('Protein', 0.0), 
            dinh_duong.get('ChatBeo', 0.0), 
            dinh_duong.get('Carbohydrate', 0.0), 
            dinh_duong.get('Vitamin', '')
        ))
        
        cong_thuc = data.get('CongThuc', {})
        # 3. Insert CongThuc
        cursor.execute("""
            INSERT INTO CongThuc (MaMonAn, HuongDan, ThoiGianNau, KhauPhan)
            VALUES (?, ?, ?, ?)
        """, (
            ma_mon_an,
            cong_thuc.get('HuongDan', ''),
            cong_thuc.get('ThoiGianNau', 0),
            cong_thuc.get('KhauPhan', 1)
        ))
        ma_cong_thuc = cursor.lastrowid
        
        # 4. Insert NguyenLieu and ChiTietNguyenLieu
        nguyen_lieu_list = cong_thuc.get('NguyenLieu', [])
        for nl in nguyen_lieu_list:
            ten_nl = nl.get('TenNguyenLieu', '')
            so_luong = str(nl.get('SoLuong', ''))
            
            if not ten_nl:
                continue
                
            cursor.execute("SELECT MaNguyenLieu FROM NguyenLieu WHERE TenNguyenLieu = ?", (ten_nl,))
            row = cursor.fetchone()
            if row:
                ma_nl = row['MaNguyenLieu']
            else:
                cursor.execute("INSERT INTO NguyenLieu (TenNguyenLieu) VALUES (?)", (ten_nl,))
                ma_nl = cursor.lastrowid
                
            cursor.execute("INSERT INTO ChiTietNguyenLieu (MaCongThuc, MaNguyenLieu, SoLuong) VALUES (?, ?, ?)", (ma_cong_thuc, ma_nl, so_luong))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Database Insert Error] {e}")
        return False

# --- ADMIN API FUNCTIONS ---

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MaNguoiDung, TenNguoiDung, Email, NgayDangKy, VaiTro FROM NguoiDung ORDER BY MaNguoiDung DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM NguoiDung WHERE MaNguoiDung = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[Delete User Error] {e}")
        return False
    finally:
        conn.close()

def get_system_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {
        'total_users': cursor.execute("SELECT COUNT(*) FROM NguoiDung").fetchone()[0],
        'total_foods': cursor.execute("SELECT COUNT(*) FROM MonAn WHERE IsDeleted = 0").fetchone()[0],
        'total_recognitions': cursor.execute("SELECT COUNT(*) FROM LichSuNhanDien").fetchone()[0]
    }
    conn.close()
    return stats

def get_all_history_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.MaLichSu, l.HinhAnh, l.KetQuaNhanDien, l.DoChinhXac, l.ThoiGianNhanDien, 
               n.TenNguoiDung, n.Email
        FROM LichSuNhanDien l
        LEFT JOIN NguoiDung n ON l.MaNguoiDung = n.MaNguoiDung
        ORDER BY l.ThoiGianNhanDien DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_foods_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MaMonAn, TenMonAn, MoTa, PhanLoai, NgayTao, IsDeleted
        FROM MonAn 
        ORDER BY MaMonAn DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_food_detail_admin(food_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM MonAn WHERE MaMonAn = ?", (food_id,))
    mon_an = cursor.fetchone()
    if not mon_an: return None
    
    result = dict(mon_an)
    
    cursor.execute("SELECT * FROM DinhDuong WHERE MaMonAn = ?", (food_id,))
    dinh_duong = cursor.fetchone()
    result['DinhDuong'] = dict(dinh_duong) if dinh_duong else None
    
    cursor.execute("SELECT * FROM CongThuc WHERE MaMonAn = ?", (food_id,))
    cong_thuc = cursor.fetchone()
    if cong_thuc:
        ct_dict = dict(cong_thuc)
        cursor.execute("""
            SELECT nl.MaNguyenLieu, nl.TenNguyenLieu, ctnl.SoLuong 
            FROM ChiTietNguyenLieu ctnl
            JOIN NguyenLieu nl ON ctnl.MaNguyenLieu = nl.MaNguyenLieu
            WHERE ctnl.MaCongThuc = ?
        """, (ct_dict['MaCongThuc'],))
        ct_dict['NguyenLieu'] = [dict(r) for r in cursor.fetchall()]
        result['CongThuc'] = ct_dict
    else:
        result['CongThuc'] = None
        
    conn.close()
    return result

def insert_food_full(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
             INSERT INTO MonAn (TenMonAn, MoTa, PhanLoai, NgayTao, IsDeleted)
             VALUES (?, ?, ?, date('now'), 0)
        """, (data.get('TenMonAn'), data.get('MoTa'), data.get('PhanLoai')))
        food_id = cursor.lastrowid
        
        dinh_duong = data.get('DinhDuong', {})
        cursor.execute("""
            INSERT INTO DinhDuong (MaMonAn, Calo, Protein, ChatBeo, Carbohydrate, Vitamin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (food_id, dinh_duong.get('Calo'), dinh_duong.get('Protein'), dinh_duong.get('ChatBeo'), dinh_duong.get('Carbohydrate'), dinh_duong.get('Vitamin')))
        
        cong_thuc = data.get('CongThuc', {})
        cursor.execute("""
            INSERT INTO CongThuc (MaMonAn, HuongDan, ThoiGianNau, KhauPhan)
            VALUES (?, ?, ?, ?)
        """, (food_id, cong_thuc.get('HuongDan'), cong_thuc.get('ThoiGianNau'), cong_thuc.get('KhauPhan')))
        ct_id = cursor.lastrowid
        
        for nl in cong_thuc.get('NguyenLieu', []):
            ten_nl = nl.get('TenNguyenLieu')
            if not ten_nl: continue
            cursor.execute("SELECT MaNguyenLieu FROM NguyenLieu WHERE TenNguyenLieu = ?", (ten_nl,))
            row = cursor.fetchone()
            if row:
                ma_nl = row['MaNguyenLieu']
            else:
                cursor.execute("INSERT INTO NguyenLieu (TenNguyenLieu) VALUES (?)", (ten_nl,))
                ma_nl = cursor.lastrowid
            cursor.execute("INSERT INTO ChiTietNguyenLieu (MaCongThuc, MaNguyenLieu, SoLuong) VALUES (?, ?, ?)", (ct_id, ma_nl, nl.get('SoLuong')))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error insert_food_full: {e}")
        return False
    finally:
        conn.close()

def update_food_full(food_id, data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
             UPDATE MonAn SET TenMonAn=?, MoTa=?, PhanLoai=?, IsDeleted=?
             WHERE MaMonAn=?
        """, (data.get('TenMonAn'), data.get('MoTa'), data.get('PhanLoai'), data.get('IsDeleted', 0), food_id))
        
        dinh_duong = data.get('DinhDuong', {})
        cursor.execute("SELECT MaDinhDuong FROM DinhDuong WHERE MaMonAn=?", (food_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE DinhDuong SET Calo=?, Protein=?, ChatBeo=?, Carbohydrate=?, Vitamin=?
                WHERE MaMonAn=?
            """, (dinh_duong.get('Calo'), dinh_duong.get('Protein'), dinh_duong.get('ChatBeo'), dinh_duong.get('Carbohydrate'), dinh_duong.get('Vitamin'), food_id))
        else:
            cursor.execute("""
                INSERT INTO DinhDuong (MaMonAn, Calo, Protein, ChatBeo, Carbohydrate, Vitamin)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (food_id, dinh_duong.get('Calo'), dinh_duong.get('Protein'), dinh_duong.get('ChatBeo'), dinh_duong.get('Carbohydrate'), dinh_duong.get('Vitamin')))
            
        cong_thuc = data.get('CongThuc', {})
        cursor.execute("SELECT MaCongThuc FROM CongThuc WHERE MaMonAn=?", (food_id,))
        ct_row = cursor.fetchone()
        if ct_row:
            ct_id = ct_row['MaCongThuc']
            cursor.execute("""
                UPDATE CongThuc SET HuongDan=?, ThoiGianNau=?, KhauPhan=? WHERE MaCongThuc=?
            """, (cong_thuc.get('HuongDan'), cong_thuc.get('ThoiGianNau'), cong_thuc.get('KhauPhan'), ct_id))
            cursor.execute("DELETE FROM ChiTietNguyenLieu WHERE MaCongThuc=?", (ct_id,))
        else:
            cursor.execute("""
                INSERT INTO CongThuc (MaMonAn, HuongDan, ThoiGianNau, KhauPhan)
                VALUES (?, ?, ?, ?)
            """, (food_id, cong_thuc.get('HuongDan'), cong_thuc.get('ThoiGianNau'), cong_thuc.get('KhauPhan')))
            ct_id = cursor.lastrowid
            
        for nl in cong_thuc.get('NguyenLieu', []):
            ten_nl = nl.get('TenNguyenLieu')
            if not ten_nl: continue
            cursor.execute("SELECT MaNguyenLieu FROM NguyenLieu WHERE TenNguyenLieu = ?", (ten_nl,))
            row = cursor.fetchone()
            if row: ma_nl = row['MaNguyenLieu']
            else:
                cursor.execute("INSERT INTO NguyenLieu (TenNguyenLieu) VALUES (?)", (ten_nl,))
                ma_nl = cursor.lastrowid
            cursor.execute("INSERT INTO ChiTietNguyenLieu (MaCongThuc, MaNguyenLieu, SoLuong) VALUES (?, ?, ?)", (ct_id, ma_nl, nl.get('SoLuong')))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error update_food_full: {e}")
        return False
    finally:
        conn.close()

def delete_food_soft(food_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE MonAn SET IsDeleted = 1 WHERE MaMonAn = ?", (food_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error delete_food_soft: {e}")
        return False
    finally:
        conn.close()

def restore_food_soft(food_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE MonAn SET IsDeleted = 0 WHERE MaMonAn = ?", (food_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error restore_food_soft: {e}")
        return False
    finally:
        conn.close()
