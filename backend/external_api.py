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
        
        if "responses" in data and len(data["responses"]) > 0:
            labels = data["responses"][0].get("labelAnnotations", [])
            if labels:
                # Trả về nhãn có độ tin cậy cao nhất
                best_label = labels[0]
                return best_label["description"], best_label["score"]
    except Exception as e:
        print(f"Vision API Error: {e}")
        
    return None, 0.0

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
                return data.get("category"), data.get("probability")
    except Exception as e:
        print(f"Spoonacular API Error: {e}")
        
    return None, 0.0

def analyze_image(image_bytes: bytes):
    """
    Ưu tiên dùng Spoonacular vì chuyên trang ẩm thực. 
    Nếu không được sẽ fallback sang Google Cloud Vision.
    """
    food_name, confidence = recognize_food_spoonacular(image_bytes)
    
    if food_name and confidence > 0.4:
        return food_name, confidence
        
    # Fallback to Vision
    return recognize_food_vision(image_bytes)
