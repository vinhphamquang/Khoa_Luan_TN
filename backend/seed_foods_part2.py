"""Seed 25 Vietnamese dishes - Part 2"""
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

# 26
add(cur,"Cơm Gà Hội An","Cơm gà đặc sản Hội An","Món cơm",420,30,12,52,"B6,B12",45,2,
    "Nấu cơm với nước luộc gà, nghệ. Gà xé sợi trộn hành tây, rau răm. Ăn kèm canh, đồ chua.",
    [("Gạo","300g"),("Thịt gà","300g"),("Hành tây","1 củ"),("Rau răm","30g"),("Nghệ","10g")])
# 27
add(cur,"Bò Lá Lốt","Bò cuốn lá lốt nướng","Món nướng",350,28,20,10,"B12,Fe",30,4,
    "Băm thịt bò trộn gia vị, sả. Cuốn trong lá lốt, nướng trên than hoa. Ăn kèm bún, rau sống.",
    [("Thịt bò","400g"),("Lá lốt","40 lá"),("Sả","2 cây"),("Đậu phộng","40g"),("Bún","200g")])
# 28
add(cur,"Canh Khổ Qua Nhồi Thịt","Canh khổ qua nhồi thịt heo","Món canh",180,16,6,18,"C,K",35,4,
    "Khoét ruột khổ qua. Nhồi thịt heo xay trộn mộc nhĩ, miến. Nấu canh đến khi khổ qua chín mềm.",
    [("Khổ qua","400g"),("Thịt heo xay","200g"),("Mộc nhĩ","20g"),("Miến","30g"),("Hành lá","20g")])
# 29
add(cur,"Bánh Đúc","Bánh đúc lạc chấm tương","Món bánh",220,8,6,36,"B1",30,4,
    "Nấu bột gạo với nước vôi trong đến đặc. Thêm lạc rang. Đổ ra khuôn, để nguội, cắt miếng. Ăn kèm tương bần.",
    [("Bột gạo","300g"),("Lạc","80g"),("Nước vôi trong","20ml"),("Tương bần","50ml")])
# 30
add(cur,"Cá Lóc Nướng Trui","Cá lóc nướng rơm miền Tây","Món nướng",280,35,12,5,"D,B12",30,2,
    "Xiên cá lóc nguyên con, nướng trên rơm hoặc than. Gỡ thịt, cuốn bánh tráng với rau sống, chấm mắm nêm.",
    [("Cá lóc","600g"),("Bánh tráng","10 cái"),("Rau sống","200g"),("Mắm nêm","50ml")])
# 31
add(cur,"Bún Cá Châu Đốc","Bún cá đặc sản An Giang","Món nước",360,25,10,45,"D,B6",40,2,
    "Nấu nước dùng từ cá lóc, mắm ruốc. Phi nghệ cho màu. Ăn bún với cá, rau, bông súng.",
    [("Bún","300g"),("Cá lóc","300g"),("Nghệ","15g"),("Mắm ruốc","30ml"),("Bông súng","100g")])
# 32
add(cur,"Đậu Hũ Sốt Cà Chua","Đậu hũ chiên sốt cà chua","Món chay",200,14,10,18,"C,Ca",20,2,
    "Chiên đậu hũ vàng. Xào cà chua nhuyễn, nêm gia vị. Cho đậu hũ vào sốt, rim nhẹ. Rắc hành lá.",
    [("Đậu hũ","400g"),("Cà chua","200g"),("Hành lá","20g"),("Nước mắm","15ml")])
# 33
add(cur,"Gà Hấp Muối","Gà hấp muối thơm","Món hấp",380,35,20,5,"B6,B12",50,4,
    "Xát muối và gia vị lên gà. Hấp trong nồi có lót giấy bạc, muối rang, sả, gừng. Hấp 40 phút.",
    [("Gà nguyên con","1.2kg"),("Muối hạt","500g"),("Sả","4 cây"),("Gừng","30g")])
# 34
add(cur,"Bún Bò Xào","Bún trộn bò xào sả ớt","Món trộn",400,28,14,45,"B12,C",20,2,
    "Xào bò với sả ớt, nước mắm. Trụng bún, xếp rau sống, bò xào lên trên, rưới nước mắm chua ngọt.",
    [("Bún","300g"),("Thịt bò","250g"),("Sả","2 cây"),("Ớt","3 quả"),("Rau sống","150g")])
# 35
add(cur,"Bánh Ít Lá Gai","Bánh ít lá gai Bình Định","Món bánh",260,6,4,52,"B1,Fe",60,6,
    "Nấu lá gai, xay nhuyễn trộn bột nếp. Nhân đậu xanh hoặc dừa. Gói lá chuối, hấp chín.",
    [("Bột nếp","300g"),("Lá gai","100g"),("Đậu xanh","150g"),("Đường","80g"),("Lá chuối","10 lá")])
# 36
add(cur,"Cá Bống Kho Tiêu","Cá bống kho tiêu miền Tây","Món kho",300,28,14,12,"D,B12",30,2,
    "Ướp cá bống với nước mắm, đường, tiêu. Kho nhỏ lửa trong nồi đất đến khi cạn nước, thơm tiêu.",
    [("Cá bống","400g"),("Tiêu xay","10g"),("Nước mắm","40ml"),("Đường","15g"),("Hành tím","3 củ")])
# 37
add(cur,"Mì Hoành Thánh","Mì hoành thánh kiểu Hoa","Món nước",380,22,10,48,"B1,Fe",30,2,
    "Gói nhân tôm thịt trong vỏ hoành thánh. Nấu nước dùng xương. Trụng mì, cho hoành thánh, chan nước dùng.",
    [("Mì trứng","200g"),("Tôm","150g"),("Thịt heo xay","100g"),("Vỏ hoành thánh","20 cái"),("Cải ngọt","100g")])
# 38
add(cur,"Chè Bưởi","Chè bưởi cốt dừa","Món chè",220,3,8,36,"C",35,4,
    "Tách cùi bưởi, ngâm nước vôi, rửa sạch. Nấu đường, thêm cùi bưởi, bột báng. Rưới nước cốt dừa.",
    [("Cùi bưởi","200g"),("Đường","100g"),("Bột báng","50g"),("Nước cốt dừa","200ml")])
# 39
add(cur,"Thịt Nướng Sả","Thịt heo nướng sả","Món nướng",420,30,24,15,"B1,B12",30,4,
    "Ướp thịt với sả băm, tỏi, nước mắm, mật ong. Nướng trên than hoa đến vàng thơm.",
    [("Thịt heo","500g"),("Sả","4 cây"),("Tỏi","5 tép"),("Mật ong","30ml"),("Nước mắm","30ml")])
# 40
add(cur,"Canh Cải Thìa Thịt Bằm","Canh cải thìa nấu thịt","Món canh",130,10,5,12,"A,C,K",15,4,
    "Xào thịt bằm, nêm gia vị. Thêm nước, đun sôi, cho cải thìa vào nấu chín. Nêm nước mắm, tiêu.",
    [("Cải thìa","300g"),("Thịt heo xay","100g"),("Nước mắm","15ml"),("Tiêu","3g")])
# 41
add(cur,"Bánh Tét","Bánh tét miền Nam","Món bánh",450,12,8,85,"B1",180,6,
    "Ngâm nếp, trộn nước cốt dừa. Nhân đậu xanh, thịt mỡ. Gói hình trụ bằng lá chuối, luộc 8 tiếng.",
    [("Nếp","1kg"),("Đậu xanh","300g"),("Thịt mỡ","200g"),("Lá chuối","nhiều"),("Nước cốt dừa","200ml")])
# 42
add(cur,"Ốc Len Xào Dừa","Ốc len xào nước cốt dừa","Món xào",280,18,14,20,"B12,Fe",25,2,
    "Luộc ốc len, khêu thịt. Xào với sả, ớt, nước cốt dừa, lá dứa. Nêm nước mắm, đường.",
    [("Ốc len","500g"),("Nước cốt dừa","150ml"),("Sả","3 cây"),("Ớt","2 quả"),("Lá dứa","3 lá")])
# 43
add(cur,"Cơm Hến","Cơm hến Huế","Món cơm",300,15,8,42,"B12,Fe",25,2,
    "Luộc hến, lấy nước. Cơm nguội trộn hến, rau sống, đậu phộng, tóp mỡ, mắm ruốc pha.",
    [("Cơm nguội","300g"),("Hến","300g"),("Đậu phộng","40g"),("Tóp mỡ","30g"),("Rau sống","100g")])
# 44
add(cur,"Gỏi Gà Bắp Cải","Gỏi gà xé trộn bắp cải","Món gỏi",220,25,8,14,"C,B6",25,2,
    "Luộc gà, xé sợi. Bắp cải thái sợi mỏng. Trộn nước mắm chua ngọt, rau răm, hành phi, đậu phộng.",
    [("Thịt gà","300g"),("Bắp cải","200g"),("Rau răm","30g"),("Đậu phộng","40g"),("Hành phi","20g")])
# 45
add(cur,"Bún Măng Vịt","Bún nấu măng với vịt","Món nước",420,30,18,40,"B6,Fe",60,4,
    "Luộc vịt, lấy nước dùng. Nấu măng tươi mềm. Chan nước dùng lên bún, xếp thịt vịt, măng, rau thơm.",
    [("Bún","400g"),("Thịt vịt","400g"),("Măng tươi","200g"),("Rau thơm","50g"),("Hành phi","20g")])
# 46
add(cur,"Bánh Căn","Bánh căn Ninh Thuận","Món bánh",280,12,8,40,"B1,Ca",25,4,
    "Đổ bột gạo vào khuôn đất nung nóng, thêm trứng hoặc tôm. Nướng đến giòn. Ăn kèm nước mắm, mỡ hành.",
    [("Bột gạo","300g"),("Trứng","4 quả"),("Tôm","100g"),("Mỡ hành","40ml"),("Nước mắm","30ml")])
# 47
add(cur,"Thịt Bò Xào Ớt","Bò xào ớt chuông","Món xào",380,30,18,20,"B12,C",15,2,
    "Thái bò mỏng, ướp nước mắm, tiêu. Xào bò lửa lớn, thêm ớt chuông, hành tây. Đảo nhanh tay.",
    [("Thịt bò","300g"),("Ớt chuông","2 quả"),("Hành tây","1 củ"),("Nước mắm","20ml"),("Dầu hào","15ml")])
# 48
add(cur,"Chè Đậu Xanh","Chè đậu xanh nước cốt dừa","Món chè",250,8,6,42,"B1,Fe",40,4,
    "Nấu đậu xanh mềm nhừ, thêm đường. Nấu nước cốt dừa béo. Chan chè ra chén, rưới nước cốt dừa.",
    [("Đậu xanh","200g"),("Đường","80g"),("Nước cốt dừa","200ml"),("Muối","2g")])
# 49
add(cur,"Bún Cá Sứa Nha Trang","Bún cá sứa đặc sản","Món nước",300,20,6,42,"D,B12",35,2,
    "Nấu nước dùng cá thu. Sứa trần sơ. Ăn bún với cá, sứa, chả cá, rau sống, nước lèo chua ngọt.",
    [("Bún","300g"),("Cá thu","200g"),("Sứa","150g"),("Chả cá","100g"),("Rau sống","100g")])
# 50
add(cur,"Vịt Nấu Chao","Vịt nấu chao miền Tây","Món nước",450,32,22,25,"B6,B12",50,4,
    "Ướp vịt với chao, sả, tỏi. Xào vịt săn, thêm nước dừa, khoai môn. Nấu đến khi vịt mềm, khoai bở.",
    [("Thịt vịt","500g"),("Chao","4 ô"),("Khoai môn","200g"),("Nước dừa","400ml"),("Sả","3 cây")])

conn.commit()
cur.close()
conn.close()
print("\n=== Part 2: Done! 25 more dishes added ===")
