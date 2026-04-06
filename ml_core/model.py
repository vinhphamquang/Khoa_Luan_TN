import torch
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights

def get_model(num_classes: int = 10, pretrained: bool = True):
    """
    Khởi tạo mô hình nhận diện (dùng ResNet18).
    Khi huấn luyện (train), để pretrained=True để Load weights dùng Transfer Learning.
    Khi sử dụng (predict), chỉ cần khởi tạo base và nạp state_dict.
    """
    weights = ResNet18_Weights.DEFAULT if pretrained else None
    model = resnet18(weights=weights)
    
    # Đổi lớp Linear cuối cùng để ra đúng số classes của project
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    
    return model
