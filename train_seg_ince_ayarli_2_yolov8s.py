from ultralytics import YOLO
import torch

if __name__ == '__main__':

    from roboflow import Roboflow

    # GPU
    device = 0 if torch.cuda.is_available() else 'cpu'
    print(f"GPU: {torch.cuda.get_device_name(0)}")

    # Dataset
    rf = Roboflow(api_key="o5ML4Hpm8zMMCy9eZAJL")
    project = rf.workspace("roadfinder1").project("otnm4_copy_3")
    version = project.version(1)
    dataset = version.download("yolov8")

    # Model
    model = YOLO('yolov8s-seg.pt')

    # Eğitim
    model.train(
        data=f"{dataset.location}/data.yaml",

        epochs=120,
        patience=25,

        imgsz=640,
        batch=32,          # 🔥 artırdık (4060 için)

        optimizer="AdamW",
        lr0=0.002,
        lrf=0.01,
        weight_decay=0.0005,
        warmup_epochs=3,
        cos_lr=True,

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

        cache='disk',       # 🔥 hız
        workers=6,         # 🔥 çok önemli

        freeze=10,

        device=0,
        amp=True,
        half=True,

        project='Otonom_Sonuclar',
        name='yolov8_seg_final_yolov8s'
    )