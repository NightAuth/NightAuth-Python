# NightAuth Python SDK — GitHub'da yıldız verin ⭐

Resmi **NightAuth** Python SDK ve eksiksiz referans istemci paketi (**PyQt6** Modern Masaüstü Arayüzü ve **Rich** İnteraktif Terminal CLI). Yazılımınızı dakikalar içinde bulut lisanslama, HWID kilitleme, gerçek zamanlı sohbet ve bellek içi yürütme ile korsanlığa ve tersine mühendisliğe karşı koruyun.

**Languages / Idiomas / Langues / Sprachen:**  
[English](../README.md) • [Español](es.md) • [Français](fr.md) • [Deutsch](de.md) • [Italiano](it.md) • [Português](pt.md) • [Русский](ru.md) • [Türkçe](tr.md) • [Polski](pl.md) • [中文](zh.md)

---

> [!NOTE]
> ### 📺 Video Eğitimleri ve Sistem Kurulum Kılavuzları
> NightAuth panelinde uygulama, plan, abonelik, bulut değişkenleri, webhook ve lisans yapılandırmasını anlatan resmi video eğitimleri ve adım adım kılavuzlar **yakında yayınlanacaktır**.

---

## 📸 Ekran Görüntüleri

### Masaüstü Uygulaması (Desktop UI — PyQt6)

| Giriş / Kimlik Doğrulama Ekranı | Yönetim Paneli & Abonelikler |
| :---: | :---: |
| ![NightAuth Desktop Login](../image/desktop.png) | ![NightAuth Desktop Dashboard](../image/desktop-dashboard.png) |

### Konsol Uygulaması (CLI — Rich)

| Terminal Giriş Ekranı | İnteraktif Konsol Paneli |
| :---: | :---: |
| ![NightAuth Console Login](../image/console.png) | ![NightAuth Console Dashboard](../image/console-dashboard.png) |

---

## 🛡️ Önerilen Güvenlik Uygulamaları

* **Yerel Derleme ve Karartma:** Python bayt kodu kolayca kaynak koduna dönüştürülebilir. Üretim dağıtımı için scriptlerinizi **Nuitka** veya **PyArmor** ile yerel C/C++ makine koduna (.pyd/.exe) derleyin.
* **Kurumsal Kod Sanallaştırma:** Derlenmiş yürütülebilir dosyayı **VMProtect**, **Themida** veya **Enigma Protector** gibi ticari koruma yazılımlarıyla koruyun.
* **Bellek Bütünlüğü ve Anti-Debug:** NightAuth, hata ayıklayıcıları ve ağ analiz araçlarını (HTTPDebugger, CheatEngine, x64dbg, Wireshark) tespit eden yerleşik korumaya sahiptir.
* **Bellekte Güvenli Yürütme:** Korunan dosyaları indirirken (`api.download()`), **baytları asla sabit diske yazmayın**. Doğrudan RAM üzerinde çalıştırın (`io.BytesIO` veya RunPE teknikleri ile) ve sonrasında temizleyin.

---

## 📦 Gereksinimler ve Kurulum

```bash
pip install -r requirements.txt
```

---

## ⚙️ Yapılandırma ve Başlatma

```python
from nightauth import api

APP_NAME = ""
APP_API_KEY = ""
APP_VERSION = "1.0"
APP_TOKEN = None

NightAuthApp = api(
    name=APP_NAME,
    apikey=APP_API_KEY,
    version=APP_VERSION,
    token=APP_TOKEN
)
```

### init()

Diffie-Hellman (X25519) anahtar değişimini ve şifreli oturumu kurmak için diğer SDK işlevlerinden önce `init()` işlevini çağırmalısınız:

```python
NightAuthApp.init()

if not NightAuthApp.response.success:
    print(f"Error: {NightAuthApp.response.message}")
    exit(1)
```

---

## 🚀 SDK Kullanım Kılavuzu

### 1. Oturum Doğrulama ve Kara Liste Kontrolü

```python
NightAuthApp.check()
if NightAuthApp.checkblack():
    exit(0)
```

### 2. Kullanıcı Adı ve Şifre ile Giriş (ve 2FA)

```python
if NightAuthApp.login(username, password, two_factor_code=""):
    print(f"Welcome {NightAuthApp.user.username}")
```

### 3. Lisans Anahtarı ile Kayıt Olma

```python
if NightAuthApp.register(username, password, license_key, email=""):
    print("Registered successfully")
```

### 4. Yalnızca Lisans Anahtarı ile Giriş (Key Only)

```python
if NightAuthApp.license(license_key):
    print("License authenticated")
```

### 5. Hesap Yükseltme / Yeni Lisans Tanımlama

```python
if NightAuthApp.upgrade(username, new_license_key):
    print("Subscription upgraded")
```

### 6. Donanım Kilidini Sıfırlama (HWID Reset)

```python
if NightAuthApp.reset_hwid(username, password, two_factor_code=""):
    print("HWID reset completed")
```

### 7. Şifremi Unuttum / Hesap Kurtarma

```python
if NightAuthApp.forgot_password(email):
    print("Recovery token sent")
```

### 8. Kullanıcı Verileri (`NightAuthApp.user`)

```python
print(NightAuthApp.user.username, NightAuthApp.user.ip, NightAuthApp.user.hwid)
for sub in NightAuthApp.user.subscriptions:
    print(sub.subscription, sub.expiry)
```

### 9. Genel Bulut Değişkenleri

```python
val = NightAuthApp.var("server_motd")
```

### 10. Kullanıcıya Özel Değişkenler

```python
NightAuthApp.set_user_var("discord", "user#0001")
val = NightAuthApp.get_user_var("discord")
```

### 11. Uygulama Denetim ve Güvenlik Günlükleri

```python
NightAuthApp.log("Security telemetry or detection")
```

### 12. Kullanıcıyı Yasaklama ve Cihaz Engelleme

```python
NightAuthApp.ban("Tampering detected")
```

### 13. Sunucu Tarafı Güvenli Webhook'lar

```python
resp = NightAuthApp.webhook("7kR0UedlVI", params="&action=notify", body='{"content": "Notice"}')
```

### 14. Bellekte Güvenli Dosya İndirme

```python
file_bytes = NightAuthApp.download("385624")
```

### 15. Canlı Sohbet Kanalları

```python
NightAuthApp.chat_send("Hello!", channel="general")
msgs = NightAuthApp.chat_get(channel="general")
```

### 16. Gerçek Zamanlı Olay Dinleyicileri (SSE)

```python
NightAuthApp.on_session_invalidated = lambda r: print(f"Session invalidated: {r}")
NightAuthApp.on_app_banned = lambda r: print(f"App banned: {r}")
NightAuthApp.on_app_status_changed = lambda s: print(f"Status changed: {s}")
NightAuthApp.on_version_updated = lambda v: print(f"Update: v{v}")
```

---

## 📄 Lisans

Bu proje **Elastic License 2.0** kapsamında lisanslanmıştır. Yasal ayrıntılar için [LICENSE](../LICENSE) dosyasını inceleyin.
