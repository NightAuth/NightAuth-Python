# NightAuth Python SDK — Lascia una stella su GitHub ⭐

SDK ufficiale **NightAuth** per Python e suite client di riferimento completa (Interfaccia Desktop moderna in **PyQt6** e CLI interattiva in **Rich**). Proteggi il tuo software da pirateria, ingegneria inversa e manomissioni grazie a licenze cloud, blocco HWID, chat in tempo reale ed esecuzione in memoria in pochi minuti.

**Languages / Idiomas / Langues / Sprachen:**  
[English](../README.md) • [Español](es.md) • [Français](fr.md) • [Deutsch](de.md) • [Italiano](it.md) • [Português](pt.md) • [Русский](ru.md) • [Türkçe](tr.md) • [Polski](pl.md) • [中文](zh.md)

---

> [!NOTE]
> ### 📺 Video Tutorial e Guide di Configurazione
> I video tutorial ufficiali e le guide dettagliate passo-passo sulla configurazione di app, abbonamenti, variabili cloud, webhook e licenze nella dashboard di NightAuth **saranno pubblicati a breve** sui nostri canali ufficiali.

---

## 📸 Screenshot

### Applicazione Desktop (Desktop UI — PyQt6)

| Schermata di Accesso / Autenticazione | Dashboard & Gestione Abbonamenti |
| :---: | :---: |
| ![NightAuth Desktop Login](../image/desktop.png) | ![NightAuth Desktop Dashboard](../image/desktop-dashboard.png) |

### Applicazione da Console (CLI — Rich)

| Accesso da Terminale | Dashboard Interattiva da Console |
| :---: | :---: |
| ![NightAuth Console Login](../image/console.png) | ![NightAuth Console Dashboard](../image/console-dashboard.png) |

---

## 🛡️ Pratiche di Sicurezza Consigliate

* **Compilazione Nativa e Offuscamento:** Il bytecode Python è vulnerabile alla decompilazione. Per la produzione, compila gli script in binari nativi C/C++ (.pyd o .exe) tramite **Nuitka** o **PyArmor**.
* **Virtualizzazione del Codice Enterprise:** Proteggi l'eseguibile risultante con strumenti professionali quali **VMProtect**, **Themida** o **Enigma Protector**.
* **Integrità della Memoria e Anti-Debug:** NightAuth include il rilevamento automatico di debugger e strumenti di monitoraggio (HTTPDebugger, CheatEngine, x64dbg, Wireshark).
* **Esecuzione Sicura in Memoria:** Quando scarichi file protetti con `api.download()`, **non salvarli sul disco rigido**. Eseguili direttamente in memoria (con `io.BytesIO` o RunPE) e pulisci i buffer subito dopo l'uso.

---

## 📦 Requisiti e Installazione

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configurazione e Inizializzazione

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

Chiama `init()` prima di qualsiasi altra operazione per avviare l'handshake Diffie-Hellman (X25519) e la sessione cifrata:

```python
NightAuthApp.init()

if not NightAuthApp.response.success:
    print(f"Error: {NightAuthApp.response.message}")
    exit(1)
```

---

## 🚀 Guida all'Uso dell'SDK

### 1. Convalida della Sessione e Controllo Blacklist

```python
NightAuthApp.check()
if NightAuthApp.checkblack():
    exit(0)
```

### 2. Accesso con Nome Utente & Password (e 2FA)

```python
if NightAuthApp.login(username, password, two_factor_code=""):
    print(f"Welcome {NightAuthApp.user.username}")
```

### 3. Registrazione con Chiave di Licenza

```python
if NightAuthApp.register(username, password, license_key, email=""):
    print("Registered successfully")
```

### 4. Autenticazione con Sola Chiave di Licenza

```python
if NightAuthApp.license(license_key):
    print("License authenticated")
```

### 5. Aggiornamento Account / Riscatto Nuova Licenza

```python
if NightAuthApp.upgrade(username, new_license_key):
    print("Subscription upgraded")
```

### 6. Ripristino del Blocco HWID (Hardware ID)

```python
if NightAuthApp.reset_hwid(username, password, two_factor_code=""):
    print("HWID reset completed")
```

### 7. Recupero Password / Account

```python
if NightAuthApp.forgot_password(email):
    print("Recovery token sent")
```

### 8. Dati Utente (`NightAuthApp.user`)

```python
print(NightAuthApp.user.username, NightAuthApp.user.ip, NightAuthApp.user.hwid)
for sub in NightAuthApp.user.subscriptions:
    print(sub.subscription, sub.expiry)
```

### 9. Variabili Cloud Globali

```python
val = NightAuthApp.var("server_motd")
```

### 10. Variabili Specifiche per Utente

```python
NightAuthApp.set_user_var("discord", "user#0001")
val = NightAuthApp.get_user_var("discord")
```

### 11. Log di Controllo e Sicurezza

```python
NightAuthApp.log("Security telemetry or detection")
```

### 12. Ban dell'Utente e Blocco Dispositivo

```python
NightAuthApp.ban("Tampering detected")
```

### 13. Webhook Sicuri Lato Server

```python
resp = NightAuthApp.webhook("7kR0UedlVI", params="&action=notify", body='{"content": "Notice"}')
```

### 14. Download Sicuro dei File in RAM

```python
file_bytes = NightAuthApp.download("385624")
```

### 15. Canali Chat in Tempo Reale

```python
NightAuthApp.chat_send("Hello!", channel="general")
msgs = NightAuthApp.chat_get(channel="general")
```

### 16. Gestori di Eventi in Tempo Reale (SSE)

```python
NightAuthApp.on_session_invalidated = lambda r: print(f"Session invalidated: {r}")
NightAuthApp.on_app_banned = lambda r: print(f"App banned: {r}")
NightAuthApp.on_app_status_changed = lambda s: print(f"Status changed: {s}")
NightAuthApp.on_version_updated = lambda v: print(f"Update: v{v}")
```

---

## 📄 Licenza

Questo progetto è concesso in licenza con **Elastic License 2.0**. Consulta il file [LICENSE](../LICENSE) per il testo legale completo.
