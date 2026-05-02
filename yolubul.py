import cv2
import numpy as np
from ultralytics import YOLO

# ==========================================
# 1. AYARLAR VE MODEL YÜKLEME
# ==========================================
# Eğittiğin modeli yüklüyoruz
model = YOLO('best.pt') 

# Videoyu Aç (Webcam için '0' yazabilirsin)
# Not: Jetson Orin Nano üzerinde Raspberry Pi Module V2 (IMX219) kameraya 
# geçtiğimizde buradaki girişi GStreamer pipeline formatına dönüştüreceğiz.
video_yolu = 'videolar/surus1.mp4' 
cap = cv2.VideoCapture(video_yolu)

# Araba düz giderken tolere edilecek piksel boşluğu (Hassasiyet)
sapma_esigi = 40 

# ==========================================
# 2. ANA DÖNGÜ (VİDEO İŞLEME)
# ==========================================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Video tamamlandı veya görüntü alınamıyor.")
        break

    height, width, _ = frame.shape
    ekran_merkez_x = width // 2

    # Tahmin Al (Hatalı eşleşmeleri engellemek için conf=0.6 kullanıyoruz)
    results = model.predict(frame, conf=0.6, verbose=False)

    komut = "SERIT ARANIYOR..."
    renk = (255, 255, 255)

    if results[0].masks is not None:
        masks = results[0].masks.xy
        class_ids = results[0].boxes.cls 
        
        # Ekranda bulunan tüm sınıfların isimlerini listeye çevir
        bulunan_siniflar = [model.names[int(cls)] for cls in class_ids]

        # ---------------------------------------------------------
        # KURAL 1: ANA HEDEF "solserit"
        # ---------------------------------------------------------
        if 'solserit' in bulunan_siniflar:
            hedef_indeks = bulunan_siniflar.index('solserit')
            mask_noktalari = np.int32(masks[hedef_indeks])
            
            M = cv2.moments(mask_noktalari)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                error = cx - ekran_merkez_x

                # ---------------------------------------------------------
                # KURAL 2: GÜVENLİK DUVARI "ortaduz"
                # ---------------------------------------------------------
                if 'ortaduz' in bulunan_siniflar:
                    duvar_indeks = bulunan_siniflar.index('ortaduz')
                    duvar_mask = np.int32(masks[duvar_indeks])
                    
                    # Ortadüz maskesinin en sol noktasını bul
                    ortaduz_en_sol_x = np.min(duvar_mask[:, 0])
                    
                    # Eğer duvara 50 pikselden fazla yaklaşıldıysa
                    if (ortaduz_en_sol_x - ekran_merkez_x) < 50:
                        komut = "ACIL SOLA KIR (Duvara Yaklasildi!)"
                        renk = (0, 0, 255)
                        error = -100 # Direksiyonu sola kırmaya zorla
                    else:
                        komut = f"SOL SERIT TAKIP (Sapma: {error})"
                        renk = (0, 255, 0)
                else:
                    komut = f"SOL SERIT TAKIP (Sapma: {error})"
                    renk = (0, 255, 0)

                # Çizim İşlemleri (Sol şerit: Yeşil)
                cv2.polylines(frame, [mask_noktalari], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1) 
                cv2.line(frame, (ekran_merkez_x, height - 50), (cx, cy), (0, 255, 255), 2) 

        # ---------------------------------------------------------
        # KURAL 3: YEDEK PLAN "solcizgi"
        # ---------------------------------------------------------
        elif 'solcizgi' in bulunan_siniflar:
            cizgi_indeks = bulunan_siniflar.index('solcizgi')
            mask_noktalari = np.int32(masks[cizgi_indeks])
            
            M = cv2.moments(mask_noktalari)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                
                # Çizginin üstünden gitmek yerine 100 piksel sağını hedefle
                hedef_x = cx + 100 
                error = hedef_x - ekran_merkez_x
                
                komut = f"SOL CIZGI ILE IDARE EDILIYOR (Sapma: {error})"
                renk = (0, 255, 255) # Sarı uyarı
                
                # Çizim İşlemleri (Sol çizgi: Pembe)
                cv2.polylines(frame, [mask_noktalari], isClosed=True, color=(255, 0, 255), thickness=2)
                cv2.circle(frame, (hedef_x, int(height/2)), 8, (0, 0, 255), -1) 

        else:
            komut = "HEDEF BULUNAMADI - YAVASLA"
            renk = (0, 0, 255)

    # ==========================================
    # 3. BİLGİLERİ EKRANA YAZDIRMA
    # ==========================================
    # Robotun (Ekranın) merkez noktası
    cv2.circle(frame, (ekran_merkez_x, height - 50), 8, (255, 0, 0), -1)
    
    # Komut çıktısı
    cv2.putText(frame, komut, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, renk, 2)

    cv2.imshow('Otonom Surus Karar Mekanizmasi', frame)

    # 'q' tuşu ile çıkış
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()