// ============================================
// Arduino Nano + ZK-BM1 Motor Sürücü Kontrolü
// 2x DC Motor - Diferansiyel Sürüş (Tank Drive)
// ZK-BM1 Pinleri: IN1, IN2, IN3, IN4, GND
// ============================================

// --- Motor A (Sol Motor) Pin Tanımları ---
#define IN1 5 // Sol Motor Yön/Hız (PWM destekli pin)
#define IN2 6 // Sol Motor Yön/Hız (PWM destekli pin)

// --- Motor B (Sağ Motor) Pin Tanımları ---
#define IN3 9  // Sağ Motor Yön/Hız (PWM destekli pin)
#define IN4 10 // Sağ Motor Yön/Hız (PWM destekli pin)

// --- Hız Ayarı ---
// Motorlar 150 RPM. 50 RPM için ~1/3 güç = 85/255
const int MOTOR_HIZ = 85;

// --- Süre (milisaniye) ---
const unsigned long SURE = 5000; // 5 saniye

void setup() {
  // Motor pinlerini çıkış olarak ayarla
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Başlangıçta motorları durdur
  motorDur();

  // Seri haberleşme (debug için)
  Serial.begin(9600);
  Serial.println("Motor kontrol basliyor...");

  // 1 saniye bekle
  delay(1000);
}

void loop() {
  // ========== 1) İLERİ - 5 saniye ==========
  Serial.println(">> ILERI");
  ileriGit();
  delay(SURE);
  motorDur();
  delay(500);

  // ========== 2) GERİ - 5 saniye ==========
  Serial.println(">> GERI");
  geriGit();
  delay(SURE);
  motorDur();
  delay(500);

  // ========== 3) SAĞA DÖN - 5 saniye ==========
  Serial.println(">> SAGA DON");
  sagaDon();
  delay(SURE);
  motorDur();
  delay(500);

  // ========== 4) SOLA DÖN - 5 saniye ==========
  Serial.println(">> SOLA DON");
  solaDon();
  delay(SURE);
  motorDur();
  delay(500);

  Serial.println("--- Dongu tamamlandi, tekrar basliyor... ---");
  delay(2000);
}

// ============================================
//           MOTOR KONTROL FONKSİYONLARI
// ============================================

// İleri git: Her iki motor ileri döner
void ileriGit() {
  // Sol Motor İleri
  analogWrite(IN1, MOTOR_HIZ);
  analogWrite(IN2, 0);

  // Sağ Motor İleri
  analogWrite(IN3, MOTOR_HIZ);
  analogWrite(IN4, 0);
}

// Geri git: Her iki motor geri döner
void geriGit() {
  // Sol Motor Geri
  analogWrite(IN1, 0);
  analogWrite(IN2, MOTOR_HIZ);

  // Sağ Motor Geri
  analogWrite(IN3, 0);
  analogWrite(IN4, MOTOR_HIZ);
}

// Sağa dön: Sol motor ileri, Sağ motor geri
void sagaDon() {
  // Sol Motor İleri
  analogWrite(IN1, MOTOR_HIZ);
  analogWrite(IN2, 0);

  // Sağ Motor Geri
  analogWrite(IN3, 0);
  analogWrite(IN4, MOTOR_HIZ);
}

// Sola dön: Sağ motor ileri, Sol motor geri
void solaDon() {
  // Sol Motor Geri
  analogWrite(IN1, 0);
  analogWrite(IN2, MOTOR_HIZ);

  // Sağ Motor İleri
  analogWrite(IN3, MOTOR_HIZ);
  analogWrite(IN4, 0);
}

// Motorları durdur
void motorDur() {
  analogWrite(IN1, 0);
  analogWrite(IN2, 0);
  analogWrite(IN3, 0);
  analogWrite(IN4, 0);
}
