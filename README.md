# AxtarGet Screen Mirroring V2.0 (Mobile-to-Mobile 120 FPS 4K HDR) 📱⚡📱

AxtarGet Screen Mirroring V2.0 - Bu Android smartfon ekranini kompyuter va **boshqa telefon (Phone B) brauzerida** 120 FPS gacha o'ta yuqori kadrlar tezligida (ultra-low latency), 4K HDR sifatida real vaqt rejimida ko'rsatish va masofadan to'liq boshqarish imkonini beruvchi professional loyiha.

---

## 🚀 Yangi Imkoniyatlar (V2.0 Update)

1. **📱 Real HTML5 Camera QR-Code Scanner:**
   - Sayt interfeysida joylashgan **"📷 Scan QR Code"** tugmasi orqali kamerani yoqib, QR kodni skanerlash va boshqa maqsadli telefon serveriga avtomartik ulanish.
   - Sayt yon panelida avto-yaratiladigan QR-kod rasmi (`/qr`).

2. **📱 Telefon Orqali Telefonni Boshqarish (Mobile-to-Mobile Remote Control):**
   - Telefon A (Maqsadli telefon) ekranini **Telefon B brauzerida** ochib, Phone B ning sensor ekrani orqali Phone A ni real vaqt rejimida boshqarish.
   - Mobil moslashuvchan (Responsive Touch UI) va `touchstart` / `touchend` imo-ishoralarini (gesture) qo'llab-quvvatlash.

3. **⚡ 120 FPS Ultra-Low Latency Stream (&lt;10ms kechikish):**
   - Veb-interfeysda kadrlar tezligini dinamik ravishda tanlash: `120 FPS (Ultra-Smooth)`, `60 FPS`, `30 FPS`.
   - Minimal buferlash va optimal matn/grafik sifat.

4. **🎬 4K HDR Sifat Rejimi:**
   - Ekranni 4K HDR Ultra, 1080p High Quality va 720p Low Latency rejimlari bo'yicha sozlash.

5. **💻 Terminal CLI Interfeysi (AxtarGet Style V2.0):**
   - Rich kutubxonasida Matrix terminal banner va status-boshqaruv.
   - QR-kod orqali boshqa mobil telefondan bir zumda ulanish (`-qr` buyrug'i).

---

## 🛠️ O'rnatish va Ishga Tushirish

### 1. Smartfonda USB Debugging (Sozlash) ni Yoqish

1. **Phone A (Maqsadli telefon)** sozlamalaridan **"USB Debugging" (USB orqali sozlash)** funksiyasini yoqing.
2. Phone A ni USB kabel orqali kompyuterga ulang yoki Wi-Fi ADB orqali bog'lang.

### 2. Serverni Ishga Tushirish

```bash
# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Serverni ishga tushirish
python server.py
```

CLI Terminalda Wi-Fi manzil va QR-kod yaratiladi (`http://192.168.x.x:8080`).

---

## 📱 TELEFON ORQALI TELEFONNI SCANNER QILIB BOSHQARISH (Phone B -> Phone A)

1. **Phone A** va **Phone B** ni bir xil Wi-Fi tarmog'iga ulang.
2. Terminalda `-qr` buyrug'ini kiriting yoki saytdagi `/qr` rasmini oching.
3. **Phone B** kamerasini terminaldagi yoki saytdagi QR-kodga qarating hamda havolani Phone B brauzerida oching. Yoki saytdagi **"📷 Scan QR Code"** tugmasini bosing.
4. Phone B ekraniga barmoq bilan tegish (Tap) va surish (Swipe) orqali Phone A ni real vaqtda to'liq boshqaring!

---

## ⚡ CLI Terminal Buyruqlari

| Buyruq | Vazifasi |
| :--- | :--- |
| `ip` | Mobil va lokal IP manzillarini ko'rsatish |
| `-qr` | Telefon B uchun Wi-Fi QR-kod chiqarish |
| `-clear` | Terminalni tozalash |
| `-exit` | Server va dastur ishini to'xtatish |

---
*AxtarGet Screen Mirroring V2.0 — High-FPS Mobile-to-Mobile Screen Streaming System.*
