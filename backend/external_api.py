import requests
import base64
import json

GOOGLE_VISION_API_KEY = "AIzaSyAplbf7CfCD9D8_9-aaTph4ft1ujFWAyjc"
SPOONACULAR_API_KEY = "5e2ecedd9919468d9b390e1540aed46f"

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
    """
    url = f"https://api.spoonacular.com/food/images/classify?apiKey={SPOONACULAR_API_KEY}"
    
    try:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = requests.post(url, files=files, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") != "failure":
                return data.get("category"), data.get("probability"), None
            return None, 0.0, f"Spoonacular API lỗi: {data.get('message', 'Không rõ lỗi')}"
        else:
            return None, 0.0, f"Spoonacular API lỗi {response.status_code}: {response.text}"
    except Exception as e:
        print(f"Spoonacular API Error: {e}")
        return None, 0.0, f"Spoonacular API Exception: {e}"

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
    Ưu tiên dùng Spoonacular vì chuyên trang ẩm thực. 
    Nếu không được sẽ fallback sang Google Cloud Vision, và cuối cùng là Gemini.
    """
    errors = []
    # 1. Thử Spoonacular trước (chuyên về đồ ăn)
    food_name, confidence, err = recognize_food_spoonacular(image_bytes)
    print(f"[DEBUG] Spoonacular => name='{food_name}', confidence={confidence}, err={err}")
    if food_name and confidence > 0:
        return food_name, confidence, None
    if err: errors.append(err)
        
    # 2. Fallback sang Gemini
    food_name_gemini, confidence_gemini, err = recognize_food_gemini(image_bytes)
    print(f"[DEBUG] Gemini Vision => name='{food_name_gemini}', confidence={confidence_gemini}, err={err}")
    if food_name_gemini:
        return food_name_gemini, confidence_gemini, None
    if err: errors.append(err)
        
    # 3. Fallback sang Google Vision (Nếu có Billing)
    food_name_v, confidence_v, err = recognize_food_vision(image_bytes)
    print(f"[DEBUG] Vision => name='{food_name_v}', confidence={confidence_v}, err={err}")
    if food_name_v:
        return food_name_v, confidence_v, None
    if err: errors.append(err)
    
    return None, 0.0, " | ".join(errors)
