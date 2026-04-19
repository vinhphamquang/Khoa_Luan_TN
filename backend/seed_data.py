import sys
import os

sys.path.append(os.path.dirname(__file__))

from db_queries import get_db_connection, insert_food_full

foods = [
    {
        "TenMonAn": "Phở Bò",
        "MoTa": "Món phở truyền thống của Việt Nam với nước dùng đậm đà từ xương bò hầm nhiều giờ, kết hợp cùng bánh phở mềm và thịt bò thái lát mỏng. Hương vị đặc trưng từ quế, hồi, thảo quả.",
        "PhanLoai": "Món nước",
        "DinhDuong": {
            "Calo": 450,
            "Protein": 25.5,
            "ChatBeo": 12.0,
            "Carbohydrate": 60.0,
            "Vitamin": "Vitamin B12, Kẽm, Sắt, Canxi"
        },
        "CongThuc": {
            "HuongDan": "1. Hầm xương bò với gừng, hành tím nướng và các gia vị phở (quế, hồi, thảo quả) trong 4-6 tiếng.\n2. Thái mỏng thịt bò.\n3. Trụng bánh phở qua nước sôi rồi cho vào tô.\n4. Xếp thịt bò, hành phi, rau thơm lên trên.\n5. Chan nước dùng thật sôi vào tô và thưởng thức.",
            "ThoiGianNau": 360,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bánh phở tươi", "SoLuong": "150g"},
                {"TenNguyenLieu": "Thịt bò (thăn/nạm/gầu)", "SoLuong": "100g"},
                {"TenNguyenLieu": "Xương ống bò", "SoLuong": "500g"},
                {"TenNguyenLieu": "Gừng, hành tím, hoa hồi, quế", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Bánh Mì Thịt Nướng",
        "MoTa": "Bánh mì Việt Nam nổi tiếng với lớp vỏ giòn rụm, nhân thịt lợn nướng xém cạnh thơm phức, ăn kèm pate béo ngậy, đồ chua và rau thơm.",
        "PhanLoai": "Ăn nhanh",
        "DinhDuong": {
            "Calo": 380,
            "Protein": 18.0,
            "ChatBeo": 15.0,
            "Carbohydrate": 45.0,
            "Vitamin": "Vitamin A, Vitamin C, Canxi"
        },
        "CongThuc": {
            "HuongDan": "1. Ướp thịt heo với sả, hành tỏi băm, nước mắm, mật ong trong 2 tiếng.\n2. Nướng thịt trên than hoa cho đến khi chín vàng xém.\n3. Xẻ bánh mì, phết pate và bơ mayo.\n4. Cho thịt nướng, dưa leo, ngò rí, đồ chua vào.\n5. Rưới thêm chút xì dầu hoặc tương ớt.",
            "ThoiGianNau": 45,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Ổ bánh mì", "SoLuong": "1 ổ"},
                {"TenNguyenLieu": "Thịt heo", "SoLuong": "80g"},
                {"TenNguyenLieu": "Pate, bơ", "SoLuong": "20g"},
                {"TenNguyenLieu": "Đồ chua (cà rốt, củ cải)", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Bún Chả Hà Nội",
        "MoTa": "Món ăn quen thuộc của người thủ đô với thịt heo nướng than hoa thơm lừng, chấm trong bát nước mắm chua ngọt thanh mát kèm theo đu đủ xanh giòn tan.",
        "PhanLoai": "Món bún",
        "DinhDuong": {
            "Calo": 550,
            "Protein": 28.0,
            "ChatBeo": 22.0,
            "Carbohydrate": 65.0,
            "Vitamin": "Vitamin C, Kẽm, Vitamin B"
        },
        "CongThuc": {
            "HuongDan": "1. Thịt băm viên và thịt ba chỉ thái mỏng ướp với nước hàng, mắm, tiêu, hành tỏi băm.\n2. Nướng thịt trên than hoa.\n3. Pha nước chấm: mắm, đường, giấm, nước lọc tỷ lệ vừa miệng, đun ấm.\n4. Cho đu đủ, cà rốt ngâm chua vào nước mắm.\n5. Dọn bún, rau sống và thịt nướng ra ăn kèm nước chấm.",
            "ThoiGianNau": 60,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bún tươi", "SoLuong": "200g"},
                {"TenNguyenLieu": "Thịt ba chỉ ba rọi", "SoHom": "100g"},
                {"TenNguyenLieu": "Thịt nạc dăm", "SoLuong": "100g"},
                {"TenNguyenLieu": "Đu đủ xanh, cà rốt", "SoLuong": "50g"}
            ]
        }
    },
    {
        "TenMonAn": "Bún Bò Huế",
        "MoTa": "Đặc sản xứ Huế với nước dùng thơm nồng mùi mắm ruốc, sả, có màu đỏ cam đẹp mắt. Ăn kèm thịt bò, giò heo, chả cua và rau sống thái nhỏ.",
        "PhanLoai": "Món nước",
        "DinhDuong": {
            "Calo": 600,
            "Protein": 35.0,
            "ChatBeo": 18.0,
            "Carbohydrate": 75.0,
            "Vitamin": "Sắt, Vitamin B6, Canxi"
        },
        "CongThuc": {
            "HuongDan": "1. Hầm móng giò và xương bò với sả cây và hành tây.\n2. Lọc mắm ruốc pha loãng lấy nước trong, đổ vào nồi nước dùng.\n3. Làm dầu sầu màu (dầu ăn phi sả, ớt, hạt điều màu) cho vào nồi.\n4. Sợi bún bò to trụng nước sôi.\n5. Xếp bún, bắp bò thái mỏng, giò heo, chả cua vào tô. Chan nước dùng sôi.",
            "ThoiGianNau": 180,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bún sợi to", "SoLuong": "200g"},
                {"TenNguyenLieu": "Bắp bò", "SoLuong": "100g"},
                {"TenNguyenLieu": "Móng giò heo", "SoLuong": "1 cục"},
                {"TenNguyenLieu": "Mắm ruốc Huế, sả cây", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Cơm Tấm Sườn Bì Chả",
        "MoTa": "Món ăn sáng/trưa/chiều huyền thoại của Sài Gòn. Cơm nấu từ hạt tấm gạo gãy, ăn với sườn cốt lết nướng mật ong xém cạnh, bì heo dai dai và chả trứng chưng béo ngậy.",
        "PhanLoai": "Cơm",
        "DinhDuong": {
            "Calo": 720,
            "Protein": 32.0,
            "ChatBeo": 25.0,
            "Carbohydrate": 80.0,
            "Vitamin": "Vitamin E, Sắt, Vitamin B1"
        },
        "CongThuc": {
            "HuongDan": "1. Gạo tấm vo sạch, hấp chín bằng xửng để cơm tơi xốp.\n2. Sườn cốt lết ướp sữa đặc, mật ong, tỏi, sả, nước mắm rồi nướng chín.\n3. Trộn bì heo luộc thái mỏng với thính gạo.\n4. Đúc chả trứng từ trứng, thịt băm, nấm mèo, miến.\n5. Dọn cơm ra đĩa, xếp sườn, bì, chả. Chan mỡ hành và nước mắm kẹo.",
            "ThoiGianNau": 90,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Gạo tấm", "SoLuong": "150g"},
                {"TenNguyenLieu": "Sườn cốt lết", "SoLuong": "150g"},
                {"TenNguyenLieu": "Trứng vịt, thịt băm", "SoLuong": "1 phần"},
                {"TenNguyenLieu": "Bì heo, mỡ hành", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Gỏi Cuốn",
        "MoTa": "Món ăn nhẹ thanh mát cực kỳ phổ biến. Tôm luộc đỏ au, thịt ba chỉ, bún và các loại rau thơm được cuộn chặt trong lớp bánh tráng mỏng. Chấm với tương đen hoặc mắm nêm.",
        "PhanLoai": "Khai vị",
        "DinhDuong": {
            "Calo": 220,
            "Protein": 15.0,
            "ChatBeo": 5.0,
            "Carbohydrate": 28.0,
            "Vitamin": "Vitamin A, Canxi, Magie"
        },
        "CongThuc": {
            "HuongDan": "1. Thịt ba chỉ luộc chín với chút muối, thái lát mỏng.\n2. Tôm luộc lột vỏ, xẻ đôi.\n3. Nhúng ướt bánh tráng.\n4. Xếp lần lượt xà lách, rau thơm, bún, thịt, tôm vào bánh tráng và cuộn chặt tay.\n5. Pha nước chấm tương đen với bơ đậu phộng và tỏi phi.",
            "ThoiGianNau": 30,
            "KhauPhan": 3,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bánh tráng", "SoLuong": "3 lá"},
                {"TenNguyenLieu": "Tôm sú", "SoLuong": "6 con"},
                {"TenNguyenLieu": "Thịt ba chỉ", "SoLuong": "50g"},
                {"TenNguyenLieu": "Rau thơm, bún", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Bánh Xèo",
        "MoTa": "Bánh xèo có lớp vỏ vàng ươm, giòn rụm bọc lấy nhân tôm, thịt, giá đỗ. Khi ăn cuốn bằng lá cải xanh, rau sống và chấm nước mắm tỏi ớt.",
        "PhanLoai": "Món ăn chơi",
        "DinhDuong": {
            "Calo": 410,
            "Protein": 16.0,
            "ChatBeo": 22.0,
            "Carbohydrate": 40.0,
            "Vitamin": "Vitamin A, Vitamin C, Chất xơ"
        },
        "CongThuc": {
            "HuongDan": "1. Pha bột bánh xèo với bột nghệ, nước cốt dừa, hành lá.\n2. Tôm, thịt thái mỏng xào sơ trong chảo.\n3. Đổ bột bánh xèo láng mỏng đều chảo, cho giá đỗ vào.\n4. Đậy nắp 2 phút cho chín rồi gập đôi bánh lại, chiên giòn.\n5. Cắt nhỏ bánh, cuốn rau sống chấm nước mắm.",
            "ThoiGianNau": 40,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bột bánh xèo", "SoLuong": "100g"},
                {"TenNguyenLieu": "Tôm, thịt ba rọi", "SoLuong": "100g"},
                {"TenNguyenLieu": "Giá đỗ", "SoLuong": "50g"},
                {"TenNguyenLieu": "Rau cải xanh, nước mắm", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Chả Giò (Nem Rán)",
        "MoTa": "Món chiên đặc sắc của ẩm thực Việt. Lớp vỏ bánh tráng giòn tan bọc bên trong là nhân thịt, miến, mộc nhĩ được băm nhuyễn, chiên ngập dầu vàng ươm.",
        "PhanLoai": "Khai vị",
        "DinhDuong": {
            "Calo": 350,
            "Protein": 12.0,
            "ChatBeo": 24.0,
            "Carbohydrate": 20.0,
            "Vitamin": "Vitamin K, Sắt"
        },
        "CongThuc": {
            "HuongDan": "1. Băm nhỏ thịt ba chỉ, ngâm mềm và băm mộc nhĩ, miến, cà rốt. Trộn đều cùng trứng gà và gia vị.\n2. Trải bánh tráng, cho nhân vào giữa và cuộn tròn lại.\n3. Chiên chả giò ngập dầu trên lửa vừa đến khi chín vàng giòn.\n4. Vớt ra để ráo dầu.\n5. Ăn kèm bún, rau sống và nước mắm chua ngọt.",
            "ThoiGianNau": 45,
            "KhauPhan": 5,
            "NguyenLieu": [
                {"TenNguyenLieu": "Thịt heo băm", "SoLuong": "200g"},
                {"TenNguyenLieu": "Miến, mộc nhĩ", "SoLuong": "30g"},
                {"TenNguyenLieu": "Bánh tráng cuốn", "SoLuong": "10 cái"},
                {"TenNguyenLieu": "Cà rốt, hành lá", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Bún Riêu Cua",
        "MoTa": "Bún riêu có màu đỏ gạch của cà chua và hạt điều, hương vị thanh tao, chua dịu. Điểm nhấn là phần riêu cua đồng xốp mềm, đậu hũ chiên béo ngậy và chút mắm tôm nồng nàn.",
        "PhanLoai": "Món nước",
        "DinhDuong": {
            "Calo": 450,
            "Protein": 22.0,
            "ChatBeo": 18.0,
            "Carbohydrate": 55.0,
            "Vitamin": "Canxi, Photpho, Vitamin C"
        },
        "CongThuc": {
            "HuongDan": "1. Cua đồng giã nhuyễn, lọc lấy nước cốt. Nấu sôi để rêu cua nổi lên, vớt rêu ra làm chả.\n2. Xào cà chua với dầu hạt điều tạo màu đỏ đẹp, đổ vào nồi nước dùng.\n3. Nêm mắm tôm, me chua (hoặc dấm bỗng) vào nước dùng.\n4. Trụng bún cho vào tô, xếp đậu hũ chiên, riêu cua, huyết heo.\n5. Chan nước dùng, thêm chút hành lá và ăn cùng rau chuối bào.",
            "ThoiGianNau": 60,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Cua đồng xay", "SoLuong": "200g"},
                {"TenNguyenLieu": "Bún tươi", "SoLuong": "200g"},
                {"TenNguyenLieu": "Cà chua, đậu hũ", "SoLuong": "Vừa đủ"},
                {"TenNguyenLieu": "Mắm tôm", "SoLuong": "1 muỗng"}
            ]
        }
    },
    {
        "TenMonAn": "Bánh Cuốn",
        "MoTa": "Món ăn sáng nhẹ nhàng tinh tế. Lớp vỏ bánh làm từ bột gạo tráng mỏng trên nồi hơi nước, bên trong cuộn mộc nhĩ thịt băm. Rắc hành phi giòn lên trên, chấm nước mắm chua ngọt.",
        "PhanLoai": "Ăn nhẹ",
        "DinhDuong": {
            "Calo": 320,
            "Protein": 12.0,
            "ChatBeo": 10.0,
            "Carbohydrate": 45.0,
            "Vitamin": "Sắt, Vitamin B"
        },
        "CongThuc": {
            "HuongDan": "1. Pha bột gạo và bột năng với nước lọc, để nghỉ.\n2. Xào thịt băm với mộc nhĩ băm, hành tím nêm gia vị.\n3. Tráng một lớp bột mỏng lên nồi hơi nước, đậy nắp 30s.\n4. Lấy bánh ra, cho nhân vào cuộn lại.\n5. Xếp lên đĩa, rắc hành phi, cắt chả lụa ăn kèm nước mắm nhạt.",
            "ThoiGianNau": 40,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bột gạo, bột năng", "SoLuong": "100g"},
                {"TenNguyenLieu": "Thịt heo băm", "SoLuong": "50g"},
                {"TenNguyenLieu": "Mộc nhĩ", "SoLuong": "10g"},
                {"TenNguyenLieu": "Hành phi, chả lụa", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Mì Quảng",
        "MoTa": "Đặc sản Quảng Nam với sợi mì dày màu vàng nghệ. Nước dùng nấu rất đậm đà nhưng chỉ chan săm sắp mặt mì. Ăn kèm thịt gà, tôm, thịt heo, trứng cút, bánh tráng nướng và rau sống.",
        "PhanLoai": "Món nước",
        "DinhDuong": {
            "Calo": 520,
            "Protein": 28.0,
            "ChatBeo": 20.0,
            "Carbohydrate": 60.0,
            "Vitamin": "Curcumin, Vitamin A, Protein"
        },
        "CongThuc": {
            "HuongDan": "1. Giã củ nén (hành tăm), ướp với gà, tôm, thịt ba chỉ và bột nghệ.\n2. Xào săn các nguyên liệu rồi đổ nước xương vào ninh mềm làm nước lèo đặc biệt.\n3. Xếp sợi mì Quảng vào tô, luộc trứng cút bỏ vào.\n4. Chan một ít nước lèo (ít hơn phở).\n5. Rắc đậu phộng rang, bẻ bánh tráng nướng lên trên.",
            "ThoiGianNau": 60,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Sợi mì Quảng", "SoLuong": "150g"},
                {"TenNguyenLieu": "Thịt gà, tôm, heo", "SoLuong": "150g"},
                {"TenNguyenLieu": "Trứng cút, đậu phộng rang", "SoLuong": "Vừa đủ"},
                {"TenNguyenLieu": "Bánh tráng nướng", "SoLuong": "1 miếng"}
            ]
        }
    },
    {
        "TenMonAn": "Hủ Tiếu Nam Vang",
        "MoTa": "Hủ tiếu Nam Vang có nguồn gốc từ Campuchia nhưng đã được người Sài Gòn biến tấu. Nước dùng ngọt thanh từ xương ống và khô mực, tôm khô. Topping cực đa dạng: tôm, thịt nạc, gan, tim, trứng cút.",
        "PhanLoai": "Món nước",
        "DinhDuong": {
            "Calo": 480,
            "Protein": 25.0,
            "ChatBeo": 14.0,
            "Carbohydrate": 62.0,
            "Vitamin": "Sắt, Canxi, Vitamin B12"
        },
        "CongThuc": {
            "HuongDan": "1. Hầm xương ống heo, tôm khô, mực khô, củ cải trắng để lấy nước dùng ngọt thanh.\n2. Luộc tôm, thịt nạc, gan heo thái lát mỏng.\n3. Phi tỏi băm ngập dầu thật giòn thơm.\n4. Trụng hủ tiếu, xà lách, giá hẹ cho vào tô.\n5. Xếp topping lên, chan nước dùng, rắc hành lá và tỏi phi.",
            "ThoiGianNau": 120,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Hủ tiếu dai", "SoLuong": "100g"},
                {"TenNguyenLieu": "Xương ống heo", "SoLuong": "200g"},
                {"TenNguyenLieu": "Tôm, gan, thịt băm", "SoLuong": "100g"},
                {"TenNguyenLieu": "Tỏi phi, hẹ", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Bún Thịt Nướng",
        "MoTa": "Món bún trộn thanh mát, dễ ăn với bún tươi rưới mắm chua ngọt, ăn kèm thịt heo nướng sả thơm lừng, mỡ hành, đậu phộng rang và vô số rau sống.",
        "PhanLoai": "Bún trộn",
        "DinhDuong": {
            "Calo": 500,
            "Protein": 22.0,
            "ChatBeo": 20.0,
            "Carbohydrate": 55.0,
            "Vitamin": "Chất xơ, Vitamin C"
        },
        "CongThuc": {
            "HuongDan": "1. Ướp thịt heo thái lát với sả, hành tỏi băm, mật ong, nước mắm, dầu mè.\n2. Nướng thịt trên than hoa cho chín vàng.\n3. Thái nhỏ xà lách, dưa leo, giá đỗ, rau thơm để dưới đáy tô.\n4. Để bún lên trên rau, gắp thịt nướng cho lên trên.\n5. Rắc đậu phộng rang, mỡ hành và chan nước mắm chua ngọt khi ăn.",
            "ThoiGianNau": 45,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bún tươi", "SoLuong": "200g"},
                {"TenNguyenLieu": "Thịt heo nạc dăm", "SoLuong": "150g"},
                {"TenNguyenLieu": "Đậu phộng rang, mỡ hành", "SoLuong": "Vừa đủ"},
                {"TenNguyenLieu": "Rau sống, nước mắm chua ngọt", "SoLuong": "1 phần"}
            ]
        }
    },
    {
        "TenMonAn": "Cá Kho Tộ",
        "MoTa": "Món ăn gia đình đặc trưng của Nam Bộ. Cá lóc hoặc cá trê được kho keo lại trong niêu đất với nước mắm, tiêu, đường caramen, vị mặn ngọt đậm đà, cực kỳ đưa cơm.",
        "PhanLoai": "Món mặn",
        "DinhDuong": {
            "Calo": 350,
            "Protein": 24.0,
            "ChatBeo": 18.0,
            "Carbohydrate": 15.0,
            "Vitamin": "Omega-3, Vitamin D, I-ốt"
        },
        "CongThuc": {
            "HuongDan": "1. Làm sạch cá, ướp với nước mắm, muối, đường, tiêu, hành tím trong 30 phút.\n2. Thắng đường trên tộ đất để làm nước màu (caramen).\n3. Cho cá vào tộ, lật đều hai mặt cho thấm màu.\n4. Thêm nước dừa tươi (hoặc nước ấm) sấp mặt cá, đun riu riu lửa.\n5. Đun đến khi nước kho kẹo lại, rắc thêm tiêu đen và hành lá.",
            "ThoiGianNau": 45,
            "KhauPhan": 2,
            "NguyenLieu": [
                {"TenNguyenLieu": "Cá lóc (hoặc cá hú)", "SoLuong": "300g"},
                {"TenNguyenLieu": "Nước mắm, đường, tiêu", "SoLuong": "Vừa đủ"},
                {"TenNguyenLieu": "Hành lá, ớt", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Canh Chua Cá Lóc",
        "MoTa": "Món canh giải nhiệt cực tốt của miền Tây, kết hợp hoàn hảo giữa vị chua của me, ngọt của dứa, cà chua, thơm của ngò gai và béo mềm của cá lóc.",
        "PhanLoai": "Canh",
        "DinhDuong": {
            "Calo": 200,
            "Protein": 15.0,
            "ChatBeo": 5.0,
            "Carbohydrate": 25.0,
            "Vitamin": "Vitamin C mạnh, Kali, Chất xơ"
        },
        "CongThuc": {
            "HuongDan": "1. Cá lóc làm sạch, chiên sơ cho săn mặt thịt (tùy ý).\n2. Dầm me chua lấy nước cốt.\n3. Đun sôi nước, cho cá và cốt me vào.\n4. Lần lượt thả dứa, cà chua, đậu bắp, bạc hà (dọc mùng), giá đỗ vào nấu chín tới.\n5. Nêm nếm mắm, đường, tắt bếp và rắc ngò gai, rau ngổ, tỏi phi lên.",
            "ThoiGianNau": 30,
            "KhauPhan": 2,
            "NguyenLieu": [
                {"TenNguyenLieu": "Cá lóc", "SoLuong": "200g"},
                {"TenNguyenLieu": "Me vắt, dứa, cà chua", "SoLuong": "1 phần"},
                {"TenNguyenLieu": "Đậu bắp, bạc hà, giá", "SoLuong": "100g"},
                {"TenNguyenLieu": "Ngò gai, rau ngổ", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Bò Lúc Lắc",
        "MoTa": "Thịt bò thăn cắt khối vuông, áp chảo nhanh tay trên lửa lớn với tỏi, hành tây, ớt chuông. Thịt mềm mọng nước bên trong, đậm đà bên ngoài, ăn kèm khoai tây chiên.",
        "PhanLoai": "Món mặn",
        "DinhDuong": {
            "Calo": 480,
            "Protein": 32.0,
            "ChatBeo": 26.0,
            "Carbohydrate": 20.0,
            "Vitamin": "Sắt, Kẽm, Vitamin C"
        },
        "CongThuc": {
            "HuongDan": "1. Thịt bò cắt cục vuông (lúc lắc), ướp tỏi, tiêu, nước tương, xíu dầu hào và dầu ăn.\n2. Cắt hành tây, ớt chuông thành miếng vuông.\n3. Phi tỏi thơm, cho thịt bò vào áp chảo nhanh tay trên lửa thật lớn (khoảng 2-3 phút).\n4. Cho hành tây, ớt chuông vào xào chung nhanh tay, nêm lại.\n5. Trút ra đĩa, xếp lên rau xà lách, cà chua, ăn kèm khoai tây chiên.",
            "ThoiGianNau": 15,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Thịt bò thăn", "SoLuong": "200g"},
                {"TenNguyenLieu": "Ớt chuông, hành tây", "SoLuong": "100g"},
                {"TenNguyenLieu": "Tỏi, xà lách, khoai tây", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Xôi Xéo",
        "MoTa": "Thức quà sáng đặc trưng của Hà Nội. Xôi nếp có màu vàng óng ả rực rỡ, dẻo thơm, ăn cùng đậu xanh giã nhuyễn và ngập tràn hành phi giòn rụm rưới mỡ gà.",
        "PhanLoai": "Ăn sáng",
        "DinhDuong": {
            "Calo": 450,
            "Protein": 10.0,
            "ChatBeo": 15.0,
            "Carbohydrate": 75.0,
            "Vitamin": "Vitamin B, Năng lượng"
        },
        "CongThuc": {
            "HuongDan": "1. Gạo nếp ngâm với nước cốt nghệ tươi 6 tiếng để có màu vàng, sau đó mang đi đồ xôi.\n2. Đậu xanh ngâm mềm, hấp chín, giã thật nhuyễn rồi nắm thành khối tròn chặt tay.\n3. Phi hành khô với mỡ gà cho thật giòn thơm.\n4. Đơm xôi ra lá sen/lá chuối, dùng dao thái mỏng nắm đậu xanh rắc lên trên xôi.\n5. Rưới mỡ hành phi giòn lên cùng và thưởng thức.",
            "ThoiGianNau": 60,
            "KhauPhan": 1,
            "NguyenLieu": [
                {"TenNguyenLieu": "Gạo nếp nương", "SoLuong": "150g"},
                {"TenNguyenLieu": "Đậu xanh bóc vỏ", "SoLuong": "50g"},
                {"TenNguyenLieu": "Hành tím phi, mỡ gà", "SoLuong": "Vừa đủ"},
                {"TenNguyenLieu": "Bột nghệ", "SoLuong": "1 muỗng nhỏ"}
            ]
        }
    },
    {
        "TenMonAn": "Bánh Khọt",
        "MoTa": "Loại bánh đổ trong khuôn nhỏ nhắn, lớp vỏ bột gạo chiên vàng giòn rụm bên dưới, mềm dẻo bên trên, với nhân tôm đỏ au ở giữa, rắc thêm xíu mỡ hành, tôm cháy.",
        "PhanLoai": "Ăn chơi",
        "DinhDuong": {
            "Calo": 380,
            "Protein": 14.0,
            "ChatBeo": 18.0,
            "Carbohydrate": 35.0,
            "Vitamin": "Canxi, Photpho, Vitamin B"
        },
        "CongThuc": {
            "HuongDan": "1. Pha bột gạo với nước cốt dừa lỏng, chút bột nghệ và hành lá.\n2. Làm nóng khuôn bánh khọt bằng gang, thoa dầu ăn vào từng ô.\n3. Đổ bột vào ngập 2/3 ô khuôn.\n4. Khi bột hơi chín, thả 1 con tôm luộc bóc vỏ vào giữa mỗi ô.\n5. Đậy nắp chờ bánh chín giòn cạnh. Lấy ra cuộn xà lách chấm nước mắm.",
            "ThoiGianNau": 30,
            "KhauPhan": 6,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bột bánh khọt", "SoLuong": "100g"},
                {"TenNguyenLieu": "Tôm đất", "SoLuong": "15 con"},
                {"TenNguyenLieu": "Nước cốt dừa", "SoLuong": "50ml"},
                {"TenNguyenLieu": "Rau xà lách, nước mắm", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Chè Trôi Nước",
        "MoTa": "Món tráng miệng ấm bụng. Từng viên chè làm từ bột nếp trắng ngần dẻo quánh, nhân đậu xanh bùi béo, ngụp lặn trong nước đường gừng thơm phức, rắc thêm mè rang.",
        "PhanLoai": "Tráng miệng",
        "DinhDuong": {
            "Calo": 310,
            "Protein": 5.0,
            "ChatBeo": 6.0,
            "Carbohydrate": 60.0,
            "Vitamin": "Carbonhydrate, Tinh bột"
        },
        "CongThuc": {
            "HuongDan": "1. Đậu xanh hấp chín, sên với đường và xíu muối làm nhân, vo viên tròn nhỏ.\n2. Bột nếp nhào với nước ấm cho dẻo, bọc kín nhân đậu xanh.\n3. Nấu sôi nồi nước đường phèn hoặc đường thốt nốt với vài lát gừng đập dập.\n4. Luộc viên chè nếp trong nước sôi đến khi nổi lên, vớt ra cho vào nồi nước đường đun nhỏ lửa 10 phút.\n5. Múc ra bát, chan cốt dừa, rắc mè rang.",
            "ThoiGianNau": 60,
            "KhauPhan": 2,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bột nếp", "SoLuong": "100g"},
                {"TenNguyenLieu": "Đậu xanh", "SoLuong": "50g"},
                {"TenNguyenLieu": "Đường phèn, gừng", "SoLuong": "Vừa đủ"},
                {"TenNguyenLieu": "Nước cốt dừa, mè rang", "SoLuong": "Vừa đủ"}
            ]
        }
    },
    {
        "TenMonAn": "Phở Cuốn",
        "MoTa": "Phiên bản thanh mát của phở. Bánh phở nguyên tảng (chưa thái sợi) cuộn chặt thịt bò xào lăn thơm phức cùng rau xà lách, mùi ta, chấm nước mắm chua ngọt.",
        "PhanLoai": "Ăn nhẹ",
        "DinhDuong": {
            "Calo": 280,
            "Protein": 18.0,
            "ChatBeo": 8.0,
            "Carbohydrate": 35.0,
            "Vitamin": "Kẽm, Sắt, Vitamin A"
        },
        "CongThuc": {
            "HuongDan": "1. Thịt bò thái mỏng ướp tỏi, hạt nêm, tiêu.\n2. Xào nhanh thịt bò trên lửa lớn cho chín mềm, không xào lâu sẽ dai.\n3. Trải tảng bánh phở vuông ra thớt.\n4. Đặt xà lách, rau thơm và thịt bò xào lên, cuộn chặt tay như gỏi cuốn.\n5. Pha nước mắm chua ngọt với tỏi ớt băm để chấm.",
            "ThoiGianNau": 20,
            "KhauPhan": 5,
            "NguyenLieu": [
                {"TenNguyenLieu": "Bánh phở tấm", "SoLuong": "10 tấm"},
                {"TenNguyenLieu": "Thịt bò thăn", "SoLuong": "150g"},
                {"TenNguyenLieu": "Xà lách, rau mùi", "SoLuong": "1 mớ"},
                {"TenNguyenLieu": "Tỏi, ớt, nước mắm", "SoLuong": "Vừa đủ"}
            ]
        }
    }
]

def seed_database():
    print(f"Bắt đầu thêm {len(foods)} món ăn vào Database...")
    success_count = 0
    
    # Lấy connection để kiểm tra xem đã có chưa
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for food in foods:
        # Kiểm tra xem món này đã tồn tại chưa
        cursor.execute("SELECT MaMonAn FROM MonAn WHERE TenMonAn = %s", (food["TenMonAn"],))
        exists = cursor.fetchone()
        
        if exists:
            print(f"⏭️ Bỏ qua '{food['TenMonAn']}' - Đã có trong DB.")
        else:
            if insert_food_full(food):
                print(f"✅ Thêm thành công '{food['TenMonAn']}'.")
                success_count += 1
            else:
                print(f"❌ Thất bại khi thêm '{food['TenMonAn']}'.")
                
    conn.close()
    print(f"\n🎉 Hoàn thành! Đã thêm mới {success_count} món ăn vào hệ thống.")

if __name__ == "__main__":
    seed_database()
