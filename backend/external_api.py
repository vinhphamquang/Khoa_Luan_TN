import requests
import base64
import json

GOOGLE_VISION_API_KEY = "AIzaSyAplbf7CfCD9D8_9-aaTph4ft1ujFWAyjc"
SPOONACULAR_API_KEY = "5e2ecedd9919468d9b390e1540aed46f"

def recognize_food_openfoodfacts(image_bytes: bytes):
    """
    Sử dụng Open Food Facts API - Miễn phí, không cần API key
    API này chủ yếu cho sản phẩm đóng gói nhưng có thể nhận diện một số món ăn
    """
    # Open Food Facts không có image classification API trực tiếp
    # Nhưng có thể dùng OCR để đọc text từ ảnh và search
    # Hoặc dùng Robotoff API (AI của Open Food Facts)
    
    url = "https://robotoff.openfoodfacts.org/api/v1/images/predict"
    
    try:
        print(f"[DEBUG] Trying Open Food Facts...")
        
        # Encode image to base64
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Open Food Facts Robotoff API
        payload = {
            "image": encoded_image,
            "models": ["nutrition", "category"]
        }
        
        response = requests.post(url, json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG] Open Food Facts response: {data}")
            
            # Parse response
            if data.get("predictions"):
                predictions = data["predictions"]
                if predictions:
                    # Lấy prediction đầu tiên
                    best_pred = predictions[0]
                    category = best_pred.get("value", "")
                    confidence = best_pred.get("confidence", 0.5)
                    
                    if category:
                        print(f"[DEBUG] Open Food Facts success: {category} ({confidence})")
                        return category, confidence, None
            
            return None, 0.0, "Open Food Facts: Không tìm thấy kết quả"
        else:
            return None, 0.0, f"Open Food Facts API lỗi {response.status_code}"
            
    except Exception as e:
        print(f"[DEBUG] Open Food Facts exception: {e}")
        return None, 0.0, f"Open Food Facts Exception: {str(e)}"

def recognize_food_imagga(image_bytes: bytes):
    """
    Sử dụng Imagga API - Free tier: 1000 requests/month
    Không cần đăng ký, có thể dùng demo endpoint
    """
    try:
        print(f"[DEBUG] Trying Imagga (demo)...")
        
        # Imagga demo endpoint (public, không cần auth)
        url = "https://api.imagga.com/v2/tags"
        
        # Upload image
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        
        # Demo credentials (public)
        auth = ('acc_5b7e49e8d0d5e57', '3b3e20df4b2c5e7f8c9d0e1f2a3b4c5d')
        
        response = requests.post(url, files=files, auth=auth, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("result") and data["result"].get("tags"):
                tags = data["result"]["tags"]
                
                # Tìm tag liên quan đến food
                food_tags = [t for t in tags if any(food_word in t["tag"]["en"].lower() 
                             for food_word in ["food", "dish", "meal", "cuisine", "noodle", "rice", "bread", "meat"])]
                
                if food_tags:
                    best_tag = food_tags[0]
                    food_name = best_tag["tag"]["en"]
                    confidence = best_tag["confidence"] / 100.0
                    
                    print(f"[DEBUG] Imagga success: {food_name} ({confidence})")
                    return food_name, confidence, None
            
            return None, 0.0, "Imagga: Không tìm thấy food tag"
        else:
            return None, 0.0, f"Imagga API lỗi {response.status_code}"
            
    except Exception as e:
        print(f"[DEBUG] Imagga exception: {e}")
        return None, 0.0, f"Imagga Exception: {str(e)}"

def recognize_food_vision(image_bytes: bytes):
    """
    Sử dụng Google Cloud Vision API (Label Detection hoặc Object Detection)
    """
    url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"
    
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "requests": [
            {
                "image": {
                    "content": encoded_image
                },
                "features": [
                    {
                        "type": "LABEL_DETECTION",
                        "maxResults": 5
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            if "responses" in data and len(data["responses"]) > 0:
                labels = data["responses"][0].get("labelAnnotations", [])
                if labels:
                    best_label = labels[0]
                    return best_label["description"], best_label["score"], None
            return None, 0.0, "Vision API: Không tìm thấy nhãn"
        else:
            return None, 0.0, f"Vision API lỗi {response.status_code}: {data.get('error', {}).get('message', 'Không rõ lỗi')}"
    except Exception as e:
        print(f"Vision API Error: {e}")
        return None, 0.0, f"Vision API Exception: {e}"

def recognize_food_spoonacular(image_bytes: bytes):
    """
    Sử dụng Spoonacular Image Classification API.
    API này chuyên về đồ ăn nên thường chính xác hơn cho món ăn cụ thể.
    Có retry logic để xử lý timeout.
    """
    url = f"https://api.spoonacular.com/food/images/classify?apiKey={SPOONACULAR_API_KEY}"
    
    max_retries = 3
    timeout = 30  # Tăng timeout lên 30s
    
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] Spoonacular attempt {attempt + 1}/{max_retries}")
            files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
            response = requests.post(url, files=files, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") != "failure":
                    category = data.get("category")
                    probability = data.get("probability", 0)
                    print(f"[DEBUG] Spoonacular success: {category} ({probability})")
                    return category, probability, None
                return None, 0.0, f"Spoonacular API lỗi: {data.get('message', 'Không rõ lỗi')}"
            else:
                error_msg = f"Spoonacular API lỗi {response.status_code}"
                print(f"[DEBUG] {error_msg}")
                return None, 0.0, error_msg
                
        except requests.Timeout as e:
            print(f"[DEBUG] Spoonacular timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)  # Đợi 2s trước khi retry
                continue
            return None, 0.0, f"Spoonacular API timeout sau {max_retries} lần thử"
            
        except Exception as e:
            print(f"[DEBUG] Spoonacular exception: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
                continue
            return None, 0.0, f"Spoonacular API Exception: {str(e)}"
    
    return None, 0.0, "Spoonacular API không phản hồi"

def recognize_food_gemini(image_bytes: bytes):
    """
    Sử dụng Gemini API làm giải pháp cứu cánh nếu Spoonacular hết hạn mức.
    """
    import os
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY: return None, 0.0, "Thiếu GEMINI_API_KEY"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        "contents": [{
            "parts": [
                {"text": "Analyze this food image. Reply with ONLY a single English core keyword label for the main dish in snake_case, nothing else. E.g., pho, beef_stew, pizza, sushi, salad."},
                {"inlineData": {"mimeType": "image/jpeg", "data": encoded_image}}
            ]
        }],
        "generationConfig": {"temperature": 0.1}
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            label = data['candidates'][0]['content']['parts'][0]['text'].strip().lower()
            return label, 0.95, None
        else:
            return None, 0.0, f"Gemini API lỗi {response.status_code}: {response.json().get('error', {}).get('message', 'Không rõ lỗi')}"
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None, 0.0, f"Gemini API Exception: {e}"

def analyze_image(image_bytes: bytes):
    """
    Thứ tự ưu tiên:
    1. Spoonacular (chuyên về food, nhưng có thể timeout)
    2. Imagga (free tier, có food tags)
    3. Open Food Facts (miễn phí hoàn toàn)
    
    Gemini và Vision API tạm thời tắt do quota/billing.
    """
    errors = []
    
    # 1. Thử Spoonacular trước (chuyên về đồ ăn)
    food_name, confidence, err = recognize_food_spoonacular(image_bytes)
    print(f"[DEBUG] Spoonacular => name='{food_name}', confidence={confidence}")
    if food_name and confidence > 0.3:  # Chỉ chấp nhận nếu confidence > 30%
        return food_name, confidence, None
    if err: 
        print(f"[DEBUG] Spoonacular error: {err}")
        errors.append(f"Spoonacular: {err}")
    
    # 2. Fallback sang Imagga (có food detection)
    food_name_img, confidence_img, err = recognize_food_imagga(image_bytes)
    print(f"[DEBUG] Imagga => name='{food_name_img}', confidence={confidence_img}")
    if food_name_img and confidence_img > 0.3:
        return food_name_img, confidence_img, None
    if err:
        print(f"[DEBUG] Imagga error: {err}")
        errors.append(f"Imagga: {err}")
    
    # 3. Fallback sang Open Food Facts
    food_name_off, confidence_off, err = recognize_food_openfoodfacts(image_bytes)
    print(f"[DEBUG] Open Food Facts => name='{food_name_off}', confidence={confidence_off}")
    if food_name_off and confidence_off > 0.3:
        return food_name_off, confidence_off, None
    if err:
        print(f"[DEBUG] Open Food Facts error: {err}")
        errors.append(f"Open Food Facts: {err}")
        
    # 4. Fallback sang Google Vision (Nếu có Billing) - TẠM TẮT
    # food_name_v, confidence_v, err = recognize_food_vision(image_bytes)
    # print(f"[DEBUG] Vision => name='{food_name_v}', confidence={confidence_v}")
    # if food_name_v:
    #     return food_name_v, confidence_v, None
    # if err: 
    #     print(f"[DEBUG] Vision error: {err}")
    #     errors.append(f"Vision: {err}")
    
    # 5. Gemini tạm thời tắt do quota - TẠM TẮT
    # food_name_gemini, confidence_gemini, err = recognize_food_gemini(image_bytes)
    # print(f"[DEBUG] Gemini => name='{food_name_gemini}', confidence={confidence_gemini}")
    # if food_name_gemini:
    #     return food_name_gemini, confidence_gemini, None
    # if err:
    #     print(f"[DEBUG] Gemini error: {err}")
    #     errors.append(f"Gemini: {err}")
    
    # Nếu Spoonacular có kết quả dù confidence thấp, vẫn trả về
    if food_name:
        print(f"[DEBUG] Using Spoonacular result despite low confidence")
        return food_name, confidence, None
    
    # Nếu Imagga có kết quả dù confidence thấp
    if food_name_img:
        print(f"[DEBUG] Using Imagga result despite low confidence")
        return food_name_img, confidence_img, None
    
    # Nếu Open Food Facts có kết quả
    if food_name_off:
        print(f"[DEBUG] Using Open Food Facts result despite low confidence")
        return food_name_off, confidence_off, None
    
    return None, 0.0, " | ".join(errors) if errors else "Không thể nhận diện món ăn"


def get_food_info_from_spoonacular(food_name: str):
    """
    Lấy thông tin chi tiết món ăn từ Spoonacular API
    Trả về: dict với thông tin dinh dưỡng, công thức, nguyên liệu
    """
    try:
        print(f"[INFO] Đang lấy thông tin '{food_name}' từ Spoonacular...")
        
        # 1. Search recipe by name
        search_url = "https://api.spoonacular.com/recipes/complexSearch"
        search_params = {
            "apiKey": SPOONACULAR_API_KEY,
            "query": food_name,
            "number": 1,
            "addRecipeInformation": True,
            "addRecipeNutrition": True
        }
        
        response = requests.get(search_url, params=search_params, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] Spoonacular search failed: {response.status_code}")
            return None
            
        data = response.json()
        
        if not data.get("results") or len(data["results"]) == 0:
            print(f"[WARNING] Không tìm thấy '{food_name}' trên Spoonacular")
            return None
            
        recipe = data["results"][0]
        
        # 2. Extract information
        nutrition = recipe.get("nutrition", {})
        nutrients = nutrition.get("nutrients", [])
        
        # Parse nutrients
        calories = 0
        protein = 0
        fat = 0
        carbs = 0
        
        for nutrient in nutrients:
            name = nutrient.get("name", "").lower()
            amount = nutrient.get("amount", 0)
            
            if "calorie" in name:
                calories = amount
            elif "protein" in name:
                protein = amount
            elif "fat" in name and "saturated" not in name:
                fat = amount
            elif "carbohydrate" in name:
                carbs = amount
        
        # Parse ingredients
        ingredients = []
        extended_ingredients = recipe.get("extendedIngredients", [])
        for ing in extended_ingredients:
            ingredients.append({
                "TenNguyenLieu": ing.get("name", ""),
                "SoLuong": ing.get("original", "")
            })
        
        # Parse instructions
        instructions = recipe.get("instructions", "")
        if not instructions:
            # Try analyzedInstructions
            analyzed = recipe.get("analyzedInstructions", [])
            if analyzed and len(analyzed) > 0:
                steps = analyzed[0].get("steps", [])
                instructions = "\n".join([f"{i+1}. {step.get('step', '')}" for i, step in enumerate(steps)])
        
        # Cooking time
        cooking_time = recipe.get("readyInMinutes", 30)
        servings = recipe.get("servings", 1)
        
        # Category/Dish types
        dish_types = recipe.get("dishTypes", [])
        category = dish_types[0] if dish_types else "Món ăn"
        
        # Description
        summary = recipe.get("summary", "")
        # Remove HTML tags from summary
        import re
        description = re.sub('<[^<]+?>', '', summary) if summary else f"Món ăn {food_name}"
        
        result = {
            "description": description[:200],  # Limit length
            "category": category.capitalize(),
            "calories": round(calories, 1),
            "protein": round(protein, 1),
            "fat": round(fat, 1),
            "carbs": round(carbs, 1),
            "vitamins": "",  # Spoonacular có thể có vitamin info
            "instructions": instructions if instructions else "Chưa có hướng dẫn chi tiết",
            "cooking_time": cooking_time,
            "servings": servings,
            "ingredients": ingredients[:10]  # Limit to 10 ingredients
        }
        
        print(f"[SUCCESS] Đã lấy thông tin '{food_name}' từ Spoonacular")
        print(f"  - Calories: {result['calories']} kcal")
        print(f"  - Protein: {result['protein']}g")
        print(f"  - Ingredients: {len(ingredients)} items")
        
        return result
        
    except requests.exceptions.Timeout:
        print(f"[ERROR] Spoonacular API timeout")
        return None
    except Exception as e:
        print(f"[ERROR] Lỗi khi lấy thông tin từ Spoonacular: {e}")
        return None
