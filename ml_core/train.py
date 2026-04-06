"""
Script này dành để user (sinh viên KLTN) tự upload dataset và chạy huấn luyện mô hình.
Hướng dẫn:
1. Chuẩn bị tập ảnh: Tổ chức Dataset của bạn dưới dạng `ImageFolder`
   - dataset/
     - train/
       - pho/ (ảnh các bát phở)
       - banh_mi/ (ảnh các ổ bánh mì)
     - val/
       - pho/
       - banh_mi/
2. Sửa lại NUM_CLASSES theo số lượng nhãn.
3. Chạy lệnh: `python -m ml_core.train` ở thư mục root.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from .model import get_model
import os

NUM_CLASSES = 10
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001
DATASET_DIR = "dataset" # Sửa path tại đây

def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Bắt đầu Training sử dụng hardware: {device}")
    
    # 1. Image transformations (Data Augmentation cho Train, Crop Center cho Val)
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    train_dir = os.path.join(DATASET_DIR, "train")
    if not os.path.exists(train_dir):
        print(f"\n[LỖI] Không tìm thấy thư mục {train_dir}!")
        print("Vui lòng tự tải Dataset đồ ăn (VD: Food-101) và cấu trúc lại thư mục như hướng dẫn.")
        return

    # 2. Load dataset
    image_datasets = {x: datasets.ImageFolder(os.path.join(DATASET_DIR, x), data_transforms[x]) for x in ['train', 'val']}
    dataloaders = {x: DataLoader(image_datasets[x], batch_size=BATCH_SIZE, shuffle=True) for x in ['train', 'val']}
    dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
    class_names = image_datasets['train'].classes
    
    print("Các nhãn class đã tìm thấy:", class_names)
    print("---------------------------------")

    # 3. Khởi tạo mô hình
    model = get_model(num_classes=len(class_names), pretrained=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 4. Training Loop
    best_acc = 0.0
    for epoch in range(EPOCHS):
        print(f"Epoch {epoch}/{EPOCHS - 1}")
        print('-' * 10)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]
            print(f"{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

            # Lưu mô hình khi có độ chính xác Validate tăng lên
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                os.makedirs("ml_core/weights", exist_ok=True)
                torch.save(model.state_dict(), "ml_core/weights/best_model.pth")
                print(">>> Đã lưu lại weights mô hình tốt nhất!")
        print()
    print(f"Hoàn thành! Độ chính xác cao nhất (Val): {best_acc:4f}")

if __name__ == "__main__":
    train()
