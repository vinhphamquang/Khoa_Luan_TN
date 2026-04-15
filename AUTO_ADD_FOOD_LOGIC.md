# Logic Tự Động Thêm Món Ăn Vào Database

## 🎯 Mục Đích

Khi người dùng upload ảnh món ăn, hệ thống sẽ:
1. ✅ Nhận diện tên món ăn từ hình ảnh (tiếng Anh)
2. ✅ Dịch tên món ăn sang tiếng Việt
3. ✅ Tìm kiếm trong database với nhiều variants (tiếng Việt, tiếng Anh, case variations)
4. ✅ Nếu không có, tự động lấy thông tin từ external API và thêm vào database
5. ✅ Trả về thông tin đầy đủ bằng tiếng Việt cho người dùng

## 📊 Workflow

```
User Upload Image
       ↓
[1] Nhận diện món ăn (analyze_image)
    → Spoonacular Image Recognition
    → Imagga (fallback)
    → Open Food Facts (fallback)
       ↓
    Food Name English (e.g., "Pho", "Spring Rolls", "Pizza")
       ↓
[2] Dịch sang tiếng Việt (translate_food_name)
    → "Pho" → "Phở"
    → "Spring Rolls" → "Gỏi Cuốn"
    → "Pizza" → "Pizza" (giữ nguyên nếu không có bản dịch)
       ↓
[3] Tạo search variants (get_search_variants)
    → ["Phở", "Pho", "phở", "PHỞ", "pho"]
       ↓
[4] Tìm trong Database (search_food_by_name)
    → Thử từng variant cho đến khi tìm thấy
       ↓
    ┌─────────────┐
    │ Có trong DB?│
    └─────────────┘
         ↓
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    │         ↓
    │    [5] Lấy thông tin từ Spoonacular API (bằng tên tiếng Anh)
    │         (get_food_info_from_spoonacular)
    │         ↓
    │    [6] Thêm vào Database (insert_food_full) - Lưu tên tiếng Việt
    │         ↓
    │    [7] Tìm lại trong Database
    │         │
    └─────────┘
         ↓
[8] Trả về thông tin cho User (tiếng Việt)
```

## 🔧 Implementation

### 1. Nhận Diện Món Ăn (analyze_image)

**File:** `backend/external_api.py`

```python
def analyze_image(image_bytes: bytes):
    # Thử Spoonacular → Imagga → Open Food Facts
    # Trả về: (food_name_english, confidence, error_msg)
```

**Kết quả:**
- `food_name_english`: Tên món ăn bằng tiếng Anh (e.g., "Pho", "Spring Rolls", "Pizza")
- `confidence`: Độ tin cậy (0.0 - 1.0)
- `error_msg`: Thông báo lỗi nếu có

### 2. Dịch Sang Tiếng Việt (translate_food_name)

**File:** `backend/food_translator.py`

```python
def translate_food_name(english_name: str) -> str:
    # Tìm trong dictionary ánh xạ Anh-Việt
    # Trả về: Tên tiếng Việt hoặc giữ nguyên nếu không tìm thấy
```

**Dictionary:**
- 100+ món ăn phổ biến
- Case-insensitive matching
- Partial matching support

**Ví dụ:**
- "pho" → "Phở"
- "spring rolls" → "Gỏi Cuốn"
- "banh mi" → "Bánh Mì"
- "pizza" → "Pizza" (giữ nguyên)

### 3. Tạo Search Variants (get_search_variants)

**File:** `backend/food_translator.py`

```python
def get_search_variants(food_name: str) -> list:
    # Tạo danh sách các biến thể để tìm kiếm
    # Trả về: List các variants
```

**Variants bao gồm:**
- Tên gốc
- Bản dịch (nếu có)
- Lowercase
- Uppercase
- Capitalize

**Ví dụ:**
- "Pho" → ["Pho", "Phở", "pho", "PHO", "phở", "PHỞ"]

### 4. Tìm Trong Database (search_food_by_name)

**File:** `backend/db_queries.py`

```python
def search_food_by_name(food_name: str):
    # 1. Lấy search variants
    # 2. Thử từng variant với LIKE query
    # 3. Tìm trong TenMonAn, PhanLoai, MoTa
    # Trả về: dict với thông tin đầy đủ hoặc None
```

**Tìm kiếm:**
- Multiple variants (tiếng Việt + tiếng Anh)
- Case-insensitive
- Fuzzy matching (LIKE %food_name%)
- Chỉ lấy món chưa bị xóa (IsDeleted = 0)

### 5. Lấy Thông Tin Từ Spoonacular (get_food_info_from_spoonacular)

**File:** `backend/external_api.py`

```python
def get_food_info_from_spoonacular(food_name: str):
    # 1. Search recipe by name (sử dụng tên tiếng Anh)
    # 2. Extract nutrition info
    # 3. Extract ingredients
    # 4. Extract cooking instructions
    # Trả về: dict với thông tin đầy đủ
```

**Thông tin lấy được:**
- `description`: Mô tả món ăn
- `category`: Phân loại (e.g., "Main course", "Dessert")
- `calories`: Calo (kcal)
- `protein`: Protein (g)
- `fat`: Chất béo (g)
- `carbs`: Carbohydrate (g)
- `vitamins`: Vitamin (nếu có)
- `instructions`: Hướng dẫn nấu
- `cooking_time`: Thời gian nấu (phút)
- `servings`: Khẩu phần
- `ingredients`: Danh sách nguyên liệu

### 6. Thêm Vào Database (insert_food_full)

**File:** `backend/db_queries.py`

```python
def insert_food_full(data: dict):
    # Insert vào 4 bảng:
    # - MonAn (lưu tên tiếng Việt)
    # - DinhDuong
    # - CongThuc
    # - NguyenLieu + ChiTietNguyenLieu
```

**Lưu ý:**
- `TenMonAn`: Lưu tên tiếng Việt
- `MoTa`: Thêm tên tiếng Anh vào cuối để tìm kiếm sau này
- Transaction để đảm bảo tính toàn vẹn

### 7. Predict Endpoint

**File:** `backend/app.py`

```python
@app.route("/predict", methods=["POST"])
def predict():
    # 1. Nhận diện món ăn từ hình ảnh (tiếng Anh)
    food_name_english, confidence, error = analyze_image(image_bytes)
    
    # 2. Dịch sang tiếng Việt
    food_name_vietnamese = translate_food_name(food_name_english)
    
    # 3. Tìm trong database (thử cả tiếng Việt và tiếng Anh)
    food_data = search_food_by_name(food_name_vietnamese)
    if not food_data:
        food_data = search_food_by_name(food_name_english)
    
    # 4. Nếu không có, lấy từ API và thêm vào (lưu tên tiếng Việt)
    if not food_data:
        external_data = get_food_info_from_spoonacular(food_name_english)
        if external_data:
            food_to_insert = {
                "TenMonAn": food_name_vietnamese,  # Lưu tên tiếng Việt
                "MoTa": external_data["description"] + f" [English: {food_name_english}]",
                ...
            }
            insert_food_full(food_to_insert)
            food_data = search_food_by_name(food_name_vietnamese)
    
    # 5. Trả về kết quả (tiếng Việt)
    response_data["predicted_class_name"] = food_name_vietnamese
    return jsonify(response_data)
```

## 📝 Ví Dụ

### Scenario 1: Món Ăn Việt Nam Đã Có Trong Database

```
User uploads: pho.jpg
  ↓
Nhận diện: "Pho" (confidence: 0.95)
  ↓
Dịch: "Pho" → "Phở"
  ↓
Search variants: ["Phở", "Pho", "phở", "PHỞ", "pho"]
  ↓
Tìm trong DB: ✅ Tìm thấy với variant "Phở" (ID: 1)
  ↓
Trả về: Thông tin Phở từ database
Message: "✅ Đã tìm thấy thông tin món 'Phở' trong cơ sở dữ liệu"
```

### Scenario 2: Món Ăn Quốc Tế Chưa Có Trong Database

```
User uploads: pizza.jpg
  ↓
Nhận diện: "Pizza" (confidence: 0.92)
  ↓
Dịch: "Pizza" → "Pizza" (giữ nguyên, không có bản dịch)
  ↓
Search variants: ["Pizza", "pizza", "PIZZA"]
  ↓
Tìm trong DB: ❌ Không tìm thấy
  ↓
Lấy từ Spoonacular API (sử dụng "Pizza"):
  - Calories: 266 kcal
  - Protein: 11g
  - Fat: 10g
  - Carbs: 33g
  - Ingredients: 8 items
  ↓
Thêm vào Database:
  - TenMonAn: "Pizza" (tiếng Việt = tiếng Anh)
  - MoTa: "Italian dish... [English: Pizza]"
  ↓
Thêm thành công: ✅ (ID: 65)
  ↓
Tìm lại trong DB: ✅ Tìm thấy (ID: 65)
  ↓
Trả về: Thông tin Pizza từ database
Message: "✨ Món ăn 'Pizza' vừa được thêm vào cơ sở dữ liệu!"
```

### Scenario 3: Món Ăn Việt Nam Có Tên Tiếng Anh

```
User uploads: spring_rolls.jpg
  ↓
Nhận diện: "Spring Rolls" (confidence: 0.88)
  ↓
Dịch: "Spring Rolls" → "Gỏi Cuốn"
  ↓
Search variants: ["Gỏi Cuốn", "Spring Rolls", "gỏi cuốn", "spring rolls"]
  ↓
Tìm trong DB: ✅ Tìm thấy với variant "Gỏi Cuốn" (ID: 15)
  ↓
Trả về: Thông tin Gỏi Cuốn từ database
Message: "✅ Đã tìm thấy thông tin món 'Gỏi Cuốn' trong cơ sở dữ liệu"
```

### Scenario 4: API Không Tìm Thấy Thông Tin

```
User uploads: unknown_food.jpg
  ↓
Nhận diện: "Unknown Dish" (confidence: 0.65)
  ↓
Tìm trong DB: ❌ Không tìm thấy
  ↓
Lấy từ Spoonacular API: ❌ Không tìm thấy
  ↓
Trả về: Chỉ có tên món ăn, không có thông tin chi tiết
Message: "⚠️ Nhận diện được 'Unknown Dish' nhưng chưa có đầy đủ thông tin"
```

## 🎨 User Experience

### Thông Báo Cho User

#### Món Có Sẵn
```
✅ Đã tìm thấy thông tin món 'Phở' trong cơ sở dữ liệu
```

#### Món Mới Thêm
```
✨ Món ăn 'Pizza' vừa được thêm vào cơ sở dữ liệu!
```

#### Không Có Thông Tin
```
⚠️ Nhận diện được 'Unknown Dish' nhưng chưa có đầy đủ thông tin. Vui lòng thử lại sau.
```

## 🔍 Logging

### Console Output

```
[INFO] Tìm kiếm 'Pizza' trong database...
[INFO] Không tìm thấy 'Pizza' trong database. Đang lấy thông tin từ external API...
[INFO] Đang lấy thông tin 'Pizza' từ Spoonacular...
[SUCCESS] Đã lấy thông tin 'Pizza' từ Spoonacular
  - Calories: 266.0 kcal
  - Protein: 11.0g
  - Ingredients: 8 items
[INFO] Đã lấy thông tin từ API. Đang thêm vào database...
[SUCCESS] Đã thêm 'Pizza' vào database!
```

## ⚡ Performance

### Caching Strategy
- Database lookup: ~10ms
- Spoonacular API call: ~2-5s
- Database insert: ~50ms

### Optimization
- Tìm trong database trước (nhanh)
- Chỉ gọi API khi cần thiết
- Cache kết quả trong database
- Lần sau không cần gọi API nữa

## 🔐 Error Handling

### API Timeout
```python
try:
    external_data = get_food_info_from_spoonacular(food_name)
except requests.exceptions.Timeout:
    # Không làm gián đoạn flow
    # Trả về kết quả với thông tin hạn chế
```

### Database Error
```python
try:
    insert_food_full(food_to_insert)
except Exception as e:
    print(f"[ERROR] Không thể thêm vào database: {e}")
    # Vẫn trả về kết quả nhận diện
```

## 📊 Database Growth

### Tự Động Mở Rộng
- Ban đầu: 64 món ăn
- Sau 100 users: ~100-150 món
- Sau 1000 users: ~300-500 món
- Database tự động mở rộng theo nhu cầu người dùng

### Quản Lý
- Admin có thể xem món mới thêm
- Admin có thể chỉnh sửa thông tin
- Admin có thể xóa món không phù hợp

## ✅ Benefits

1. **Tự Động Hóa**: Không cần admin thêm món thủ công
2. **Mở Rộng**: Database tự động mở rộng
3. **Chính Xác**: Thông tin từ Spoonacular API đáng tin cậy
4. **Hiệu Quả**: Chỉ gọi API khi cần thiết
5. **User-Friendly**: Người dùng luôn nhận được thông tin

## 🚀 Future Improvements

- [ ] Cache API responses để giảm số lần gọi
- [ ] Sử dụng multiple API sources (fallback)
- [ ] AI review để cải thiện chất lượng dữ liệu
- [ ] User feedback để điều chỉnh thông tin
- [ ] Batch processing cho nhiều món cùng lúc

---

**Cập nhật:** 14/04/2026  
**Trạng thái:** ✅ Đã triển khai


## 🌐 Vietnamese Translation System

### Dictionary Coverage
- 100+ món ăn phổ biến
- Món ăn Việt Nam: Phở, Bánh Mì, Bún Chả, Gỏi Cuốn, Chả Giò, v.v.
- Món ăn quốc tế: Pizza, Sushi, Burger (giữ nguyên nếu không có bản dịch)

### Translation Logic
1. Case-insensitive matching
2. Partial matching support (e.g., "spring rolls" matches "fresh spring rolls")
3. Fallback to original name if no translation found

### Search Strategy
- Generate multiple variants (Vietnamese + English + case variations)
- Try each variant until match found
- Search in TenMonAn, PhanLoai, and MoTa fields
- Example: "Pho" → ["Pho", "Phở", "pho", "PHO", "phở", "PHỞ"]

### Translation Examples

```
[TRANSLATE] 'Pho' → 'Phở'
[TRANSLATE] 'Spring Rolls' → 'Gỏi Cuốn' (partial match)
[TRANSLATE] 'Banh Mi' → 'Bánh Mì'
[TRANSLATE] 'Bun Cha' → 'Bún Chả'
[TRANSLATE] 'Pizza' → 'Pizza' (giữ nguyên, không tìm thấy bản dịch)
[TRANSLATE] 'Sushi' → 'Sushi' (giữ nguyên)
```

## ✅ Benefits of Vietnamese Translation

1. **User-Friendly**: Người dùng Việt Nam thấy tên món ăn quen thuộc
2. **Accurate Search**: Tìm kiếm linh hoạt với nhiều variants
3. **Database Consistency**: Lưu tên tiếng Việt trong database
4. **Bilingual Support**: Hỗ trợ cả tiếng Việt và tiếng Anh
5. **Extensible**: Dễ dàng thêm món ăn mới vào dictionary

## 🚀 Future Improvements

- [ ] Mở rộng dictionary với nhiều món ăn hơn (200+)
- [ ] Hỗ trợ nhiều ngôn ngữ (Anh, Việt, Trung, Nhật, Hàn)
- [ ] Machine learning để tự động dịch tên món ăn mới
- [ ] User feedback để cải thiện bản dịch
- [ ] Fuzzy matching algorithm tốt hơn (Levenshtein distance)
- [ ] Cache translation results để tăng performance

---

**Cập nhật:** 15/04/2026  
**Trạng thái:** ✅ Đã hoàn thành tích hợp Vietnamese Translation System
