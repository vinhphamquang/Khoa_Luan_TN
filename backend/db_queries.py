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
        
        # Tập Alias cho Bún Chả
        'bun cha': 'Bun cha',
        'pork meatball': 'Bun cha',
        'grilled pork': 'Bun cha',
        'meatball': 'Bun cha',
        'noodles with pork': 'Bun cha'
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
    cursor.execute("""
        SELECT * FROM MonAn 
        WHERE TenMonAn LIKE ? OR PhanLoai LIKE ? OR TenMonAn LIKE ?
    """, (f'%{mapped_name}%', f'%{mapped_name}%', f'%{food_name}%'))
    
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
