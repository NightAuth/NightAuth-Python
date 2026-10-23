# NightAuth Python SDK — Deixe uma estrela no GitHub ⭐

SDK oficial do **NightAuth** para Python e suíte de cliente de referência completa (Interface Desktop moderna em **PyQt6** e CLI interativa em **Rich**). Proteja seu software contra pirataria, engenharia reversa e adulteração com licenciamento em nuvem, bloqueio de HWID, chat em tempo real e execução em memória em minutos.

**Languages / Idiomas / Langues / Sprachen:**  
[English](../README.md) • [Español](es.md) • [Français](fr.md) • [Deutsch](de.md) • [Italiano](it.md) • [Português](pt.md) • [Русский](ru.md) • [Türkçe](tr.md) • [Polski](pl.md) • [中文](zh.md)

---

> [!NOTE]
> ### 📺 Tutoriais em Vídeo e Guias de Configuração
> Tutoriais em vídeo oficiais e guias passo a passo explicando como configurar aplicativos, planos, assinaturas, variáveis na nuvem, webhooks e licenças no painel do NightAuth **serão publicados em breve**.

---

## 📸 Capturas de Tela

### Aplicativo Desktop (Desktop UI — PyQt6)

| Tela de Login / Autenticação | Painel de Controle & Assinaturas |
| :---: | :---: |
| ![NightAuth Desktop Login](../image/desktop.png) | ![NightAuth Desktop Dashboard](../image/desktop-dashboard.png) |

### Aplicativo de Console (CLI — Rich)

| Login no Terminal | Painel Interativo de Console |
| :---: | :---: |
| ![NightAuth Console Login](../image/console.png) | ![NightAuth Console Dashboard](../image/console-dashboard.png) |

---

## 🛡️ Práticas de Segurança Recomendadas

* **Compilação Nativa e Ofuscação:** O bytecode Python pode ser descompilado facilmente. Para ambientes de produção, compile seus scripts para binários nativos C/C++ (.pyd ou .exe) usando **Nuitka** ou **PyArmor**.
* **Virtualização de Código Empresarial:** Proteja o executável final utilizando empacotadores e protetores profissionais como **VMProtect**, **Themida** ou **Enigma Protector**.
* **Integridade de Memória e Anti-Debug:** O NightAuth possui detecção integrada contra ferramentas de inspeção e debuggers (HTTPDebugger, CheatEngine, x64dbg, Wireshark).
* **Execução Segura em Memória:** Ao baixar arquivos protegidos (`api.download()`), **não salve os bytes no disco rígido**. Execute-os diretamente na memória RAM (via `io.BytesIO` ou RunPE) e limpe os buffers após o término.

---

## 📦 Requisitos e Instalação

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração e Inicialização

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

Você deve chamar `init()` antes de qualquer operação para estabelecer a troca de chaves Diffie-Hellman (X25519) e a sessão criptografada:

```python
NightAuthApp.init()

if not NightAuthApp.response.success:
    print(f"Error: {NightAuthApp.response.message}")
    exit(1)
```

---

## 🚀 Guia de Uso do SDK

### 1. Validação de Sessão & Verificação de Lista Negra

```python
NightAuthApp.check()
if NightAuthApp.checkblack():
    exit(0)
```

### 2. Login com Usuário e Senha (e 2FA)

```python
if NightAuthApp.login(username, password, two_factor_code=""):
    print(f"Welcome {NightAuthApp.user.username}")
```

### 3. Registro com Chave de Licença

```python
if NightAuthApp.register(username, password, license_key, email=""):
    print("Registered successfully")
```

### 4. Autenticação Apenas com Chave de Licença

```python
if NightAuthApp.license(license_key):
    print("License authenticated")
```

### 5. Atualização de Conta / Resgatar Nova Chave

```python
if NightAuthApp.upgrade(username, new_license_key):
    print("Subscription upgraded")
```

### 6. Redefinir Bloqueio de HWID

```python
if NightAuthApp.reset_hwid(username, password, two_factor_code=""):
    print("HWID reset completed")
```

### 7. Recuperação de Senha / Conta

```python
if NightAuthApp.forgot_password(email):
    print("Recovery token sent")
```

### 8. Dados do Usuário (`NightAuthApp.user`)

```python
print(NightAuthApp.user.username, NightAuthApp.user.ip, NightAuthApp.user.hwid)
for sub in NightAuthApp.user.subscriptions:
    print(sub.subscription, sub.expiry)
```

### 9. Variáveis Globais na Nuvem

```python
val = NightAuthApp.var("server_motd")
```

### 10. Variáveis por Usuário

```python
NightAuthApp.set_user_var("discord", "user#0001")
val = NightAuthApp.get_user_var("discord")
```

### 11. Logs de Auditoria e Segurança

```python
NightAuthApp.log("Security telemetry or detection")
```

### 12. Banir Usuário & Bloquear Dispositivo

```python
NightAuthApp.ban("Tampering detected")
```

### 13. Webhooks Seguros do Lado do Servidor

```python
resp = NightAuthApp.webhook("7kR0UedlVI", params="&action=notify", body='{"content": "Notice"}')
```

### 14. Download Seguro de Arquivos na Memória

```python
file_bytes = NightAuthApp.download("385624")
```

### 15. Canais de Chat em Tempo Real

```python
NightAuthApp.chat_send("Hello!", channel="general")
msgs = NightAuthApp.chat_get(channel="general")
```

### 16. Ouvintes de Eventos em Tempo Real (SSE)

```python
NightAuthApp.on_session_invalidated = lambda r: print(f"Session invalidated: {r}")
NightAuthApp.on_app_banned = lambda r: print(f"App banned: {r}")
NightAuthApp.on_app_status_changed = lambda s: print(f"Status changed: {s}")
NightAuthApp.on_version_updated = lambda v: print(f"Update: v{v}")
```

---

## 📄 Licença

Este projeto é licenciado sob a **Elastic License 2.0**. Consulte o arquivo [LICENSE](../LICENSE) para o texto completo.
