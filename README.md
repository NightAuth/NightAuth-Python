# NightAuth Python SDK — Star us on GitHub ⭐

Official **NightAuth** Python SDK & Reference Client Suite (Modern Desktop UI in **PyQt6** and Interactive Terminal CLI in **Rich**). Protect your software against piracy, reverse engineering, and tampering with cloud licensing, HWID locking, realtime chat, and memory streaming in minutes.

Official Portal: [https://nightauth.org](https://nightauth.org)  
Documentation: [https://nightauth.org/docs](https://nightauth.org/docs)  
Technical Architecture Benchmark: [NightAuth vs KeyAuth vs Auth.gg](https://nightauth.org/blog/nightauth-vs-keyauth-authgg-comparison)

---

**Languages / Idiomas / Langues / Sprachen:**  
[English](README.md) • [Español](lang/es.md) • [Français](lang/fr.md) • [Deutsch](lang/de.md) • [Italiano](lang/it.md) • [Português](lang/pt.md) • [Русский](lang/ru.md) • [Türkçe](lang/tr.md) • [Polski](lang/pl.md) • [中文](lang/zh.md)

---

> [!NOTE]
> ### 📺 Video Tutorials & System Setup Guides
> Official video tutorials and detailed step-by-step guides explaining how to configure applications, plans, subscriptions, cloud variables, webhooks, and licenses in the NightAuth Dashboard **will be published soon** on our official portal and YouTube channel.

---

## 📸 Screenshots

### Desktop Application (PyQt6 Enterprise Dark Theme)

| Start / Authentication Screen | Dashboard & Subscription Management |
| :---: | :---: |
| ![NightAuth Desktop Login](image/desktop.png) | ![NightAuth Desktop Dashboard](image/desktop-dashboard.png) |

### Console Application (Rich Interactive Terminal)

| Terminal Login Screen | Interactive Console Dashboard |
| :---: | :---: |
| ![NightAuth Console Login](image/console.png) | ![NightAuth Console Dashboard](image/console-dashboard.png) |

---

## 🛡️ Recommended Security Practices

* **Native Compilation & Obfuscation:** Python bytecode is easily decompiled by tools like decompyle++ or uncompyle6. For production software distribution, compile your scripts into native C/C++ machine code (`.pyd` or `.exe`) using **Nuitka** or **PyArmor**.
* **Enterprise Code Virtualization:** Protect the compiled executable using commercial code virtualizers and protectors such as **VMProtect**, **Themida**, or **Enigma Protector**.
* **Memory Integrity & Anti-Debugging:** NightAuth includes built-in protection against monitoring tools, network interceptors, and debuggers (`HTTPDebugger`, `CheatEngine`, `x64dbg`, `Wireshark`, etc.). Keep these security protections enabled in production releases.
* **In-Memory Secure File Execution:** When downloading protected payloads or binaries with `api.download()`, **do not write bytes to the physical hard drive** where end-users can copy them. Instead, stream and execute the payload directly in memory (e.g., using `io.BytesIO` or reflective loader / RunPE techniques) and zero out the memory buffers immediately after execution.

---

## 📦 Requirements & Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Core dependencies:
* `requests` (Encrypted HTTPS transport)
* `pycryptodome` (Modern cryptography primitives)
* `PyQt6` (High-performance native GUI)
* `rich` (Interactive styled terminal interface)
* `qrcode` & `pillow` (2FA authenticator QR code generation)
* `websocket-client` (Realtime SSE and socket listener)

---

## ⚙️ Configuration & Initialization

Define your application credentials exactly as shown in the **Manage Apps** tab of the NightAuth dashboard:

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

### Initialize Cryptographic Handshake (`init`)

You must call `init()` prior to executing any other SDK functions. This establishes an ephemeral Diffie-Hellman (X25519) key exchange and an encrypted session:

```python
NightAuthApp.init()

if not NightAuthApp.response.success:
    print(f"Initialization Failed: {NightAuthApp.response.message}")
    exit(1)
```

---

## 🚀 SDK Usage Guide

### 1. Check Session Validation & Blacklist Status

```python
# Validate active session status with the server
NightAuthApp.check()
print(f"Session Status: {NightAuthApp.response.message}")

# Check if client HWID or IP address is blacklisted
if NightAuthApp.checkblack():
    print("Access Denied: Machine or IP is blacklisted.")
    exit(0)
```

### 2. Login with Username & Password (and 2FA)

```python
username = input("Username: ")
password = input("Password: ")
two_factor = input("2FA Code (optional): ")

if NightAuthApp.login(username, password, two_factor_code=two_factor):
    print(f"Welcome back, {NightAuthApp.user.username}!")
else:
    print(f"Login failed: {NightAuthApp.response.message}")
```

### 3. Register with License Key

```python
username = input("Desired Username: ")
password = input("Password: ")
license_key = input("License Key: ")
email = input("Email (optional): ")

if NightAuthApp.register(username, password, license_key, email):
    print(f"Account registered successfully: {NightAuthApp.user.username}")
else:
    print(f"Registration failed: {NightAuthApp.response.message}")
```

### 4. Authenticate with License Key Only

```python
license_key = input("Enter license key: ")

if NightAuthApp.license(license_key):
    print("License authenticated successfully. Access granted.")
else:
    print(f"Access denied: {NightAuthApp.response.message}")
```

### 5. Upgrade Account / Claim License Key

```python
username = input("Account Username: ")
new_key = input("New License Key: ")

if NightAuthApp.upgrade(username, new_key):
    print(f"License redeemed successfully: {NightAuthApp.response.message}")
else:
    print(f"Upgrade failed: {NightAuthApp.response.message}")
```

### 6. Reset Hardware ID (HWID Lock)

```python
username = input("Username: ")
password = input("Password: ")
two_factor = input("2FA Code (if enabled): ")

if NightAuthApp.reset_hwid(username, password, two_factor_code=two_factor):
    print("HWID lock reset successfully. You can now log in on this machine.")
else:
    print(f"HWID reset failed: {NightAuthApp.response.message}")
```

### 7. Forgot Password / Account Recovery

```python
email = input("Enter registered email: ")

if NightAuthApp.forgot_password(email):
    print("Password reset email sent. Check your inbox.")
else:
    print(f"Recovery failed: {NightAuthApp.response.message}")
```

### 8. User Data (`NightAuthApp.user`)

Access comprehensive profile data once authenticated:

```python
print("=== USER PROFILE ===")
print("Username:     ", NightAuthApp.user.username)
print("Client IP:    ", NightAuthApp.user.ip)
print("Hardware ID:  ", NightAuthApp.user.hwid)
print("Registered:   ", NightAuthApp.user.created_at)
print("Last Login:   ", NightAuthApp.user.last_login_at)

# Active subscriptions
for sub in NightAuthApp.user.subscriptions:
    print(f"Plan: {sub.subscription} | Expires: {sub.expiry} | Key: {sub.key}")
```

### 9. Cloud Variables (Global)

Fetch global configuration variables configured in the dashboard:

```python
motd = NightAuthApp.var("server_motd")
print("Cloud Variable:", motd)
```

### 10. User Variables

Read and write isolated, user-specific persistent variables in the cloud:

```python
# Set a user variable
NightAuthApp.set_user_var("discord_tag", "user#0001")

# Retrieve a user variable
tag = NightAuthApp.get_user_var("discord_tag")
print("Stored Discord:", tag)
```

### 11. Application Audit Logs

Send security alerts or telemetry logs directly to the dashboard or Discord webhook:

```python
NightAuthApp.log("Suspicious memory modification attempt detected.")
```

### 12. Ban User & Blacklist Machine

Instantly terminate the session, ban the user account, and blacklist their HWID and IP:

```python
NightAuthApp.ban("Security tampering detected by Anti-Cheat.")
```

### 13. Server-Sided Webhooks

Execute HTTP requests to external third-party APIs without exposing secret keys or URLs in the client application:

```python
resp = NightAuthApp.webhook("7kR0UedlVI", params="&action=notify", body='{"content": "Client notification"}')
print("Webhook Response:", resp)
```

### 14. Secure In-Memory File Download

Download encrypted server-side assets and process them directly in RAM:

```python
file_bytes = NightAuthApp.download("385624")

if file_bytes:
    print(f"Downloaded {len(file_bytes)} bytes securely.")
    # Process or execute file_bytes directly in memory using io.BytesIO
```

### 15. Realtime Chat Channels

```python
# Send a message to a channel
NightAuthApp.chat_send("Hello community!", channel="general")

# Fetch latest messages
messages = NightAuthApp.chat_get(channel="general")
if messages:
    for msg in messages:
        print(f"[{msg.get('author')}]: {msg.get('message')}")
```

### 16. Realtime Event Handlers (Server-Sent Events)

React immediately to administrative changes from the dashboard:

```python
NightAuthApp.on_session_invalidated = lambda reason: print(f"[ALERT] Session Invalidated: {reason}")
NightAuthApp.on_app_banned = lambda reason: print(f"[CRITICAL] Application Banned: {reason}")
NightAuthApp.on_app_status_changed = lambda status: print(f"[INFO] App Status: {status}")
NightAuthApp.on_version_updated = lambda ver: print(f"[UPDATE] New Version: v{ver}")
```

---

## 🖥️ Run the Console and Desktop Clients

The SDK lives in `sdk/nightauth.py`. The interactive terminal client is `console/main.py`, and the PyQt desktop client is `desktop/main.py`.

From this `source` directory, install dependencies and launch either client:

```bash
python -m pip install -r requirements.txt
python console/main.py
python desktop/main.py
```

The desktop client requires a graphical session. Configure the app name, API key, version, and optional token in the entry point before distributing your build.

---

---

## 🆚 Why NightAuth? (KeyAuth & Auth.gg Comparison)

| Feature | NightAuth | KeyAuth | Auth.gg |
| :--- | :---: | :---: | :---: |
| **Cryptography** | **End-to-End Curve25519 (X25519) + ChaCha20-Poly1305** | Static AES-CBC (Vulnerable to MITM & Proxy Interception) | Legacy HTTPS / Plain JSON |
| **Hardware ID (HWID)** | **Multi-Component Cryptographic Hash (Anti-Spoofing)** | Raw WMI Strings (Trivially Spoofed) | Simple Registry / MAC |
| **Edge Network Latency** | **< 35ms Global Anycast Edge Network** | Single-Origin VPS (Frequent Network Outages) | Unmaintained / High Latency |
| **Reseller System & Bots** | **Built-in Multi-Tier Credit Balances + Discord & Telegram Bots** | Manual API / Third-Party Scripts | Incomplete / Deprecated |
| **In-Memory Streaming** | **Zero-Disk Decryption with Direct Memory Execution & Buffer Wiping** | Disk Writes Required | Not Supported |
| **Internationalization** | **10 Languages Supported Out of the Box across Documentation & SDKs** | English Only | English Only |

Read the full architectural benchmark: [NightAuth vs KeyAuth vs Auth.gg](https://nightauth.org/blog/nightauth-vs-keyauth-authgg-comparison)

---

## 📄 License

This project is licensed under the **Elastic License 2.0**.

* You may not provide the software to third parties as a hosted or managed service.
* You may not move, change, disable, or circumvent the license key functionality.
* You may not alter, remove, or obscure any licensing or copyright notices.

See the [LICENSE](LICENSE) file for the full legal text.
