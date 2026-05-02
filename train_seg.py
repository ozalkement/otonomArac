from ultralytics import YOLO
from roboflow import Roboflow
import torch

# 1. Donanım Hazırlığı
device = 0 if torch.cuda.is_available() else 'cpu'
print(f"Eğitim Başlıyor! Kullanılan Cihaz: {torch.cuda.get_device_name(0)}")

# 2. Veriyi Roboflow'dan Çek (Segmentasyon formatında)



rf = Roboflow(api_key="o5ML4Hpm8zMMCy9eZAJL")
project = rf.workspace("roadfinder1").project("otnm3")
version = project.version(2)
dataset = version.download("yolov8")

# 3. Model Seçimi: MUTLAKA -seg uzantılı olanı kullanıyoruz
# Instance Segmentation için doğru model budur.
model = YOLO('yolov8n-seg.pt')

# 4. Eğitimi Başlat
if __name__ == '__main__':
    model.train(
        data=f"{dataset.location}/data.yaml",
        epochs=100,      # 4060 ile 100 epoch çok hızlı biter
        imgsz=640,
        device=device,
        workers=4,       # İşlemcin güçlüyse 8 de yapabilirsin
        batch=16,        # Kartın belleği (8GB) için 16 idealdir
        project='Otonom_Sonuclar',
        name='yolov8_seg_4060'
    )