import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'food_recognition.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_mapped_food_name(food_name: str) -> str:
    """Ánh xạ tên/nhãn tiếng Anh thường gặp từ API về tên món ăn trong Database"""
    food_lower = food_name.lower().strip()
    alias_map = {
        # Tập Alias cho Phở
        'chowder': 'Pho',
        'noodle soup': 'Pho',
        'noodle': 'Pho',
        'pho': 'Pho',
        'beef soup': 'Pho',
        'soup': 'Pho',
        'broth': 'Pho',
        
        # Tập Alias cho Bánh Mì
        'sandwich': 'Banh mi',
        'baguette': 'Banh mi',
        'banh mi': 'Banh mi',
        'bread': 'Banh mi',
        'burger': 'Banh mi',
        'burrito': 'Banh mi',
        'wrap': 'Banh mi',
        
        # Tập Alias cho Bún Chả
        'bun cha': 'Bun cha',
        'pork meatball': 'Bun cha',
        'grilled pork': 'Bun cha',
        'meatball': 'Bun cha',
        'noodles with pork': 'Bun cha',
        
        # Tập Alias cho Bún bò Huế
        'bun bo hue': 'Bún bò Huế',
        'bun bo': 'Bún bò Huế',
        'beef stew': 'Bún bò Huế',
        'beef_stew': 'Bún bò Huế',
        'spicy beef noodle': 'Bún bò Huế',
        'beef noodle': 'Bún bò Huế'
    }
    return alias_map.get(food_lower, food_name)

def search_food_by_name(food_name: str):
    """
    Search for a food item by name or English translation in the database.
    Since Google Cloud Vision might return English labels (e.g., 'Pho', 'Banh mi', 'Noodle'),
    we will use a LIKE query.
    """
    mapped_name = get_mapped_food_name(food_name)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Look for MonAn (Tìm theo tên đã map HOẶC tên gốc)
    # Thêm MoTa LIKE ? để quét các món do AI sinh ra (AI sẽ nhúng tên tiếng Anh vào MoTa)
    cursor.execute("""
        SELECT * FROM MonAn 
        WHERE TenMonAn LIKE ? OR PhanLoai LIKE ? OR TenMonAn LIKE ? OR MoTa LIKE ?
    """, (f'%{mapped_name}%', f'%{mapped_name}%', f'%{food_name}%', f'%{food_name}%'))
    
    mon_an = cursor.fetchone()
    
    if not mon_an:
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
        conn.commit()
        return True, "Đăng ký thành công"
    except sqlite3.IntegrityError:
        return False, "Email đã được sử dụng"
    except Exception as e:
        return False, str(e)
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
