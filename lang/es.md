# NightAuth Python SDK — Danos una estrella en GitHub ⭐

SDK oficial de **NightAuth** para Python y suite de referencia completa (Interfaz Desktop en **PyQt6** y Consola Interactiva en **Rich**). Protege tu software contra piratería, ingeniería inversa y manipulación con licenciamiento cloud, bloqueo de HWID, chat en vivo y ejecución en memoria en minutos.

**Languages / Idiomas / Langues / Sprachen:**  
[English](../README.md) • [Español](es.md) • [Français](fr.md) • [Deutsch](de.md) • [Italiano](it.md) • [Português](pt.md) • [Русский](ru.md) • [Türkçe](tr.md) • [Polski](pl.md) • [中文](zh.md)

---

> [!NOTE]
> ### 📺 Tutoriales en Video y Configuración del Sistema
> Los video-tutoriales oficiales y las guías paso a paso de cómo configurar aplicaciones, planes, suscripciones, variables en la nube, webhooks y licencias en el panel de control de NightAuth **serán publicados próximamente** en nuestro portal y canal oficial.

---

## 📸 Capturas de Pantalla

### Aplicación de Escritorio (Desktop UI — PyQt6)

| Pantalla de Inicio / Autenticación | Panel de Control & Estadísticas |
| :---: | :---: |
| ![NightAuth Desktop Login](../image/desktop.png) | ![NightAuth Desktop Dashboard](../image/desktop-dashboard.png) |

### Aplicación de Consola (CLI — Rich)

| Inicio de Sesión en Terminal | Panel Interactivo de Consola |
| :---: | :---: |
| ![NightAuth Console Login](../image/console.png) | ![NightAuth Console Dashboard](../image/console-dashboard.png) |

---

## 🛡️ Prácticas de Seguridad Recomendadas

* **Compilación Nativa y Ofuscación:** Python es interpretado. Para distribuir tu software en producción, compila tus scripts a binarios C/C++ nativos (.pyd o .exe) usando **Nuitka** o **PyArmor**.
* **Virtualización de Código Empresarial:** Protege el ejecutable resultante utilizando virtualizadores de código y empaquetadores como **VMProtect**, **Themida** o **Enigma Protector**.
* **Integridad de Memoria y Anti-Debug:** NightAuth incluye escaneo integrado contra monitores y depuradores (HTTPDebugger, CheatEngine, x64dbg, Wireshark). Mantén estas protecciones activas en producción.
* **Ejecución Segura en Memoria:** Al descargar archivos con `api.download()`, **no guardes los bytes en el disco duro**. Transmítelos y ejecútalos directamente en memoria (mediante `io.BytesIO` o técnicas RunPE) y borra los búferes inmediatamente tras su uso.

---

## 📦 Requisitos e Instalación

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuración e Inicialización

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

Debes invocar `init()` antes de cualquier otra llamada. Establece el intercambio de claves efímeras Diffie-Hellman (X25519) y la sesión cifrada:

```python
NightAuthApp.init()

if not NightAuthApp.response.success:
    print(f"Error: {NightAuthApp.response.message}")
    exit(1)
```

---

## 🚀 Guía de Uso del SDK

### 1. Comprobar Validación de Sesión y Blacklist

```python
NightAuthApp.check()
if NightAuthApp.checkblack():
    exit(0)
```

### 2. Inicio de Sesión (Login con Usuario, Contraseña y 2FA)

```python
if NightAuthApp.login(username, password, two_factor_code=""):
    print(f"Welcome {NightAuthApp.user.username}")
```

### 3. Registro con Clave de Licencia

```python
if NightAuthApp.register(username, password, license_key, email=""):
    print("Registered successfully")
```

### 4. Acceso con Solo Clave de Licencia (Key Only)

```python
if NightAuthApp.license(license_key):
    print("License authenticated")
```

### 5. Actualizar Suscripción / Canjear Clave (Upgrade)

```python
if NightAuthApp.upgrade(username, new_license_key):
    print("Subscription upgraded")
```

### 6. Restablecer HWID (Hardware ID Lock)

```python
if NightAuthApp.reset_hwid(username, password, two_factor_code=""):
    print("HWID reset completed")
```

### 7. Recuperación de Contraseña (Forgot Password)

```python
if NightAuthApp.forgot_password(email):
    print("Recovery token sent")
```

### 8. Datos del Usuario Autenticado (`NightAuthApp.user`)

```python
print(NightAuthApp.user.username, NightAuthApp.user.ip, NightAuthApp.user.hwid)
for sub in NightAuthApp.user.subscriptions:
    print(sub.subscription, sub.expiry)
```

### 9. Variables en la Nube (Globales)

```python
val = NightAuthApp.var("server_motd")
```

### 10. Variables por Usuario (User Variables)

```python
NightAuthApp.set_user_var("discord", "user#0001")
val = NightAuthApp.get_user_var("discord")
```

### 11. Logs de Aplicación y Auditoría

```python
NightAuthApp.log("Security telemetry or detection")
```

### 12. Baneo de Usuarios

```python
NightAuthApp.ban("Tampering detected")
```

### 13. Webhooks Seguros del Lado del Servidor

```python
resp = NightAuthApp.webhook("7kR0UedlVI", params="&action=notify", body='{"content": "Notice"}')
```

### 14. Descarga Segura de Archivos en Memoria

```python
file_bytes = NightAuthApp.download("385624")
```

### 15. Canales de Chat en Vivo

```python
NightAuthApp.chat_send("Hello!", channel="general")
msgs = NightAuthApp.chat_get(channel="general")
```

### 16. Eventos en Tiempo Real (SSE)

```python
NightAuthApp.on_session_invalidated = lambda r: print(f"Session invalidated: {r}")
NightAuthApp.on_app_banned = lambda r: print(f"App banned: {r}")
NightAuthApp.on_app_status_changed = lambda s: print(f"Status changed: {s}")
NightAuthApp.on_version_updated = lambda v: print(f"Update: v{v}")
```

---

## 📄 Licencia

Este proyecto está bajo la licencia **Elastic License 2.0**. Consulta el archivo [LICENSE](../LICENSE) para el texto legal completo.
