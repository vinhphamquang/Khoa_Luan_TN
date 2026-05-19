import os, sys, psycopg2
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if 'sslmode' not in DATABASE_URL:
    DATABASE_URL += ('&' if '?' in DATABASE_URL else '?') + 'sslmode=require'

FOODS = [
{"name":"Phở Bò","desc":"Phở bò truyền thống với nước dùng ninh xương, bánh phở và thịt bò","cat":"Món nước","cal":450,"pro":25,"fat":12,"carb":55,"vit":"B12, B6, Sắt","time":120,"serve":2,"guide":"Ninh xương bò 4-6 tiếng với gừng, hành nướng, quế, hồi, thảo quả. Trụng bánh phở, xếp thịt bò, chan nước dùng. Ăn kèm giá đỗ, rau thơm, chanh, ớt.","ings":[("Bánh phở","400g"),("Thịt bò","300g"),("Xương bò","1kg"),("Gừng","50g"),("Hành tây","2 củ"),("Quế","1 thanh"),("Hồi","3 cánh"),("Thảo quả","2 quả"),("Nước mắm","3 tbsp"),("Giá đỗ","200g"),("Rau thơm","1 bó")]},
{"name":"Bún Bò Huế","desc":"Bún bò Huế cay nồng đặc trưng với nước dùng sả, ớt và mắm ruốc","cat":"Món nước","cal":520,"pro":28,"fat":18,"carb":58,"vit":"B12, C, Sắt","time":150,"serve":2,"guide":"Ninh xương heo, bò với sả, ớt, mắm ruốc. Thêm chả cua, huyết. Trụng bún, chan nước dùng nóng. Ăn kèm rau sống, chanh.","ings":[("Bún tươi","400g"),("Thịt bò bắp","300g"),("Giò heo","200g"),("Sả","5 cây"),("Mắm ruốc","2 tbsp"),("Ớt bột","1 tbsp"),("Chả cua","200g"),("Rau sống","200g")]},
{"name":"Cơm Tấm","desc":"Cơm tấm Sài Gòn với sườn nướng, bì, chả, trứng ốp la","cat":"Món cơm","cal":650,"pro":35,"fat":22,"carb":75,"vit":"B1, B6, Kẽm","time":45,"serve":1,"guide":"Ướp sườn với sả, tỏi, nước mắm, đường, nướng trên than. Nấu cơm tấm. Chiên trứng ốp la. Bày ra đĩa với bì, chả, đồ chua, nước mắm pha.","ings":[("Gạo tấm","200g"),("Sườn heo","200g"),("Trứng","1 quả"),("Bì heo","50g"),("Chả trứng","50g"),("Đồ chua","50g"),("Nước mắm","2 tbsp"),("Tỏi","3 tép"),("Sả","2 cây")]},
{"name":"Bánh Mì","desc":"Bánh mì Việt Nam giòn rụm với nhân thịt, pate, rau sống","cat":"Món ăn nhanh","cal":380,"pro":18,"fat":15,"carb":42,"vit":"B1, B2, C","time":15,"serve":1,"guide":"Nướng giòn bánh mì. Phết bơ, pate lên ruột bánh. Xếp thịt nguội, chả lụa, dưa leo, đồ chua, rau mùi, ớt. Rưới nước tương.","ings":[("Bánh mì","1 ổ"),("Pate","30g"),("Thịt nguội","50g"),("Chả lụa","30g"),("Dưa leo","1/2 quả"),("Đồ chua","30g"),("Rau mùi","1 nhánh"),("Ớt","1 quả")]},
{"name":"Gỏi Cuốn","desc":"Gỏi cuốn tôm thịt tươi mát cuốn bánh tráng với rau sống","cat":"Món khai vị","cal":180,"pro":15,"fat":3,"carb":25,"vit":"A, C, K","time":30,"serve":2,"guide":"Luộc tôm, thịt. Nhúng bánh tráng nước ấm, xếp rau, bún, tôm, thịt rồi cuốn chặt. Pha nước chấm mắm nêm hoặc tương đen.","ings":[("Bánh tráng","10 cái"),("Tôm","200g"),("Thịt heo","150g"),("Bún tươi","100g"),("Rau xà lách","100g"),("Rau thơm","50g"),("Tương đen","50ml")]},
{"name":"Chả Giò","desc":"Chả giò (nem rán) giòn rụm với nhân thịt heo, mộc nhĩ, miến","cat":"Món chiên","cal":320,"pro":14,"fat":20,"carb":22,"vit":"B1, B6, Sắt","time":45,"serve":4,"guide":"Trộn nhân thịt heo xay, mộc nhĩ, miến, cà rốt, hành. Cuốn bánh tráng, chiên vàng giòn. Ăn kèm nước mắm chua ngọt và rau sống.","ings":[("Bánh tráng","20 cái"),("Thịt heo xay","300g"),("Mộc nhĩ","20g"),("Miến","50g"),("Cà rốt","1 củ"),("Trứng","2 quả"),("Hành tím","3 củ")]},
{"name":"Bún Chả","desc":"Bún chả Hà Nội với chả viên, chả miếng nướng than và nước chấm","cat":"Món nước","cal":480,"pro":30,"fat":16,"carb":52,"vit":"B6, B12, C","time":60,"serve":2,"guide":"Ướp thịt ba chỉ và thịt xay viên với nước mắm, đường, tỏi, tiêu. Nướng trên than hoa. Pha nước chấm chua ngọt với đu đủ, cà rốt. Ăn với bún và rau sống.","ings":[("Thịt ba chỉ","200g"),("Thịt xay","200g"),("Bún tươi","300g"),("Nước mắm","3 tbsp"),("Đường","2 tbsp"),("Tỏi","5 tép"),("Đu đủ xanh","100g"),("Rau sống","200g")]},
{"name":"Bánh Xèo","desc":"Bánh xèo giòn vàng với nhân tôm, thịt, giá đỗ","cat":"Món chiên","cal":420,"pro":18,"fat":22,"carb":38,"vit":"A, B1, C","time":40,"serve":2,"guide":"Pha bột bánh xèo với nước cốt dừa, bột nghệ. Đổ bột mỏng trên chảo nóng, thêm tôm, thịt, giá. Gấp đôi, chiên giòn. Cuốn rau sống, chấm nước mắm.","ings":[("Bột bánh xèo","200g"),("Tôm","150g"),("Thịt heo","100g"),("Giá đỗ","200g"),("Nước cốt dừa","100ml"),("Bột nghệ","1 tsp"),("Rau sống","300g")]},
{"name":"Hủ Tiếu","desc":"Hủ tiếu Nam Vang với nước dùng trong, tôm, thịt, gan","cat":"Món nước","cal":400,"pro":25,"fat":10,"carb":50,"vit":"B12, Sắt, Kẽm","time":90,"serve":2,"guide":"Ninh xương heo lấy nước dùng trong. Trụng hủ tiếu, xếp tôm, thịt băm, gan. Chan nước dùng, thêm hành phi, tỏi phi.","ings":[("Hủ tiếu","300g"),("Tôm","150g"),("Thịt heo xay","150g"),("Gan heo","100g"),("Xương heo","500g"),("Hành phi","2 tbsp"),("Tỏi phi","1 tbsp")]},
{"name":"Mì Quảng","desc":"Mì Quảng đặc sản miền Trung với nước dùng đậm đà, đậu phộng","cat":"Món nước","cal":470,"pro":26,"fat":15,"carb":55,"vit":"B6, E, Sắt","time":60,"serve":2,"guide":"Nấu nước dùng từ xương, tôm. Ướp thịt gà hoặc heo với nghệ. Trụng mì, chan nước dùng vừa xâm xấp. Rắc đậu phộng rang, bánh tráng nướng, rau sống.","ings":[("Mì Quảng","300g"),("Thịt gà","200g"),("Tôm","150g"),("Đậu phộng","50g"),("Nghệ","1 tsp"),("Bánh tráng","4 cái"),("Rau sống","200g")]},
{"name":"Cao Lầu","desc":"Cao lầu Hội An với sợi mì đặc biệt, thịt heo và rau sống","cat":"Món nước","cal":430,"pro":22,"fat":14,"carb":52,"vit":"B1, B6, Sắt","time":50,"serve":2,"guide":"Luộc sợi cao lầu. Thái thịt heo xá xíu. Xếp mì, thịt, rau sống, giá. Rưới nước xá xíu và dầu phi hành.","ings":[("Sợi cao lầu","300g"),("Thịt heo xá xíu","200g"),("Giá đỗ","100g"),("Rau sống","150g"),("Bánh tráng nướng","3 cái"),("Nước xá xíu","100ml")]},
{"name":"Bún Riêu Cua","desc":"Bún riêu cua với nước dùng cà chua chua thanh, riêu cua đồng","cat":"Món nước","cal":380,"pro":22,"fat":12,"carb":45,"vit":"A, B12, Canxi","time":90,"serve":2,"guide":"Giã cua đồng lọc lấy nước và gạch. Nấu nước dùng với cà chua, mắm tôm. Cho riêu cua vào, thêm đậu phụ, huyết. Trụng bún, chan nước dùng.","ings":[("Bún tươi","400g"),("Cua đồng","500g"),("Cà chua","3 quả"),("Đậu phụ","2 bìa"),("Mắm tôm","1 tbsp"),("Hành lá","3 cây"),("Rau sống","200g")]},
{"name":"Canh Chua Cá","desc":"Canh chua cá miền Nam với thơm, đậu bắp, giá đỗ","cat":"Món canh","cal":280,"pro":25,"fat":8,"carb":28,"vit":"A, C, B12","time":30,"serve":2,"guide":"Nấu nước dùng với thơm, cà chua, me. Cho cá lóc vào, thêm đậu bắp, giá đỗ, bạc hà. Nêm nước mắm, đường. Rắc rau ngổ.","ings":[("Cá lóc","400g"),("Thơm","1/2 quả"),("Cà chua","2 quả"),("Đậu bắp","100g"),("Giá đỗ","100g"),("Me","30g"),("Rau ngổ","1 bó")]},
{"name":"Thịt Kho Tàu","desc":"Thịt kho tàu (thịt kho trứng) đậm đà với nước dừa","cat":"Món kho","cal":550,"pro":30,"fat":35,"carb":20,"vit":"B1, B12, Sắt","time":90,"serve":4,"guide":"Rim đường thắng màu caramel. Cho thịt ba chỉ vào đảo đều. Đổ nước dừa tươi, nước mắm, tiêu. Thêm trứng luộc. Kho liu riu 1-2 tiếng đến khi mềm.","ings":[("Thịt ba chỉ","500g"),("Trứng vịt","4 quả"),("Nước dừa tươi","500ml"),("Nước mắm","3 tbsp"),("Đường","2 tbsp"),("Hành tím","3 củ"),("Tỏi","5 tép")]},
{"name":"Cá Kho Tộ","desc":"Cá kho tộ miền Nam đậm đà trong nồi đất","cat":"Món kho","cal":350,"pro":28,"fat":18,"carb":15,"vit":"D, B12, Omega-3","time":45,"serve":2,"guide":"Ướp cá basa với nước mắm, đường, tiêu, nước hàng. Phi hành tỏi trong nồi đất, xếp cá vào. Kho lửa nhỏ đến khi cá thấm gia vị, nước kho sánh lại.","ings":[("Cá basa","400g"),("Nước mắm","3 tbsp"),("Đường","1.5 tbsp"),("Nước hàng","1 tbsp"),("Hành tím","3 củ"),("Tỏi","4 tép"),("Ớt","2 quả"),("Tiêu","1 tsp")]},
{"name":"Gà Nướng Mật Ong","desc":"Gà nướng mật ong vàng óng, thơm lừng","cat":"Món nướng","cal":480,"pro":38,"fat":25,"carb":18,"vit":"B6, B12, Kẽm","time":90,"serve":4,"guide":"Ướp gà với mật ong, nước mắm, tỏi, gừng, ngũ vị hương 2 tiếng. Nướng ở 200°C trong 45-60 phút, quét thêm mật ong giữa chừng.","ings":[("Gà nguyên con","1.2kg"),("Mật ong","3 tbsp"),("Nước mắm","2 tbsp"),("Tỏi","5 tép"),("Gừng","30g"),("Ngũ vị hương","1 tsp")]},
{"name":"Bò Lúc Lắc","desc":"Bò lúc lắc xào tỏi bơ thơm phức, ăn kèm cơm hoặc salad","cat":"Món xào","cal":420,"pro":32,"fat":25,"carb":12,"vit":"B12, B6, Sắt, Kẽm","time":20,"serve":2,"guide":"Thái bò thành khối vuông, ướp nước tương, tỏi, tiêu, đường. Phi tỏi bơ, cho bò vào xào lửa lớn nhanh tay. Bò chín tái vừa mềm.","ings":[("Thịt bò thăn","300g"),("Bơ","30g"),("Tỏi","5 tép"),("Nước tương","2 tbsp"),("Tiêu","1 tsp"),("Hành tây","1 củ"),("Cà chua","1 quả")]},
{"name":"Gà Xào Sả Ớt","desc":"Gà xào sả ớt cay thơm đậm đà, ăn với cơm nóng","cat":"Món xào","cal":380,"pro":30,"fat":18,"carb":20,"vit":"B6, C, Sắt","time":30,"serve":2,"guide":"Ướp gà với sả băm, ớt, nước mắm, đường. Phi sả ớt thơm, cho gà vào xào lửa lớn. Thêm ít nước, rim đến khi cạn nước, gà thấm gia vị.","ings":[("Thịt gà","400g"),("Sả","5 cây"),("Ớt","5 quả"),("Nước mắm","2 tbsp"),("Đường","1 tbsp"),("Tỏi","3 tép"),("Hành tím","2 củ")]},
{"name":"Cơm Chiên Dương Châu","desc":"Cơm chiên với tôm, lạp xưởng, trứng, đậu Hà Lan","cat":"Món cơm","cal":520,"pro":20,"fat":18,"carb":65,"vit":"B1, B6, A","time":20,"serve":2,"guide":"Xào tôm, lạp xưởng trước. Cho cơm nguội vào xào lửa lớn, tạo không gian cho trứng. Thêm đậu Hà Lan, cà rốt, nêm nước mắm, tiêu.","ings":[("Cơm nguội","400g"),("Tôm","100g"),("Lạp xưởng","2 cây"),("Trứng","2 quả"),("Đậu Hà Lan","50g"),("Cà rốt","1 củ"),("Hành lá","3 cây")]},
{"name":"Bánh Cuốn","desc":"Bánh cuốn Thanh Trì mỏng mềm nhân thịt, mộc nhĩ","cat":"Món hấp","cal":280,"pro":14,"fat":8,"carb":38,"vit":"B1, B6, Sắt","time":60,"serve":2,"guide":"Pha bột gạo với nước, tráng mỏng trên vải hấp. Nhân thịt xay xào mộc nhĩ, hành. Cuộn bánh, ăn kèm chả quế và nước mắm chua ngọt.","ings":[("Bột gạo","200g"),("Thịt heo xay","150g"),("Mộc nhĩ","20g"),("Hành khô","3 củ"),("Chả quế","100g"),("Nước mắm","2 tbsp"),("Giá đỗ","100g")]},
{"name":"Xôi Xéo","desc":"Xôi xéo Hà Nội dẻo thơm với đậu xanh, hành phi","cat":"Món xôi","cal":450,"pro":12,"fat":15,"carb":68,"vit":"B1, E, Sắt","time":60,"serve":2,"guide":"Ngâm nếp 4 tiếng, hấp chín. Đậu xanh hấp chín tán nhuyễn. Xếp xôi, đậu xanh, rưới mỡ hành phi. Rắc hành phi giòn.","ings":[("Gạo nếp","300g"),("Đậu xanh","150g"),("Hành tím","5 củ"),("Mỡ hành","50ml"),("Muối","1 tsp")]},
{"name":"Bò Kho","desc":"Bò kho mềm thơm sả ớt, ăn với bánh mì hoặc bún","cat":"Món kho","cal":480,"pro":30,"fat":22,"carb":35,"vit":"B12, A, Sắt","time":120,"serve":4,"guide":"Ướp bò với sả, ớt, bột cà ri. Phi hành tỏi, xào bò. Thêm nước, cà rốt, khoai tây. Hầm liu riu 2 tiếng đến khi bò mềm.","ings":[("Thịt bò gầu","500g"),("Cà rốt","2 củ"),("Sả","4 cây"),("Bột cà ri","1 tbsp"),("Nước dừa","200ml"),("Hành tây","1 củ"),("Khoai tây","2 củ")]},
{"name":"Lẩu Thái","desc":"Lẩu Thái Tom Yum chua cay với hải sản và rau","cat":"Lẩu","cal":350,"pro":28,"fat":12,"carb":30,"vit":"C, B12, Sắt","time":40,"serve":4,"guide":"Nấu nước dùng với sả, lá chanh, galangal, ớt, cà chua. Cho nước cốt chanh, nước mắm. Nhúng hải sản, nấm, rau.","ings":[("Tôm","300g"),("Mực","200g"),("Nấm","200g"),("Sả","3 cây"),("Lá chanh","5 lá"),("Ớt","3 quả"),("Cà chua","2 quả"),("Rau muống","200g")]},
{"name":"Lẩu Gà Lá É","desc":"Lẩu gà lá é thơm ngọt tự nhiên, thanh mát","cat":"Lẩu","cal":380,"pro":32,"fat":15,"carb":25,"vit":"B6, C, K","time":45,"serve":4,"guide":"Luộc gà lấy nước dùng trong. Cho lá é, sả, gừng vào nước dùng. Thái gà miếng vừa. Nhúng rau, nấm ăn kèm bún.","ings":[("Gà ta","1 con"),("Lá é","1 bó"),("Sả","3 cây"),("Gừng","30g"),("Nấm","200g"),("Rau muống","200g"),("Bún tươi","300g")]},
{"name":"Chả Cá Lã Vọng","desc":"Chả cá Hà Nội chiên nghệ thì là, ăn kèm bún, mắm tôm","cat":"Món chiên","cal":420,"pro":30,"fat":22,"carb":25,"vit":"D, B12, Omega-3","time":40,"serve":2,"guide":"Ướp cá lăng với nghệ, sả, mẻ. Chiên cá sơ, sau đó xào với thì là, hành lá trên chảo nóng. Ăn kèm bún, mắm tôm, đậu phộng.","ings":[("Cá lăng","400g"),("Nghệ tươi","30g"),("Thì là","1 bó"),("Hành lá","1 bó"),("Bún tươi","200g"),("Mắm tôm","2 tbsp"),("Đậu phộng","50g")]}
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
print(f"\n=== Da them {count}/{len(FOODS)} mon (phan 1) ===")
conn.close()
