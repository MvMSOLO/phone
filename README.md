# AxtarGet Screen Mirroring V1.4 📱💻

AxtarGet Screen Mirroring V1.4 - Bu Android smartfon ekranini Wi-Fi yoki USB (ADB) orqali kompyuter brauzerida real vaqt rejimida past kechikish (low latency) bilan ko'rsatish va masofadan to'liq boshqarish imkonini beruvchi professional loyiha.

---

## 🌟 Asosiy Imkoniyatlar va Xususiyatlar

1. **Terminal / CLI UI Interfeysi (AxtarGet Style):**
   - Matrix / Hacker stilidagi yashil va oq rangli interfeys (Rich kutubxonasi).
   - "AxtarGet Screen Mirroring V1.4" ASCII banner.
   - Real vaqt rejimida ishlovchi server va ADB status paneli.
   - Interaktiv Terminal Buyruqlari:
     - `ip` - Barcha lokal va Wi-Fi IP manzillarini ko'rsatish.
     - `-qr` - Smartfon orqali tezkor ulanish uchun terminalda QR-kod chiqarish.
     - `-clear` - Terminal ekranini tozalash.
     - `-exit` - Serverni xavfsiz to'xtatish va dasturdan chiqish.

2. **Yuqori Unumdorlik va Past Kechikish (Backend):**
   - **FastAPI va WebSockets:** Kadrlar ketma-ketligini va boshqaruv buyruqlarini minimal kechikish bilan uzatish.
   - **ADB Boshqaruvi:** `adb exec-out screencap -p` va `adb shell input` orqali sichqoncha va klaviatura amallarini bajarish.
   - **Fallback Stream:** Telefoni ulangan bo'lmagan holatda grafik interaktiv kutish ekrani.

3. **Veb Interfeys va Boshqaruv (Frontend):**
   - Dynamic HTML5 Canvas video pleer.
   - **Sichqoncha bilan boshqaruv:**
     - Bosish (Click) -> Telefon ekranidagi tegish (Tap).
     - Surish (Drag) -> Ekranni surish / skroll qilish (Swipe).
   - **Navigatsiya tugmalari:** Orqaga (Back), Bosh sahifa (Home), So'nggi ilovalar (Recents), Yoqish/O'chirish (Power), Ovoz (+/-).
   - **Matn yuborish:** Kompyuter klaviaturasida yozilgan matnni telefondagi faol maydonga yuborish.

---

## 🛠️ O'rnatish va Ishga Tushirish Qo'llanmasi

### 1. Smartfonda USB Debugging (Sozlash) ni Yoqish

1. Smartfoningizda **Sozlamalar (Settings)** -> **Telefon haqida (About Phone)** bo'limiga kiring.
2. **Build number** tugmasini 7 marta uzluksiz bosing ("Siz endi dasturchisiz" xabari chiqquncha).
3. **Dasturchi opsiyalari (Developer Options)** bo'limiga kiring.
4. **USB Debugging (USB orqali sozlash)** funksiyasini yoqing.
5. Smartfonni USB kabel orqali kompyuterga ulang va ekranda "Allow USB Debugging?" so'rovi chiqsa, **"Ruxsat berish (Allow)"** tugmasini bosing.

---

### 2. Loyihani Kompyuterda Ishga Tushirish

#### Python muhitini tayyorlash va kutubxonalarni o'rnatish:

```bash
# Python kutubxonalarini o'rnatish
pip install -r requirements.txt
```

#### Dasturni ishga tushirish:

```bash
# Windows / Linux / macOS
python server.py
```

Dastur ishga tushgach, CLI terminalda AxtarGet dashboard namoyon bo'ladi va brauzer orqali kiritiladigan manzillar ko'rsatiladi:
- Local access: `http://127.0.0.1:8080`
- Network Wi-Fi access: `http://192.168.x.x:8080`

---

### 3. Wi-Fi Orqali Telefonda Ekran Ko'rsatish (Simsiz Ulanish)

1. Kompyuteringiz va smartfoningiz **bir xil Wi-Fi tarmog'iga** ulangan bo'lishi kerak.
2. Dastur terminalida `-qr` buyrug'ini kiriting.
3. Smartfon kamerasini terminaldagi **QR-kodga** qarating va hosil bo'lgan havolani brauzerda oching (`http://192.168.x.x:8080`).
4. Endi siz smartfoningiz ekranini brauzeringizda ko'rishingiz va sichqoncha orqali boshqarishingiz mumkin!

---

## 📂 Loyiha Fayllar Stukturasi

```
axtarget-screen-mirroring/
├── requirements.txt      # Barcha kerakli Python kutubxonalari
├── server.py            # Terminal CLI, AxtarGet Banner, Status Dashboard, QR-kod generator
├── web_app.py           # FastAPI, WebSockets streaming server va ADB input ishlovchisi
├── templates/
│   └── index.html       # HTML5 Canvas ekran pleeri va masofaviy boshqaruv paneli
└── README.md            # Batafsil loyiha qo'llanmasi
```

---

## ⚡ Foydali Buyruqlar Ro'yxati (Terminal CLI)

| Buyruq | Tavsif |
| :--- | :--- |
| `ip` | Ulanish uchun lokal va Wi-Fi IP manzillarini ko'rsatadi |
| `-qr` | Wi-Fi orqali smartfon brauzerida ochish uchun QR-kod chiqaradi |
| `-clear` | Terminal ekranini tozalaydi |
| `-exit` | Web server va dastur ishini to'xtatadi |

---
*AxtarGet Screen Mirroring V1.4 — Real-time Android Remote Mirroring & Control System.*
