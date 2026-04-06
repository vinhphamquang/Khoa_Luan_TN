import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
import io
import os
from .model import get_model

# Cấu hình tĩnh
NUM_CLASSES = 10 
MODEL_PATH = "ml_core/weights/best_model.pth"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_inference_model():
    model = get_model(num_classes=NUM_CLASSES, pretrained=False)
    
    # Nạp tệp weights nếu user đã copy vào folder `ml_core/weights/`
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        print(f"[INFO] Load weights thành công từ {MODEL_PATH}")
    else:
        print(f"[CẢNH BÁO] Không tìm thấy file {MODEL_PATH}. Trả về random predictions!")
        
    model.to(device)
    model.eval()
    return model

# Khởi tạo model sẵn trong bộ nhớ RAM lúc FastAPI chạy để tăng tốc inference
resnet_model = load_inference_model()

# Transform chuẩn của torchvision models pre-trained on ImageNet
img_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def predict_image(image_bytes: bytes) -> tuple[int, float]:
    """
    Hàm xử lý Request: Nhận luồng byte ảnh, chuyển qua Model và xuất ra nhãn dụ đoán.
    Returns:
        class_index (int)
        confidence (float)
    """
    try:
        # Load Pillow Image và Convert sang RGB tránh ảnh PNG 4- channels
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Tiền xử lý & thêm batch dimension (B, C, H, W)
        tensor = img_transform(img).unsqueeze(0).to(device)
        
        # Chạy qua model mà không cần track gradients
        with torch.no_grad():
            outputs = resnet_model(tensor)
            probabilities = F.softmax(outputs, dim=1)[0] # Mảng xác suất (0-1)
            
            conf, predicted_class = torch.max(probabilities, 0)
            
        return predicted_class.item(), conf.item()
    except Exception as e:
        print(f"[ERROR prediction]: {e}")
        return -1, 0.0
