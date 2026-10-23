# NightAuth Python SDK — Zostaw gwiazdkę na GitHubie ⭐

Oficjalny pakiet **NightAuth** Python SDK oraz kompletny zestaw referencyjny klienta (Nowoczesne GUI w **PyQt6** i interaktywny terminal w **Rich**). Chroń swoje oprogramowanie przed piractwem, inżynierią wsteczną i modyfikacjami w zaledwie kilka minut dzięki licencjonowaniu w chmurze, blokadzie HWID, czatowi na żywo oraz strumieniowaniu w pamięci RAM.

**Languages / Idiomas / Langues / Sprachen:**  
[English](../README.md) • [Español](es.md) • [Français](fr.md) • [Deutsch](de.md) • [Italiano](it.md) • [Português](pt.md) • [Русский](ru.md) • [Türkçe](tr.md) • [Polski](pl.md) • [中文](zh.md)

---

> [!NOTE]
> ### 📺 Poradniki Wideo i Konfiguracja Systemu
> Oficjalne wideoporadniki oraz szczegółowe instrukcje krok po kroku dotyczące konfiguracji aplikacji, subskrypcji, zmiennych w chmurze, webhooków i licencji w panelu NightAuth **zostaną opublikowane wkrótce**.

---

## 📸 Zrzuty Ekranu

### Aplikacja Desktopowa (Desktop UI — PyQt6)

| Ekran Logowania / Uwierzytelniania | Panel Zarządzania & Subskrypcje |
| :---: | :---: |
| ![NightAuth Desktop Login](../image/desktop.png) | ![NightAuth Desktop Dashboard](../image/desktop-dashboard.png) |

### Aplikacja Konsolowa (CLI — Rich)

| Logowanie w Terminalu | Interaktywny Panel Konsolowy |
| :---: | :---: |
| ![NightAuth Console Login](../image/console.png) | ![NightAuth Console Dashboard](../image/console-dashboard.png) |

---

## 🛡️ Zalecane Praktyki Bezpieczeństwa

* **Natywna Kompilacja i Obfuskacja:** Kod bajtowy Pythona jest łatwy do dekompilacji. Do dystrybucji produkcyjnej skompiluj swoje skrypty do natywnego kodu maszynowego C/C++ (.pyd lub .exe) przy użyciu narzędzi **Nuitka** lub **PyArmor**.
* **Wirtualizacja Kodu Enterprise:** Zabezpiecz plik wykonywalny za pomocą komercyjnych protektorów, takich jak **VMProtect**, **Themida** lub **Enigma Protector**.
* **Integralność Pamięci i Anti-Debug:** NightAuth posiada wbudowany moduł wykrywania debuggerów i narzędzi do inspekcji sieci (HTTPDebugger, CheatEngine, x64dbg, Wireshark).
* **Bezpieczne Wykonywanie w Pamięci:** Pobierając chronione pliki (`api.download()`), **nie zapisuj bajtów na dysku twardym**. Uruchamiaj je bezpośrednio w pamięci RAM (np. poprzez `io.BytesIO` lub RunPE) i natychmiast czyść bufory.

---

## 📦 Wymagania i Instalacja

```bash
pip install -r requirements.txt
```

---

## ⚙️ Konfiguracja i Inicjalizacja

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

Przed wykonaniem jakichkolwiek innych funkcji SDK należy wywołać `init()`, aby przeprowadzić wymianę kluczy Diffie-Hellman (X25519) i ustanowić zaszyfrowaną sesję:

```python
NightAuthApp.init()

if not NightAuthApp.response.success:
    print(f"Error: {NightAuthApp.response.message}")
    exit(1)
```

---

## 🚀 Przewodnik po SDK

### 1. Walidacja Sesji i Sprawdzenie Czarnej Listy

```python
NightAuthApp.check()
if NightAuthApp.checkblack():
    exit(0)
```

### 2. Logowanie Użytkownikiem i Hasłem (oraz 2FA)

```python
if NightAuthApp.login(username, password, two_factor_code=""):
    print(f"Welcome {NightAuthApp.user.username}")
```

### 3. Rejestracja z Kluczem Licencyjnym

```python
if NightAuthApp.register(username, password, license_key, email=""):
    print("Registered successfully")
```

### 4. Logowanie Samym Kluczem Licencyjnym (Key Only)

```python
if NightAuthApp.license(license_key):
    print("License authenticated")
```

### 5. Uaktualnienie Konta / Realizacja Nowego Klucza

```python
if NightAuthApp.upgrade(username, new_license_key):
    print("Subscription upgraded")
```

### 6. Reset Blokady Sprzętowej (HWID Reset)

```python
if NightAuthApp.reset_hwid(username, password, two_factor_code=""):
    print("HWID reset completed")
```

### 7. Odzyskiwanie Hasła / Konta

```python
if NightAuthApp.forgot_password(email):
    print("Recovery token sent")
```

### 8. Dane Użytkownika (`NightAuthApp.user`)

```python
print(NightAuthApp.user.username, NightAuthApp.user.ip, NightAuthApp.user.hwid)
for sub in NightAuthApp.user.subscriptions:
    print(sub.subscription, sub.expiry)
```

### 9. Globalne Zmienne w Chmurze

```python
val = NightAuthApp.var("server_motd")
```

### 10. Zmienne Użytkownika w Chmurze

```python
NightAuthApp.set_user_var("discord", "user#0001")
val = NightAuthApp.get_user_var("discord")
```

### 11. Dzienniki Audytu i Bezpieczeństwa

```python
NightAuthApp.log("Security telemetry or detection")
```

### 12. Blokowanie Użytkownika i Sprzętu (Ban)

```python
NightAuthApp.ban("Tampering detected")
```

### 13. Bezpieczne Webhooki po Stronie Serwera

```python
resp = NightAuthApp.webhook("7kR0UedlVI", params="&action=notify", body='{"content": "Notice"}')
```

### 14. Bezpieczne Pobieranie Plików do Pamięci

```python
file_bytes = NightAuthApp.download("385624")
```

### 15. Kanały Czatu na Żywo

```python
NightAuthApp.chat_send("Hello!", channel="general")
msgs = NightAuthApp.chat_get(channel="general")
```

### 16. Odbiorniki Zdarzeń w Czasie Rzeczywistym (SSE)

```python
NightAuthApp.on_session_invalidated = lambda r: print(f"Session invalidated: {r}")
NightAuthApp.on_app_banned = lambda r: print(f"App banned: {r}")
NightAuthApp.on_app_status_changed = lambda s: print(f"Status changed: {s}")
NightAuthApp.on_version_updated = lambda v: print(f"Update: v{v}")
```

---

## 📄 Licencja

Ten projekt jest udostępniany na licencji **Elastic License 2.0**. Szczegóły prawne znajdują się w pliku [LICENSE](../LICENSE).
