from ultralytics import YOLO
import torch

# 1. RTX 4060'ı kullan
device = 0 if torch.cuda.is_available() else 'cpu'

# 2. Modeli yükle (Colab'da eğittiğin best.pt'yi Drive'dan indirip buraya koyabilirsin)
# Veya kendi bilgisayarında eğittiğin yeni seg modelini kullan
model = YOLO('best.pt') 

# 3. Videoyu işle (Kendi bilgisayarında takılma yapmayacaktır)
results = model.predict(
    source='videolar/surus1.mp4', 
    save=True, 
    conf=0.4,       # Güven eşiği
    imgsz=640,      # Boyut
    device=device,  # 4060 GPU kullanımı
    stream=True     # ÖNEMLİ: Videoyu parça parça işleyerek belleği şişirmez
)

# Stream=True kullandığımız için bir döngü ile kareleri geçiyoruz
for r in results:
    pass 

print("Video başarıyla tamamlandı ve 'runs/detect/predict' klasörüne kaydedildi.")