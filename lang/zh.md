# NightAuth Python SDK — 在 GitHub 上为我们点亮星标 ⭐

官方 **NightAuth** Python SDK 及完整参考客户端套件（基于 **PyQt6** 的现代化桌面客户端与基于 **Rich** 的终端交互式控制台）。在数分钟内为您的软件集成云端授权激活、硬件防盗绑定（HWID Lock）、反作弊检测、实时聊天与内存防转储保护。

**Languages / Idiomas / Langues / Sprachen:**  
[English](../README.md) • [Español](es.md) • [Français](fr.md) • [Deutsch](de.md) • [Italiano](it.md) • [Português](pt.md) • [Русский](ru.md) • [Türkçe](tr.md) • [Polski](pl.md) • [中文](zh.md)

---

> [!NOTE]
> ### 📺 视频教程与系统部署指南
> 官方视频操作教程以及关于如何在 NightAuth 管理后台配置应用、订阅计划、云端变量、Webhook 与密钥分发的分步指南**即将发布**，敬请关注官方网站与频道。

---

## 📸 界面截图

### 桌面图形界面客户端 (Desktop UI — PyQt6)

| 登录 / 激活认证界面 | 用户面板与授权监控 |
| :---: | :---: |
| ![NightAuth Desktop Login](../image/desktop.png) | ![NightAuth Desktop Dashboard](../image/desktop-dashboard.png) |

### 控制台客户端 (CLI — Rich)

| 终端登录交互 | 控制台交互式仪表盘 |
| :---: | :---: |
| ![NightAuth Console Login](../image/console.png) | ![NightAuth Console Dashboard](../image/console-dashboard.png) |

---

## 🛡️ 推荐安全防护实践

* **原生机器码编译与代码混淆：** Python 字节码极易被反编译还原。发布商业软件时，务必使用 **Nuitka** 或 **PyArmor** 将脚本编译为原生 C/C++ 二进制文件（.pyd 或 .exe）。
* **企业级代码虚拟化保护：** 使用商业级代码加壳与虚拟化保护器（如 **VMProtect**、**Themida** 或 **Enigma Protector**）对最终二进制文件进行保护。
* **内存完整性与反调试防护：** NightAuth 原生集成了针对常见逆向与监控工具的防护检测（HTTPDebugger、CheatEngine、x64dbg、Wireshark 等）。请确保在生产环境中保持启用。
* **内存中安全执行与加载：** 使用 `api.download()` 下载受保护的核心二进制文件时，**切勿将未加密的字节写入物理磁盘**。请直接在内存中执行载入（例如配合 `io.BytesIO` 或内存注入/RunPE 技术），使用完毕后立即覆写清空内存缓冲区。

---

## 📦 依赖环境与快速安装

```bash
pip install -r requirements.txt
```

---

## ⚙️ 应用程序配置与客户端实例化

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

在调用任何其他 SDK 功能之前，必须首先调用 `init()` 完成 Diffie-Hellman（X25519）临时密钥协商与加密会话绑定：

```python
NightAuthApp.init()

if not NightAuthApp.response.success:
    print(f"Error: {NightAuthApp.response.message}")
    exit(1)
```

---

## 🚀 SDK 核心功能调用指南

### 1. 校验当前会话与硬件黑名单状态

```python
NightAuthApp.check()
if NightAuthApp.checkblack():
    exit(0)
```

### 2. 用户名密码登录认证（支持 2FA 双因素验证）

```python
if NightAuthApp.login(username, password, two_factor_code=""):
    print(f"Welcome {NightAuthApp.user.username}")
```

### 3. 凭授权卡密注册新用户

```python
if NightAuthApp.register(username, password, license_key, email=""):
    print("Registered successfully")
```

### 4. 纯卡密授权登录（Key Only 免注册模式）

```python
if NightAuthApp.license(license_key):
    print("License authenticated")
```

### 5. 账户升级与充值续费（Upgrade 绑定新卡密）

```python
if NightAuthApp.upgrade(username, new_license_key):
    print("Subscription upgraded")
```

### 6. 换绑解绑硬件锁（HWID Reset）

```python
if NightAuthApp.reset_hwid(username, password, two_factor_code=""):
    print("HWID reset completed")
```

### 7. 找回密码 / 账户重置验证

```python
if NightAuthApp.forgot_password(email):
    print("Recovery token sent")
```

### 8. 读取已认证用户信息 (`NightAuthApp.user`)

```python
print(NightAuthApp.user.username, NightAuthApp.user.ip, NightAuthApp.user.hwid)
for sub in NightAuthApp.user.subscriptions:
    print(sub.subscription, sub.expiry)
```

### 9. 读取云端全局变量 (Cloud Variables)

```python
val = NightAuthApp.var("server_motd")
```

### 10. 读写用户专属持久化变量 (User Variables)

```python
NightAuthApp.set_user_var("discord", "user#0001")
val = NightAuthApp.get_user_var("discord")
```

### 11. 发送安全审计与反作弊告警日志

```python
NightAuthApp.log("Security telemetry or detection")
```

### 12. 封禁违规用户与拉黑机器硬件码

```python
NightAuthApp.ban("Tampering detected")
```

### 13. 服务端代理安全 Webhook 请求

```python
resp = NightAuthApp.webhook("7kR0UedlVI", params="&action=notify", body='{"content": "Notice"}')
```

### 14. 安全内存文件下载与动态加载

```python
file_bytes = NightAuthApp.download("385624")
```

### 15. 用户端实时在线聊天室频道

```python
NightAuthApp.chat_send("Hello!", channel="general")
msgs = NightAuthApp.chat_get(channel="general")
```

### 16. 实时管理事件推送监听器 (SSE)

```python
NightAuthApp.on_session_invalidated = lambda r: print(f"Session invalidated: {r}")
NightAuthApp.on_app_banned = lambda r: print(f"App banned: {r}")
NightAuthApp.on_app_status_changed = lambda s: print(f"Status changed: {s}")
NightAuthApp.on_version_updated = lambda v: print(f"Update: v{v}")
```

---

## 📄 软件许可证协议

本项目基于 **Elastic License 2.0** 许可证开源。请查阅项目中的 [LICENSE](../LICENSE) 文件了解完整法律协议。
