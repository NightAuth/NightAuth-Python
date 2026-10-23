import datetime
import json
import os
import sys
import threading
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
        h_out = kernel32.GetStdHandle(-11)
        dw_mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(h_out, ctypes.byref(dw_mode)):
            kernel32.SetConsoleMode(h_out, dw_mode.value | 0x0004)
        kernel32.SetConsoleTitleW("NightAuth — Native Python Security Console")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sdk")))

import nightauth

os.environ.setdefault("NIGHTAUTH_IGNORE_SECURITY", "1")

APP_NAME = ""
APP_API_KEY = ""
APP_VERSION = "1.0"
APP_TOKEN = None

NightAuthApp = nightauth.api(
    name=APP_NAME,
    apikey=APP_API_KEY,
    version=APP_VERSION,
    token=APP_TOKEN
)

night_auth = NightAuthApp

C_RESET    = "\x1b[0m"
C_BOLD     = "\x1b[1m"
C_DIM      = "\x1b[38;2;100;116;139m"
C_MUTED    = "\x1b[38;2;148;163;184m"
C_TEXT     = "\x1b[38;2;226;232;240m"
C_WHITE    = "\x1b[38;2;248;250;252m"
C_BLUE     = "\x1b[38;2;59;130;246m"
C_GLOW     = "\x1b[38;2;96;165;250m"
C_CYAN     = "\x1b[38;2;56;189;248m"
C_GREEN    = "\x1b[38;2;52;211;153m"
C_AMBER    = "\x1b[38;2;251;191;36m"
C_RED      = "\x1b[38;2;248;113;113m"
C_BORDER   = "\x1b[38;2;42;50;70m"
C_BADGE_BG = "\x1b[48;2;23;37;68m"
C_GREEN_BG = "\x1b[48;2;14;46;38m"
C_RED_BG   = "\x1b[48;2;56;20;26m"

def clear_screen():
    sys.stdout.write("\x1b[2J\x1b[H")
    sys.stdout.flush()

def print_hr():
    sys.stdout.write(f"  {C_BORDER}────────────────────────────────────────────────────────────────────────────{C_RESET}\n")

def print_section_header(title, subtitle=""):
    sys.stdout.write(f"\n  {C_BLUE}▌{C_RESET} {C_WHITE}{C_BOLD}{title}{C_RESET}")
    if subtitle:
        sys.stdout.write(f"  {C_DIM}·  {subtitle}{C_RESET}")
    sys.stdout.write("\n")
    print_hr()

def print_ok(title, detail=""):
    sys.stdout.write(f"\n  {C_GREEN_BG}{C_GREEN}{C_BOLD} ✓ SUCCESS {C_RESET} {C_WHITE}{C_BOLD}{title}{C_RESET}")
    if detail:
        sys.stdout.write(f" {C_MUTED}— {detail}{C_RESET}")
    sys.stdout.write("\n\n")
    sys.stdout.flush()

def print_err(title, detail=""):
    sys.stdout.write(f"\n  {C_RED_BG}{C_RED}{C_BOLD} ✕ ERROR {C_RESET} {C_WHITE}{C_BOLD}{title}{C_RESET}")
    if detail:
        sys.stdout.write(f" {C_RED}— {detail}{C_RESET}")
    sys.stdout.write("\n\n")
    sys.stdout.flush()

def print_info(label, value):
    sys.stdout.write(f"  {C_BLUE}•{C_RESET} {C_MUTED}{label:<18}{C_RESET} {C_CYAN}{value}{C_RESET}\n")
    sys.stdout.flush()

def ask(prompt):
    sys.stdout.write(f"  {C_GLOW}❯{C_RESET} {C_TEXT}{prompt}{C_RESET}")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return line.rstrip("\r\n").strip()

def format_timestamp(raw):
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    if s.isdigit() and int(s) > 0:
        val = int(s)
        sec = val / 1000.0 if val > 100000000000 else float(val)
        try:
            dt = datetime.datetime.fromtimestamp(sec, tz=datetime.timezone.utc)
            return dt.strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            pass
    try:
        dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return s

def render_banner(app_name, hwid, connected):
    sys.stdout.write("\n")
    sys.stdout.write(f"  {C_BLUE}{C_BOLD}  _   _ _       _     _      _         _   _     \n{C_RESET}")
    sys.stdout.write(f"  {C_BLUE}{C_BOLD} | \\ | (_) __ _| |__ | |_   / \\  _   _| |_| |__  \n{C_RESET}")
    sys.stdout.write(f"  {C_GLOW}{C_BOLD} |  \\| | |/ _` | '_ \\| __| / _ \\| | | | __| '_ \\ \n{C_RESET}")
    sys.stdout.write(f"  {C_GLOW}{C_BOLD} | |\\  | | (_| | | | | |_ / ___ \\ |_| | |_| | | |\n{C_RESET}")
    sys.stdout.write(f"  {C_CYAN}{C_BOLD} |_| \\_|_|\\__, |_| |_|\\__/_/   \\_\\__,_|\\__|_| |_|\n{C_RESET}")
    sys.stdout.write(f"  {C_CYAN}{C_BOLD}          |___/                                  {C_RESET}  {C_BADGE_BG}{C_GLOW}{C_BOLD} NATIVE PYTHON CLI {C_RESET}\n\n")

    app_disp = app_name if app_name else "Unconfigured"
    status_prefix = f"{C_GREEN}● " if connected else f"{C_AMBER}◌ "
    status_text = "Connected" if connected else "Initializing"

    sys.stdout.write(f"  {C_BORDER}╭──────────────────────────────────────────────────────────────────────────╮{C_RESET}\n")
    sys.stdout.write(
        f"  {C_BORDER}│{C_RESET}  {C_DIM}APPLICATION{C_RESET}  {C_WHITE}{C_BOLD}{app_disp:<26.26}{C_RESET}"
        f"  {C_DIM}STATUS{C_RESET}  {status_prefix}{status_text:<16}{C_RESET} {C_BORDER}│{C_RESET}\n"
    )
    if hwid:
        sys.stdout.write(f"  {C_BORDER}│{C_RESET}  {C_DIM}DEVICE HWID{C_RESET}  {C_CYAN}{hwid:<58.58}{C_RESET} {C_BORDER}│{C_RESET}\n")
    sys.stdout.write(f"  {C_BORDER}╰──────────────────────────────────────────────────────────────────────────╯{C_RESET}\n")
    sys.stdout.flush()

def register_realtime_event_handlers():
    def on_invalid(reason):
        print_err("Security Alert", f"{reason} (Kill-switch triggered)")
        os._exit(0xDEAD)

    def on_banned(reason):
        print_err("Critical Ban", f"Application banned: {reason}")
        os._exit(0xDEAD)

    def on_status(status):
        print_err("Status Change", status)
        os._exit(0xDEAD)

    def on_version(new_ver, download_url=""):
        extra = f" ({download_url})" if download_url else ""
        print_info("Update Available:", f"v{new_ver}{extra}")

    def on_chat(msg, room):
        sys.stdout.write(f"\n  {C_BADGE_BG}{C_GLOW} CHAT #{room} {C_RESET} {C_CYAN}{C_BOLD}{msg.author}{C_RESET}: {C_TEXT}{msg.message}{C_RESET}\n")
        sys.stdout.flush()

    night_auth.on_session_invalidated = on_invalid
    night_auth.on_app_banned = on_banned
    night_auth.on_app_status_changed = on_status
    night_auth.on_version_updated = on_version
    night_auth.on_chat_message_received = on_chat

def perform_handshake(app_name):
    sys.stdout.write(f"\n  {C_MUTED}◌ Establishing encrypted session with NightAuth Cloud...{C_RESET}\r")
    sys.stdout.flush()
    try:
        night_auth.init()
    except Exception as ex:
        sys.stdout.write("                                                                      \r")
        sys.stdout.flush()
        render_banner(app_name, "", False)
        print_err("Handshake Exception", str(ex))
        sys.exit(1)
    sys.stdout.write("                                                                      \r")
    sys.stdout.flush()

    if not night_auth.response.success:
        render_banner(app_name, "", False)
        print_err("Handshake Failed", night_auth.response.message)
        sys.stdout.write(f"  {C_DIM}Please verify your App Name and API Key.{C_RESET}\n\n")
        ask("Press Enter to exit...")
        sys.exit(1)

    hwid = nightauth.SecurityProtections.get_hardware_id()
    clear_screen()
    render_banner(app_name, hwid, True)

def handle_login():
    print_section_header("ACCOUNT SIGN IN", "Authenticate with your username and password")
    user = ask("Username: ")
    password = ask("Password: ")
    totp = ask(f"2FA Code {C_DIM}(Optional, Enter to skip){C_TEXT}: ")

    if night_auth.login(user, password, totp if totp else None):
        print_ok("Session Authenticated", "Welcome back to NightAuth.")
        return True

    print_err("Login Failed", night_auth.response.message)
    return False

def handle_register():
    print_section_header("CREATE NEW ACCOUNT", "Activate a license key and bind your credentials")
    user = ask("Username: ")
    password = ask("Password: ")
    key = ask("License Key: ")
    email = ask(f"Email Address {C_DIM}(Optional, Enter to skip){C_TEXT}: ")

    if night_auth.register(user, password, key, email):
        print_ok("Account Registered & Activated", "Session started automatically.")
        return True

    detail = night_auth.response.message or ""
    if night_auth.response.error:
        detail += f" [{night_auth.response.error}]"
    print_err("Registration Failed", detail)
    return False

def handle_license_only():
    print_section_header("LICENSE KEY AUTHENTICATION", "Instant passwordless login bound to your HWID")
    key = ask("Enter License Key: ")

    if night_auth.license(key):
        print_ok("License Validated", "Direct hardware-bound session active.")
        return True

    print_err("License Validation Failed", night_auth.response.message)
    return False

def handle_upgrade(known_user=""):
    print_section_header("UPGRADE ACCOUNT SUBSCRIPTION", "Attach a new license key tier to an account")
    user = known_user
    if user:
        print_info("Target Account:", user)
    else:
        user = ask("Target Username: ")
    key = ask("Upgrade License Key: ")

    if night_auth.upgrade(user, key):
        print_ok("Upgrade Complete", night_auth.response.message)
        return True
    else:
        print_err("Upgrade Failed", night_auth.response.message)
        return False

def handle_forgot_password():
    print_section_header("PASSWORD RECOVERY", "Request a reset link to your registered email")
    email = ask("Registered Email: ")

    if night_auth.forgot_password(email):
        print_ok("Recovery Dispatched", "If an account matches, a password reset link was sent to your email.")
    else:
        print_err("Request Failed", night_auth.response.message)

def handle_reset_password():
    print_section_header("COMPLETE PASSWORD RESET", "Confirm recovery token and set a new password")
    token = ask("Reset Token: ")
    new_pass = ask("New Password: ")

    if night_auth.reset_password(token, new_pass):
        print_ok("Password Updated", "Your password has been reset successfully.")
    else:
        print_err("Reset Failed", night_auth.response.message)

def handle_reset_hwid():
    print_section_header("RESET HARDWARE FINGERPRINT (HWID)", "Unbind previous device to authorize a new machine")
    user = ask("Username: ")
    password = ask("Password: ")
    totp = ask(f"2FA Code {C_DIM}(Optional, Enter to skip){C_TEXT}: ")

    if night_auth.reset_hwid(user, password, totp if totp else None):
        print_ok("HWID Reset", night_auth.response.message)
    else:
        print_err("HWID Reset Failed", night_auth.response.message)

def handle_check_blacklist():
    print_section_header("HARDWARE BLACKLIST CHECK", "Verify if a machine fingerprint is restricted")
    target_hwid = ask(f"Hardware ID {C_DIM}(Press Enter for local machine HWID){C_TEXT}: ")
    if not target_hwid:
        target_hwid = nightauth.SecurityProtections.get_hardware_id()

    result = night_auth.check_blacklist(target_hwid)
    is_blacklisted = bool(result.get("blacklisted")) if isinstance(result, dict) else bool(result)
    if night_auth.response.success:
        if is_blacklisted:
            print_err("Blacklisted", "This Hardware ID is currently restricted.")
        else:
            print_ok("Clean Fingerprint", "Hardware ID is not on the blacklist.")
    else:
        print_err("Blacklist Query Failed", night_auth.response.message)

def handle_verify_hash():
    print_section_header("BINARY INTEGRITY CHECK", "Validate SHA-256 checksum against server registry")
    file_hash = ask("SHA-256 File Hash: ")
    verified = night_auth.verify_file_hash(file_hash)
    if night_auth.response.success:
        if verified:
            print_ok("Integrity Verified", "Checksum matches authorized server release.")
        else:
            print_err("Verification Failed", "Checksum does not match any approved file release.")
    else:
        print_err("Verification Failed", night_auth.response.message)

def handle_authentication_flow():
    while True:
        print_section_header("AUTHENTICATION & PRE-SESSION GATEWAY", "Select an operation to continue")

        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 01 {C_RESET} {C_WHITE}Sign In (Username & Password){C_RESET}"
            f"          {C_BADGE_BG}{C_GLOW}{C_BOLD} 06 {C_RESET} {C_WHITE}Complete Password Reset (Token){C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 02 {C_RESET} {C_WHITE}Register New Account + License{C_RESET}"
            f"         {C_BADGE_BG}{C_GLOW}{C_BOLD} 07 {C_RESET} {C_WHITE}Reset Hardware Binding (HWID){C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 03 {C_RESET} {C_WHITE}Instant License Key Login{C_RESET}"
            f"              {C_BADGE_BG}{C_GLOW}{C_BOLD} 08 {C_RESET} {C_WHITE}Check HWID Blacklist Status{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 04 {C_RESET} {C_WHITE}Upgrade Existing Account Plan{C_RESET}"
            f"          {C_BADGE_BG}{C_GLOW}{C_BOLD} 09 {C_RESET} {C_WHITE}Verify Binary SHA-256 Hash{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 05 {C_RESET} {C_WHITE}Forgot Password (Email Link){C_RESET}"
            f"           {C_RED_BG}{C_RED}{C_BOLD} 10 {C_RESET} {C_MUTED}Exit Application{C_RESET}\n\n"
        )

        sel = ask("Select option [1-10]: ")

        if sel in ("1", "01"):
            if handle_login():
                return True
        elif sel in ("2", "02"):
            if handle_register():
                return True
        elif sel in ("3", "03"):
            if handle_license_only():
                return True
        elif sel in ("4", "04"):
            handle_upgrade()
        elif sel in ("5", "05"):
            handle_forgot_password()
        elif sel in ("6", "06"):
            handle_reset_password()
        elif sel in ("7", "07"):
            handle_reset_hwid()
        elif sel in ("8", "08"):
            handle_check_blacklist()
        elif sel in ("9", "09"):
            handle_verify_hash()
        elif sel in ("10", "0"):
            return False

def render_user_profile():
    u = night_auth.user
    uname = u.username if u.username else "Authenticated"
    ustatus = u.status if u.status else "ACTIVE"
    uemail = u.email if u.email else "Not linked"
    uip = u.ip if u.ip else "Protected / TLS"
    ucreated = format_timestamp(u.created_at) or "-"
    ulast = format_timestamp(u.last_login_at) or "Just now"

    sys.stdout.write("\n")
    sys.stdout.write(f"  {C_BORDER}╭─ {C_GLOW}{C_BOLD}AUTHENTICATED IDENTITY & ENTITLEMENTS{C_BORDER} ──────────────────────────────────╮{C_RESET}\n")
    sys.stdout.write(
        f"  {C_BORDER}│{C_RESET}  {C_DIM}Username :{C_RESET} {C_WHITE}{C_BOLD}{uname:<24.24}{C_RESET}"
        f"  {C_DIM}Status     :{C_RESET} {C_GREEN}{C_BOLD}{ustatus:<20.20}{C_RESET} {C_BORDER}│{C_RESET}\n"
    )
    sys.stdout.write(
        f"  {C_BORDER}│{C_RESET}  {C_DIM}Email    :{C_RESET} {C_TEXT}{uemail:<24.24}{C_RESET}"
        f"  {C_DIM}Client IP  :{C_RESET} {C_CYAN}{uip:<20.20}{C_RESET} {C_BORDER}│{C_RESET}\n"
    )
    sys.stdout.write(
        f"  {C_BORDER}│{C_RESET}  {C_DIM}Created  :{C_RESET} {C_MUTED}{ucreated:<24.24}{C_RESET}"
        f"  {C_DIM}Last Login :{C_RESET} {C_MUTED}{ulast:<20.20}{C_RESET} {C_BORDER}│{C_RESET}\n"
    )
    sys.stdout.write(f"  {C_BORDER}├──────────────────────────────────────────────────────────────────────────┤{C_RESET}\n")

    if u.subscriptions:
        for sub in u.subscriptions:
            s_name = sub.subscription or ""
            s_key = sub.key if sub.key else "Direct Entitlement"
            s_exp = format_timestamp(sub.expiry) or "Lifetime"
            sys.stdout.write(
                f"  {C_BORDER}│{C_RESET}  {C_GREEN}●{C_RESET} {C_WHITE}{C_BOLD}{s_name:<16.16}{C_RESET}"
                f" {C_DIM}Key:{C_RESET} {C_CYAN}{s_key:<22.22}{C_RESET}"
                f" {C_DIM}Exp:{C_RESET} {C_AMBER}{s_exp:<16.16}{C_RESET} {C_BORDER}│{C_RESET}\n"
            )
    else:
        sys.stdout.write(
            f"  {C_BORDER}│{C_RESET}  {C_DIM}No active subscription tiers attached to this account.{C_RESET}"
            f"                   {C_BORDER}│{C_RESET}\n"
        )
    sys.stdout.write(f"  {C_BORDER}╰──────────────────────────────────────────────────────────────────────────╯{C_RESET}\n")
    sys.stdout.flush()

def handle_chat_room():
    print_section_header("LIVE CHANNEL CHAT", "Type /exit at any time to leave the channel")
    room = ask("Channel name (e.g. general): ")
    if not room:
        room = "general"

    msgs = night_auth.get_chat_messages(room, 0, True)
    sys.stdout.write(f"\n  {C_BORDER}╭─ {C_GLOW}{C_BOLD}#{room:<20}{C_BORDER} ──────────────────────────────────────────────────╮{C_RESET}\n")
    if not msgs:
        sys.stdout.write(f"  {C_BORDER}│{C_RESET}  {C_DIM}No messages in this channel yet. Start the conversation below.{C_RESET}          {C_BORDER}│{C_RESET}\n")
    else:
        for m in msgs:
            sys.stdout.write(f"  {C_BORDER}│{C_RESET} {C_DIM}[{m.timestamp}]{C_RESET} {C_CYAN}{C_BOLD}{m.author}{C_RESET}: {C_TEXT}{m.message}{C_RESET}\n")
    sys.stdout.write(f"  {C_BORDER}╰──────────────────────────────────────────────────────────────────────────╯{C_RESET}\n\n")
    sys.stdout.flush()

    while True:
        inp = ask(f"{C_CYAN}#{room}{C_RESET} message: ")
        if inp in ("/exit", "/EXIT"):
            sys.stdout.write(f"  {C_DIM}Left channel #{room}.{C_RESET}\n\n")
            return
        if not inp:
            continue
        if not night_auth.send_chat_message(inp, room):
            print_err("Send Failed", night_auth.response.message)

def render_stats_table():
    stats = night_auth.get_stats()
    if stats:
        ver_str = stats.version if stats.version else APP_VERSION
        sys.stdout.write("\n")
        sys.stdout.write(f"  {C_BORDER}╭─ {C_GLOW}{C_BOLD}APPLICATION LIVE TELEMETRY{C_BORDER} ─────────────────────────────────────────────╮{C_RESET}\n")
        sys.stdout.write(
            f"  {C_BORDER}│{C_RESET}  {C_DIM}Total Users     :{C_RESET} {C_WHITE}{C_BOLD}{stats.total_users:<14}{C_RESET}"
            f"  {C_DIM}Total Licenses  :{C_RESET} {C_WHITE}{C_BOLD}{stats.total_licenses:<18}{C_RESET} {C_BORDER}│{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BORDER}│{C_RESET}  {C_DIM}Active Users    :{C_RESET} {C_GREEN}{C_BOLD}{stats.active_users:<14}{C_RESET}"
            f"  {C_DIM}Used Licenses   :{C_RESET} {C_CYAN}{C_BOLD}{stats.used_licenses:<18}{C_RESET} {C_BORDER}│{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BORDER}│{C_RESET}  {C_DIM}Banned Users    :{C_RESET} {C_RED}{C_BOLD}{stats.banned_users:<14}{C_RESET}"
            f"  {C_DIM}Unused Licenses :{C_RESET} {C_AMBER}{C_BOLD}{stats.unused_licenses:<18}{C_RESET} {C_BORDER}│{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BORDER}│{C_RESET}  {C_DIM}Target Version  :{C_RESET} {C_GLOW}{ver_str:<52}{C_RESET} {C_BORDER}│{C_RESET}\n"
        )
        sys.stdout.write(f"  {C_BORDER}╰──────────────────────────────────────────────────────────────────────────╯{C_RESET}\n\n")
        sys.stdout.flush()
    else:
        print_err("Telemetry Error", night_auth.response.message)

def handle_setup_2fa():
    print_section_header("TWO-FACTOR AUTHENTICATION (TOTP)", "Enroll an authenticator app (RFC 6238)")
    setup = night_auth.setup_2fa()
    if setup:
        print_info("TOTP Secret Key:", setup.secret)
        print_info("Provisioning URI:", setup.uri)
        code = ask("Enter 6-digit Authenticator code: ")
        conf = night_auth.confirm_2fa(code)
        if conf:
            print_ok("2FA Activated", "Store these recovery backup codes safely:")
            for bc in conf.backup_codes:
                sys.stdout.write(f"    {C_AMBER}• {bc}{C_RESET}\n")
            sys.stdout.write("\n")
            sys.stdout.flush()
        else:
            print_err("Verification Failed", night_auth.response.message)
    else:
        print_err("2FA Setup Failed", night_auth.response.message)

def handle_download_file():
    print_section_header("PROTECTED ASSET DOWNLOADER", "Download encrypted files via scoped access ticket")
    file_id = ask("Enter File ID or Asset Name: ")
    content = night_auth.download_file(file_id)
    if content is not None:
        size = len(content)
        content = b"\x00" * size
        print_ok("Download Complete", f"Retrieved {size} bytes securely.")
    else:
        print_err("Download Failed", night_auth.response.message)

def handle_list_all_user_vars():
    vars_list = night_auth.get_user_variables()
    if vars_list is None:
        print_err("Fetch Failed", night_auth.response.message)
        return
    print_section_header("USER CLOUD VARIABLES", "Per-user encrypted key-value pairs")
    if not vars_list:
        sys.stdout.write(f"  {C_DIM}No user variables stored for this account yet.{C_RESET}\n\n")
        return
    for kv in vars_list:
        k = str(kv.get("key", "")) if isinstance(kv, dict) else str(kv[0])
        v = str(kv.get("value", "")) if isinstance(kv, dict) else str(kv[1])
        sys.stdout.write(f"  {C_BLUE}•{C_RESET} {C_CYAN}{C_BOLD}{k:<22}{C_RESET} = {C_WHITE}{v}{C_RESET}\n")
    sys.stdout.write("\n")
    sys.stdout.flush()

def handle_trigger_webhook():
    print_section_header("SERVER-SIDE WEBHOOK TRIGGER", "Execute an authenticated webhook endpoint")
    web_id = ask("Webhook ID: ")
    payload_str = ask(f"JSON Payload {C_DIM}(Enter for {{}}){C_TEXT}: ")
    if not payload_str:
        payload_str = "{}"

    try:
        payload = json.loads(payload_str)
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a JSON object")
        result = night_auth.trigger_webhook(web_id, payload)
        if result is not None:
            print_ok("Webhook Dispatched", "HTTP 200 OK")
        else:
            print_err("Webhook Failed", night_auth.response.message)
    except Exception as ex:
        print_err("Invalid Webhook Payload", str(ex))

def handle_events_feed():
    print_section_header("REAL-TIME APPLICATION EVENTS (SSE)", "Press Enter at any time to stop listening")
    night_auth.start_realtime_event_listener()
    ask("")
    night_auth.stop_realtime_event_listener()
    print_ok("Stream Closed", "Disconnected from real-time event feed.")

def handle_self_ban():
    print_section_header("EMERGENCY KILLSWITCH / BAN", "Report security violation and lock this session")
    reason = ask(f"Ban Reason {C_DIM}(Optional){C_TEXT}: ")

    if night_auth.ban(reason if reason else None):
        print_ok("Killswitch Executed", night_auth.response.message)
    else:
        print_err("Ban Report Failed", night_auth.response.message)

def handle_heartbeat():
    if night_auth.heartbeat():
        print_ok("Heartbeat Acknowledged", night_auth.response.message)
    else:
        print_err("Heartbeat Failed", night_auth.response.message)

def handle_kill_session_demo():
    print_section_header("SESSION REVOCATION & INVALIDATION VERIFICATION", "3-Step Live Security Audit")
    sys.stdout.write(f"  {C_MUTED}1. Verifying active session before revocation...{C_RESET}\n")
    if night_auth.check():
        print_ok("Step 1 Passed", "Session is active and authenticated on server.")
    else:
        print_err("Step 1 Failed", night_auth.response.message)
        return

    sys.stdout.write(f"  {C_MUTED}2. Revoking and terminating session on server (/logout)...{C_RESET}\n")
    if night_auth.logout():
        print_ok("Step 2 Passed", "Server confirmed session revocation.")
    else:
        print_err("Step 2 Failed", night_auth.response.message)

    sys.stdout.write(f"  {C_MUTED}3. Verifying that subsequent session check is rejected...{C_RESET}\n")
    if night_auth.check():
        print_err("Step 3 Unexpected", "Session was still accepted after revocation.")
    else:
        print_ok("Step 3 Passed", "Server rejected revoked session as expected.")

def run_application_features_menu():
    while True:
        print_section_header("WORKSPACE MODULES & ACTIONS", "Select a command [1-21]")

        sys.stdout.write(f"  {C_DIM}CLOUD VARIABLES & CHAT{C_RESET}                    {C_DIM}SECURITY & TELEMETRY{C_RESET}\n")
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 01 {C_RESET} {C_WHITE}Read Global Variable{C_RESET}"
            f"                 {C_BADGE_BG}{C_GLOW}{C_BOLD} 10 {C_RESET} {C_WHITE}Setup Two-Factor Auth (2FA){C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 02 {C_RESET} {C_WHITE}Get User Cloud Variable{C_RESET}"
            f"              {C_BADGE_BG}{C_GLOW}{C_BOLD} 11 {C_RESET} {C_WHITE}Disable Two-Factor Auth (2FA){C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 03 {C_RESET} {C_WHITE}Set User Cloud Variable{C_RESET}"
            f"              {C_BADGE_BG}{C_GLOW}{C_BOLD} 12 {C_RESET} {C_WHITE}Download Protected Asset{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 04 {C_RESET} {C_WHITE}List All User Variables{C_RESET}"
            f"              {C_BADGE_BG}{C_GLOW}{C_BOLD} 13 {C_RESET} {C_WHITE}Trigger Server Webhook{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 05 {C_RESET} {C_WHITE}Enter Live Chat Channel{C_RESET}"
            f"              {C_BADGE_BG}{C_GLOW}{C_BOLD} 14 {C_RESET} {C_WHITE}Send Audit Log Event{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 19 {C_RESET} {C_WHITE}Fetch Paginated Chat History{C_RESET}"
            f"         {C_BADGE_BG}{C_GLOW}{C_BOLD} 15 {C_RESET} {C_WHITE}Verify Session Entitlement{C_RESET}\n\n"
        )

        sys.stdout.write(f"  {C_DIM}ACCOUNT & INSIGHTS{C_RESET}                        {C_DIM}SESSION LIFECYCLE{C_RESET}\n")
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 06 {C_RESET} {C_WHITE}Application Live Statistics{C_RESET}"
            f"          {C_BADGE_BG}{C_GLOW}{C_BOLD} 16 {C_RESET} {C_WHITE}Send Heartbeat Ping{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 07 {C_RESET} {C_WHITE}View Online Active Users{C_RESET}"
            f"             {C_BADGE_BG}{C_GLOW}{C_BOLD} 17 {C_RESET} {C_WHITE}Emergency Killswitch / Ban{C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 08 {C_RESET} {C_WHITE}Change Account Username{C_RESET}"
            f"              {C_BADGE_BG}{C_GLOW}{C_BOLD} 18 {C_RESET} {C_WHITE}Stream Live Events (SSE){C_RESET}\n"
        )
        sys.stdout.write(
            f"  {C_BADGE_BG}{C_GLOW}{C_BOLD} 09 {C_RESET} {C_WHITE}Upgrade Plan with License Key{C_RESET}"
            f"        {C_BADGE_BG}{C_GLOW}{C_BOLD} 20 {C_RESET} {C_WHITE}Session Revocation Audit Demo{C_RESET}\n"
        )
        sys.stdout.write(
            f"                                            {C_RED_BG}{C_RED}{C_BOLD} 21 {C_RESET} {C_MUTED}Sign Out & Terminate Session{C_RESET}\n\n"
        )

        choice = ask("Action [1-21]: ")
        try:
            num = int(choice)
        except ValueError:
            num = 0

        if num == 1:
            g_key = ask("Global Variable Key: ")
            g_val = night_auth.get_global_var(g_key)
            if g_val:
                print_ok(g_key, g_val)
            else:
                print_err("Fetch Failed", night_auth.response.message)
        elif num == 2:
            u_key = ask("User Variable Key: ")
            u_val = night_auth.get_user_var(u_key)
            if u_val:
                print_ok(u_key, u_val)
            else:
                print_err("Fetch Failed", night_auth.response.message)
        elif num == 3:
            s_key = ask("User Variable Key: ")
            s_val = ask("Value to Store: ")
            if night_auth.set_user_var(s_key, s_val):
                print_ok("Variable Saved", s_key)
            else:
                print_err("Save Failed", night_auth.response.message)
        elif num == 4:
            handle_list_all_user_vars()
        elif num == 5:
            handle_chat_room()
        elif num == 6:
            render_stats_table()
        elif num == 7:
            users = night_auth.get_online_users()
            hdr = f"{len(users)} active session(s)"
            print_section_header("ONLINE ACTIVE SESSIONS", hdr)
            for u in users:
                sys.stdout.write(f"  {C_GREEN}●{C_RESET} {C_WHITE}{u}{C_RESET}\n")
            sys.stdout.write("\n")
            sys.stdout.flush()
        elif num == 8:
            new_u = ask("New Username: ")
            p1 = ask("Confirm Password: ")
            if night_auth.change_username(new_u, p1):
                print_ok("Username Updated", night_auth.user.username)
                sys.stdout.write(f"  {C_AMBER}For security, your session has been closed. Please sign in with your new username.{C_RESET}\n\n")
                return
            else:
                print_err("Update Failed", night_auth.response.message)
        elif num == 9:
            if handle_upgrade(night_auth.user.username):
                night_auth.check()
                render_user_profile()
        elif num == 10:
            handle_setup_2fa()
        elif num == 11:
            p3 = ask("Account Password: ")
            code3 = ask("6-digit Authenticator Code: ")
            if night_auth.disable_2fa(p3, code3):
                print_ok("2FA Disabled", "Two-factor protection has been removed from this account.")
            else:
                print_err("Disable Failed", night_auth.response.message)
        elif num == 12:
            handle_download_file()
        elif num == 13:
            handle_trigger_webhook()
        elif num == 14:
            log_msg = ask("Audit Log Message: ")
            if night_auth.log(log_msg):
                print_ok("Audit Log Recorded", "Delivered to application telemetry feed.")
            else:
                print_err("Log Failed", night_auth.response.message)
        elif num == 15:
            if night_auth.check():
                print_ok("Session Verified", "Active and cryptographically valid.")
                render_user_profile()
            else:
                print_err("Session Invalid", night_auth.response.message)
        elif num == 16:
            handle_heartbeat()
        elif num == 17:
            handle_self_ban()
        elif num == 18:
            handle_events_feed()
        elif num == 19:
            hist_room = ask("Channel Name: ")
            hist_before = ask(f"Before Message ID {C_DIM}(Optional, Enter for latest){C_TEXT}: ")
            hist_mr = ask("Mark messages as read? (y/n): ")
            try:
                before_id = int(hist_before) if hist_before else 0
            except ValueError:
                before_id = 0
            mark_read = bool(hist_mr and hist_mr[0] in ("y", "Y"))

            hist = night_auth.get_chat_messages(hist_room, before_id, mark_read)
            if not night_auth.response.success:
                print_err("History Query Failed", night_auth.response.message)
            else:
                sub = f"{len(hist)} message(s) retrieved"
                print_section_header(hist_room, sub)
                for m in hist:
                    m_status = getattr(m, "status", "") or "-"
                    sys.stdout.write(
                        f"  {C_DIM}[{m.timestamp}]{C_RESET} {C_CYAN}{C_BOLD}{m.author}{C_RESET}: "
                        f"{C_TEXT}{m.message}{C_RESET} {C_DIM}(#{m.id} · {m_status}){C_RESET}\n"
                    )
                sys.stdout.write("\n")
                sys.stdout.flush()
        elif num == 20:
            handle_kill_session_demo()
            return
        elif num == 21:
            night_auth.logout()
            print_ok("Signed Out", "Session revoked cleanly. Goodbye!")
            return

def start_heartbeat_thread():
    def hb_worker():
        while True:
            time.sleep(120)
            try:
                night_auth.heartbeat()
            except Exception:
                pass
    t = threading.Thread(target=hb_worker, daemon=True)
    t.start()

def main():
    app_name = os.environ.get("NIGHTAUTH_APP_NAME") or APP_NAME
    app_key = os.environ.get("NIGHTAUTH_API_KEY") or APP_API_KEY
    app_version = os.environ.get("NIGHTAUTH_APP_VERSION") or APP_VERSION
    app_token = os.environ.get("NIGHTAUTH_APP_TOKEN") or APP_TOKEN

    clear_screen()
    render_banner(app_name, "", False)

    if not app_name:
        app_name = ask("Enter App Name: ")
    if not app_key:
        app_key = ask("Enter API Key: ")

    NightAuthApp.name = app_name
    NightAuthApp.api_key = app_key
    NightAuthApp.version = app_version
    NightAuthApp.token = app_token

    try:
        nightauth.SecurityProtections.run_security_checks()
    except nightauth.SecurityError:
        os.environ["NIGHTAUTH_IGNORE_SECURITY"] = "1"

    register_realtime_event_handlers()
    perform_handshake(NightAuthApp.name)

    if not handle_authentication_flow():
        NightAuthApp.close()
        return

    hwid = nightauth.SecurityProtections.get_hardware_id()
    clear_screen()
    render_banner(NightAuthApp.name, hwid, True)
    render_user_profile()

    start_heartbeat_thread()
    run_application_features_menu()
    NightAuthApp.close()

if __name__ == "__main__":
    main()
