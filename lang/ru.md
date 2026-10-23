# NightAuth Python SDK — Поставьте звезду на GitHub ⭐

Официальный **NightAuth** Python SDK и полный эталонный клиентский комплекс (современный Desktop GUI на **PyQt6** и интерактивный CLI в терминале на **Rich**). Защитите свое ПО от пиратства, реверс-инжиниринга и взлома с помощью облачного лицензирования, привязки к HWID, чата в реальном времени и исполнения в оперативной памяти.

**Languages / Idiomas / Langues / Sprachen:**  
[English](../README.md) • [Español](es.md) • [Français](fr.md) • [Deutsch](de.md) • [Italiano](it.md) • [Português](pt.md) • [Русский](ru.md) • [Türkçe](tr.md) • [Polski](pl.md) • [中文](zh.md)

---

> [!NOTE]
> ### 📺 Видеоуроки и инструкции по настройке системы
> Официальные видеоуроки и пошаговые руководства по настройке приложений, планов подписки, облачных переменных, вебхуков и ключей в панели NightAuth **будут опубликованы в ближайшее время** на официальном портале и канале.

---

## 📸 Скриншоты

### Десктопное приложение (Desktop UI — PyQt6)

| Окно входа / Аутентификация | Панель управления & Подписки |
| :---: | :---: |
| ![NightAuth Desktop Login](../image/desktop.png) | ![NightAuth Desktop Dashboard](../image/desktop-dashboard.png) |

### Консольное приложение (CLI — Rich)

| Вход через терминал | Интерактивная консоль |
| :---: | :---: |
| ![NightAuth Console Login](../image/console.png) | ![NightAuth Console Dashboard](../image/console-dashboard.png) |

---

## 🛡️ Рекомендуемые практики безопасности

* **Нативная компиляция и обфускация:** Байт-код Python легко декомпилируется. Для продакшн-распространения компилируйте скрипты в нативный машинный код C/C++ (.pyd или .exe) с помощью **Nuitka** или **PyArmor**.
* **Корпоративная виртуализация кода:** Защищайте полученный исполняемый файл профессиональными протекторами, такими как **VMProtect**, **Themida** или **Enigma Protector**.
* **Целостность памяти и Anti-Debug:** В NightAuth встроен модуль сканирования отладчиков и сетевых перехватчиков (HTTPDebugger, CheatEngine, x64dbg, Wireshark).
* **Безопасное исполнение в RAM:** При скачивании защищенных файлов (`api.download()`) **не сохраняйте байты на диск**. Загружайте и выполняйте полезную нагрузку напрямую из оперативной памяти (через `io.BytesIO` или RunPE).

---

## 📦 Требования и установка

```bash
pip install -r requirements.txt
```

---

## ⚙️ Конфигурация и инициализация

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

Вызовите `init()` перед любыми другими операциями для выполнения обмена ключами Diffie-Hellman (X25519) и установки сессии:

```python
NightAuthApp.init()

if not NightAuthApp.response.success:
    print(f"Error: {NightAuthApp.response.message}")
    exit(1)
```

---

## 🚀 Руководство по использованию SDK

### 1. Проверка сессии и статуса в черном списке

```python
NightAuthApp.check()
if NightAuthApp.checkblack():
    exit(0)
```

### 2. Вход по логину и паролю (и 2FA)

```python
if NightAuthApp.login(username, password, two_factor_code=""):
    print(f"Welcome {NightAuthApp.user.username}")
```

### 3. Регистрация с лицензионным ключом

```python
if NightAuthApp.register(username, password, license_key, email=""):
    print("Registered successfully")
```

### 4. Вход только по ключу лицензии (Key Only)

```python
if NightAuthApp.license(license_key):
    print("License authenticated")
```

### 5. Апгрейд аккаунта / Активация нового ключа

```python
if NightAuthApp.upgrade(username, new_license_key):
    print("Subscription upgraded")
```

### 6. Сброс привязки к оборудованию (Reset HWID)

```python
if NightAuthApp.reset_hwid(username, password, two_factor_code=""):
    print("HWID reset completed")
```

### 7. Восстановление пароля / аккаунта

```python
if NightAuthApp.forgot_password(email):
    print("Recovery token sent")
```

### 8. Данные пользователя (`NightAuthApp.user`)

```python
print(NightAuthApp.user.username, NightAuthApp.user.ip, NightAuthApp.user.hwid)
for sub in NightAuthApp.user.subscriptions:
    print(sub.subscription, sub.expiry)
```

### 9. Глобальные облачные переменные

```python
val = NightAuthApp.var("server_motd")
```

### 10. Пользовательские переменные

```python
NightAuthApp.set_user_var("discord", "user#0001")
val = NightAuthApp.get_user_var("discord")
```

### 11. Журнал аудита и безопасности

```python
NightAuthApp.log("Security telemetry or detection")
```

### 12. Блокировка пользователя и устройства

```python
NightAuthApp.ban("Tampering detected")
```

### 13. Безопасные вебхуки на стороне сервера

```python
resp = NightAuthApp.webhook("7kR0UedlVI", params="&action=notify", body='{"content": "Notice"}')
```

### 14. Безопасная загрузка файлов в память

```python
file_bytes = NightAuthApp.download("385624")
```

### 15. Каналы онлайн-чата

```python
NightAuthApp.chat_send("Hello!", channel="general")
msgs = NightAuthApp.chat_get(channel="general")
```

### 16. Обработчики событий реального времени (SSE)

```python
NightAuthApp.on_session_invalidated = lambda r: print(f"Session invalidated: {r}")
NightAuthApp.on_app_banned = lambda r: print(f"App banned: {r}")
NightAuthApp.on_app_status_changed = lambda s: print(f"Status changed: {s}")
NightAuthApp.on_version_updated = lambda v: print(f"Update: v{v}")
```

---

## 📄 Лицензия

Проект распространяется по лицензии **Elastic License 2.0**. Полный текст доступен в файле [LICENSE](../LICENSE).
