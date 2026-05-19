import os, sys, psycopg2
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if 'sslmode' not in DATABASE_URL:
    DATABASE_URL += ('&' if '?' in DATABASE_URL else '?') + 'sslmode=require'

FOODS = [
{"name":"Bánh Canh Cua","desc":"Bánh canh cua với sợi bánh canh dày mềm, nước dùng ngọt cua","cat":"Món nước","cal":380,"pro":22,"fat":10,"carb":48,"vit":"B12, Canxi, Sắt","time":60,"serve":2,"guide":"Nấu nước dùng từ cua, gạch cua. Trụng sợi bánh canh, chan nước dùng. Thêm thịt cua, hành lá, tiêu.","ings":[("Bánh canh bột gạo","300g"),("Cua","500g"),("Hành lá","3 cây"),("Nước mắm","2 tbsp"),("Tiêu","1 tsp")]},
{"name":"Bún Thịt Nướng","desc":"Bún thịt nướng với thịt heo nướng than, rau sống, đậu phộng","cat":"Món trộn","cal":450,"pro":28,"fat":16,"carb":48,"vit":"B6, C, Sắt","time":40,"serve":2,"guide":"Ướp thịt heo với sả, tỏi, nước mắm, mật ong. Nướng trên than. Bày bún, rau sống, thịt nướng, đậu phộng, hành phi. Rưới nước mắm chua ngọt.","ings":[("Thịt heo","300g"),("Bún tươi","300g"),("Rau sống","200g"),("Đậu phộng","30g"),("Sả","3 cây"),("Nước mắm","3 tbsp")]},
{"name":"Phở Gà","desc":"Phở gà thanh nhẹ với nước dùng trong, thịt gà ta","cat":"Món nước","cal":400,"pro":28,"fat":10,"carb":50,"vit":"B6, B12, Kẽm","time":90,"serve":2,"guide":"Luộc gà ta, lấy nước dùng trong. Trụng bánh phở, xếp thịt gà xé, chan nước dùng. Thêm hành lá, rau thơm, chanh, ớt.","ings":[("Bánh phở","400g"),("Gà ta","500g"),("Gừng","30g"),("Hành tây","1 củ"),("Rau thơm","1 bó"),("Nước mắm","2 tbsp")]},
{"name":"Bún Mắm","desc":"Bún mắm miền Tây đậm đà với mắm cá linh, hải sản","cat":"Món nước","cal":480,"pro":30,"fat":15,"carb":52,"vit":"B12, D, Sắt","time":60,"serve":2,"guide":"Nấu nước dùng từ mắm cá linh, lọc trong. Thêm tôm, mực, cá, thịt heo. Trụng bún, chan nước dùng, thêm rau sống.","ings":[("Bún tươi","400g"),("Mắm cá linh","100ml"),("Tôm","150g"),("Mực","100g"),("Cá basa","150g"),("Cà tím","1 quả"),("Rau sống","200g")]},
{"name":"Cháo Lòng","desc":"Cháo lòng heo nóng hổi với lòng heo và huyết","cat":"Món cháo","cal":350,"pro":20,"fat":12,"carb":40,"vit":"B12, Sắt, Kẽm","time":60,"serve":2,"guide":"Nấu cháo trắng nhừ. Luộc lòng heo, thái miếng. Cho lòng, huyết vào cháo. Nêm nước mắm, tiêu. Rắc hành lá, giá đỗ.","ings":[("Gạo","200g"),("Lòng heo","300g"),("Huyết heo","100g"),("Hành lá","3 cây"),("Giá đỗ","100g"),("Tiêu","1 tsp")]},
{"name":"Cháo Gà","desc":"Cháo gà nấu nhừ, thanh đạm, bổ dưỡng","cat":"Món cháo","cal":300,"pro":22,"fat":8,"carb":38,"vit":"B6, B12, Kẽm","time":45,"serve":2,"guide":"Luộc gà, xé thịt. Nấu gạo với nước luộc gà đến nhừ. Cho thịt gà xé vào. Rắc hành lá, gừng thái sợi, tiêu.","ings":[("Gạo","200g"),("Thịt gà","300g"),("Gừng","20g"),("Hành lá","3 cây"),("Nước mắm","1 tbsp")]},
{"name":"Nem Nướng Nha Trang","desc":"Nem nướng Nha Trang giòn thơm cuốn bánh tráng","cat":"Món nướng","cal":380,"pro":22,"fat":18,"carb":30,"vit":"B1, B6, C","time":40,"serve":2,"guide":"Xay thịt heo với tỏi, đường, bột nổi. Viên thành viên, nướng trên than. Cuốn bánh tráng với rau sống, bún, chấm nước chấm.","ings":[("Thịt heo nạc","400g"),("Tỏi","5 tép"),("Đường","1 tbsp"),("Bánh tráng","10 cái"),("Rau sống","200g"),("Bún tươi","100g")]},
{"name":"Bò Né","desc":"Bò né (bò bít tết) trên đĩa nóng kèm trứng ốp la, pate","cat":"Món áp chảo","cal":550,"pro":35,"fat":30,"carb":30,"vit":"B12, B6, Sắt","time":20,"serve":1,"guide":"Ướp bò với tiêu, bơ, nước tương. Áp chảo trên đĩa gang nóng. Thêm trứng ốp la, pate, bánh mì. Ăn ngay khi còn nóng xèo xèo.","ings":[("Thịt bò","200g"),("Trứng","2 quả"),("Pate","30g"),("Bánh mì","1 ổ"),("Bơ","20g"),("Nước tương","1 tbsp")]},
{"name":"Cơm Gà Hội An","desc":"Cơm gà Hội An với cơm nấu nước luộc gà, gà xé phay","cat":"Món cơm","cal":480,"pro":30,"fat":15,"carb":55,"vit":"B6, B12, Kẽm","time":50,"serve":2,"guide":"Luộc gà, lấy nước luộc nấu cơm. Gà xé phay trộn hành tây, rau răm. Ăn kèm canh, đồ chua.","ings":[("Gạo","300g"),("Gà ta","400g"),("Hành tây","1 củ"),("Rau răm","1 bó"),("Nghệ","1 tsp"),("Nước mắm","2 tbsp")]},
{"name":"Thịt Kho Trứng Cút","desc":"Thịt kho trứng cút ngọt mặn đậm đà","cat":"Món kho","cal":480,"pro":28,"fat":28,"carb":22,"vit":"B12, D, Sắt","time":60,"serve":4,"guide":"Thắng đường caramel. Cho thịt ba chỉ kho với nước dừa, nước mắm. Thêm trứng cút luộc. Kho liu riu đến mềm.","ings":[("Thịt ba chỉ","400g"),("Trứng cút","20 quả"),("Nước dừa","300ml"),("Nước mắm","2 tbsp"),("Đường","2 tbsp"),("Hành tím","3 củ")]},
{"name":"Gỏi Gà","desc":"Gỏi gà bắp cải trộn rau răm, đậu phộng","cat":"Món gỏi","cal":280,"pro":25,"fat":12,"carb":18,"vit":"C, K, B6","time":25,"serve":2,"guide":"Luộc gà, xé sợi. Thái bắp cải, hành tây sợi mỏng. Trộn gà, rau với nước mắm chua ngọt. Rắc đậu phộng, rau răm.","ings":[("Thịt gà","300g"),("Bắp cải","200g"),("Hành tây","1 củ"),("Rau răm","1 bó"),("Đậu phộng","30g"),("Nước mắm","2 tbsp")]},
{"name":"Sườn Xào Chua Ngọt","desc":"Sườn heo xào sốt chua ngọt với dứa, cà chua","cat":"Món xào","cal":450,"pro":25,"fat":22,"carb":35,"vit":"C, B1, B6","time":35,"serve":2,"guide":"Chiên sơ sườn. Xào cà chua, dứa với đường, giấm, nước mắm tạo sốt. Cho sườn vào rim đến khi sốt sánh đều.","ings":[("Sườn heo","400g"),("Dứa","1/2 quả"),("Cà chua","2 quả"),("Đường","2 tbsp"),("Giấm","1 tbsp"),("Nước mắm","2 tbsp"),("Tỏi","3 tép")]},
{"name":"Rau Muống Xào Tỏi","desc":"Rau muống xào tỏi giòn xanh, đơn giản mà ngon","cat":"Món rau","cal":120,"pro":5,"fat":6,"carb":12,"vit":"A, C, K, Sắt","time":10,"serve":2,"guide":"Phi tỏi băm thơm với dầu nóng. Cho rau muống vào xào lửa lớn nhanh tay. Nêm nước mắm, đường. Rau chín tới vẫn giòn xanh.","ings":[("Rau muống","300g"),("Tỏi","5 tép"),("Nước mắm","1 tbsp"),("Đường","1/2 tsp"),("Dầu ăn","2 tbsp")]},
{"name":"Đậu Hũ Sốt Cà Chua","desc":"Đậu hũ chiên giòn sốt cà chua thơm ngon","cat":"Món chay","cal":250,"pro":15,"fat":14,"carb":18,"vit":"C, Canxi, Sắt","time":20,"serve":2,"guide":"Chiên đậu hũ vàng giòn. Xào cà chua nhuyễn với hành tỏi. Cho đậu hũ vào rim với sốt cà chua, nêm nước mắm. Rắc hành lá.","ings":[("Đậu hũ","2 bìa"),("Cà chua","3 quả"),("Hành lá","2 cây"),("Tỏi","3 tép"),("Nước mắm","1 tbsp")]},
{"name":"Canh Khổ Qua Nhồi Thịt","desc":"Canh khổ qua nhồi thịt thanh mát, giải nhiệt","cat":"Món canh","cal":220,"pro":18,"fat":8,"carb":20,"vit":"C, A, K, Sắt","time":40,"serve":2,"guide":"Khoét ruột khổ qua, nhồi thịt heo xay trộn mộc nhĩ, miến. Nấu nước dùng, cho khổ qua nhồi vào nấu chín mềm. Nêm nước mắm.","ings":[("Khổ qua","3 quả"),("Thịt heo xay","200g"),("Mộc nhĩ","10g"),("Miến","20g"),("Nước mắm","1 tbsp"),("Hành lá","2 cây")]},
{"name":"Tôm Rim Nước Dừa","desc":"Tôm rim nước dừa ngọt bùi, đậm đà","cat":"Món rim","cal":320,"pro":25,"fat":15,"carb":18,"vit":"B12, D, Selen","time":25,"serve":2,"guide":"Phi hành tỏi, cho tôm vào xào sơ. Đổ nước dừa, nước mắm, đường, tiêu. Rim lửa nhỏ đến khi nước sánh, tôm thấm gia vị.","ings":[("Tôm sú","400g"),("Nước dừa","200ml"),("Nước mắm","2 tbsp"),("Đường","1 tbsp"),("Hành tím","2 củ"),("Tỏi","3 tép"),("Tiêu","1 tsp")]},
{"name":"Gà Kho Gừng","desc":"Gà kho gừng ấm bụng, thơm nồng vị gừng","cat":"Món kho","cal":380,"pro":30,"fat":18,"carb":18,"vit":"B6, C, Sắt","time":40,"serve":2,"guide":"Ướp gà với nước mắm, đường, tiêu. Phi gừng thái sợi thơm. Cho gà vào kho với nước, rim đến khi cạn nước, gà thấm.","ings":[("Thịt gà","400g"),("Gừng","50g"),("Nước mắm","2 tbsp"),("Đường","1 tbsp"),("Hành tím","2 củ"),("Tiêu","1 tsp")]},
{"name":"Bánh Bèo","desc":"Bánh bèo chén Huế mỏng mềm với nhân tôm chấy","cat":"Món hấp","cal":220,"pro":10,"fat":8,"carb":30,"vit":"B1, D, Selen","time":40,"serve":2,"guide":"Pha bột gạo với nước, đổ vào chén nhỏ hấp chín. Làm nhân tôm chấy phi hành. Rưới lên bánh, thêm mỡ hành, ăn kèm nước mắm.","ings":[("Bột gạo","200g"),("Tôm khô","50g"),("Hành phi","2 tbsp"),("Mỡ hành","30ml"),("Nước mắm","2 tbsp")]},
{"name":"Bánh Tráng Trộn","desc":"Bánh tráng trộn Sài Gòn với trứng cút, khô bò, rau răm","cat":"Món ăn vặt","cal":280,"pro":12,"fat":10,"carb":35,"vit":"C, B6, A","time":10,"serve":1,"guide":"Cắt bánh tráng sợi. Trộn với trứng cút, khô bò, xoài xanh, rau răm. Thêm tương ớt, nước mắm chua ngọt, sa tế. Trộn đều.","ings":[("Bánh tráng","5 cái"),("Trứng cút","5 quả"),("Khô bò","30g"),("Xoài xanh","1/2 quả"),("Rau răm","1 nhánh"),("Tương ớt","1 tbsp")]},
{"name":"Bún Đậu Mắm Tôm","desc":"Bún đậu mắm tôm Hà Nội với đậu hũ chiên, chả cốm","cat":"Món ăn","cal":450,"pro":22,"fat":25,"carb":35,"vit":"Canxi, B1, K","time":20,"serve":2,"guide":"Chiên đậu hũ vàng giòn. Bày bún lá, đậu hũ, chả cốm, thịt luộc. Pha mắm tôm với chanh, đường, ớt, quất.","ings":[("Bún lá","200g"),("Đậu hũ","3 bìa"),("Chả cốm","100g"),("Thịt luộc","100g"),("Mắm tôm","2 tbsp"),("Chanh","1 quả"),("Ớt","2 quả")]},
{"name":"Cơm Hến","desc":"Cơm hến Huế thanh đạm với hến xào, rau sống, mắm ruốc","cat":"Món cơm","cal":320,"pro":18,"fat":8,"carb":45,"vit":"B12, Sắt, Canxi","time":30,"serve":2,"guide":"Luộc hến lấy nước và thịt. Xào hến với gia vị. Bày cơm nguội, hến xào, rau sống, đậu phộng. Rưới nước hến, mắm ruốc ớt.","ings":[("Cơm nguội","300g"),("Hến","500g"),("Rau sống","200g"),("Đậu phộng","30g"),("Mắm ruốc","1 tbsp"),("Ớt","3 quả")]},
{"name":"Bánh Khọt","desc":"Bánh khọt Vũng Tàu giòn xốp nhân tôm, ăn kèm rau sống","cat":"Món chiên","cal":350,"pro":15,"fat":18,"carb":32,"vit":"D, B1, Selen","time":30,"serve":2,"guide":"Pha bột gạo với nước cốt dừa, bột nghệ. Đổ bột vào khuôn nóng, cho tôm lên. Chiên vàng giòn. Ăn kèm rau sống, nước mắm chua ngọt.","ings":[("Bột gạo","200g"),("Nước cốt dừa","100ml"),("Tôm","200g"),("Bột nghệ","1 tsp"),("Hành lá","3 cây"),("Rau sống","200g")]},
{"name":"Thịt Heo Quay","desc":"Thịt heo quay da giòn rụm, thịt mềm ngọt","cat":"Món quay","cal":520,"pro":28,"fat":35,"carb":10,"vit":"B1, B12, Sắt","time":120,"serve":4,"guide":"Ướp thịt ba rọi với ngũ vị hương, muối, tỏi. Để da khô, xăm lỗ nhỏ. Quay ở 220°C đến khi da phồng giòn vàng.","ings":[("Thịt ba rọi","1kg"),("Ngũ vị hương","1 tbsp"),("Muối","2 tbsp"),("Tỏi","5 tép"),("Giấm","1 tbsp")]},
{"name":"Bún Cá","desc":"Bún cá Châu Đốc với nước dùng mắm, cá lóc chiên","cat":"Món nước","cal":400,"pro":28,"fat":14,"carb":42,"vit":"D, B12, Omega-3","time":50,"serve":2,"guide":"Nấu nước dùng từ mắm cá, lọc trong. Chiên cá lóc vàng. Trụng bún, chan nước dùng, xếp cá chiên. Ăn kèm rau sống.","ings":[("Bún tươi","400g"),("Cá lóc","400g"),("Mắm cá","50ml"),("Cà tím","1 quả"),("Rau sống","200g"),("Thơm","1/4 quả")]},
{"name":"Gà Chiên Nước Mắm","desc":"Gà chiên giòn tẩm nước mắm chua ngọt Việt Nam","cat":"Món chiên","cal":480,"pro":32,"fat":25,"carb":28,"vit":"B6, B12, Kẽm","time":40,"serve":2,"guide":"Ướp đùi gà với tỏi, tiêu. Chiên vàng giòn. Nấu sốt nước mắm, đường, tỏi phi, ớt. Rưới sốt lên gà, rắc hành phi.","ings":[("Đùi gà","4 cái"),("Nước mắm","3 tbsp"),("Đường","2 tbsp"),("Tỏi","5 tép"),("Ớt","2 quả"),("Hành phi","2 tbsp")]}
]

conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
cursor = conn.cursor()
count = 0

for f in FOODS:
    try:
        cursor.execute("SELECT MaMonAn FROM MonAn WHERE LOWER(TenMonAn) = LOWER(%s)", (f["name"],))
        if cursor.fetchone():
            print(f"  [SKIP] {f['name']} - da ton tai")
            continue
        cursor.execute("INSERT INTO MonAn (TenMonAn, MoTa, PhanLoai) VALUES (%s,%s,%s) RETURNING MaMonAn",
            (f["name"], f["desc"], f["cat"]))
        mid = cursor.fetchone()[0]
        cursor.execute("INSERT INTO DinhDuong (MaMonAn,Calo,Protein,ChatBeo,Carbohydrate,Vitamin) VALUES (%s,%s,%s,%s,%s,%s)",
            (mid, f["cal"], f["pro"], f["fat"], f["carb"], f["vit"]))
        cursor.execute("INSERT INTO CongThuc (MaMonAn,HuongDan,ThoiGianNau,KhauPhan) VALUES (%s,%s,%s,%s) RETURNING MaCongThuc",
            (mid, f["guide"], f["time"], f["serve"]))
        cid = cursor.fetchone()[0]
        for ing_name, ing_qty in f["ings"]:
            cursor.execute("INSERT INTO NguyenLieu (TenNguyenLieu) VALUES (%s) ON CONFLICT DO NOTHING RETURNING MaNguyenLieu", (ing_name,))
            r = cursor.fetchone()
            if r:
                nid = r[0]
            else:
                cursor.execute("SELECT MaNguyenLieu FROM NguyenLieu WHERE TenNguyenLieu = %s", (ing_name,))
                nid = cursor.fetchone()[0]
            cursor.execute("INSERT INTO ChiTietNguyenLieu (MaCongThuc,MaNguyenLieu,SoLuong) VALUES (%s,%s,%s)", (cid, nid, ing_qty))
        count += 1
        print(f"  [OK] {count}. {f['name']}")
    except Exception as e:
        print(f"  [ERR] {f['name']}: {e}")
        conn.rollback()
        continue

conn.commit()

# Kiem tra tong
cursor.execute("SELECT COUNT(*) FROM MonAn")
total = cursor.fetchone()[0]
print(f"\n=== Da them {count}/{len(FOODS)} mon (phan 2) ===")
print(f"=== TONG CONG: {total} mon trong database ===")
conn.close()
