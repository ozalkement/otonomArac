import cv2
import numpy as np
from ultralytics import YOLO

# Eğittiğin modeli yüklüyoruz
model = YOLO('best.pt') 
video_yolu = 'videolar/surus1.mp4' 
cap = cv2.VideoCapture(video_yolu)

sapma_esigi = 40 

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Video tamamlandı veya görüntü alınamıyor.")
        break

    height, width, _ = frame.shape
    ekran_merkez_x = width // 2

    results = model.predict(frame, conf=0.6, verbose=False)

    komut = "SERIT ARANIYOR..."
    renk = (255, 255, 255)
    error = 0 # Varsayılan error değeri

    if results[0].masks is not None:
        masks = results[0].masks.xy
        class_ids = results[0].boxes.cls 
        
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

                # Güvenlik Duvarı Kontrolü (ortaduz)
                if 'ortaduz' in bulunan_siniflar:
                    duvar_indeks = bulunan_siniflar.index('ortaduz')
                    duvar_mask = np.int32(masks[duvar_indeks])
                    ortaduz_en_sol_x = np.min(duvar_mask[:, 0])
                    
                    if (ortaduz_en_sol_x - ekran_merkez_x) < 50:
                        komut = "ACIL SOLA KIR (Duvara Yaklasildi!)"
                        renk = (0, 0, 255)
                        error = -150 
                    else:
                        komut = f"SOL SERIT TAKIP (Sapma: {error})"
                        renk = (0, 255, 0)
                else:
                    komut = f"SOL SERIT TAKIP (Sapma: {error})"
                    renk = (0, 255, 0)

                cv2.polylines(frame, [mask_noktalari], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1) 
                cv2.line(frame, (ekran_merkez_x, height - 50), (cx, cy), (0, 255, 255), 2) 

        # ---------------------------------------------------------
        # KURAL 2: YEDEK PLAN "solcizgi"
        # ---------------------------------------------------------
        elif 'solcizgi' in bulunan_siniflar:
            cizgi_indeks = bulunan_siniflar.index('solcizgi')
            mask_noktalari = np.int32(masks[cizgi_indeks])
            
            M = cv2.moments(mask_noktalari)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                
                hedef_x = cx + 100 
                error = hedef_x - ekran_merkez_x
                
                komut = f"SOL CIZGI KULLANILIYOR (Sapma: {error})"
                renk = (0, 255, 255) 
                
                cv2.polylines(frame, [mask_noktalari], isClosed=True, color=(255, 0, 255), thickness=2)
                cv2.circle(frame, (hedef_x, int(height/2)), 8, (0, 0, 255), -1) 

        # ---------------------------------------------------------
        # KURAL 3: VİRAJ/KAYIP DURUMU - "sagserit" İLE HAYATTA KAL
        # ---------------------------------------------------------
        elif 'sagserit' in bulunan_siniflar:
            sag_indeks = bulunan_siniflar.index('sagserit')
            mask_noktalari = np.int32(masks[sag_indeks])
            
            M = cv2.moments(mask_noktalari)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # ÖNEMLİ: Sağ şeridin merkezinden (cx) gitmek tehlikeli olabilir 
                # (ortadüz duvarına çarpabilirsin). Bu yüzden sağ şeridin 
                # biraz daha SOLUNU (örneğin 150 piksel solunu) hedef alıyoruz.
                hedef_x = cx - 150 
                error = hedef_x - ekran_merkez_x

                komut = f"VİRAJ! SAG SERIT ILE DONULUYOR (Sapma: {error})"
                renk = (255, 165, 0) # Turuncu Uyarı
                
                # Görselleştirme (Sağ şerit: Mavi)
                cv2.polylines(frame, [mask_noktalari], isClosed=True, color=(255, 0, 0), thickness=2)
                # Kırmızı nokta gerçek sağ şerit merkezi, mavi nokta bizim güvenli hedefimiz
                cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1) 
                cv2.circle(frame, (hedef_x, cy), 10, (255, 0, 0), -1)
                cv2.line(frame, (ekran_merkez_x, height - 50), (hedef_x, cy), (0, 255, 255), 2) 

        # ---------------------------------------------------------
        # KURAL 4: SON ÇARE - "sagcizgi"
        # ---------------------------------------------------------
        elif 'sagcizgi' in bulunan_siniflar:
            sag_cizgi_indeks = bulunan_siniflar.index('sagcizgi')
            mask_noktalari = np.int32(masks[sag_cizgi_indeks])
            
            M = cv2.moments(mask_noktalari)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                
                # Sağ çizginin oldukça soluna (örneğin 250 piksel soluna) kaç
                hedef_x = cx - 250 
                error = hedef_x - ekran_merkez_x
                
                komut = f"KRITIK VİRAJ: SAG CIZGI (Sapma: {error})"
                renk = (0, 0, 255) # Kırmızı Uyarı
                
                cv2.polylines(frame, [mask_noktalari], isClosed=True, color=(255, 255, 0), thickness=2)
                cv2.circle(frame, (hedef_x, int(height/2)), 8, (0, 0, 255), -1)

        else:
            komut = "HEDEF BULUNAMADI - YAVASLA"
            renk = (0, 0, 255)
            error = 0

    # Bilgileri Ekrana Yazdır
    cv2.circle(frame, (ekran_merkez_x, height - 50), 8, (255, 0, 0), -1)
    cv2.putText(frame, komut, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, renk, 2)

    cv2.imshow('Otonom Surus - Viraj Destekli', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()