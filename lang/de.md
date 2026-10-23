# NightAuth Python SDK — Gib uns einen Stern auf GitHub ⭐

Offizielles **NightAuth** Python SDK & vollständige Referenz-Client-Suite (Moderne Desktop-Benutzeroberfläche in **PyQt6** und interaktives Terminal in **Rich**). Schützen Sie Ihre Software in wenigen Minuten vor Piraterie, Reverse Engineering und Manipulation durch Cloud-Lizenzierung, HWID-Sperrung, Live-Chat und Streaming im Arbeitsspeicher.

**Languages / Idiomas / Langues / Sprachen:**  
[English](../README.md) • [Español](es.md) • [Français](fr.md) • [Deutsch](de.md) • [Italiano](it.md) • [Português](pt.md) • [Русский](ru.md) • [Türkçe](tr.md) • [Polski](pl.md) • [中文](zh.md)

---

> [!NOTE]
> ### 📺 Video-Tutorials & Einrichtungsanleitungen
> Offizielle Video-Tutorials und Schritt-für-Schritt-Anleitungen zur Konfiguration von Anwendungen, Tarifen, Abonnements, Cloud-Variablen, Webhooks und Lizenzen im NightAuth-Dashboard **werden in Kürze veröffentlicht**.

---

## 📸 Screenshots

### Desktop-Anwendung (Desktop UI — PyQt6)

| Anmelde- / Authentifizierungsfenster | Dashboard & Abonnementverwaltung |
| :---: | :---: |
| ![NightAuth Desktop Login](../image/desktop.png) | ![NightAuth Desktop Dashboard](../image/desktop-dashboard.png) |

### Konsolenanwendung (CLI — Rich)

| Terminal-Anmeldung | Interaktives Konsolen-Dashboard |
| :---: | :---: |
| ![NightAuth Console Login](../image/console.png) | ![NightAuth Console Dashboard](../image/console-dashboard.png) |

---

## 🛡️ Empfohlene Sicherheitspraktiken

* **Native Kompilierung & Obfuskation:** Python-Bytecode kann leicht dekompiliert werden. Für produktive Software kompilieren Sie Ihre Skripte mit **Nuitka** oder **PyArmor** in nativen C/C++-Maschinencode (.pyd oder .exe).
* **Enterprise-Code-Virtualisierung:** Schützen Sie die ausführbare Datei mit professionellen Protectoren wie **VMProtect**, **Themida** oder **Enigma Protector**.
* **Speicherintegrität & Anti-Debugging:** NightAuth erkennt Debugger und Sniffer (HTTPDebugger, CheatEngine, x64dbg, Wireshark). Belassen Sie diesen Schutz in der Produktion aktiviert.
* **Sichere Ausführung im RAM:** Speichern Sie geschützte Dateien (`api.download()`) **nicht auf der Festplatte**. Führen Sie diese direkt im Arbeitsspeicher aus (z. B. via `io.BytesIO` oder RunPE) und leeren Sie die Puffer nach der Nutzung.

---

## 📦 Voraussetzungen & Installation

```bash
pip install -r requirements.txt
```

---

## ⚙️ Konfiguration & Initialisierung

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

Rufen Sie `init()` vor allen anderen SDK-Funktionen auf, um den Diffie-Hellman-Schlüsselaustausch (X25519) und die verschlüsselte Sitzung zu starten:

```python
NightAuthApp.init()

if not NightAuthApp.response.success:
    print(f"Error: {NightAuthApp.response.message}")
    exit(1)
```

---

## 🚀 SDK-Nutzungsanleitung

### 1. Sitzungsvalidierung & Blacklist-Prüfung

```python
NightAuthApp.check()
if NightAuthApp.checkblack():
    exit(0)
```

### 2. Anmeldung mit Benutzername & Passwort (und 2FA)

```python
if NightAuthApp.login(username, password, two_factor_code=""):
    print(f"Welcome {NightAuthApp.user.username}")
```

### 3. Registrierung mit Lizenzschlüssel

```python
if NightAuthApp.register(username, password, license_key, email=""):
    print("Registered successfully")
```

### 4. Nur-Lizenz-Authentifizierung (Key Only)

```python
if NightAuthApp.license(license_key):
    print("License authenticated")
```

### 5. Konto-Upgrade / Lizenz einlösen

```python
if NightAuthApp.upgrade(username, new_license_key):
    print("Subscription upgraded")
```

### 6. Hardware-ID zurücksetzen (HWID-Reset)

```python
if NightAuthApp.reset_hwid(username, password, two_factor_code=""):
    print("HWID reset completed")
```

### 7. Passwort vergessen / Kontowiederherstellung

```python
if NightAuthApp.forgot_password(email):
    print("Recovery token sent")
```

### 8. Benutzerdaten (`NightAuthApp.user`)

```python
print(NightAuthApp.user.username, NightAuthApp.user.ip, NightAuthApp.user.hwid)
for sub in NightAuthApp.user.subscriptions:
    print(sub.subscription, sub.expiry)
```

### 9. Globale Cloud-Variablen

```python
val = NightAuthApp.var("server_motd")
```

### 10. Benutzerspezifische Cloud-Variablen

```python
NightAuthApp.set_user_var("discord", "user#0001")
val = NightAuthApp.get_user_var("discord")
```

### 11. Audit- und Sicherheits-Logs

```python
NightAuthApp.log("Security telemetry or detection")
```

### 12. Benutzer sperren & Gerät blockieren

```python
NightAuthApp.ban("Tampering detected")
```

### 13. Serverseitige sichere Webhooks

```python
resp = NightAuthApp.webhook("7kR0UedlVI", params="&action=notify", body='{"content": "Notice"}')
```

### 14. Sicherer Dateidownload im Speicher

```python
file_bytes = NightAuthApp.download("385624")
```

### 15. Live-Chat-Kanäle

```python
NightAuthApp.chat_send("Hello!", channel="general")
msgs = NightAuthApp.chat_get(channel="general")
```

### 16. Echtzeit-Ereignishandler (SSE)

```python
NightAuthApp.on_session_invalidated = lambda r: print(f"Session invalidated: {r}")
NightAuthApp.on_app_banned = lambda r: print(f"App banned: {r}")
NightAuthApp.on_app_status_changed = lambda s: print(f"Status changed: {s}")
NightAuthApp.on_version_updated = lambda v: print(f"Update: v{v}")
```

---

## 📄 Lizenz

Dieses Projekt unterliegt der **Elastic License 2.0**. Den vollständigen Text finden Sie in der Datei [LICENSE](../LICENSE).
