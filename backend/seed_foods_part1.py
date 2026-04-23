"""Seed 25 Vietnamese dishes - Part 1"""
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()

def add(cur, name, desc, cat, cal, pro, fat, carb, vit, time, serv, guide, ingr):
    cur.execute("SELECT 1 FROM MonAn WHERE LOWER(TenMonAn)=LOWER(%s)", (name,))
    if cur.fetchone():
        print(f"SKIP: {name}"); return
    cur.execute("INSERT INTO MonAn(TenMonAn,MoTa,PhanLoai) VALUES(%s,%s,%s) RETURNING MaMonAn", (name,desc,cat))
    mid = cur.fetchone()[0]
    cur.execute("INSERT INTO DinhDuong(MaMonAn,Calo,Protein,ChatBeo,Carbohydrate,Vitamin) VALUES(%s,%s,%s,%s,%s,%s)", (mid,cal,pro,fat,carb,vit))
    cur.execute("INSERT INTO CongThuc(MaMonAn,HuongDan,ThoiGianNau,KhauPhan) VALUES(%s,%s,%s,%s) RETURNING MaCongThuc", (mid,guide,time,serv))
    cid = cur.fetchone()[0]
    for ing_name, qty in ingr:
        cur.execute("INSERT INTO NguyenLieu(TenNguyenLieu) VALUES(%s) ON CONFLICT DO NOTHING RETURNING MaNguyenLieu", (ing_name,))
        r = cur.fetchone()
        if r: nid = r[0]
        else:
            cur.execute("SELECT MaNguyenLieu FROM NguyenLieu WHERE TenNguyenLieu=%s", (ing_name,))
            nid = cur.fetchone()[0]
        cur.execute("INSERT INTO ChiTietNguyenLieu(MaCongThuc,MaNguyenLieu,SoLuong) VALUES(%s,%s,%s)", (cid,nid,qty))
    print(f"OK: {name}")

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# 1
add(cur,"Phở Gà","Phở với thịt gà","Món nước",350,28,8,42,"B1,B6",60,2,
    "Ninh xương gà lấy nước dùng. Trụng bánh phở, xếp thịt gà xé, chan nước dùng, thêm hành, rau thơm.",
    [("Bánh phở","400g"),("Thịt gà","300g"),("Hành tây","1 củ"),("Gừng","1 nhánh"),("Rau thơm","50g")])
# 2
add(cur,"Bún Mắm","Bún mắm miền Tây","Món nước",420,30,15,45,"A,B12",50,2,
    "Nấu nước mắm cá linh, thêm mắm ruốc. Cho tôm, mực, thịt heo quay. Ăn với bún, rau sống.",
    [("Bún","400g"),("Tôm","200g"),("Mực","150g"),("Thịt heo quay","200g"),("Mắm cá","50ml")])
# 3
add(cur,"Cháo Lòng","Cháo nấu với lòng heo","Món cháo",380,22,16,38,"B12,Fe",45,2,
    "Nấu cháo gạo nhuyễn. Luộc lòng heo, cắt miếng. Chan cháo, thêm lòng, hành phi, tiêu.",
    [("Gạo","200g"),("Lòng heo","300g"),("Hành phi","30g"),("Tiêu","5g"),("Rau mùi","20g")])
# 4
add(cur,"Bánh Canh Cua","Bánh canh với cua","Món nước",390,25,12,48,"B12,Ca",40,2,
    "Nấu nước dùng từ xương. Gỡ thịt cua, xào sơ. Cho bánh canh vào nước dùng, thêm cua, hành.",
    [("Bánh canh","400g"),("Cua","300g"),("Hành lá","30g"),("Tiêu","5g"),("Nước dùng","1L")])
# 5
add(cur,"Gà Nướng Mật Ong","Gà nướng tẩm mật ong","Món nướng",450,38,22,18,"B6,B12",60,4,
    "Ướp gà với mật ong, tỏi, nước mắm 2 tiếng. Nướng ở 200°C trong 45 phút, phết thêm mật ong.",
    [("Đùi gà","800g"),("Mật ong","60ml"),("Tỏi","4 tép"),("Nước mắm","30ml"),("Tiêu","5g")])
# 6
add(cur,"Canh Bí Đao Tôm","Canh bí đao nấu tôm","Món canh",120,12,3,14,"C,K",25,4,
    "Tôm bóc vỏ, xào sơ. Bí đao gọt vỏ, cắt miếng. Nấu nước dùng, cho bí và tôm vào, nêm nếm.",
    [("Bí đao","400g"),("Tôm","200g"),("Hành lá","20g"),("Nước mắm","15ml")])
# 7
add(cur,"Thịt Kho Tàu","Thịt heo kho với trứng","Món kho",520,35,32,15,"B1,B12",90,4,
    "Rim đường thắng caramel. Cho thịt ba chỉ vào kho với nước dừa, nước mắm. Thêm trứng luộc, kho nhỏ lửa.",
    [("Thịt ba chỉ","500g"),("Trứng vịt","4 quả"),("Nước dừa","400ml"),("Nước mắm","40ml"),("Đường","30g")])
# 8
add(cur,"Gỏi Đu Đủ","Gỏi đu đủ xanh kiểu Việt","Món gỏi",150,8,5,22,"A,C",20,2,
    "Bào đu đủ xanh thành sợi, ngâm nước đá. Trộn nước mắm chua ngọt, thêm tôm khô, rau răm, đậu phộng.",
    [("Đu đủ xanh","300g"),("Tôm khô","50g"),("Đậu phộng","40g"),("Rau răm","20g"),("Nước mắm","30ml")])
# 9
add(cur,"Lẩu Thái","Lẩu chua cay kiểu Thái","Món lẩu",380,28,14,35,"C,B6",40,4,
    "Nấu nước dùng với sả, galangal, lá chanh. Thêm nước cốt me, sa tế. Nhúng hải sản, rau, nấm.",
    [("Tôm sú","300g"),("Mực","200g"),("Nấm","200g"),("Sả","3 cây"),("Ớt","5 quả")])
# 10
add(cur,"Cơm Chiên Dương Châu","Cơm chiên với tôm, lạp xưởng","Món cơm",480,18,16,62,"B1,B6",20,2,
    "Xào tôm, lạp xưởng, đậu Hà Lan, cà rốt. Cho cơm nguội vào đảo đều, thêm trứng, nêm nước mắm.",
    [("Cơm nguội","400g"),("Tôm","150g"),("Lạp xưởng","100g"),("Trứng","2 quả"),("Đậu Hà Lan","50g")])
# 11
add(cur,"Nem Nướng Nha Trang","Nem nướng đặc sản Nha Trang","Món nướng",380,25,18,30,"B1,B12",35,4,
    "Xay thịt heo với gia vị, tỏi, đường. Nặn viên, xiên que, nướng trên than hoa. Ăn kèm bánh tráng, rau sống.",
    [("Thịt heo nạc","500g"),("Tỏi","6 tép"),("Đường","20g"),("Bánh tráng","10 cái"),("Rau sống","200g")])
# 12
add(cur,"Bánh Bèo","Bánh bèo Huế","Món bánh",280,10,8,42,"B1",30,4,
    "Pha bột gạo với nước, hấp trong chén nhỏ. Làm nhân tôm chấy, mỡ hành. Rưới lên bánh, ăn kèm nước mắm.",
    [("Bột gạo","300g"),("Tôm khô","100g"),("Mỡ hành","50ml"),("Nước mắm","30ml")])
# 13
add(cur,"Bò Né","Bò né bít tết Sài Gòn","Món chiên",520,35,30,28,"B12,Fe",15,1,
    "Áp chảo bò trên khuôn gang nóng. Thêm trứng ốp la, pate, đồ chua. Ăn với bánh mì.",
    [("Thịt bò","200g"),("Trứng","2 quả"),("Pate","50g"),("Bánh mì","1 ổ"),("Bơ","20g")])
# 14
add(cur,"Chả Cá Lã Vọng","Chả cá Hà Nội","Món cá",360,30,18,15,"D,B12",40,2,
    "Ướp cá lăng với nghệ, mẻ, riềng. Chiên sơ, rồi cho lên chảo dầu với thì là, hành lá. Ăn kèm bún, mắm tôm.",
    [("Cá lăng","500g"),("Nghệ","20g"),("Thì là","100g"),("Hành lá","100g"),("Mắm tôm","30ml")])
# 15
add(cur,"Hủ Tiếu Mỹ Tho","Hủ tiếu đặc sản Mỹ Tho","Món nước",370,22,10,50,"B1,B6",35,2,
    "Ninh xương heo lấy nước dùng trong. Trụng hủ tiếu, xếp thịt, tôm, gan. Chan nước dùng, thêm hành phi.",
    [("Hủ tiếu","300g"),("Thịt heo","200g"),("Tôm","100g"),("Gan heo","50g"),("Hành phi","20g")])
# 16
add(cur,"Gà Kho Gừng","Gà kho với gừng","Món kho",380,32,18,12,"B6,B12",40,4,
    "Chặt gà miếng, ướp nước mắm, đường. Phi gừng thơm, cho gà vào đảo, thêm nước, kho đến khi sệt.",
    [("Thịt gà","500g"),("Gừng","50g"),("Nước mắm","40ml"),("Đường","20g"),("Tiêu","5g")])
# 17
add(cur,"Bún Mọc","Bún mọc Hà Nội","Món nước",340,24,10,42,"B1,Fe",35,2,
    "Nấu nước dùng từ xương heo. Làm mọc từ giò sống. Cho mọc vào nước dùng, ăn với bún, rau sống.",
    [("Bún","300g"),("Giò sống","200g"),("Nấm mèo","30g"),("Hành lá","20g"),("Nước dùng","1L")])
# 18
add(cur,"Bánh Tráng Trộn","Bánh tráng trộn Sài Gòn","Món ăn vặt",250,8,10,35,"C",10,1,
    "Cắt bánh tráng nhỏ, trộn với trứng cút, khô bò, tôm khô, xoài xanh, rau răm, sa tế.",
    [("Bánh tráng","100g"),("Trứng cút","5 quả"),("Khô bò","30g"),("Xoài xanh","50g"),("Sa tế","10g")])
# 19
add(cur,"Lẩu Mắm","Lẩu mắm miền Tây","Món lẩu",400,30,15,38,"B12,D",45,4,
    "Nấu nước mắm cá linh/cá sặc với sả. Cho thịt heo quay, cá, tôm, mực. Nhúng rau đồng, bông súng.",
    [("Mắm cá","100ml"),("Cá lóc","300g"),("Tôm","200g"),("Thịt heo quay","200g"),("Rau đồng","500g")])
# 20
add(cur,"Xôi Gà","Xôi nếp với gà xé","Món xôi",450,28,16,52,"B1,B6",60,2,
    "Ngâm nếp, hấp chín. Luộc gà, xé nhỏ. Xếp xôi, gà, rưới mỡ hành, hành phi.",
    [("Nếp","400g"),("Thịt gà","300g"),("Mỡ hành","40ml"),("Hành phi","30g")])
# 21
add(cur,"Sườn Xào Chua Ngọt","Sườn heo xào sốt chua ngọt","Món xào",480,28,24,40,"B1,C",35,4,
    "Chiên sườn giòn. Làm sốt từ cà chua, dấm, đường. Xào sườn với sốt, thêm hành tây, ớt chuông.",
    [("Sườn heo","500g"),("Cà chua","200g"),("Dấm","30ml"),("Đường","30g"),("Ớt chuông","1 quả")])
# 22
add(cur,"Cá Chiên Xù","Cá phi lê chiên giòn","Món chiên",380,28,18,28,"D,B12",25,2,
    "Cá phi lê ướp gia vị, lăn bột chiên xù, chiên vàng giòn. Ăn kèm tương ớt, rau sống.",
    [("Cá basa","400g"),("Bột chiên xù","100g"),("Trứng","2 quả"),("Bột mì","50g")])
# 23
add(cur,"Rau Muống Xào Tỏi","Rau muống xào với tỏi","Món xào",80,4,3,10,"A,C,K",10,2,
    "Phi tỏi thơm, cho rau muống vào xào lửa lớn, nêm nước mắm, đường. Đảo nhanh tay.",
    [("Rau muống","300g"),("Tỏi","4 tép"),("Nước mắm","15ml"),("Đường","5g")])
# 24
add(cur,"Bún Ốc","Bún ốc Hà Nội","Món nước",320,18,8,45,"B12,Fe",35,2,
    "Nấu nước dùng cà chua chua ngọt. Luộc ốc, khêu thịt. Chan nước dùng lên bún, thêm ốc, rau kinh giới.",
    [("Bún","300g"),("Ốc","500g"),("Cà chua","200g"),("Rau kinh giới","50g"),("Ớt","3 quả")])
# 25
add(cur,"Bánh Bao","Bánh bao nhân thịt trứng","Món hấp",320,15,12,40,"B1,B6",40,4,
    "Nhào bột, ủ nở. Làm nhân thịt heo, trứng cút, nấm. Gói nhân, hấp 15 phút.",
    [("Bột mì","300g"),("Thịt heo","200g"),("Trứng cút","4 quả"),("Nấm mèo","20g"),("Men nở","5g")])

conn.commit()
cur.close()
conn.close()
print("\n=== Part 1: Done! 25 dishes added ===")
