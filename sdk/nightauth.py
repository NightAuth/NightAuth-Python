
import base64
import functools
import hashlib
import http.client
import json
import os
import platform
import socket
import ssl
import subprocess
import threading
import time
import urllib.parse
import urllib.request
import urllib.error
import uuid
import zlib
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes

DEFAULT_API_URL = "https://nightauth.org/api/v1"
DEFAULT_SIGNING_PUBLIC_KEY = "cdb2285db481666ce40003aadb874c8751dbeb9a0672a37f740dfe881ecdc742"
DEFAULT_SEALED_BOX_PUBLIC_KEY = "b773fc4f6cf1a0938e78e714c3d84cb386584bea24728923008471a6cd203213"
HKDF_INFO = b"nightauth-v1-e2e"
SEAL_INFO = b"nightauth-v1-init-seal"

MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_DOWNLOAD_RESPONSE_BYTES = MAX_FILE_BYTES * 4 // 3 + 1024 * 1024

@dataclass
class Response:
    success: bool = False
    message: str = ""
    error: Optional[str] = None
    url: Optional[str] = None

@dataclass
class SubscriptionData:
    subscription: str = ""
    key: str = ""
    expiry: str = ""
    time_left: int = 0

@dataclass
class UserData:
    username: str = ""
    email: str = ""
    hwid: str = ""
    ip: str = ""
    status: str = ""
    created_at: str = ""
    last_login_at: str = ""
    subscriptions: List[SubscriptionData] = field(default_factory=list)

@dataclass
class AppData:
    total_users: int = 0
    online_users: int = 0
    total_keys: int = 0
    version: str = ""

@dataclass
class AppStats:
    total_users: int = 0
    active_users: int = 0
    banned_users: int = 0
    total_licenses: int = 0
    used_licenses: int = 0
    unused_licenses: int = 0
    version: str = ""

    @property
    def total_keys(self) -> int:
        return self.total_licenses

    @property
    def online_users(self) -> int:
        return self.active_users

@dataclass
class ChatMessage:
    id: str = ""
    author: str = ""
    message: str = ""
    timestamp: str = ""

@dataclass
class TwoFactorSetupData:
    secret: str = ""
    qr_data_url: str = ""
    uri: str = ""

@dataclass
class TwoFactorConfirmData:
    backup_codes: List[str] = field(default_factory=list)

class SecurityProtections:
    BLACKLISTED_PROCESSES = (
        "fiddler", "wireshark", "httpdebugger", "httpdebuggerui", "x64dbg", "x32dbg",
        "ida", "ida64", "charles", "dnspy", "de4dot", "scylla", "processhacker",
        "cheatengine", "ollydbg"
    )
    _cached_hwid: Optional[str] = None
    _hwid_lock = threading.Lock()

    @classmethod
    def run_security_checks(cls) -> None:
        if os.getenv("NIGHTAUTH_IGNORE_SECURITY") == "1":
            return
        cls.check_system_proxy()
        cls.check_blacklisted_processes()

    @classmethod
    def check_system_proxy(cls) -> None:
        if os.getenv("NIGHTAUTH_IGNORE_SECURITY") == "1":
            return
        try:
            proxies = urllib.request.getproxies()
            if proxies and ("http" in proxies or "https" in proxies):
                raise SecurityError("System proxy detected. Disable proxies or debuggers to run.")
        except SecurityError:
            raise
        except Exception:
            pass

    @classmethod
    def check_blacklisted_processes(cls) -> None:
        if os.getenv("NIGHTAUTH_IGNORE_SECURITY") == "1":
            return
        try:
            if platform.system() == "Windows":
                out = subprocess.check_output("tasklist /FO CSV /NH", shell=True, text=True, stderr=subprocess.DEVNULL)
                lower_out = out.lower()
                for bad in cls.BLACKLISTED_PROCESSES:
                    if bad in lower_out:
                        raise SecurityError(f"Blacklisted process detected: {bad}")
        except SecurityError:
            raise
        except Exception:
            pass

    @classmethod
    def get_hardware_id(cls) -> str:
        if cls._cached_hwid is not None:
            return cls._cached_hwid
        with cls._hwid_lock:
            if cls._cached_hwid is not None:
                return cls._cached_hwid
            try:
                hostname = (os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME") or socket.gethostname() or "unknown_host").strip().upper()
                username = (os.getenv("USERNAME") or os.getenv("USER") or "unknown_user").strip().lower()
                raw = f"{hostname}-{username}-nightauth-hwid"
                cls._cached_hwid = hashlib.sha256(raw.encode("utf-8")).hexdigest().lower()
                return cls._cached_hwid
            except Exception:
                cls._cached_hwid = hashlib.sha256(socket.gethostname().encode("utf-8")).hexdigest().lower()
                return cls._cached_hwid

class ResponseTooLarge(ValueError):
    """A response body went over the size bound; carries the real HTTP status."""

    def __init__(self, message: str, status: int = 0):
        super().__init__(message)
        self.status = status

class SecurityError(Exception):
    pass

class CryptographicException(Exception):
    """Security failure: the handshake signature, key or timestamp does not verify, or a response is not bound
    to its request, not encrypted, or does not decrypt. The answer is never trusted."""

class NightAuthStreamException(Exception):
    """The event stream was refused by the server (status/error) or failed in transport (status 0, network_error)."""

    def __init__(self, status_code: int, error: Optional[str], message: Optional[str] = None):
        super().__init__(message or error or "Stream exception")
        self.status_code = status_code
        self.error = error

class _StreamHTTPConnection(http.client.HTTPConnection):
    """Connection of the event stream. It reports its socket as soon as it connects, so a stop can shut the stream
    down while the request still waits for the response headers, which the server sends with its first frame."""

    def __init__(self, *args: Any, on_socket: Optional[Callable[[Any], None]] = None, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._on_socket = on_socket

    def connect(self) -> None:
        super().connect()
        if self._on_socket is not None:
            self._on_socket(self.sock)

class _StreamHTTPSConnection(http.client.HTTPSConnection):
    """TLS variant of _StreamHTTPConnection (the socket is reported after the TLS handshake)."""

    def __init__(self, *args: Any, on_socket: Optional[Callable[[Any], None]] = None, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._on_socket = on_socket

    def connect(self) -> None:
        super().connect()
        if self._on_socket is not None:
            self._on_socket(self.sock)

class _StreamHTTPHandler(urllib.request.HTTPHandler):
    def __init__(self, on_socket: Callable[[Any], None]):
        super().__init__()
        self._on_socket = on_socket

    def http_open(self, req):
        return self.do_open(functools.partial(_StreamHTTPConnection, on_socket=self._on_socket), req)

class _StreamHTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self, context: ssl.SSLContext, on_socket: Callable[[Any], None]):
        super().__init__(context=context)
        self._on_socket = on_socket

    def https_open(self, req):
        return self.do_open(functools.partial(_StreamHTTPSConnection, on_socket=self._on_socket), req,
                            context=self._context)

def _shutdown_socket(sock: Any) -> None:
    try:
        if sock is not None:
            sock.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass

class SseParser:
    """SSE frame parser: data lines (multi-line), plain decimal id lines, comments and unknown fields ignored,
    CRLF/LF/CR accepted; an event above MAX_EVENT_CHARS is a protocol error."""

    MAX_EVENT_CHARS = 65536

    def __init__(self, on_frame: Callable[[str, Optional[str]], None]):
        self._on_frame = on_frame
        self._buffer = ""
        self._data: List[str] = []
        self._data_chars = 0
        self._id: Optional[str] = None
        self._skip_lf = False

    def push(self, text: str) -> None:
        data = self._buffer + text
        self._buffer = ""
        if self._skip_lf and data[:1] == "\n":
            data = data[1:]
        self._skip_lf = False
        start = 0
        i = 0
        while i < len(data):
            c = data[i]
            if c != "\n" and c != "\r":
                i += 1
                continue
            self._line(data[start:i])
            if c == "\r":
                if data[i + 1:i + 2] == "\n":
                    i += 1
                elif i + 1 >= len(data):
                    self._skip_lf = True
            i += 1
            start = i
        self._buffer = data[start:]
        if len(self._buffer) + self._data_chars > self.MAX_EVENT_CHARS:
            raise ValueError("Event exceeds size limit.")

    def _line(self, line: str) -> None:
        if line == "":
            frame_id = self._id
            self._id = None
            if not self._data:
                return
            payload = "\n".join(self._data)
            self._data = []
            self._data_chars = 0
            self._on_frame(payload, frame_id)
            return
        if line[0] == ":":
            return
        colon = line.find(":")
        field_name = line if colon < 0 else line[:colon]
        value = "" if colon < 0 else line[colon + 1:]
        if value[:1] == " ":
            value = value[1:]
        if field_name == "data":
            self._data.append(value)
            self._data_chars += len(value) + 1
        elif field_name == "id" and value.isascii() and value.isdigit() and 1 <= len(value) <= 15:
            self._id = value

class Api:
    SERVER_SIGNING_PUBLIC_KEY = DEFAULT_SIGNING_PUBLIC_KEY
    SERVER_SEALED_BOX_PUBLIC_KEY = DEFAULT_SEALED_BOX_PUBLIC_KEY
    HKDF_INFO = HKDF_INFO
    SEAL_INFO = SEAL_INFO

    def __init__(
        self,
        name: str = "",
        api_key: Optional[str] = None,
        version: str = "1.0",
        token: Optional[str] = None,
        api_url: Optional[str] = None,
        security_check: Optional[Callable[[], None]] = None,
        allow_insecure_loopback: bool = False,
        apiKey: Optional[str] = None,
        apikey: Optional[str] = None,
        **kwargs: Any
    ):
        resolved_key = api_key if api_key is not None else (apiKey if apiKey is not None else apikey)
        self.name = name or ""
        self.api_key = resolved_key or ""
        self.version = version or "1.0"
        self.token = token
        self.api_url = (api_url or DEFAULT_API_URL).rstrip("/")
        self.allow_insecure_loopback = allow_insecure_loopback

        parsed = urllib.parse.urlsplit(self.api_url)
        is_loopback = parsed.hostname in ("localhost", "127.0.0.1", "::1")
        if parsed.scheme != "https" and not (parsed.scheme == "http" and is_loopback and allow_insecure_loopback):
            raise ValueError("HTTPS is required; insecure loopback needs explicit allow_insecure_loopback=True")

        self.response = Response()
        self.user = UserData()
        self.app = AppData()
        self.pending_download_url: str = ""
        self.required_version: str = ""

        self.on_session_invalidated: Optional[Callable[[str], None]] = None
        self.on_app_banned: Optional[Callable[[str], None]] = None
        self.on_app_status_changed: Optional[Callable[[str], None]] = None
        self.on_version_updated: Optional[Callable[[str], None]] = None
        self.on_chat_message_received: Optional[Callable[[ChatMessage, str], None]] = None
        self.on_resync_required: Optional[Callable[[], None]] = None
        self.last_event_id: Optional[str] = None
        self.stream_exception: Optional[NightAuthStreamException] = None

        self._session_key: Optional[str] = None
        self._shared_key: Optional[bytes] = None
        self._is_initialized = False
        self._security_check = security_check or SecurityProtections.run_security_checks
        self._events_stop_event: Optional[threading.Event] = None
        self._events_response = None
        self._events_socket = None
        self._events_thread: Optional[threading.Thread] = None
        self._disposed = False
        self._call_lock = threading.RLock()

        self._security_check()

    @property
    def user_data(self) -> UserData:
        return self.user

    @property
    def app_data(self) -> AppData:
        return self.app

    def set_server_keys(self, signing_key_hex: str, sealed_box_key_hex: str) -> None:
        """Pins this client to another server's public keys (self-hosted, staging, rotation). Both are 32-byte keys
        in hex; anything else raises ValueError and keeps the current keys. The next handshake verifies against them."""
        keys = []
        for name, value in (("signing_key_hex", signing_key_hex), ("sealed_box_key_hex", sealed_box_key_hex)):
            text = str(value or "")
            if len(text) != 64 or any(c not in "0123456789abcdefABCDEF" for c in text):
                raise ValueError(f"{name} must be 32 bytes as hex")
            keys.append(text.lower())
        self.SERVER_SIGNING_PUBLIC_KEY, self.SERVER_SEALED_BOX_PUBLIC_KEY = keys

    def init(self) -> None:
        self._security_check()

        if not self.name or not self.api_key:
            self._set_error("Application credentials missing: please specify name and apikey.", "missing_credentials")
            return

        self._session_key = None
        self._shared_key = None
        self._is_initialized = False

        client_priv = X25519PrivateKey.generate()
        client_pub = client_priv.public_key()
        client_pub_bytes = client_pub.public_bytes_raw()
        k1_hex = client_pub_bytes.hex().lower()

        new_session_key = uuid.uuid4().hex

        payload = {
            "apikey": self.api_key,
            "name": self.name,
            "version": self.version,
            "id": new_session_key,
            "k1": k1_hex
        }

        sealed_payload_b64 = self.crypto_box_seal(json.dumps(payload), self.SERVER_SEALED_BOX_PUBLIC_KEY)
        request_body = json.dumps({"p": sealed_payload_b64})

        try:
            status_code, resp_content = self._post_raw("/init", request_body)
        except Exception as e:
            self._set_error("Initialization failed: network request failed.", self._transport_code(e))
            return

        try:
            resp_json = json.loads(resp_content)
        except Exception:
            resp_json = None

        if status_code != 200:
            if isinstance(resp_json, dict):
                if resp_json.get("downloadUrl"):
                    self.pending_download_url = str(resp_json["downloadUrl"])
                if resp_json.get("requiredVersion"):
                    self.required_version = str(resp_json["requiredVersion"])
                if isinstance(resp_json.get("error"), str) and resp_json["error"]:
                    self._set_error(resp_json.get("message") or resp_json["error"], resp_json["error"])
                else:
                    self._set_error("Initialization failed: invalid response.", "invalid_response")
            else:
                self._set_error("Initialization failed: invalid response.", "invalid_response")
            return

        if not isinstance(resp_json, dict):
            self._set_error("Failed to parse handshake response", "invalid_response")
            return

        if not resp_json.get("success"):
            self._set_error(
                resp_json.get("message") or resp_json.get("error") or "Failed to initialize handshake",
                resp_json.get("error")
            )
            return

        k2_hex = resp_json.get("k2", "")
        ts = resp_json.get("ts", 0)
        sig_b64 = resp_json.get("sig", "")

        now_ms = int(time.time() * 1000)
        if (not isinstance(k2_hex, str) or len(k2_hex) != 64 or not isinstance(ts, (int, float))
                or not self.verify_server_signature(k2_hex, self.SERVER_SIGNING_PUBLIC_KEY, ts, sig_b64)
                or ts < now_ms - 90000 or ts > now_ms + 90000):
            self._set_error("Security integrity breach: Invalid server signature.")
            raise CryptographicException("Untrusted or stale initialization response.")

        server_pub_bytes = bytes.fromhex(k2_hex)
        server_pub = X25519PublicKey.from_public_bytes(server_pub_bytes)
        secret = client_priv.exchange(server_pub)

        self._shared_key = self.hkdf_extract_and_expand(secret, self.HKDF_INFO, 32)
        self._session_key = new_session_key
        self._is_initialized = True

        self._set_success("Initialized successfully.")

    def login(self, username: str, password: str, totp_code: Optional[str] = None) -> bool:
        self._check_init()
        self._security_check()

        body = self._create_base_payload()
        body["version"] = self.version
        body["username"] = username
        body["password"] = password
        body["hwid"] = SecurityProtections.get_hardware_id()
        if totp_code:
            body["totpCode"] = totp_code

        resp = self._send_encrypted("/login", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Login failed"
            err = resp.get("error") if resp else "login_failed"
            self._set_error(msg or "Login failed", err)
            return False

        self._populate_user_data(resp)
        self.start_realtime_event_listener()
        self._set_success("Logged in successfully.")
        return True

    def register(self, username: str, password: str, key: str, email: str = "") -> bool:
        self._check_init()
        self._security_check()

        body = self._create_base_payload()
        body["version"] = self.version
        body["username"] = username
        body["password"] = password
        body["key"] = key
        if email:
            body["email"] = email
        body["hwid"] = SecurityProtections.get_hardware_id()

        resp = self._send_encrypted("/register", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Registration failed"
            err = resp.get("error") if resp else "registration_failed"
            self._set_error(msg or "Registration failed", err)
            return False

        self._populate_user_data(resp)
        self.start_realtime_event_listener()
        self._set_success("Registered successfully.")
        return True

    def license(self, key: str, totp_code: Optional[str] = None) -> bool:
        """Redeems a license key. totp_code is required by the server when the key's user has 2FA enabled."""
        self._check_init()
        self._security_check()

        body = self._create_base_payload()
        body["version"] = self.version
        body["key"] = key
        body["hwid"] = SecurityProtections.get_hardware_id()
        if totp_code:
            body["totpCode"] = totp_code

        resp = self._send_encrypted("/license", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "License activation failed"
            err = resp.get("error") if resp else "license_failed"
            self._set_error(msg or "License activation failed", err)
            return False

        self._populate_user_data(resp)
        self.start_realtime_event_listener()
        self._set_success("License verified successfully.")
        return True

    def upgrade(self, username: str, key: str) -> bool:
        self._check_init()
        body = self._create_base_payload()
        if username and username.strip():
            body["username"] = username
        body["key"] = key

        resp = self._send_encrypted("/upgrade", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Upgrade failed"
            err = resp.get("error") if resp else "upgrade_failed"
            self._set_error(msg or "Upgrade failed", err)
            return False

        self._set_success("Subscription upgraded successfully.")
        return True

    def heartbeat(self) -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["version"] = self.version

        resp = self._send_encrypted("/heartbeat", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Heartbeat rejected"
            err = resp.get("error") if resp else "heartbeat_failed"
            self._set_error(msg or "Heartbeat rejected", err)
            if err in ("session_invalid", "session_not_validated", "unauthenticated"):
                self.stop_realtime_event_listener()
                if self.on_session_invalidated:
                    self.on_session_invalidated("Session terminated or invalid (Heartbeat failure)")
            return False

        self._set_success("Session alive.")
        return True

    def check(self) -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["version"] = self.version

        resp = self._send_encrypted("/check", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Session invalid"
            err = resp.get("error") if resp else "check_failed"
            self._set_error(msg or "Session invalid", err)
            if err in ("session_invalid", "no_active_subscription", "subscription_paused", "unauthenticated"):
                self.stop_realtime_event_listener()
                if self.on_session_invalidated:
                    self.on_session_invalidated(f"Session check rejected: {err}")
            return False

        self.user.subscriptions.clear()
        subs = resp.get("subscriptions", [])
        if isinstance(subs, list):
            for item in subs:
                if not isinstance(item, dict):
                    continue
                tl = item.get("timeleft", item.get("timeLeft", 0))
                self.user.subscriptions.append(SubscriptionData(
                    subscription=str(item.get("subscription", "")),
                    key=str(item.get("key", "")),
                    expiry=str(item.get("expiry", item.get("expiresAt", ""))),
                    time_left=int(tl) if tl is not None else 0
                ))

        self._set_success("Session valid.")
        return True

    def logout(self) -> bool:
        self.stop_realtime_event_listener()
        body = self._create_base_payload()

        self._check_init()
        result = None
        try:
            result = self._send_encrypted("/logout", body)
        except CryptographicException:
            raise
        except Exception:
            result = None
        confirmed = isinstance(result, dict) and result.get("success") is True

        self.user = UserData()
        self._session_key = None
        self._shared_key = None
        self._is_initialized = False
        code = result.get("error") if isinstance(result, dict) else None
        if confirmed:
            self._set_success("Logged out successfully.")
        elif code in ("network_error", "timeout", "invalid_response", "response_too_large", "handshake_required"):
            self._set_error(str(result.get("message") or code), code)
        else:
            self._set_error("Local session cleared; server revocation unconfirmed.", "logout_unconfirmed")
        return confirmed

    def change_username(self, new_username: str, password: str) -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["newUsername"] = new_username
        body["password"] = password

        resp = self._send_encrypted("/change-username", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Failed to change username"
            err = resp.get("error") if resp else "change_username_failed"
            self._set_error(msg or "Failed to change username", err)
            return False

        self.user.username = new_username
        self.stop_realtime_event_listener()
        self._set_success("Username changed successfully.")
        return True

    def reset_hwid(self, username: str, password: str, totp_code: Optional[str] = None) -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["username"] = username
        body["password"] = password
        if totp_code:
            body["totpCode"] = totp_code

        resp = self._send_encrypted("/hwid-reset", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "HWID reset failed"
            err = resp.get("error") if resp else "hwid_reset_failed"
            self._set_error(msg or "HWID reset failed", err)
            return False

        self.stop_realtime_event_listener()
        self._set_success(resp.get("message") or "HWID reset successfully.")
        return True

    def ban(self, reason: Optional[str] = None) -> bool:
        self._check_init()
        body = self._create_base_payload()
        if reason:
            body["reason"] = reason

        resp = self._send_encrypted("/ban", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Failed to self-report ban"
            err = resp.get("error") if resp else "ban_failed"
            self._set_error(msg or "Failed to self-report ban", err)
            return False

        self._set_success("Account banned.")
        return True

    def check_blacklist(self, hwid: Optional[str] = None) -> Dict[str, Any]:
        """Returns the server's full answer (`success`, `blacklisted`, `error`, ...), so a refusal is
        never mistaken for "not blacklisted"."""
        self._check_init()
        body = self._create_base_payload()
        body["hwid"] = hwid or SecurityProtections.get_hardware_id()

        resp = self._send_encrypted("/check-blacklist", body)
        if not resp or resp.get("success") is not True:
            self._set_error(
                (resp or {}).get("message") or "Blacklist check failed",
                (resp or {}).get("error") or "check_blacklist_failed"
            )
        else:
            self._set_success(resp.get("message") or "Blacklist checked.")
        return resp if isinstance(resp, dict) else {"success": False, "error": "invalid_response", "message": "Unexpected check-blacklist reply."}

    def checkblack(self) -> bool:
        """Helper checking if current machine HWID is blacklisted."""
        res = self.check_blacklist()
        return bool(res.get("blacklisted", False))

    def check_black(self) -> bool:
        return self.checkblack()

    def verify_file_hash(self, file_hash: str) -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["hash"] = file_hash

        resp = self._send_encrypted("/verify-hash", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Hash check failed"
            err = resp.get("error") if resp else "verify_hash_failed"
            self._set_error(msg or "Hash check failed", err)
            return False

        return bool(resp.get("verified") is True)

    def forgot_password(self, email: str) -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["email"] = email

        resp = self._send_encrypted("/forgot-password", body)
        if not resp or resp.get("success") is not True:
            self._set_error((resp or {}).get("message") or "Forgot password failed", (resp or {}).get("error") or "forgot_password_failed")
            return False
        self._set_success("Password reset requested.")
        return True

    def reset_password(self, token: str, new_password: str) -> bool:
        body = {
            "token": token,
            "newPassword": new_password
        }
        try:
            status, text = self._post_raw("/reset-password", json.dumps(body))
        except Exception as e:
            self._set_error("Failed to reset password: network request failed.", self._transport_code(e))
            return False

        try:
            resp = json.loads(text)
        except Exception:
            resp = None
        if not isinstance(resp, dict):
            self._set_error("Failed to reset password: invalid response.", "invalid_response")
            return False

        if not resp.get("success"):
            msg = resp.get("message") or resp.get("error") or "Failed to reset password"
            self._set_error(msg, resp.get("error") or "reset_password_failed")
            return False

        self._set_success("Password has been reset.")
        return True

    def setup_2fa(self) -> Optional[TwoFactorSetupData]:
        self._check_init()
        body = self._create_base_payload()

        resp = self._send_encrypted("/2fa/setup", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "2FA setup failed"
            err = resp.get("error") if resp else "2fa_setup_failed"
            self._set_error(msg or "2FA setup failed", err)
            return None

        return TwoFactorSetupData(
            secret=str(resp.get("secret", "")),
            qr_data_url=str(resp.get("qr", "")),
            uri=str(resp.get("uri", ""))
        )

    def confirm_2fa(self, code: str) -> Optional[TwoFactorConfirmData]:
        self._check_init()
        body = self._create_base_payload()
        body["code"] = code

        resp = self._send_encrypted("/2fa/confirm", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "2FA confirmation failed"
            err = resp.get("error") if resp else "2fa_confirm_failed"
            self._set_error(msg or "2FA confirmation failed", err)
            return None

        result = TwoFactorConfirmData()
        arr = resp.get("backupCodes", [])
        if isinstance(arr, list):
            result.backup_codes = [str(b) for b in arr if b is not None]
        return result

    def disable_2fa(self, password: str, code: str) -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["password"] = password
        body["code"] = code

        resp = self._send_encrypted("/2fa/disable", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Failed to disable 2FA"
            err = resp.get("error") if resp else "2fa_disable_failed"
            self._set_error(msg or "Failed to disable 2FA", err)
            return False

        self._set_success("2FA disabled.")
        return True

    def get_global_var(self, key: str) -> str:
        self._check_init()
        body = self._create_base_payload()
        body["varName"] = key

        resp = self._send_encrypted("/global-var", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Variable not found"
            err = resp.get("error") if resp else "var_not_found"
            self._set_error(msg or "Variable not found", err)
            return ""

        return str(resp.get("value", ""))

    def get_user_variables(self) -> Optional[List[Dict[str, Any]]]:
        self._check_init()
        body = self._create_base_payload()

        resp = self._send_encrypted("/user-vars/get", body)
        if not resp or not resp.get("success"):
            self._set_error(
                (resp or {}).get("message") or "User variables not found",
                (resp or {}).get("error") or "user_vars_get_failed"
            )
            return None
        self._set_success("User variables retrieved.")
        variables = resp.get("variables")
        return variables if isinstance(variables, list) else []

    def get_user_var(self, key: str) -> str:
        self._check_init()
        body = self._create_base_payload()
        body["key"] = key

        resp = self._send_encrypted("/user-vars/get", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "User variable not found"
            err = resp.get("error") if resp else "user_var_not_found"
            self._set_error(msg or "User variable not found", err)
            return ""

        if "value" in resp and resp["value"] is not None:
            return str(resp["value"])
        if "variables" in resp and isinstance(resp["variables"], list):
            for item in resp["variables"]:
                if isinstance(item, dict) and item.get("key") == key:
                    return str(item.get("value", ""))
        return ""

    def set_user_var(self, key: str, value: str) -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["key"] = key
        body["value"] = value

        resp = self._send_encrypted("/user-vars/set", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Failed to set variable"
            err = resp.get("error") if resp else "set_user_var_failed"
            self._set_error(msg or "Failed to set variable", err)
            return False

        self._set_success("User variable saved.")
        return True

    def download_file(self, file_id: str) -> Optional[bytes]:
        """Download a file with a file-scoped ticket.

        Sends an encrypted access-ticket request, then GET /files/download?ticket=...
        The server returns base64(gzip(content)); the decompressed bytes are returned.
        Redirects are refused. Returns None on failure, with api.response set.
        """
        self._check_init()
        ticket_body = self._create_base_payload()
        ticket_body["scope"] = "file"
        ticket_body["resourceId"] = str(file_id)

        ticket_resp = self._send_encrypted("/access-ticket", ticket_body)
        if not ticket_resp or not ticket_resp.get("success") or not ticket_resp.get("ticket"):
            msg = ticket_resp.get("message") if ticket_resp else None
            err = ticket_resp.get("error") if ticket_resp else None
            self._set_error(msg or "File access ticket denied", err or "ticket_denied")
            return None

        ticket = str(ticket_resp["ticket"])
        try:
            status, raw = self._get_raw(
                f"/files/download?ticket={urllib.parse.quote(ticket, safe='')}",
                MAX_DOWNLOAD_RESPONSE_BYTES,
            )
        except Exception as e:
            failure = self._transport_failure(e)
            self._set_error(failure["message"], failure["error"])
            return None

        if 300 <= status < 400:
            self._set_error("File download redirected to an external location; redirects are refused.", "external_download")
            self.response.url = getattr(self, "_last_get_location", None)
            return None

        try:
            resp = json.loads(raw.decode("utf-8"))
        except Exception:
            resp = None
        if status != 200 or not isinstance(resp, dict) or resp.get("success") is not True:
            msg = resp.get("message") if isinstance(resp, dict) else None
            err = resp.get("error") if isinstance(resp, dict) else None
            self._set_error(msg or f"File download failed (HTTP {status})", err or "download_http_error")
            return None

        data_b64 = resp.get("data")
        if not isinstance(data_b64, str) or not data_b64:
            self._set_error("File response is missing content", "download_missing_field")
            return None

        try:
            gz = base64.b64decode(data_b64, validate=True)
            decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
            out = decompressor.decompress(gz, MAX_FILE_BYTES + 1)
            if decompressor.unconsumed_tail or len(out) > MAX_FILE_BYTES or not decompressor.eof:
                raise ValueError("file exceeds size limit or is truncated")
        except Exception:
            self._set_error("File content could not be decompressed", "download_decode_failed")
            return None
        return out

    def get_chat_messages(self, channel: str = "general", before: Optional[int] = None,
                          mark_read: Optional[bool] = None) -> List[ChatMessage]:
        """Reads one page (up to 50, newest first) of a room. before pages back from a message id; mark_read marks
        the returned messages read when the app enables read receipts. None fields are not sent."""
        self._check_init()
        body = self._create_base_payload()
        body["room"] = channel
        if before is not None:
            body["before"] = int(before)
        if mark_read is not None:
            body["markRead"] = bool(mark_read)

        resp = self._send_encrypted("/chat/get", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Failed to fetch messages"
            err = resp.get("error") if resp else "chat_fetch_failed"
            self._set_error(msg or "Failed to fetch messages", err)
            return []

        result: List[ChatMessage] = []
        msgs = resp.get("messages", [])
        if isinstance(msgs, list):
            for item in msgs:
                if isinstance(item, dict):
                    result.append(ChatMessage(
                        id=str(item.get("id", "")),
                        author=str(item.get("author", "")),
                        message=str(item.get("content", item.get("message", ""))),
                        timestamp=str(item.get("timestamp", item.get("createdAt", "")))
                    ))
        return result

    def send_chat_message(self, message: str, channel: str = "general") -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["room"] = channel
        body["content"] = message

        resp = self._send_encrypted("/chat/send", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Failed to send chat message"
            err = resp.get("error") if resp else "chat_send_failed"
            self._set_error(msg or "Failed to send chat message", err)
            return False

        self._set_success("Message sent.")
        return True

    def log(self, message: str) -> bool:
        self._check_init()
        body = self._create_base_payload()
        body["message"] = message

        resp = self._send_encrypted("/log", body)
        if not resp or resp.get("success") is not True:
            self._set_error((resp or {}).get("message") or "Log failed", (resp or {}).get("error") or "log_failed")
            return False
        self._set_success("Log entry saved.")
        return True

    def get_stats(self) -> Optional[AppStats]:
        self._check_init()
        body = self._create_base_payload()

        resp = self._send_encrypted("/stats", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Failed to retrieve stats"
            err = resp.get("error") if resp else "stats_failed"
            self._set_error(msg or "Failed to retrieve stats", err)
            return None

        users_dict = resp.get("users", {}) or {}
        lic_dict = resp.get("licenses", {}) or {}

        return AppStats(
            version=str(resp.get("version", self.version)),
            total_users=int(users_dict.get("total", 0)),
            active_users=int(users_dict.get("active", 0)),
            banned_users=int(users_dict.get("banned", 0)),
            total_licenses=int(lic_dict.get("total", 0)),
            used_licenses=int(lic_dict.get("used", 0)),
            unused_licenses=int(lic_dict.get("notUsed", 0))
        )

    def get_online_users(self) -> List[str]:
        self._check_init()
        body = self._create_base_payload()

        resp = self._send_encrypted("/online-users", body)
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else "Failed to fetch online users"
            err = resp.get("error") if resp else "online_users_failed"
            self._set_error(msg or "Failed to fetch online users", err)
            return []

        users_arr = resp.get("users", [])
        if isinstance(users_arr, list):
            return [str(u) for u in users_arr if u is not None]
        return []

    def trigger_webhook(self, web_id: str, custom_payload: Optional[Dict[str, Any]] = None,
                        content: Optional[str] = None, params: Optional[str] = None,
                        file: Optional[Any] = None, file_name: Optional[str] = None) -> Optional[str]:
        """Invoke a webhook. Returns the remote endpoint's answer (`data` from the server; text as-is, JSON otherwise).

        The web id travels inside the encrypted body. With `file` the request is sent as multipart
        (`envelope` + `file` parts).
        """
        self._check_init()
        body = self._create_base_payload()
        body["webId"] = web_id
        if custom_payload is not None:
            body["payload"] = custom_payload
        if content is not None:
            body["content"] = str(content)
        if params is not None:
            body["params"] = str(params)

        transport = None
        if file is not None:
            file_bytes = bytes(file) if isinstance(file, (bytes, bytearray)) else str(file).encode("utf-8")
            safe_name = str(file_name or "file.bin").replace('"', "%22").replace("\r", "%0D").replace("\n", "%0A")

            def transport(envelope: Dict[str, Any]) -> Tuple[bytes, str]:
                boundary = "NightAuthBoundary" + uuid.uuid4().hex
                head = (f'--{boundary}\r\nContent-Disposition: form-data; name="envelope"\r\n\r\n'
                        f'{json.dumps(envelope)}\r\n'
                        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{safe_name}"\r\n'
                        f'Content-Type: application/octet-stream\r\n\r\n').encode("utf-8")
                tail = f'\r\n--{boundary}--\r\n'.encode("utf-8")
                return head + file_bytes + tail, f"multipart/form-data; boundary={boundary}"

        resp = (self._send_encrypted("/webhook", body, transport) if transport
                else self._send_encrypted("/webhook", body))
        if not resp or not resp.get("success"):
            msg = resp.get("message") if resp else None
            err = resp.get("error") if resp else None
            if resp and not err and "status" in resp:
                msg = msg or f"Remote endpoint returned HTTP {resp['status']}"
            self._set_error(msg or "Webhook trigger failed", err or "webhook_failed")
            return None

        data = resp["data"] if "data" in resp else resp.get("response", "")
        if data is None:
            return ""
        return data if isinstance(data, str) else json.dumps(data)

    _FATAL_TICKET_ERRORS = frozenset((
        "session_invalid", "session_not_validated", "unauthenticated", "blacklisted",
        "app_paused", "app_disabled", "subscription_paused", "no_active_subscription",
    ))

    def start_realtime_event_listener(self, retry_delay: float = 5.0, max_attempts: int = 5,
                                      last_event_id: Optional[str] = None) -> None:
        self.stop_realtime_event_listener()

        self._events_stop_event = threading.Event()
        stop_ev = self._events_stop_event

        def worker() -> None:
            attempts = 0
            while not stop_ev.is_set() and not self._disposed and attempts < max_attempts:
                attempts += 1
                try:
                    ticket_payload = self._create_base_payload()
                    ticket_payload["scope"] = "events"

                    ticket_json = self._send_encrypted("/access-ticket", ticket_payload)
                    ticket = ticket_json.get("ticket", "") if ticket_json and ticket_json.get("success") else ""
                    if not ticket:
                        if ticket_json and ticket_json.get("error") in self._FATAL_TICKET_ERRORS:
                            self.stop_realtime_event_listener()
                            if self.on_session_invalidated:
                                self.on_session_invalidated(f"Event stream rejected: {ticket_json.get('error')}")
                            return
                        stop_ev.wait(retry_delay)
                        continue
                    if stop_ev.is_set():
                        break

                    def keep_socket(sock: Any) -> None:
                        if self._events_stop_event is stop_ev:
                            self._events_socket = sock

                    outcome = self._consume_event_stream(ticket, last_event_id or self.last_event_id, stop_ev,
                                                         lambda resp: setattr(self, "_events_response", resp),
                                                         keep_socket)
                    if outcome["refused"] or outcome["protocol_error"]:
                        return
                    if outcome["delivered"]:
                        attempts = 0
                    if not stop_ev.is_set():
                        stop_ev.wait(min(retry_delay, 1.0))
                except Exception:
                    if stop_ev.is_set():
                        break
                    stop_ev.wait(min(retry_delay, 3.0))

        self._events_thread = threading.Thread(target=worker, name="NightAuth_RealtimeEventsThread", daemon=True)
        self._events_thread.start()

    def _consume_event_stream(self, ticket: str, last_event_id: Optional[str] = None,
                              stop_event: Optional[threading.Event] = None,
                              on_open: Optional[Callable[[Any], None]] = None,
                              on_socket: Optional[Callable[[Any], None]] = None) -> Dict[str, bool]:
        """Opens GET /events?ticket=... with Last-Event-ID (when known) and feeds every frame to
        _handle_realtime_event. Returns when the stream ends: refused (server status), protocol_error (oversize
        event) or delivered. A refusal sets stream_exception with the server code; a transport error sets a
        network_error stream_exception. Redirects are refused. on_open(response) lets a caller close it;
        on_socket(sock) gets the socket as soon as it connects, before the headers, so a stop can shut it down."""
        outcome = {"refused": False, "protocol_error": False, "delivered": False}
        if self._disposed or (stop_event is not None and stop_event.is_set()):
            return outcome
        sse_url = self._resolve_url(f"/events?ticket={urllib.parse.quote(ticket)}")
        headers = {"User-Agent": "NightAuth-Python-SDK/1.0"}
        if last_event_id is not None and str(last_event_id).isascii() and str(last_event_id).isdigit() \
                and 1 <= len(str(last_event_id)) <= 15:
            headers["Last-Event-ID"] = str(last_event_id)
        req = urllib.request.Request(sse_url, headers=headers)

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        def socket_ready(sock: Any) -> None:
            if on_socket is not None:
                on_socket(sock)
            if stop_event is not None and stop_event.is_set():
                _shutdown_socket(sock)

        opener = urllib.request.build_opener(NoRedirect, _StreamHTTPHandler(socket_ready),
                                             _StreamHTTPSHandler(self._make_ssl_context(), socket_ready))
        try:
            with opener.open(req, timeout=60) as response:
                if on_open:
                    on_open(response)

                def on_frame(data: str, frame_id: Optional[str]) -> None:
                    if stop_event is not None and stop_event.is_set():
                        return
                    outcome["delivered"] = True
                    self._handle_realtime_event(data, frame_id)
                    if frame_id is not None:
                        self.last_event_id = frame_id

                parser = SseParser(on_frame)
                while not (stop_event is not None and stop_event.is_set()):
                    chunk = response.read1(4096) if hasattr(response, "read1") else response.read(4096)
                    if not chunk:
                        break
                    try:
                        parser.push(chunk.decode("utf-8", errors="ignore"))
                    except ValueError:
                        outcome["protocol_error"] = True
                        self.stream_exception = NightAuthStreamException(200, "invalid_response", "Event exceeds size limit.")
                        break
        except urllib.error.HTTPError as e:
            outcome["refused"] = True
            code = None
            try:
                body = json.loads(e.read(65536).decode("utf-8", errors="ignore"))
                code = body.get("error") if isinstance(body, dict) and isinstance(body.get("error"), str) else None
            except Exception:
                code = None
            finally:
                e.close()
            self.stream_exception = NightAuthStreamException(e.code, code, code or f"HTTP {e.code}")
            self._set_error(code or f"HTTP {e.code}", code or "stream_refused")
        except Exception as e:
            if not (stop_event is not None and stop_event.is_set()):
                self.stream_exception = NightAuthStreamException(0, "network_error", str(e) or "network_error")
        return outcome

    def stop_realtime_event_listener(self) -> None:
        if self._events_stop_event:
            self._events_stop_event.set()
        self._events_stop_event = None
        response, self._events_response = self._events_response, None
        sock, self._events_socket = self._events_socket, None
        _shutdown_socket(sock)
        _shutdown_socket(getattr(getattr(getattr(response, "fp", None), "raw", None), "_sock", None))
        self._events_thread = None

    def _handle_realtime_event(self, json_string: str, event_id: Optional[str] = None) -> None:
        try:
            node = json.loads(json_string)
            if not isinstance(node, dict):
                return
            ev_type = node.get("type", "")
            if ev_type == "session-invalid":
                self.stop_realtime_event_listener()
                self.user = UserData()
                if self.on_session_invalidated:
                    self.on_session_invalidated("Your session has been terminated by administrator or system.")
            elif ev_type == "app-banned":
                self.stop_realtime_event_listener()
                self.user = UserData()
                reason = node.get("reason") or "Application has been banned."
                if self.on_app_banned:
                    self.on_app_banned(reason)
            elif ev_type == "resync-required":
                if self.on_resync_required:
                    self.on_resync_required()
            elif ev_type in ("app-paused", "app-disabled"):
                self.stop_realtime_event_listener()
                self.user = UserData()
                if self.on_app_status_changed:
                    self.on_app_status_changed(f"Application status changed to: {ev_type}")
            elif ev_type == "version":
                new_ver = node.get("version", "")
                download_url = str(node.get("downloadUrl", ""))
                if download_url:
                    self.pending_download_url = download_url
                if new_ver:
                    self.app.version = new_ver
                    self.required_version = new_ver
                    if self.on_version_updated:
                        try:
                            self.on_version_updated(new_ver, download_url)
                        except TypeError:
                            self.on_version_updated(new_ver)
            elif ev_type == "chat-message":
                room = node.get("room", "general")
                msg = ChatMessage(
                    id=str(node.get("id", "")),
                    author=str(node.get("author", "unknown")),
                    message=str(node.get("content", "")),
                    timestamp=str(node.get("createdAt", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
                )
                if self.on_chat_message_received:
                    self.on_chat_message_received(msg, room)
        except Exception:
            pass

    def _create_base_payload(self) -> Dict[str, Any]:
        obj: Dict[str, Any] = {
            "apikey": self.api_key,
            "name": self.name
        }
        if self.token:
            obj["token"] = self.token
        return obj

    def _has_session(self) -> bool:
        return bool(self._shared_key and self._session_key)

    def _check_init(self) -> None:
        if not self._has_session():
            self._establish_session()

    def _establish_session(self) -> bool:
        """Drop the local session and run one fresh handshake. Returns True when a session exists."""
        self._session_key = None
        self._shared_key = None
        self._is_initialized = False
        self.init()
        return self._has_session()

    def _session_failure(self) -> Dict[str, Any]:
        if not self.response.success and self.response.error:
            return {"success": False, "error": self.response.error, "message": self.response.message}
        return {"success": False, "error": "not_initialized", "message": "Session is not initialized."}

    @staticmethod
    def _is_handshake_expired(result: Dict[str, Any]) -> bool:
        if result.get("error") in ("network_error", "timeout"):
            return False
        message = str(result.get("message") or "").lower()
        return ("handshake" in message or "initialize app" in message
                or result.get("error") in ("handshake_required", "session_invalid", "unauthenticated"))

    def _make_ssl_context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        parsed = urllib.parse.urlsplit(self.api_url)
        is_loopback = parsed.hostname in ("localhost", "127.0.0.1", "::1")
        if parsed.scheme == "http" and is_loopback and self.allow_insecure_loopback:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def _send_encrypted(self, path: str, payload: Dict[str, Any], transport: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        with self._call_lock:
            return self._send_encrypted_locked(path, payload, transport)

    def _send_encrypted_locked(self, path: str, payload: Dict[str, Any], transport: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        if not self._has_session():
            return self._session_failure()
        result = self._send_once(path, payload, transport)
        if not result.get("success") and self._is_handshake_expired(result):
            if self._establish_session():
                result = self._send_once(path, payload, transport)
        return result

    @staticmethod
    def _transport_code(e: BaseException) -> str:
        """Error code of a request that got no usable answer."""
        if isinstance(e, ResponseTooLarge):
            return "response_too_large"
        reason = getattr(e, "reason", e)
        return "timeout" if isinstance(reason, (TimeoutError, socket.timeout)) else "network_error"

    @staticmethod
    def _transport_failure(e: BaseException) -> Dict[str, Any]:
        reason = getattr(e, "reason", e)
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return {"success": False, "error": "timeout", "message": "The request timed out."}
        return {"success": False, "error": "network_error", "message": "Network request failed."}

    @staticmethod
    def _plain_refusal(status_code: int, body: Any) -> Dict[str, Any]:
        """Unencrypted replies carry no session proof: they are refusals, never successes."""
        if not isinstance(body, dict):
            return {"success": False, "error": "invalid_response", "message": "Response body is not a JSON object."}
        error = body.get("error") if isinstance(body.get("error"), str) and body.get("error") else None
        if error is None:
            error = "response_not_authenticated" if 200 <= status_code < 300 else f"HTTP {status_code}"
        message = body.get("message") if isinstance(body.get("message"), str) and body.get("message") else error
        return {"success": False, "error": error, "message": message}

    def _send_once(self, path: str, payload: Dict[str, Any], transport: Optional[Any] = None) -> Dict[str, Any]:
        rid = uuid.uuid4().hex
        ts = int(time.time() * 1000)
        url = self._resolve_url(path)
        url_path = urllib.parse.urlsplit(url).path
        aad = f"POST:{url_path}:{self._session_key}:{rid}:{ts}"
        json_plain = json.dumps(payload)
        ct_b64, nonce_b64 = self.aes_gcm_encrypt(self._shared_key, json_plain, aad)

        envelope = {
            "id": self._session_key,
            "ct": ct_b64,
            "n": nonce_b64,
            "rid": rid,
            "ts": ts
        }

        post_body: Any = json.dumps(envelope)
        post_content_type = "application/json"
        if callable(transport):
            custom_body, custom_type = transport(envelope)
            if custom_body:
                post_body = custom_body
                if custom_type:
                    post_content_type = custom_type

        try:
            if post_content_type == "application/json":
                status_code, resp_raw = self._post_raw(path, post_body)
            else:
                status_code, resp_raw = self._post_raw(path, post_body, post_content_type)
        except ResponseTooLarge as e:
            return {"success": False, "error": "response_too_large", "message": "Response exceeds size limit.", "status": e.status}
        except Exception as e:
            return self._transport_failure(e)

        try:
            enc_resp = json.loads(resp_raw)
        except Exception:
            return {"success": False, "error": "invalid_response", "message": "Response body is not a JSON object."}

        if isinstance(enc_resp, dict) and "ct" in enc_resp and "n" in enc_resp:
            res_ct = enc_resp["ct"]
            res_n = enc_resp["n"]
            if "rid" not in enc_resp or "ts" not in enc_resp:
                raise CryptographicException("Response is not bound to this request.")
            res_rid = enc_resp["rid"]
            res_ts = enc_resp["ts"]
            if res_rid != rid or res_ts != ts:
                raise CryptographicException("Response is not authenticated to this request.")

            res_aad = f"v1:res:{self._session_key}:{res_rid}:{res_ts}"
            try:
                decrypted_plain = self.aes_gcm_decrypt(self._shared_key, res_ct, res_n, res_aad)
            except Exception as e:
                raise CryptographicException("Response could not be authenticated.") from e
            try:
                decrypted = json.loads(decrypted_plain)
            except Exception:
                return {"success": False, "error": "invalid_response", "message": "Decrypted response is not JSON."}
            if not isinstance(decrypted, dict):
                return {"success": False, "error": "invalid_response", "message": "Decrypted response is not a JSON object."}
            return decrypted

        if 200 <= status_code < 300 and isinstance(enc_resp, dict) and enc_resp.get("success") is True:
            raise CryptographicException("Response is not authenticated to this request.")
        return self._plain_refusal(status_code, enc_resp)

    def _resolve_url(self, path: str) -> str:
        base = self.api_url.rstrip("/")
        if not path.startswith("/"):
            path = "/" + path
        return f"{base}{path}"

    def _post_raw(self, path: str, json_body: Any, content_type: str = "application/json") -> Tuple[int, str]:
        url = self._resolve_url(path)
        data = json_body if isinstance(json_body, (bytes, bytearray)) else json_body.encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": content_type,
                "User-Agent": "NightAuth-Python-SDK/1.0"
            },
            method="POST"
        )
        ctx = self._make_ssl_context()

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
        try:
            with opener.open(req, timeout=20) as resp:
                return resp.status, self._read_limited_response(resp).decode("utf-8")
        except urllib.error.HTTPError as e:
            try:
                return e.code, self._read_limited_response(e).decode("utf-8")
            finally:
                e.close()

    def _get_raw(self, path_and_query: str, max_bytes: int) -> Tuple[int, bytes]:
        url = self._resolve_url(path_and_query)
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "NightAuth-Python-SDK/1.0"
            },
            method="GET"
        )
        ctx = self._make_ssl_context()

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ctx))
        self._last_get_location = None
        try:
            with opener.open(req, timeout=20) as resp:
                return resp.status, self._read_limited_response(resp, max_bytes)
        except urllib.error.HTTPError as e:
            try:
                self._last_get_location = e.headers.get("Location") if e.headers is not None else None
                return e.code, self._read_limited_response(e, max_bytes)
            finally:
                e.close()

    @staticmethod
    def _read_limited_response(response, limit: int = 5 * 1024 * 1024) -> bytes:
        body = response.read(limit + 1)
        if len(body) > limit:
            status = getattr(response, "status", None) or getattr(response, "code", None) or 0
            raise ResponseTooLarge("Response exceeds size limit", int(status))
        return body

    @classmethod
    def aes_gcm_encrypt(cls, key: bytes, plaintext: str, aad: str) -> Tuple[str, str]:
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        plain_bytes = plaintext.encode("utf-8")
        aad_bytes = aad.encode("utf-8")
        ct_with_tag = aesgcm.encrypt(nonce, plain_bytes, aad_bytes)
        return base64.b64encode(ct_with_tag).decode("utf-8"), base64.b64encode(nonce).decode("utf-8")

    @classmethod
    def aes_gcm_decrypt(cls, key: bytes, ct_b64: str, n_b64: str, aad: str) -> str:
        nonce = base64.b64decode(n_b64)
        ct_with_tag = base64.b64decode(ct_b64)
        aesgcm = AESGCM(key)
        aad_bytes = aad.encode("utf-8")
        plain_bytes = aesgcm.decrypt(nonce, ct_with_tag, aad_bytes)
        return plain_bytes.decode("utf-8")

    @classmethod
    def verify_server_signature(cls, k2_hex: str, vk_hex: str, ts: int, sig_b64: str) -> bool:
        try:
            vk_bytes = bytes.fromhex(vk_hex)
            sig_bytes = base64.b64decode(sig_b64)
            data = f"{k2_hex}.{vk_hex}.{ts}".encode("utf-8")
            pub_key = Ed25519PublicKey.from_public_bytes(vk_bytes)
            pub_key.verify(sig_bytes, data)
            return True
        except Exception:
            return False

    @classmethod
    def crypto_box_seal(cls, plaintext: str, recipient_pub_key_hex: str) -> str:
        recipient_pub_bytes = bytes.fromhex(recipient_pub_key_hex)
        recipient_pub = X25519PublicKey.from_public_bytes(recipient_pub_bytes)

        ephem_priv = X25519PrivateKey.generate()
        ephem_pub = ephem_priv.public_key()
        ephem_pub_bytes = ephem_pub.public_bytes_raw()

        raw_secret = ephem_priv.exchange(recipient_pub)
        enc_key = cls.hkdf_extract_and_expand(raw_secret, cls.SEAL_INFO, 32)

        nonce = os.urandom(12)
        aesgcm = AESGCM(enc_key)
        plain_bytes = plaintext.encode("utf-8")
        ct_with_tag = aesgcm.encrypt(nonce, plain_bytes, ephem_pub_bytes)

        cipher_bytes = ct_with_tag[:-16]
        tag = ct_with_tag[-16:]

        result = ephem_pub_bytes + nonce + tag + cipher_bytes
        return base64.b64encode(result).decode("utf-8")

    @classmethod
    def hkdf_extract_and_expand(cls, ikm: bytes, info: bytes, length: int) -> bytes:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=None,
            info=info
        )
        return hkdf.derive(ikm)

    def _populate_user_data(self, data: Dict[str, Any]) -> None:
        u = data.get("user") or data.get("info")
        if not isinstance(u, dict):
            return

        self.user.username = str(u.get("username") or "")
        self.user.email = str(u.get("email") or "")
        self.user.hwid = str(u.get("hwid") or "")
        self.user.ip = str(u.get("ip") or "")
        self.user.status = str(u.get("status") or "active")
        self.user.created_at = str(u.get("createdAt") or u.get("createdate") or "")
        self.user.last_login_at = str(u.get("lastLoginAt") or u.get("lastlogin") or "")

        self.user.subscriptions.clear()
        sub_arr = u.get("subscriptions", [])
        if isinstance(sub_arr, list):
            for item in sub_arr:
                if not isinstance(item, dict):
                    continue
                tl = item.get("timeleft", item.get("timeLeft", 0))
                self.user.subscriptions.append(SubscriptionData(
                    subscription=str(item.get("subscription") or ""),
                    key=str(item.get("key") or ""),
                    expiry=str(item.get("expiry") or item.get("expiresAt") or ""),
                    time_left=int(tl) if tl is not None else 0
                ))

        app_obj = data.get("app")
        if isinstance(app_obj, dict):
            self.app.total_users = int(app_obj.get("totalUsers", 0))
            self.app.online_users = int(app_obj.get("onlineUsers", 0))
            self.app.total_keys = int(app_obj.get("totalKeys", 0))
            self.app.version = str(app_obj.get("version", self.version))

    @staticmethod
    def _format_human_error_message(msg: str, err: Optional[str]) -> str:
        candidate = msg.strip() if msg and msg.strip() else (err or "Operation failed")
        mapping = {
            "rate_limited": "Too many requests. Please wait a moment and try again.",
            "invalid_credentials": "The credentials provided do not match our records.",
            "invalid_apikey": "The API key provided is invalid or unrecognized.",
            "app_not_found": "Application was not found. Please check your credentials.",
            "app_disabled": "This application is currently disabled by administrator policy.",
            "app_paused": "Application is currently paused for maintenance.",
            "invalid_token": "Authentication token is invalid or expired.",
            "feature_disabled": "This feature is currently disabled for this application.",
            "session_invalid": "Session is no longer valid. Please sign in again.",
            "session_not_validated": "Session is no longer valid. Please sign in again.",
            "invalid_hwid": "Device signature is invalid or unrecognized.",
            "hwid_mismatch": "Device signature mismatch. Please reset your HWID.",
            "vpn_blocked": "Anonymous proxies and VPN connections are not permitted.",
            "blacklisted": "Your hardware identifier or IP address has been restricted.",
            "username_taken": "This username is already registered. Please choose another.",
            "email_taken": "This email address is already registered.",
            "invalid_license": "The license key provided is invalid or unrecognized.",
            "license_used": "This license key has already been activated.",
            "no_active_subscription": "No active subscription found for this account.",
            "expired": "No active subscription found for this account.",
            "subscription_paused": "Your subscription is temporarily suspended.",
            "paused": "Your subscription is temporarily suspended."
        }
        return mapping.get(candidate, candidate)

    def _set_error(self, msg: str, err: Optional[str] = None) -> None:
        friendly = self._format_human_error_message(msg, err)
        self.response.success = False
        self.response.message = friendly
        self.response.error = err or (msg if msg else "error")

    def _set_success(self, msg: str) -> None:
        self.response.success = True
        self.response.message = msg
        self.response.error = None

    def close(self) -> None:
        if self._disposed:
            return
        self._disposed = True
        self.stop_realtime_event_listener()

    def apply_update(self, download_url: Optional[str] = None) -> bool:
        """Unsigned executable replacement was removed. Use SignedUpdateInstaller."""
        self._set_error("Unsigned auto-update is disabled. Verify a signed release manifest with SignedUpdateInstaller.", "unsigned_update_disabled")
        return False

    def download_signed_update(self, manifest_url: str, pinned_release_key_hex: str, destination: str) -> str:
        """Download and verify a signed release manifest and artifact using SignedUpdateInstaller."""
        return SignedUpdateInstaller.download(manifest_url, pinned_release_key_hex, self.name, destination)

    get_var = get_global_var
    var = get_global_var
    fetch_all_user_vars = get_user_variables
    fetch_user_vars = get_user_variables
    get_file = download_file
    file = download_file
    webhook = trigger_webhook


@dataclass
class VerifiedUpdate:
    application: str
    version: str
    sequence: int
    url: str
    size: int
    expires_at: int
    digest: bytes


class SignedUpdate:
    MAX_ARTIFACT_BYTES: int = 256 * 1024 * 1024
    MAX_MANIFEST_BYTES: int = 64 * 1024

    @staticmethod
    def verify(
        envelope_json: str,
        pinned_public_key_hex: str,
        expected_application: str,
        minimum_sequence: int = 0
    ) -> VerifiedUpdate:
        if len(envelope_json.encode("utf-8")) > SignedUpdate.MAX_MANIFEST_BYTES or minimum_sequence < 0 or not expected_application or not expected_application.strip():
            raise ValueError("Invalid manifest parameters.")
        try:
            envelope = json.loads(envelope_json)
            if not isinstance(envelope, dict):
                raise ValueError("Manifest envelope must be a JSON object.")
            payload_b64 = envelope.get("payload")
            sig_b64 = envelope.get("signature")
            if not isinstance(payload_b64, str) or not isinstance(sig_b64, str):
                raise ValueError("Manifest envelope missing payload or signature.")
            payload = base64.b64decode(payload_b64)
            signature = base64.b64decode(sig_b64)
            key_bytes = bytes.fromhex(pinned_public_key_hex)
            if len(payload) > 32768 or len(signature) != 64 or len(key_bytes) != 32:
                raise ValueError("Invalid manifest size, signature or key length.")

            verifier = Ed25519PublicKey.from_public_bytes(key_bytes)
            try:
                verifier.verify(signature, payload)
            except Exception as e:
                raise CryptographicException("Release signature rejected.") from e

            data = json.loads(payload.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Manifest payload must be a JSON object.")

            app = str(data.get("application", ""))
            version = str(data.get("version", ""))
            sequence = data.get("sequence")
            size = data.get("size")
            raw_url = str(data.get("url", ""))
            expires_at = data.get("expiresAt")
            sha256_hex = str(data.get("sha256", ""))
            schema = data.get("schema")

            if schema != 1 or app != expected_application or not version or len(version) > 100:
                raise ValueError("Release identity or schema rejected.")
            if not isinstance(sequence, int) or sequence <= minimum_sequence or sequence > 9007199254740991:
                raise ValueError("Release sequence rejected.")
            if not isinstance(size, int) or size < 1 or size > SignedUpdate.MAX_ARTIFACT_BYTES:
                raise ValueError("Release artifact size rejected.")
            if not isinstance(expires_at, int) or expires_at <= int(time.time()):
                raise ValueError("Release expired.")

            parsed_url = urllib.parse.urlsplit(raw_url)
            if parsed_url.scheme != "https" or parsed_url.username or parsed_url.password or parsed_url.fragment:
                raise ValueError("Release URL must be HTTPS without userinfo or fragment.")

            digest = bytes.fromhex(sha256_hex)
            if len(digest) != 32:
                raise ValueError("Invalid sha256 digest length.")

            return VerifiedUpdate(
                application=app,
                version=version,
                sequence=sequence,
                url=raw_url,
                size=size,
                expires_at=expires_at,
                digest=digest
            )
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            if isinstance(e, CryptographicException):
                raise
            raise ValueError(f"Malformed release manifest: {e}") from e

    @staticmethod
    def download(update: VerifiedUpdate, destination: str, timeout: int = 300) -> str:
        if not update or not isinstance(update, VerifiedUpdate):
            raise ValueError("update must be a VerifiedUpdate instance")
        if update.expires_at <= int(time.time()):
            raise ValueError("Release expired.")

        target = os.path.abspath(destination)
        if os.path.exists(target):
            raise IOError("Destination file already exists.")

        target_dir = os.path.dirname(target)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        temporary = f"{target}.{uuid.uuid4().hex}.partial"

        class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(_NoRedirectHandler)
        req = urllib.request.Request(update.url, headers={"User-Agent": "NightAuth-Updater/1.0"})

        try:
            with opener.open(req, timeout=timeout) as resp:
                if resp.status != 200:
                    raise urllib.error.HTTPError(update.url, resp.status, "Artifact must return HTTP 200 without redirects.", resp.headers, None)
                content_len = resp.headers.get("Content-Length")
                if content_len is not None:
                    try:
                        if int(content_len) != update.size:
                            raise ValueError("Artifact length differs from signed manifest.")
                    except ValueError:
                        pass

                hasher = hashlib.sha256()
                total = 0
                with open(temporary, "wb") as f:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > update.size:
                            raise ValueError("Artifact exceeds signed size.")
                        hasher.update(chunk)
                        f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())

                if total != update.size or hasher.digest() != update.digest:
                    raise CryptographicException("Artifact hash or size rejected.")

            if update.expires_at <= int(time.time()):
                raise ValueError("Release expired during download.")

            os.replace(temporary, target)
            return target
        finally:
            if os.path.exists(temporary):
                try:
                    os.remove(temporary)
                except OSError:
                    pass


class SignedUpdateInstaller:
    MAX_MANIFEST_BYTES: int = 64 * 1024
    _lock = threading.Lock()

    @staticmethod
    def get_sequence_path(application: str) -> str:
        if not application or len(application) > 100 or any(c in r'<>:"/\|?*' for c in application):
            raise ValueError("Invalid application identifier.")
        if platform.system() == "Windows":
            root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
        else:
            root = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        directory = os.path.join(root, "NightAuth", "release-sequences")
        os.makedirs(directory, exist_ok=True)
        app_hash = hashlib.sha256(application.encode("utf-8")).hexdigest()
        return os.path.join(directory, f"{app_hash}.seq")

    @staticmethod
    def _read_sequence(path: str) -> int:
        if not os.path.exists(path):
            return 0
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            seq = int(content)
            if seq < 0:
                raise ValueError("Negative sequence stored.")
            return seq
        except Exception as e:
            raise ValueError("Stored release sequence is corrupt; refusing update.") from e

    @staticmethod
    def _write_sequence_atomically(path: str, sequence: int) -> None:
        temporary = f"{path}.{uuid.uuid4().hex}.tmp"
        try:
            with open(temporary, "w", encoding="utf-8") as f:
                f.write(str(sequence))
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                try:
                    os.remove(temporary)
                except OSError:
                    pass

    @classmethod
    def download(
        cls,
        manifest_url: str,
        pinned_release_key_hex: str,
        application: str,
        destination: str,
        timeout: int = 30
    ) -> str:
        parsed_url = urllib.parse.urlsplit(manifest_url)
        if parsed_url.scheme != "https" or parsed_url.username or parsed_url.password or parsed_url.fragment:
            raise ValueError("Release manifest must use an HTTPS URL without user info or fragment.")

        state_path = cls.get_sequence_path(application)
        lock_path = state_path + ".lock"

        with cls._lock:
            lock_fd = None
            start_time = time.time()
            while True:
                try:
                    lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                    break
                except OSError:
                    if time.time() - start_time > 10.0:
                        raise TimeoutError("Could not acquire update lock.")
                    time.sleep(0.1)

            try:
                current_sequence = cls._read_sequence(state_path)

                class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                    def redirect_request(self, req, fp, code, msg, headers, newurl):
                        return None

                opener = urllib.request.build_opener(_NoRedirectHandler)
                req = urllib.request.Request(manifest_url, headers={"User-Agent": "NightAuth-Updater/1.0"})
                with opener.open(req, timeout=timeout) as resp:
                    if resp.status != 200:
                        raise urllib.error.HTTPError(manifest_url, resp.status, "Release manifest must return HTTP 200 without redirects.", resp.headers, None)
                    manifest_bytes = resp.read(cls.MAX_MANIFEST_BYTES + 1)
                    if len(manifest_bytes) > cls.MAX_MANIFEST_BYTES:
                        raise ValueError("Release manifest exceeds the maximum allowed size.")

                envelope_json = manifest_bytes.decode("utf-8")
                verified = SignedUpdate.verify(envelope_json, pinned_release_key_hex, application, current_sequence)
                full_destination = SignedUpdate.download(verified, destination)
                cls._write_sequence_atomically(state_path, verified.sequence)
                return full_destination
            finally:
                if lock_fd is not None:
                    os.close(lock_fd)
                    try:
                        os.remove(lock_path)
                    except OSError:
                        pass


# Compatibility aliases
NightAuth = Api
api = Api
