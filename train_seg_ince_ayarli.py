from ultralytics import YOLO
from roboflow import Roboflow
import torch

# 1. Donanım
device = 0 if torch.cuda.is_available() else 'cpu'
print(f"Eğitim Başlıyor! Kullanılan Cihaz: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

# 2. Dataset (Roboflow)
rf = Roboflow(api_key="o5ML4Hpm8zMMCy9eZAJL")
project = rf.workspace("roadfinder1").project("otnm3")
version = project.version(2)
dataset = version.download("yolov8")

# 3. Model (Segmentation)
model = YOLO('yolov8n-seg.pt')

# 4. Eğitim
if __name__ == '__main__':
    model.train(
        data=f"{dataset.location}/data.yaml",

        # 🔥 EĞİTİM STRATEJİSİ
        epochs=120,
        patience=25,

        # 📐 Görüntü
        imgsz=640,
        batch=16,

        # ⚙️ OPTIMIZER
        optimizer="AdamW",
        lr0=0.002,
        lrf=0.01,
        weight_decay=0.0005,
        warmup_epochs=3,
        cos_lr=True,

        # 🔥 AUGMENTATION (EN KRİTİK)
        mosaic=1.0,
        mixup=0.2,
        copy_paste=0.1,

        degrees=5,
        translate=0.1,
        scale=0.5,
        shear=2,
        perspective=0.0005,

        fliplr=0.5,
        flipud=0.0,

        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,

        close_mosaic=10,

        # ⚡ Performans
        cache=True,
        workers=4,

        # 🧠 Küçük dataset için kritik
        freeze=10,

        # 💾 Çıktı
        project='Otonom_Sonuclar',
        name='yolov8_seg_4060_opt',

        device=device
    )