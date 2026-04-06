import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'food_recognition.db')

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Xoá data cũ để reset (nếu chạy nhiều lần)
    cursor.execute("DELETE FROM ChiTietNguyenLieu")
    cursor.execute("DELETE FROM CongThuc")
    cursor.execute("DELETE FROM DinhDuong")
    cursor.execute("DELETE FROM NguyenLieu")
    cursor.execute("DELETE FROM MonAn")

    # ----- THÊM MÓN: PHỞ BÒ -----
    # 1. Món ăn
    cursor.execute("""
        INSERT INTO MonAn (TenMonAn, MoTa, PhanLoai, NgayTao) 
        VALUES ('Pho', 'Phở bò truyền thống Việt Nam với nước cốt hầm xương đậm đà, thịt bò mềm và bánh phở dai.', 'Món nước', datetime('now'))
    """)
    ma_pho = cursor.lastrowid

    # 2. Dinh Dưỡng
    cursor.execute("""
        INSERT INTO DinhDuong (MaMonAn, Calo, Protein, ChatBeo, Carbohydrate, Vitamin) 
        VALUES (?, 450, 25.5, 12.0, 58.0, 'Vitamin B12, Kẽm')
    """, (ma_pho,))

    # 3. Công Thức
    cursor.execute("""
        INSERT INTO CongThuc (MaMonAn, HuongDan, ThoiGianNau, KhauPhan) 
        VALUES (?, '1. Hầm xương bò với hoa hồi, thảo quả, quế trong 6 giờ.\n2. Thái mỏng thịt bò.\n3. Trụng phở qua nước sôi.\n4. Xếp phở ra bát, đặt thịt bò, hành lá lên trên và chan nước dùng nóng hổi.', 360, 1)
    """, (ma_pho,))
    ma_ct_pho = cursor.lastrowid

    # 4. Nguyên Liệu
    nguyen_lieu_pho = [('Xương ống bò',), ('Thịt bò thăn',), ('Bánh phở',), ('Hành ngò, rau thơm',), ('Hoa hồi, quế, thảo quả',)]
    cursor.executemany("INSERT INTO NguyenLieu (TenNguyenLieu) VALUES (?)", nguyen_lieu_pho)
    # Lấy IDs
    nl_ids = [cursor.execute("SELECT MaNguyenLieu FROM NguyenLieu WHERE TenNguyenLieu=?", (n[0],)).fetchone()[0] for n in nguyen_lieu_pho]

    # 5. Chi Tiết Nguyên Liệu
    ctnl_pho = [
        (ma_ct_pho, nl_ids[0], '1 kg'),
        (ma_ct_pho, nl_ids[1], '200g'),
        (ma_ct_pho, nl_ids[2], '150g'),
        (ma_ct_pho, nl_ids[3], '1 mớ'),
        (ma_ct_pho, nl_ids[4], '1 gói')
    ]
    cursor.executemany("INSERT INTO ChiTietNguyenLieu (MaCongThuc, MaNguyenLieu, SoLuong) VALUES (?, ?, ?)", ctnl_pho)

    # ----- THÊM MÓN: BÁNH MÌ -----
    cursor.execute("""
        INSERT INTO MonAn (TenMonAn, MoTa, PhanLoai, NgayTao) 
        VALUES ('Banh mi', 'Bánh mì Việt Nam giòn rụm với nhân pate, thịt nướng, chả lụa và rau củ muối chua.', 'Bánh', datetime('now'))
    """)
    ma_bm = cursor.lastrowid

    cursor.execute("""
        INSERT INTO DinhDuong (MaMonAn, Calo, Protein, ChatBeo, Carbohydrate, Vitamin) 
        VALUES (?, 350, 15.0, 10.0, 48.0, 'Vitamin A, Sắt')
    """, (ma_bm,))

    cursor.execute("""
        INSERT INTO CongThuc (MaMonAn, HuongDan, ThoiGianNau, KhauPhan) 
        VALUES (?, '1. Nướng nóng vỏ bánh mì.\n2. Phết bơ và pate vào bên trong.\n3. Xếp lần lượt chả lụa, thịt nướng.\n4. Thêm đồ chua, dưa leo, ngò rí và xịt nước tương hoặc tương ớt.', 10, 1)
    """, (ma_bm,))
    ma_ct_bm = cursor.lastrowid

    nguyen_lieu_bm = [('Bánh mì không',), ('Pate gan',), ('Thịt nướng/Chả lụa',), ('Đồ chua (Cà rốt, củ cải)',), ('Dưa leo, ngò rí',)]
    cursor.executemany("INSERT INTO NguyenLieu (TenNguyenLieu) VALUES (?)", nguyen_lieu_bm)
    nl_ids_bm = [cursor.execute("SELECT MaNguyenLieu FROM NguyenLieu WHERE TenNguyenLieu=?", (n[0],)).fetchone()[0] for n in nguyen_lieu_bm]
    
    ctnl_bm = [
        (ma_ct_bm, nl_ids_bm[0], '1 ổ'),
        (ma_ct_bm, nl_ids_bm[1], '20g'),
        (ma_ct_bm, nl_ids_bm[2], '50g'),
        (ma_ct_bm, nl_ids_bm[3], '30g'),
        (ma_ct_bm, nl_ids_bm[4], 'Vừa đủ')
    ]
    cursor.executemany("INSERT INTO ChiTietNguyenLieu (MaCongThuc, MaNguyenLieu, SoLuong) VALUES (?, ?, ?)", ctnl_bm)


    # ----- THÊM MÓN: BÚN CHẢ -----
    cursor.execute("""
        INSERT INTO MonAn (TenMonAn, MoTa, PhanLoai, NgayTao) 
        VALUES ('Bun cha', 'Bún chả Hà Nội - sự hòa quyện tuyệt vời giữa thịt lợn nướng xém cạnh, chả băm nhuyễn và nước mắm chua ngọt.', 'Món nước trộn', datetime('now'))
    """)
    ma_bc = cursor.lastrowid

    cursor.execute("""
        INSERT INTO DinhDuong (MaMonAn, Calo, Protein, ChatBeo, Carbohydrate, Vitamin) 
        VALUES (?, 520, 28.0, 18.0, 65.0, 'Canxi, Kali')
    """, (ma_bc,))

    cursor.execute("""
        INSERT INTO CongThuc (MaMonAn, HuongDan, ThoiGianNau, KhauPhan) 
        VALUES (?, '1. Ướp thịt heo thái lát và thịt băm với hành tỏi, mắm, đường.\n2. Nướng thịt và chả trên than hoa.\n3. Pha nước mắm chua ngọt với đu đủ xanh, cà rốt.\n4. Trình bày bún, rau sống, và thịt nướng chan nước mắm.', 45, 1)
    """, (ma_bc,))
    ma_ct_bc = cursor.lastrowid

    nguyen_lieu_bc = [('Thịt ba chỉ',), ('Thịt nạc vai băm',), ('Bún tươi',), ('Nước mắm pha chua ngọt',), ('Rau thơm (tía tô, xà lách)',)]
    cursor.executemany("INSERT INTO NguyenLieu (TenNguyenLieu) VALUES (?)", nguyen_lieu_bc)
    nl_ids_bc = [cursor.execute("SELECT MaNguyenLieu FROM NguyenLieu WHERE TenNguyenLieu=?", (n[0],)).fetchone()[0] for n in nguyen_lieu_bc]
    
    ctnl_bc = [
        (ma_ct_bc, nl_ids_bc[0], '100g'),
        (ma_ct_bc, nl_ids_bc[1], '100g'),
        (ma_ct_bc, nl_ids_bc[2], '200g'),
        (ma_ct_bc, nl_ids_bc[3], '1 chén nhỏ'),
        (ma_ct_bc, nl_ids_bc[4], '1 mớ')
    ]
    cursor.executemany("INSERT INTO ChiTietNguyenLieu (MaCongThuc, MaNguyenLieu, SoLuong) VALUES (?, ?, ?)", ctnl_bc)

    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
