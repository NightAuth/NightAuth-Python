import datetime
import hashlib
import io
import json
import os
import sys
import threading
import time
from typing import Optional, List, Dict, Any, Set

try:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QByteArray, QPoint, QEvent
    from PyQt6.QtGui import (
        QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QLinearGradient,
        QBrush, QPen, QCursor
    )
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
        QTextEdit, QScrollArea, QFrame, QMessageBox, QStackedWidget,
        QHeaderView, QSizePolicy, QProgressBar, QDialog, QGridLayout,
        QButtonGroup, QFileDialog, QRadioButton, QListWidget, QListWidgetItem
    )
except ImportError:
    print("PyQt6 is required to run NightAuth Desktop UI. Please install it using: pip install -r requirements.txt")
    sys.exit(1)

try:
    import qrcode
except ImportError:
    qrcode = None

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sdk")))
import nightauth

os.environ.setdefault("NIGHTAUTH_IGNORE_SECURITY", "1")

APP_NAME = ""
APP_API_KEY = ""
APP_VERSION = "1.0"
APP_TOKEN = None

NightAuthApp = nightauth.api(
    name=os.getenv("NIGHTAUTH_APP_NAME") or APP_NAME,
    apikey=os.getenv("NIGHTAUTH_API_KEY") or APP_API_KEY,
    version=os.getenv("NIGHTAUTH_APP_VERSION") or APP_VERSION,
    token=os.getenv("NIGHTAUTH_APP_TOKEN") or APP_TOKEN
)

SVG_USER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>"""

SVG_LOCK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>"""

SVG_MAIL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>"""

SVG_KEY = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<circle cx="7.5" cy="15.5" r="5.5"/><path d="m11.5 11.5 8.5-8.5"/><path d="m17 4 3 3"/><path d="m14 7 2 2"/></svg>"""

SVG_EYE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>"""

SVG_EYE_OFF = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>"""

SVG_SHIELD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>"""

SVG_DATABASE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></svg>"""

SVG_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>"""

SVG_BAR_CHART = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>"""

SVG_DOWNLOAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>"""

SVG_WEBHOOK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>"""

SVG_CLOCK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>"""

SVG_CHECK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
<polyline points="20 6 9 17 4 12"/></svg>"""

def create_svg_pixmap(svg_template: str, size: int = 18, color: str = "#94A3B8") -> QPixmap:
    code = svg_template.replace("{color}", color)
    renderer = QSvgRenderer(QByteArray(code.encode("utf-8")))
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return pix

def create_svg_icon(svg_template: str, size: int = 18, color: str = "#94A3B8") -> QIcon:
    return QIcon(create_svg_pixmap(svg_template, size=size, color=color))

WPF_STYLESHEET = """
QWidget {
    font-family: 'Segoe UI', Inter, Arial, sans-serif;
    color: #f4f4f5;
    font-size: 13px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QLabel {
    background-color: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
}

QFrame {
    background-color: transparent;
    border: none;
}

QFrame[class="card"], QFrame.card {
    background-color: #0d0d10;
    border: 1px solid #26262b;
    border-radius: 12px;
}

QFrame[class="card-sm"], QFrame.card-sm {
    background-color: #0d0d10;
    border: 1px solid #26262b;
    border-radius: 10px;
}

QScrollBar:vertical {
    background-color: #0d0d10;
    width: 6px;
    border-radius: 3px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #26262b;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #3b82f6;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QLineEdit {
    background-color: #0E1017;
    color: #f4f4f5;
    border: 1px solid #232736;
    border-radius: 8px;
    padding: 0px 12px;
    font-size: 13px;
    min-height: 38px;
}
QLineEdit:hover {
    border: 1px solid #3F475E;
    background-color: #121520;
}
QLineEdit:focus {
    border: 1px solid #3b82f6;
    background-color: #0E1017;
}
QLineEdit:disabled {
    opacity: 0.56;
}

QPushButton[class="primary-btn"], QPushButton.primary-btn, QPushButton#btnSubmit {
    background-color: #3b82f6;
    color: #ffffff;
    font-weight: 600;
    font-size: 12.5px;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    min-height: 20px;
}
QPushButton[class="primary-btn"]:hover, QPushButton.primary-btn:hover, QPushButton#btnSubmit:hover {
    background-color: #2563eb;
}
QPushButton[class="primary-btn"]:pressed, QPushButton.primary-btn:pressed, QPushButton#btnSubmit:pressed {
    background-color: #1d4ed8;
}
QPushButton[class="primary-btn"]:disabled, QPushButton.primary-btn:disabled, QPushButton#btnSubmit:disabled {
    background-color: #1e293b;
    color: #64748b;
}

QPushButton[class="ghost-btn"], QPushButton.ghost-btn {
    background-color: transparent;
    color: #a1a1aa;
    border: 1px solid #26262b;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 500;
    font-size: 12.5px;
}
QPushButton[class="ghost-btn"]:hover, QPushButton.ghost-btn:hover {
    background-color: #1a1a1e;
    color: #f4f4f5;
}

QPushButton[class="link-btn"], QPushButton.link-btn {
    background-color: transparent;
    color: #a1a1aa;
    border: none;
    font-size: 12px;
    padding: 2px 4px;
}
QPushButton[class="link-btn"]:hover, QPushButton.link-btn:hover {
    color: #f4f4f5;
    text-decoration: underline;
}

QPushButton[class="nav-item"], QPushButton.nav-item {
    background-color: transparent;
    color: #a1a1aa;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
}
QPushButton[class="nav-item"]:hover, QPushButton.nav-item:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: #f4f4f5;
}
QPushButton[class="nav-item"]:checked, QPushButton.nav-item:checked {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid #3b82f6;
    border-left: 3px solid #3b82f6;
    color: #ffffff;
    font-weight: bold;
}

QPushButton[class="segmented-tab"], QPushButton.segmented-tab {
    background-color: transparent;
    color: #8F9BB3;
    font-weight: 600;
    font-size: 11px;
    border: none;
    border-radius: 6px;
    padding: 7px 2px;
}
QPushButton[class="segmented-tab"]:hover, QPushButton.segmented-tab:hover {
    background-color: #171C2B;
    color: #F1F5F9;
}
QPushButton[class="segmented-tab"]:checked, QPushButton.segmented-tab:checked {
    background-color: #3b82f6;
    color: #ffffff;
    font-weight: bold;
}

QTableWidget {
    background-color: #0E1017;
    border: 1px solid #26262b;
    border-radius: 8px;
    gridline-color: #1a1a1e;
    color: #f4f4f5;
    font-size: 12px;
}
QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1a1a1e;
}
QHeaderView::section {
    background-color: #131316;
    color: #6b6b74;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #26262b;
    font-weight: bold;
    font-size: 10.5px;
    text-transform: uppercase;
}

QTextEdit {
    background-color: #0E1017;
    border: 1px solid #232736;
    border-radius: 8px;
    color: #f4f4f5;
    padding: 10px;
    font-size: 13px;
}
"""

def format_timestamp(raw):
    if not raw or not str(raw).strip():
        return "—"
    s = str(raw).strip()
    if s.isdigit() and int(s) > 0:
        val = int(s)
        if val > 100_000_000_000:
            val = val // 1000
        dt = datetime.datetime.fromtimestamp(val, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    try:
        dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return s

def format_time_remaining(total_seconds):
    if total_seconds <= 0:
        return "Expired"
    days = total_seconds // 86400
    rem = total_seconds % 86400
    hours = rem // 3600
    rem = rem % 3600
    mins = rem // 60
    secs = rem % 60
    if days >= 1:
        return f"{days}d {hours}h ({total_seconds}s)"
    if hours >= 1:
        return f"{hours}h {mins}m ({total_seconds}s)"
    if mins >= 1:
        return f"{mins}m {secs}s ({total_seconds}s)"
    return f"{total_seconds}s"

def make_primary_btn(text: str, parent=None) -> QPushButton:
    btn = QPushButton(text, parent)
    btn.setFixedHeight(38)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet("""
        QPushButton {
            background-color: #3b82f6;
            color: #ffffff;
            font-size: 12.5px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
        QPushButton:pressed {
            background-color: #1d4ed8;
        }
        QPushButton:disabled {
            background-color: #1e293b;
            color: #64748b;
        }
    """)
    return btn

def make_ghost_btn(text: str, parent=None) -> QPushButton:
    btn = QPushButton(text, parent)
    btn.setFixedHeight(38)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            color: #a1a1aa;
            border: 1px solid #26262b;
            border-radius: 8px;
            padding: 8px 14px;
            font-weight: 500;
            font-size: 12.5px;
        }
        QPushButton:hover {
            background-color: #1a1a1e;
            color: #f4f4f5;
        }
        QPushButton:pressed {
            background-color: #26262b;
        }
    """)
    return btn

class ApiWorker(QThread):
    result_signal = pyqtSignal(bool, str, object)

    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            res = self.task_func(*self.args, **self.kwargs)
            self.result_signal.emit(True, "", res)
        except Exception as e:
            self.result_signal.emit(False, str(e), None)

ACTIVE_WORKERS: Set[ApiWorker] = set()

def run_async(task_func, on_done_callback):
    worker = ApiWorker(task_func)
    ACTIVE_WORKERS.add(worker)

    def on_result(ok, err, res):
        try:
            on_done_callback(ok, err, res)
        except Exception:
            pass

    def on_finished():
        ACTIVE_WORKERS.discard(worker)
        worker.deleteLater()

    worker.result_signal.connect(on_result)
    worker.finished.connect(on_finished)
    worker.start()
    return worker

class DraggableTitleBar(QFrame):
    """Exact replica of WPF Custom TitleBar with drag window and minimize/close buttons."""
    def __init__(self, parent_window, title: str = "NIGHTAUTH", subtitle: str = "NATIVE PYTHON SECURITY CLIENT", height: int = 50):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.setFixedHeight(height)
        self.setObjectName("TitleBar")
        self.setStyleSheet("""
            QFrame#TitleBar {
                background-color: #131316;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border-bottom: 1px solid #26262b;
            }
        """)
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 10, 0)
        layout.setSpacing(10)

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        self.lbl_logo = QLabel()
        logo_size = 28 if height >= 50 else 26
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(logo_size, logo_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl_logo.setPixmap(pix)
        else:
            self.lbl_logo.setPixmap(create_svg_pixmap(SVG_SHIELD, size=logo_size, color="#3B82F6"))
        self.lbl_logo.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.lbl_logo)

        t_box = QVBoxLayout()
        t_box.setSpacing(0)
        t_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-size: 14px; font-weight: 900; color: #ffffff; border: none; background: transparent;")
        self.lbl_sub = QLabel(subtitle)
        self.lbl_sub.setStyleSheet("font-size: 9.5px; font-weight: bold; color: #6b6b74; border: none; background: transparent;")
        t_box.addWidget(self.lbl_title)
        t_box.addWidget(self.lbl_sub)
        layout.addLayout(t_box)

        layout.addStretch()

        self.btn_min = QPushButton("−")
        self.btn_min.setFixedSize(32, 32)
        self.btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_min.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #a1a1aa;
                font-size: 15px;
                font-weight: bold;
                border: 1px solid transparent;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.08);
                color: #ffffff;
            }
        """)
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.btn_min)

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #a1a1aa;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid transparent;
                border-radius: 7px;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: #ffffff;
            }
        """)
        self.btn_close.clicked.connect(QApplication.instance().quit)
        layout.addWidget(self.btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.parent_window.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.parent_window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

class IconInputRow(QWidget):
    """Input field with icon on the left, matching WPF NightAuthIconTextBox."""
    def __init__(self, svg_icon: str, placeholder: str = "", is_password: bool = False, max_length: int = 0):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._is_focused = False
        self._is_hovered = False

        self.container = QFrame()
        self.container.setObjectName("inputContainer")
        self.container.setFixedHeight(38)
        self.container.setStyleSheet("""
            QFrame#inputContainer {
                background-color: #0E1017;
                border: 1px solid #232736;
                border-radius: 8px;
            }
        """)
        c_layout = QHBoxLayout(self.container)
        c_layout.setContentsMargins(12, 0, 8, 0)
        c_layout.setSpacing(10)

        self.icon_lbl = QLabel()
        self.icon_lbl.setPixmap(create_svg_pixmap(svg_icon, size=15, color="#64748B"))
        self.icon_lbl.setStyleSheet("border: none; background: transparent;")
        c_layout.addWidget(self.icon_lbl)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        if max_length > 0:
            self.line_edit.setMaxLength(max_length)
        if is_password:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.line_edit.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #f4f4f5;
                font-size: 13px;
                padding: 0;
            }
        """)
        pal = self.line_edit.palette()
        pal.setColor(QPalette.ColorRole.PlaceholderText, QColor("#525B75"))
        self.line_edit.setPalette(pal)
        c_layout.addWidget(self.line_edit, 1)

        self.is_password = is_password
        self.eye_btn = None
        if is_password:
            self.eye_btn = QPushButton()
            self.eye_btn.setFixedSize(28, 28)
            self.eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.eye_btn.setIcon(create_svg_icon(SVG_EYE, size=16, color="#6b6b74"))
            self.eye_btn.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { color: #f4f4f5; }")
            self.eye_btn.clicked.connect(self._toggle_password_visible)
            c_layout.addWidget(self.eye_btn)

        layout.addWidget(self.container)

        self.line_edit.installEventFilter(self)
        self.container.installEventFilter(self)

    def eventFilter(self, obj, event):
        t = event.type()
        if t == QEvent.Type.FocusIn:
            self._is_focused = True
            self._update_container_style()
        elif t == QEvent.Type.FocusOut:
            self._is_focused = False
            self._update_container_style()
        elif t == QEvent.Type.Enter:
            self._is_hovered = True
            self._update_container_style()
        elif t == QEvent.Type.Leave:
            self._is_hovered = False
            self._update_container_style()
        return super().eventFilter(obj, event)

    def _update_container_style(self):
        if self._is_focused:
            self.container.setStyleSheet("""
                QFrame#inputContainer {
                    background-color: #0E1017;
                    border: 1px solid #3b82f6;
                    border-radius: 8px;
                }
            """)
        elif self._is_hovered:
            self.container.setStyleSheet("""
                QFrame#inputContainer {
                    background-color: #121520;
                    border: 1px solid #3F475E;
                    border-radius: 8px;
                }
            """)
        else:
            self.container.setStyleSheet("""
                QFrame#inputContainer {
                    background-color: #0E1017;
                    border: 1px solid #232736;
                    border-radius: 8px;
                }
            """)

    def _toggle_password_visible(self):
        if self.line_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_btn.setIcon(create_svg_icon(SVG_EYE_OFF, size=16, color="#3b82f6"))
        else:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_btn.setIcon(create_svg_icon(SVG_EYE, size=16, color="#6b6b74"))

    def text(self) -> str:
        return self.line_edit.text()

    def setText(self, val: str):
        self.line_edit.setText(val)

    def clear(self):
        self.line_edit.clear()

class NightAuthDesktopApp(QMainWindow):
    event_invalidated_signal = pyqtSignal(str)
    event_banned_signal = pyqtSignal(str)
    event_status_signal = pyqtSignal(str)
    event_version_signal = pyqtSignal(str)
    event_chat_signal = pyqtSignal(object, str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(1020, 680)
        self.setMinimumSize(1020, 680)
        self.setWindowTitle(f"NightAuth — {NightAuthApp.name}" if NightAuthApp.name else "NightAuth")

        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        self.setStyleSheet(WPF_STYLESHEET)

        self.night_auth = NightAuthApp
        self._current_user = None
        self._current_chat_room = "general"
        self._auth_mode = "login"

        self._init_window_structure()
        self._bind_realtime_events()
        self._init_app_handshake()

    def _bind_realtime_events(self):
        self.event_invalidated_signal.connect(self._handle_event_invalidated)
        self.event_banned_signal.connect(self._handle_event_banned)
        self.event_status_signal.connect(self._handle_event_status)
        self.event_version_signal.connect(self._handle_event_version)
        self.event_chat_signal.connect(self._handle_event_chat)

        self.night_auth.on_session_invalidated = lambda r: self.event_invalidated_signal.emit(str(r))
        self.night_auth.on_app_banned = lambda r: self.event_banned_signal.emit(str(r))
        self.night_auth.on_app_status_changed = lambda s: self.event_status_signal.emit(str(s))
        self.night_auth.on_version_updated = lambda v: self.event_version_signal.emit(str(v))
        self.night_auth.on_chat_message_received = lambda m, room: self.event_chat_signal.emit(m, room)

    def _init_window_structure(self):
        self.root_frame = QFrame()
        self.root_frame.setObjectName("RootBorder")
        self.root_frame.setStyleSheet("""
            QFrame#RootBorder {
                background-color: #050506;
                border: 1px solid #26262b;
                border-radius: 16px;
            }
        """)
        self.setCentralWidget(self.root_frame)

        self.main_vbox = QVBoxLayout(self.root_frame)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        self.main_vbox.setSpacing(0)

        self.title_bar = DraggableTitleBar(
            self,
            title="NIGHTAUTH",
            subtitle="NATIVE PYTHON SECURITY CLIENT",
            height=50
        )
        self.main_vbox.addWidget(self.title_bar)

        self.main_stack = QStackedWidget()
        self.main_vbox.addWidget(self.main_stack, 1)

        self.auth_page = self._build_auth_screen()
        self.main_stack.addWidget(self.auth_page)

        self.dashboard_page = self._build_dashboard_screen()
        self.main_stack.addWidget(self.dashboard_page)

        self.main_stack.setCurrentIndex(0)

    def _build_auth_screen(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        hero_panel = QFrame()
        hero_panel.setFixedWidth(390)
        hero_panel.setObjectName("heroPanel")
        hero_panel.setStyleSheet("""
            QFrame#heroPanel {
                background-color: #0D101A;
                border: 1px solid #26262b;
                border-radius: 12px;
            }
        """)
        h_layout = QVBoxLayout(hero_panel)
        h_layout.setContentsMargins(24, 22, 24, 22)
        h_layout.setSpacing(0)

        badge_box = QHBoxLayout()
        self.lbl_telemetry_badge = QLabel("●  ZERO-TRUST TELEMETRY")
        self.lbl_telemetry_badge.setStyleSheet("""
            background-color: #111A2E;
            color: #93C5FD;
            border: 1px solid #253E70;
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        badge_box.addWidget(self.lbl_telemetry_badge)
        badge_box.addStretch()
        h_layout.addLayout(badge_box)
        h_layout.addSpacing(12)

        lbl_title1 = QLabel("Enterprise Cloud")
        lbl_title1.setStyleSheet("font-size: 21px; font-weight: 800; color: #ffffff; border: none; background: transparent;")
        lbl_title2 = QLabel("Licensing & Identity")
        lbl_title2.setStyleSheet("font-size: 21px; font-weight: 800; color: #60A5FA; border: none; background: transparent;")
        h_layout.addWidget(lbl_title1)
        h_layout.addWidget(lbl_title2)
        h_layout.addSpacing(8)

        lbl_desc = QLabel("Cryptographically bound sessions, hardware fingerprinting, real-time cloud variables, and tamper-evident delivery.")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 12px; color: #6b6b74; line-height: 17px; border: none; background: transparent;")
        h_layout.addWidget(lbl_desc)
        h_layout.addSpacing(18)

        features = [
            ("Instant License Key & Account Activation", "Zero-trust session negotiation with anti-replay protection"),
            ("Automatic Device HWID Binding & Reset", "Hardware fingerprint locking with self-service reset support"),
            ("Cloud Variables, Live Chat & File Delivery", "Deliver encrypted configuration and assets on demand"),
            ("Two-Factor (2FA) Account Protection", "Time-based OTP security with instant identity verification")
        ]
        for f_title, f_desc in features:
            f_card = QFrame()
            f_card.setStyleSheet("background-color: #0E0F14; border: 1px solid #1E2434; border-radius: 8px;")
            fc_layout = QHBoxLayout(f_card)
            fc_layout.setContentsMargins(10, 7, 10, 7)
            fc_layout.setSpacing(10)

            dot = QLabel("✓")
            dot.setFixedSize(22, 22)
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setStyleSheet("background-color: #0C2A20; color: #22C55E; border: 1px solid #185C46; border-radius: 5px; font-weight: bold; font-size: 11px;")
            fc_layout.addWidget(dot)

            t_col = QVBoxLayout()
            t_col.setSpacing(1)
            lt = QLabel(f_title)
            lt.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: bold; border: none; background: transparent;")
            ld = QLabel(f_desc)
            ld.setStyleSheet("color: #6b6b74; font-size: 10px; border: none; background: transparent;")
            t_col.addWidget(lt)
            t_col.addWidget(ld)
            fc_layout.addLayout(t_col, 1)

            h_layout.addWidget(f_card)
            h_layout.addSpacing(8)

        h_layout.addStretch()

        bound_card = QFrame()
        bound_card.setStyleSheet("background-color: #0E0F14; border: 1px solid #1E2434; border-radius: 8px;")
        bc_layout = QVBoxLayout(bound_card)
        bc_layout.setContentsMargins(12, 10, 12, 10)
        bc_layout.setSpacing(3)

        lbl_bc_hdr = QLabel("BOUND APPLICATION & DEVICE")
        lbl_bc_hdr.setStyleSheet("color: #60A5FA; font-size: 9.5px; font-weight: 800; border: none; background: transparent;")

        display_name = self.night_auth.name if self.night_auth.name else "Unconfigured"
        self.lbl_bound_app = QLabel(display_name)
        self.lbl_bound_app.setStyleSheet("color: #ffffff; font-size: 12.5px; font-weight: bold; border: none; background: transparent;")

        try:
            hwid = nightauth.SecurityProtections.get_hardware_id()
        except Exception:
            hwid = "Detected on Auth"
        self.lbl_bound_hwid = QLabel(f"HWID: {hwid}")
        self.lbl_bound_hwid.setStyleSheet("color: #6b6b74; font-family: Consolas, monospace; font-size: 10.5px; border: none; background: transparent;")

        bc_layout.addWidget(lbl_bc_hdr)
        bc_layout.addWidget(self.lbl_bound_app)
        bc_layout.addWidget(self.lbl_bound_hwid)
        h_layout.addWidget(bound_card)

        layout.addWidget(hero_panel)

        action_card = QFrame()
        action_card.setObjectName("actionCard")
        action_card.setStyleSheet("""
            QFrame#actionCard {
                background-color: #0d0d10;
                border: 1px solid #26262b;
                border-radius: 12px;
            }
        """)
        a_layout = QVBoxLayout(action_card)
        a_layout.setContentsMargins(28, 20, 28, 20)
        a_layout.setSpacing(0)

        self.tab_container = QFrame()
        self.tab_container.setObjectName("tabContainer")
        self.tab_container.setFixedHeight(38)
        self.tab_container.setStyleSheet("""
            QFrame#tabContainer {
                background-color: #0A0D17;
                border: 1px solid #1C2133;
                border-radius: 8px;
            }
        """)
        tc_layout = QHBoxLayout(self.tab_container)
        tc_layout.setContentsMargins(3, 3, 3, 3)
        tc_layout.setSpacing(2)

        tab_style = """
            QPushButton {
                background-color: transparent;
                color: #8F9BB3;
                font-weight: 600;
                font-size: 11px;
                border: none;
                border-radius: 6px;
                padding: 7px 2px;
            }
            QPushButton:hover {
                background-color: #171C2B;
                color: #F1F5F9;
            }
            QPushButton:checked {
                background-color: #3b82f6;
                color: #ffffff;
                font-weight: bold;
            }
        """

        self.btn_tab_login = QPushButton("Sign In")
        self.btn_tab_reg = QPushButton("Register")
        self.btn_tab_lic = QPushButton("License")
        self.btn_tab_upg = QPushButton("Upgrade")
        self.btn_tab_hwid = QPushButton("Reset HWID")

        tabs = [
            (self.btn_tab_login, "login"),
            (self.btn_tab_reg, "register"),
            (self.btn_tab_lic, "license"),
            (self.btn_tab_upg, "upgrade"),
            (self.btn_tab_hwid, "reset_hwid")
        ]
        self.tab_group = QButtonGroup(self)
        self.tab_group.setExclusive(True)

        for btn, mode in tabs:
            btn.setCheckable(True)
            btn.setStyleSheet(tab_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, m=mode: self._set_auth_mode(m))
            self.tab_group.addButton(btn)
            tc_layout.addWidget(btn)

        self.btn_tab_login.setChecked(True)
        a_layout.addWidget(self.tab_container)
        a_layout.addSpacing(14)

        self.lbl_auth_heading = QLabel("Sign in to your account")
        self.lbl_auth_heading.setStyleSheet("font-size: 17px; font-weight: bold; color: #ffffff; border: none; background: transparent;")
        self.lbl_auth_sub = QLabel("Enter your credentials to negotiate a secure zero-trust session.")
        self.lbl_auth_sub.setWordWrap(True)
        self.lbl_auth_sub.setStyleSheet("font-size: 12px; color: #7E8BA6; line-height: 17px; border: none; background: transparent;")
        a_layout.addWidget(self.lbl_auth_heading)
        a_layout.addWidget(self.lbl_auth_sub)
        a_layout.addSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 0px; }")
        scroll.viewport().setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setStyleSheet("QWidget#scrollContent { background: transparent; border: none; }")
        f_layout = QVBoxLayout(scroll_content)
        f_layout.setContentsMargins(0, 0, 0, 0)
        f_layout.setSpacing(11)

        self.row_username = QWidget()
        self.row_username.setStyleSheet("background: transparent; border: none;")
        ru_layout = QVBoxLayout(self.row_username)
        ru_layout.setContentsMargins(0, 0, 0, 0)
        ru_layout.setSpacing(4)
        self.lbl_field_user = QLabel("USERNAME")
        self.lbl_field_user.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #a1a1aa; border: none; background: transparent;")
        self.inp_username = IconInputRow(SVG_USER, placeholder="Enter your username")
        ru_layout.addWidget(self.lbl_field_user)
        ru_layout.addWidget(self.inp_username)
        f_layout.addWidget(self.row_username)

        self.row_password = QWidget()
        self.row_password.setStyleSheet("background: transparent; border: none;")
        rp_layout = QVBoxLayout(self.row_password)
        rp_layout.setContentsMargins(0, 0, 0, 0)
        rp_layout.setSpacing(4)
        lbl_p_box = QHBoxLayout()
        lbl_p_box.setContentsMargins(0, 0, 0, 0)
        self.lbl_field_pass = QLabel("PASSWORD")
        self.lbl_field_pass.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #a1a1aa; border: none; background: transparent;")
        self.btn_forgot_link = QPushButton("Forgot password?")
        self.btn_forgot_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_forgot_link.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #a1a1aa;
                border: none;
                font-size: 12px;
                padding: 2px 4px;
            }
            QPushButton:hover {
                color: #f4f4f5;
                text-decoration: underline;
            }
        """)
        self.btn_forgot_link.clicked.connect(lambda: self._set_auth_mode("forgot_password"))
        lbl_p_box.addWidget(self.lbl_field_pass)
        lbl_p_box.addStretch()
        lbl_p_box.addWidget(self.btn_forgot_link)
        self.inp_password = IconInputRow(SVG_LOCK, placeholder="Enter your password", is_password=True)
        rp_layout.addLayout(lbl_p_box)
        rp_layout.addWidget(self.inp_password)
        f_layout.addWidget(self.row_password)

        self.row_totp = QWidget()
        self.row_totp.setStyleSheet("background: transparent; border: none;")
        rt_layout = QVBoxLayout(self.row_totp)
        rt_layout.setContentsMargins(0, 0, 0, 0)
        rt_layout.setSpacing(4)
        lbl_totp = QLabel("2FA CODE (OPTIONAL)")
        lbl_totp.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #a1a1aa; border: none; background: transparent;")
        self.inp_totp = IconInputRow(SVG_LOCK, placeholder="Enter 6-digit code (if enabled)", max_length=10)
        rt_layout.addWidget(lbl_totp)
        rt_layout.addWidget(self.inp_totp)
        f_layout.addWidget(self.row_totp)

        self.row_email = QWidget()
        self.row_email.setStyleSheet("background: transparent; border: none;")
        re_layout = QVBoxLayout(self.row_email)
        re_layout.setContentsMargins(0, 0, 0, 0)
        re_layout.setSpacing(4)
        self.lbl_field_email = QLabel("EMAIL")
        self.lbl_field_email.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #a1a1aa; border: none; background: transparent;")
        self.inp_email = IconInputRow(SVG_MAIL, placeholder="Enter your email")
        re_layout.addWidget(self.lbl_field_email)
        re_layout.addWidget(self.inp_email)
        f_layout.addWidget(self.row_email)

        self.row_token = QWidget()
        self.row_token.setStyleSheet("background: transparent; border: none;")
        rk_layout = QVBoxLayout(self.row_token)
        rk_layout.setContentsMargins(0, 0, 0, 0)
        rk_layout.setSpacing(4)
        lbl_token = QLabel("RESET TOKEN")
        lbl_token.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #a1a1aa; border: none; background: transparent;")
        self.inp_token = IconInputRow(SVG_KEY, placeholder="Enter the reset token received by email")
        rk_layout.addWidget(lbl_token)
        rk_layout.addWidget(self.inp_token)
        f_layout.addWidget(self.row_token)

        self.btn_forgot_toggle = QPushButton("Already have a reset token?")
        self.btn_forgot_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_forgot_toggle.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #a1a1aa;
                border: none;
                font-size: 12px;
                padding: 2px 4px;
            }
            QPushButton:hover {
                color: #f4f4f5;
                text-decoration: underline;
            }
        """)
        self.btn_forgot_toggle.clicked.connect(self._toggle_forgot_token_mode)
        f_layout.addWidget(self.btn_forgot_toggle)

        self.row_license = QWidget()
        self.row_license.setStyleSheet("background: transparent; border: none;")
        rl_layout = QVBoxLayout(self.row_license)
        rl_layout.setContentsMargins(0, 0, 0, 0)
        rl_layout.setSpacing(4)
        lbl_license = QLabel("LICENSE KEY")
        lbl_license.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #a1a1aa; border: none; background: transparent;")
        self.inp_license = IconInputRow(SVG_KEY, placeholder="Enter your license key")
        self.lbl_license_hint = QLabel("First time using this key creates your account automatically — no separate registration needed.")
        self.lbl_license_hint.setWordWrap(True)
        self.lbl_license_hint.setStyleSheet("font-size: 10.5px; color: #6b6b74; margin-top: 4px; border: none; background: transparent;")
        rl_layout.addWidget(lbl_license)
        rl_layout.addWidget(self.inp_license)
        rl_layout.addWidget(self.lbl_license_hint)
        f_layout.addWidget(self.row_license)

        f_layout.addSpacing(6)

        self.btn_submit = QPushButton("Sign In")
        self.btn_submit.setObjectName("btnSubmit")
        self.btn_submit.setFixedHeight(38)
        self.btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit.setStyleSheet("""
            QPushButton#btnSubmit {
                background-color: #3b82f6;
                color: #ffffff;
                font-size: 12.5px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 9px 16px;
            }
            QPushButton#btnSubmit:hover {
                background-color: #2563eb;
            }
            QPushButton#btnSubmit:pressed {
                background-color: #1d4ed8;
            }
            QPushButton#btnSubmit:disabled {
                background-color: #1e293b;
                color: #64748b;
            }
        """)
        self.btn_submit.clicked.connect(self._handle_auth_submit)
        f_layout.addWidget(self.btn_submit)

        self.lbl_auth_error = QLabel("")
        self.lbl_auth_error.setWordWrap(True)
        self.lbl_auth_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_auth_error.setStyleSheet("color: #f43f5e; font-size: 12px; margin-top: 8px; border: none; background: transparent;")
        self.lbl_auth_error.setVisible(False)
        f_layout.addWidget(self.lbl_auth_error)

        self.btn_switch_mode = QPushButton("Need an account? Register")
        self.btn_switch_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_switch_mode.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #a1a1aa;
                border: none;
                font-size: 12px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #f4f4f5;
                text-decoration: underline;
            }
        """)
        self.btn_switch_mode.clicked.connect(self._handle_switch_mode)
        f_layout.addWidget(self.btn_switch_mode, 0, Qt.AlignmentFlag.AlignCenter)

        f_layout.addStretch()
        scroll.setWidget(scroll_content)
        a_layout.addWidget(scroll, 1)

        layout.addWidget(action_card, 1)

        self._set_auth_mode("login")
        return container

    def _set_auth_mode(self, mode: str):
        self._auth_mode = mode
        self.lbl_auth_error.setVisible(False)

        is_tabbed = mode in ("login", "register", "license", "upgrade", "reset_hwid")
        self.tab_container.setVisible(is_tabbed)

        if mode == "login":
            self.btn_tab_login.setChecked(True)
        elif mode == "register":
            self.btn_tab_reg.setChecked(True)
        elif mode == "license":
            self.btn_tab_lic.setChecked(True)
        elif mode == "upgrade":
            self.btn_tab_upg.setChecked(True)
        elif mode == "reset_hwid":
            self.btn_tab_hwid.setChecked(True)

        self.row_username.setVisible(False)
        self.row_password.setVisible(False)
        self.row_totp.setVisible(False)
        self.row_email.setVisible(False)
        self.row_token.setVisible(False)
        self.btn_forgot_toggle.setVisible(False)
        self.row_license.setVisible(False)
        self.lbl_license_hint.setVisible(False)
        self.btn_forgot_link.setVisible(True)
        self.lbl_field_user.setText("USERNAME")
        self.lbl_field_email.setText("EMAIL")

        if mode == "login":
            self.lbl_auth_heading.setText("Sign in to your account")
            self.lbl_auth_sub.setText("Enter your credentials to negotiate a secure zero-trust session.")
            self.row_username.setVisible(True)
            self.row_password.setVisible(True)
            self.row_totp.setVisible(True)
            self.btn_submit.setText("Sign In")
            self.btn_switch_mode.setText("Need an account? Register")

        elif mode == "license":
            self.lbl_auth_heading.setText("Instant license access")
            self.lbl_auth_sub.setText("Authenticate directly using an active license key without username.")
            self.row_license.setVisible(True)
            self.lbl_license_hint.setVisible(True)
            self.btn_submit.setText("Continue with License")
            self.btn_switch_mode.setText("Need an account? Register")

        elif mode == "register":
            self.lbl_auth_heading.setText("Create your account")
            self.lbl_auth_sub.setText("Registers a username bound to an unused license key.")
            self.row_username.setVisible(True)
            self.row_password.setVisible(True)
            self.btn_forgot_link.setVisible(False)
            self.row_license.setVisible(True)
            self.row_email.setVisible(True)
            self.lbl_field_email.setText("EMAIL (OPTIONAL)")
            self.btn_submit.setText("Create Account")
            self.btn_switch_mode.setText("Already have an account? Sign In")

        elif mode == "forgot_password":
            self.lbl_auth_heading.setText("Forgot password")
            self.lbl_auth_sub.setText("Enter your email to receive a password reset link.")
            self.row_email.setVisible(True)
            self.btn_forgot_toggle.setText("Already have a reset token?")
            self.btn_forgot_toggle.setVisible(True)
            self.btn_submit.setText("Send Reset Link")
            self.btn_switch_mode.setText("Back to Sign In")

        elif mode == "reset_password_token":
            self.lbl_auth_heading.setText("Reset password with token")
            self.lbl_auth_sub.setText("Enter the reset token received by email and your new password.")
            self.row_token.setVisible(True)
            self.row_password.setVisible(True)
            self.btn_forgot_link.setVisible(False)
            self.btn_forgot_toggle.setText("Need a token? Request email")
            self.btn_forgot_toggle.setVisible(True)
            self.btn_submit.setText("Set New Password")
            self.btn_switch_mode.setText("Back to Sign In")

        elif mode == "upgrade":
            self.lbl_auth_heading.setText("Upgrade plan with license key")
            self.lbl_auth_sub.setText("Adds this license's time to the target account's subscription.")
            self.lbl_field_user.setText("TARGET USERNAME")
            self.row_username.setVisible(True)
            self.row_license.setVisible(True)
            self.btn_submit.setText("Apply Upgrade")
            self.btn_switch_mode.setText("Back to Sign In")

        elif mode == "reset_hwid":
            self.lbl_auth_heading.setText("Reset hardware ID")
            self.lbl_auth_sub.setText("For when a HWID mismatch blocks login itself.")
            self.row_username.setVisible(True)
            self.row_password.setVisible(True)
            self.row_totp.setVisible(True)
            self.btn_forgot_link.setVisible(False)
            self.btn_submit.setText("Reset HWID")
            self.btn_switch_mode.setText("Back to Sign In")

    def _toggle_forgot_token_mode(self):
        if self._auth_mode == "forgot_password":
            self._set_auth_mode("reset_password_token")
        else:
            self._set_auth_mode("forgot_password")

    def _handle_switch_mode(self):
        if self._auth_mode in ("register", "forgot_password", "reset_password_token", "upgrade", "reset_hwid", "license"):
            self._set_auth_mode("login")
        else:
            self._set_auth_mode("register")

    def _handle_auth_submit(self):
        self.btn_submit.setEnabled(False)
        self.btn_submit.setText("Processing...")
        self.lbl_auth_error.setVisible(False)

        u = self.inp_username.text().strip()
        p = self.inp_password.text()
        em = self.inp_email.text().strip()
        lic = self.inp_license.text().strip()
        totp = self.inp_totp.text().strip() or None
        tok = self.inp_token.text().strip()
        mode = self._auth_mode

        def task():
            if mode == "login":
                return self.night_auth.login(u, p, totp)
            elif mode == "license":
                return self.night_auth.license(lic)
            elif mode == "register":
                return self.night_auth.register(u, p, lic, em or None)
            elif mode == "forgot_password":
                return self.night_auth.forgot_password(em)
            elif mode == "reset_password_token":
                return self.night_auth.reset_password(tok, p)
            elif mode == "upgrade":
                return self.night_auth.upgrade(u, lic)
            elif mode == "reset_hwid":
                return self.night_auth.reset_hwid(u, p, totp)
            return None

        def on_done(ok, err, res):
            self.btn_submit.setEnabled(True)
            self._restore_submit_button_text()

            if not ok or not res:
                server_msg = getattr(getattr(self.night_auth, "response", None), "message", None)
                msg = err or server_msg or "Operation failed."
                self.lbl_auth_error.setText(f"Error: {msg}")
                self.lbl_auth_error.setVisible(True)
                return

            msg = getattr(self.night_auth.response, "message", None) or "Operation completed successfully."
            if mode in ("login", "license"):
                self._current_user = getattr(self.night_auth, "user", None) or getattr(self.night_auth, "user_data", None)
                self._enter_dashboard()
            elif mode == "register":
                QMessageBox.information(self, "NightAuth", "Account created successfully! You can now sign in.")
                self._set_auth_mode("login")
            elif mode == "forgot_password":
                QMessageBox.information(self, "NightAuth", "Reset token sent! Check your inbox, then enter the token.")
                self._set_auth_mode("reset_password_token")
            elif mode == "reset_password_token":
                QMessageBox.information(self, "NightAuth", "Password reset successful! Sign in with your new password.")
                self._set_auth_mode("login")
            elif mode in ("upgrade", "reset_hwid"):
                QMessageBox.information(self, "NightAuth", msg)
                self._set_auth_mode("login")

        run_async(task, on_done)

    def _restore_submit_button_text(self):
        modes = {
            "login": "Sign In",
            "license": "Continue with License",
            "register": "Create Account",
            "forgot_password": "Send Reset Link",
            "reset_password_token": "Set New Password",
            "upgrade": "Apply Upgrade",
            "reset_hwid": "Reset HWID"
        }
        self.btn_submit.setText(modes.get(self._auth_mode, "Submit"))

    def _build_dashboard_screen(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setObjectName("dashSidebar")
        sidebar.setStyleSheet("""
            QFrame#dashSidebar {
                background-color: #131316;
                border-right: 1px solid #26262b;
            }
        """)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(12, 18, 12, 16)
        sb_layout.setSpacing(4)

        self.dash_nav_group = QButtonGroup(self)
        self.dash_nav_group.setExclusive(True)

        nav_items = [
            ("01  Overview", 0),
            ("02  Subscriptions", 1),
            ("03  Variables", 2),
            ("04  Live Chat", 3),
            ("05  Statistics", 4),
            ("06  Security", 5),
            ("07  Files && Hooks", 6)
        ]
        self.nav_buttons = []
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("class", "nav-item")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=idx: self._on_dash_nav_clicked(i))
            self.dash_nav_group.addButton(btn, idx)
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        self.nav_buttons[0].setChecked(True)
        sb_layout.addStretch()

        bottom_strip = QFrame()
        bottom_strip.setStyleSheet("border-top: 1px solid #26262b; background: transparent;")
        bs_layout = QVBoxLayout(bottom_strip)
        bs_layout.setContentsMargins(0, 14, 0, 0)
        bs_layout.setSpacing(8)

        lbl_user_box = QHBoxLayout()
        lbl_user_box.setSpacing(4)
        lbl_si = QLabel("SIGNED IN AS ")
        lbl_si.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #6b6b74;")
        self.lbl_dash_username = QLabel("User")
        self.lbl_dash_username.setStyleSheet("font-size: 11.5px; font-weight: bold; color: #f4f4f5;")
        lbl_user_box.addWidget(lbl_si)
        lbl_user_box.addWidget(self.lbl_dash_username)
        lbl_user_box.addStretch()
        bs_layout.addLayout(lbl_user_box)

        btn_logout = QPushButton("Log Out")
        btn_logout.setProperty("class", "ghost-btn")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { color: #f43f5e; border: 1px solid #26262b; } QPushButton:hover { background-color: #1a1a1e; }")
        btn_logout.clicked.connect(self._action_logout)
        bs_layout.addWidget(btn_logout)

        sb_layout.addWidget(bottom_strip)
        layout.addWidget(sidebar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        sc_layout = QVBoxLayout(scroll_content)
        sc_layout.setContentsMargins(32, 28, 32, 28)
        sc_layout.setSpacing(0)

        self.dash_stack = QStackedWidget()
        sc_layout.addWidget(self.dash_stack, 1)

        self.tab_overview = self._build_overview_tab()
        self.dash_stack.addWidget(self.tab_overview)

        self.tab_subs = self._build_subscriptions_tab()
        self.dash_stack.addWidget(self.tab_subs)

        self.tab_vars = self._build_variables_tab()
        self.dash_stack.addWidget(self.tab_vars)

        self.tab_chat = self._build_chat_tab()
        self.dash_stack.addWidget(self.tab_chat)

        self.tab_stats = self._build_stats_tab()
        self.dash_stack.addWidget(self.tab_stats)

        self.tab_sec = self._build_security_tab()
        self.dash_stack.addWidget(self.tab_sec)

        self.tab_files = self._build_files_tab()
        self.dash_stack.addWidget(self.tab_files)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        return container

    def _on_dash_nav_clicked(self, idx: int):
        self.dash_stack.setCurrentIndex(idx)
        if idx == 0:
            self._refresh_overview()
        elif idx == 1:
            self._refresh_subscriptions()
        elif idx == 4:
            self._refresh_stats()

    def _enter_dashboard(self):
        self.title_bar.lbl_sub.setText("CONTROL DASHBOARD")
        u = getattr(self._current_user, "username", "Authenticated User")
        self.lbl_dash_username.setText(u)
        self.main_stack.setCurrentIndex(1)
        self._on_dash_nav_clicked(0)

    def _action_logout(self):
        def task():
            try:
                self.night_auth.logout()
            except Exception:
                pass
        run_async(task, lambda ok, err, res: None)
        self._current_user = None
        self.title_bar.lbl_sub.setText("NATIVE PYTHON SECURITY CLIENT")
        self.main_stack.setCurrentIndex(0)
        self._set_auth_mode("login")

    def _build_overview_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        t = QLabel("Overview")
        t.setStyleSheet("font-size: 22px; font-weight: bold; color: #f4f4f5;")
        sub = QLabel("Account information and active subscription details.")
        sub.setStyleSheet("font-size: 12.5px; color: #6b6b74;")
        layout.addWidget(t)
        layout.addWidget(sub)
        layout.addSpacing(20)

        card = QFrame()
        card.setProperty("class", "card")
        c_layout = QGridLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setHorizontalSpacing(40)
        c_layout.setVerticalSpacing(16)

        lbl_e_hdr = QLabel("EMAIL ADDRESS")
        lbl_e_hdr.setStyleSheet("font-size: 11px; font-weight: bold; color: #6b6b74;")
        self.lbl_ov_email = QLabel("—")
        self.lbl_ov_email.setStyleSheet("font-size: 13.5px; color: #f4f4f5;")

        lbl_ip_hdr = QLabel("IP ADDRESS")
        lbl_ip_hdr.setStyleSheet("font-size: 11px; font-weight: bold; color: #6b6b74;")
        self.lbl_ov_ip = QLabel("—")
        self.lbl_ov_ip.setStyleSheet("font-size: 13px; font-family: Consolas, monospace; color: #a1a1aa;")

        lbl_c_hdr = QLabel("ACCOUNT CREATED")
        lbl_c_hdr.setStyleSheet("font-size: 11px; font-weight: bold; color: #6b6b74;")
        self.lbl_ov_created = QLabel("—")
        self.lbl_ov_created.setStyleSheet("font-size: 13.5px; color: #f4f4f5;")

        lbl_ll_hdr = QLabel("LAST LOGIN (UTC)")
        lbl_ll_hdr.setStyleSheet("font-size: 11px; font-weight: bold; color: #6b6b74;")
        self.lbl_ov_lastlogin = QLabel("—")
        self.lbl_ov_lastlogin.setStyleSheet("font-size: 13px; color: #a1a1aa;")

        c_layout.addWidget(lbl_e_hdr, 0, 0)
        c_layout.addWidget(self.lbl_ov_email, 1, 0)
        c_layout.addWidget(lbl_ip_hdr, 2, 0)
        c_layout.addWidget(self.lbl_ov_ip, 3, 0)

        c_layout.addWidget(lbl_c_hdr, 0, 1)
        c_layout.addWidget(self.lbl_ov_created, 1, 1)
        c_layout.addWidget(lbl_ll_hdr, 2, 1)
        c_layout.addWidget(self.lbl_ov_lastlogin, 3, 1)
        layout.addWidget(card)
        layout.addSpacing(20)

        sec_sub = QHBoxLayout()
        sec_sub.setSpacing(8)
        bar1 = QFrame()
        bar1.setFixedSize(3, 13)
        bar1.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        sec_sub_lbl = QLabel("Active Subscriptions & Entitlements")
        sec_sub_lbl.setStyleSheet("font-size: 13.5px; font-weight: bold; color: #f4f4f5;")
        sec_sub.addWidget(bar1)
        sec_sub.addWidget(sec_sub_lbl)
        sec_sub.addStretch()
        layout.addLayout(sec_sub)
        layout.addSpacing(12)

        self.subs_container = QVBoxLayout()
        self.subs_container.setSpacing(10)
        layout.addLayout(self.subs_container)
        layout.addSpacing(20)

        sec_ins = QHBoxLayout()
        sec_ins.setSpacing(8)
        bar2 = QFrame()
        bar2.setFixedSize(3, 13)
        bar2.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        sec_ins_lbl = QLabel("Application Live Insights")
        sec_ins_lbl.setStyleSheet("font-size: 13.5px; font-weight: bold; color: #f4f4f5;")
        sec_ins.addWidget(bar2)
        sec_ins.addWidget(sec_ins_lbl)
        sec_ins.addStretch()
        layout.addLayout(sec_ins)
        layout.addSpacing(10)

        ins_card = QFrame()
        ins_card.setProperty("class", "card")
        ic_layout = QHBoxLayout(ins_card)
        ic_layout.setContentsMargins(20, 20, 20, 20)

        col1 = QVBoxLayout()
        col1.setSpacing(5)
        l1 = QLabel("TOTAL USERS")
        l1.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #6b6b74;")
        self.lbl_ins_users = QLabel("—")
        self.lbl_ins_users.setStyleSheet("font-size: 24px; font-weight: bold; color: #f4f4f5;")
        col1.addWidget(l1)
        col1.addWidget(self.lbl_ins_users)

        col2 = QVBoxLayout()
        col2.setSpacing(5)
        l2 = QLabel("TOTAL LICENSES")
        l2.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #6b6b74;")
        self.lbl_ins_lic = QLabel("—")
        self.lbl_ins_lic.setStyleSheet("font-size: 24px; font-weight: bold; color: #f4f4f5;")
        col2.addWidget(l2)
        col2.addWidget(self.lbl_ins_lic)

        col3 = QVBoxLayout()
        col3.setSpacing(5)
        l3 = QLabel("ONLINE NOW")
        l3.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #6b6b74;")
        self.lbl_ins_online = QLabel("—")
        self.lbl_ins_online.setStyleSheet("font-size: 24px; font-weight: bold; color: #10b981;")
        col3.addWidget(l3)
        col3.addWidget(self.lbl_ins_online)

        ic_layout.addLayout(col1)
        ic_layout.addLayout(col2)
        ic_layout.addLayout(col3)
        layout.addWidget(ins_card)

        layout.addStretch()
        return w

    def _refresh_overview(self):
        u = self._current_user
        if not u:
            return
        self.lbl_ov_email.setText(getattr(u, "email", None) or "Not linked")
        self.lbl_ov_ip.setText(getattr(u, "ip", None) or "—")
        self.lbl_ov_created.setText(format_timestamp(getattr(u, "created_at", None)))
        self.lbl_ov_lastlogin.setText(format_timestamp(getattr(u, "last_login_at", None) or getattr(u, "last_login", None)))

        while self.subs_container.count():
            item = self.subs_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        subs = getattr(u, "subscriptions", []) or []
        if not subs:
            no_sub = QFrame()
            no_sub.setProperty("class", "card")
            ns_layout = QVBoxLayout(no_sub)
            ns_layout.setContentsMargins(20, 24, 20, 24)
            ns_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_ns1 = QLabel("No active subscription found")
            lbl_ns1.setStyleSheet("font-size: 13.5px; font-weight: 600; color: #a1a1aa;")
            lbl_ns2 = QLabel("Use a license key in the Subscriptions section to activate a plan.")
            lbl_ns2.setStyleSheet("font-size: 11.5px; color: #6b6b74; margin-top: 4px;")
            ns_layout.addWidget(lbl_ns1, 0, Qt.AlignmentFlag.AlignCenter)
            ns_layout.addWidget(lbl_ns2, 0, Qt.AlignmentFlag.AlignCenter)
            self.subs_container.addWidget(no_sub)
        else:
            for s in subs:
                s_card = QFrame()
                s_card.setProperty("class", "card")
                sc_layout = QHBoxLayout(s_card)
                sc_layout.setContentsMargins(18, 16, 18, 16)

                left_col = QVBoxLayout()
                left_col.setSpacing(6)
                badge_row = QHBoxLayout()
                badge_row.setSpacing(10)

                plan_name = getattr(s, 'subscription', 'Default') or "Default"
                plan_badge = QFrame()
                plan_badge.setObjectName("planBadge")
                plan_badge.setStyleSheet("""
                    QFrame#planBadge {
                        background-color: rgba(59, 130, 246, 0.12);
                        border: 1px solid rgba(59, 130, 246, 0.35);
                        border-radius: 6px;
                    }
                """)
                pb_layout = QHBoxLayout(plan_badge)
                pb_layout.setContentsMargins(8, 3, 8, 3)
                pb_layout.setSpacing(6)
                dot = QLabel("●")
                dot.setStyleSheet("color: #3b82f6; font-size: 8px;")
                p_lbl = QLabel(plan_name)
                p_lbl.setStyleSheet("color: #3b82f6; font-size: 12px; font-weight: bold;")
                pb_layout.addWidget(dot)
                pb_layout.addWidget(p_lbl)
                badge_row.addWidget(plan_badge)

                act_lbl = QLabel("ACTIVE PLAN")
                act_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #6b6b74;")
                badge_row.addWidget(act_lbl)
                badge_row.addStretch()
                left_col.addLayout(badge_row)

                key_row = QHBoxLayout()
                key_row.setSpacing(4)
                k_prefix = QLabel("KEY: ")
                k_prefix.setStyleSheet("font-size: 11px; font-weight: bold; color: #6b6b74;")
                k_val = QLabel(getattr(s, 'key', '—') or "Active Account")
                k_val.setStyleSheet("font-family: Consolas, monospace; font-size: 12.5px; color: #f4f4f5;")
                key_row.addWidget(k_prefix)
                key_row.addWidget(k_val)
                key_row.addStretch()
                left_col.addLayout(key_row)

                sc_layout.addLayout(left_col, 1)

                right_col = QVBoxLayout()
                right_col.setSpacing(6)
                right_col.setAlignment(Qt.AlignmentFlag.AlignRight)

                rem_sec = int(getattr(s, "time_left", 0) or 0)
                time_badge = QFrame()
                time_badge.setObjectName("timeBadge")
                time_badge.setStyleSheet("""
                    QFrame#timeBadge {
                        background-color: rgba(255, 255, 255, 0.07);
                        border: 1px solid #26262b;
                        border-radius: 6px;
                    }
                """)
                tb_layout = QHBoxLayout(time_badge)
                tb_layout.setContentsMargins(10, 4, 10, 4)
                tb_layout.setSpacing(6)
                tb_icon = QLabel()
                tb_icon.setPixmap(create_svg_pixmap(SVG_CLOCK, size=11, color="#a1a1aa"))
                tb_lbl = QLabel(format_time_remaining(rem_sec))
                tb_lbl.setStyleSheet("font-size: 11.5px; font-weight: 600; color: #f4f4f5;")
                tb_layout.addWidget(tb_icon)
                tb_layout.addWidget(tb_lbl)
                right_col.addWidget(time_badge, 0, Qt.AlignmentFlag.AlignRight)

                exp_lbl = QLabel(f"Expires: {format_timestamp(getattr(s, 'expiry', None))} UTC")
                exp_lbl.setStyleSheet("font-size: 11px; color: #6b6b74;")
                right_col.addWidget(exp_lbl, 0, Qt.AlignmentFlag.AlignRight)

                sc_layout.addLayout(right_col)
                self.subs_container.addWidget(s_card)

        app_data = getattr(self.night_auth, "app", None) or getattr(self.night_auth, "app_data", None)
        if app_data:
            self.lbl_ins_users.setText(str(getattr(app_data, "total_users", "—")))
            self.lbl_ins_lic.setText(str(getattr(app_data, "total_keys", "—")))
            self.lbl_ins_online.setText(str(getattr(app_data, "online_users", "—")))

        def fetch_live_insights():
            stats = self.night_auth.get_stats()
            online = self.night_auth.get_online_users()
            return stats, online

        def on_insights_done(ok, err, res):
            if ok and res:
                stats, online = res
                if stats:
                    self.lbl_ins_users.setText(str(stats.total_users))
                    self.lbl_ins_lic.setText(str(stats.total_licenses))
                if online is not None:
                    self.lbl_ins_online.setText(str(len(online)))

        run_async(fetch_live_insights, on_insights_done)

    def _build_subscriptions_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        t = QLabel("Subscriptions")
        t.setStyleSheet("font-size: 22px; font-weight: bold; color: #f4f4f5;")
        sub = QLabel("Active subscription licenses and expiration information.")
        sub.setStyleSheet("font-size: 12.5px; color: #6b6b74; margin-bottom: 20px;")
        layout.addWidget(t)
        layout.addWidget(sub)

        card = QFrame()
        card.setProperty("class", "card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(14)

        top_h = QHBoxLayout()
        bar = QFrame()
        bar.setFixedSize(3, 13)
        bar.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        h_lbl = QLabel("Active License Tiers")
        h_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        top_h.addWidget(bar)
        top_h.addWidget(h_lbl)
        top_h.addStretch()

        btn_ref = make_ghost_btn("Refresh Subscriptions")
        btn_ref.clicked.connect(self._refresh_subscriptions)
        top_h.addWidget(btn_ref)
        c_layout.addLayout(top_h)

        self.tbl_subs = QTableWidget(0, 4)
        self.tbl_subs.setHorizontalHeaderLabels(["SUBSCRIPTION", "LICENSE KEY", "EXPIRATION", "TIME REMAINING"])
        self.tbl_subs.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_subs.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl_subs.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_subs.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_subs.setFixedHeight(180)
        c_layout.addWidget(self.tbl_subs)
        layout.addWidget(card)

        upg_card = QFrame()
        upg_card.setProperty("class", "card")
        uc_layout = QVBoxLayout(upg_card)
        uc_layout.setContentsMargins(20, 20, 20, 20)
        uc_layout.setSpacing(12)

        upg_h = QHBoxLayout()
        bar2 = QFrame()
        bar2.setFixedSize(3, 13)
        bar2.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        uh_lbl = QLabel("Upgrade Plan with License Key")
        uh_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        upg_h.addWidget(bar2)
        upg_h.addWidget(uh_lbl)
        upg_h.addStretch()
        uc_layout.addLayout(upg_h)

        lbl_k = QLabel("LICENSE KEY")
        lbl_k.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #6b6b74;")
        self.inp_dash_upg_key = IconInputRow(SVG_KEY, placeholder="Enter license key to extend subscription")
        uc_layout.addWidget(lbl_k)
        uc_layout.addWidget(self.inp_dash_upg_key)

        btn_apply_upg = make_primary_btn("Apply Upgrade")
        btn_apply_upg.clicked.connect(self._handle_dash_upgrade)
        uc_layout.addWidget(btn_apply_upg, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(upg_card)

        layout.addStretch()
        return w

    def _populate_subscriptions_table(self):
        u = self._current_user
        if not u:
            return
        subs = getattr(u, "subscriptions", []) or []
        self.tbl_subs.setRowCount(len(subs))
        for row, s in enumerate(subs):
            sub_name = QTableWidgetItem(getattr(s, "subscription", "—"))
            key_item = QTableWidgetItem(getattr(s, "key", "—"))
            key_item.setFont(QFont("Consolas", 10))
            exp_item = QTableWidgetItem(format_timestamp(getattr(s, "expiry", None)))
            rem_sec = int(getattr(s, "time_left", 0) or 0)
            rem_item = QTableWidgetItem(format_time_remaining(rem_sec))

            self.tbl_subs.setItem(row, 0, sub_name)
            self.tbl_subs.setItem(row, 1, key_item)
            self.tbl_subs.setItem(row, 2, exp_item)
            self.tbl_subs.setItem(row, 3, rem_item)

    def _refresh_subscriptions(self):
        self._populate_subscriptions_table()
        def task():
            return self.night_auth.check()
        def on_done(ok, err, res):
            if ok and res:
                self._current_user = self.night_auth.user_data
            self._populate_subscriptions_table()
            self.lbl_status.setText("Subscriptions refreshed from server.")
        run_async(task, on_done)

    def _handle_dash_upgrade(self):
        k = self.inp_dash_upg_key.text().strip()
        if not k:
            QMessageBox.warning(self, "NightAuth", "Please enter a valid license key.")
            return
        u = getattr(self._current_user, "username", "")
        def task():
            return self.night_auth.upgrade(u, k)
        def on_done(ok, err, res):
            if ok and res:
                QMessageBox.information(self, "NightAuth", "Subscription upgraded successfully!")
                self.inp_dash_upg_key.clear()
                self._current_user = self.night_auth.user_data
                self._refresh_subscriptions()
            else:
                QMessageBox.critical(self, "NightAuth", f"Upgrade failed: {err or 'Unknown error'}")
        run_async(task, on_done)

    def _build_variables_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        t = QLabel("Variables")
        t.setStyleSheet("font-size: 22px; font-weight: bold; color: #f4f4f5;")
        sub = QLabel("Inspect global cloud runtime variables or manage user-scoped personal storage.")
        sub.setStyleSheet("font-size: 12.5px; color: #6b6b74; margin-bottom: 16px;")
        layout.addWidget(t)
        layout.addWidget(sub)

        card1 = QFrame()
        card1.setProperty("class", "card")
        c1_layout = QVBoxLayout(card1)
        c1_layout.setContentsMargins(16, 14, 16, 14)
        c1_layout.setSpacing(10)

        h1 = QHBoxLayout()
        bar1 = QFrame()
        bar1.setFixedSize(3, 13)
        bar1.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        lh1 = QLabel("Global Variables")
        lh1.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        sub1 = QLabel("•  App-wide constants")
        sub1.setStyleSheet("font-size: 11.5px; color: #6b6b74; margin-left: 6px;")
        h1.addWidget(bar1)
        h1.addWidget(lh1)
        h1.addWidget(sub1)
        h1.addStretch()
        c1_layout.addLayout(h1)

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.inp_var_key = IconInputRow(SVG_KEY, placeholder="Variable key (e.g. motd, api_url)")
        self.inp_var_val = IconInputRow(SVG_DATABASE, placeholder="Returned value will appear here...")
        self.inp_var_val.line_edit.setReadOnly(True)
        btn_fetch_var = make_primary_btn("Fetch Value")
        btn_fetch_var.clicked.connect(self._handle_fetch_global_var)

        row1.addWidget(self.inp_var_key, 2)
        row1.addWidget(self.inp_var_val, 3)
        row1.addWidget(btn_fetch_var, 1)
        c1_layout.addLayout(row1)
        layout.addWidget(card1)

        card2 = QFrame()
        card2.setProperty("class", "card")
        c2_layout = QVBoxLayout(card2)
        c2_layout.setContentsMargins(16, 14, 16, 14)
        c2_layout.setSpacing(10)

        h2 = QHBoxLayout()
        bar2 = QFrame()
        bar2.setFixedSize(3, 13)
        bar2.setStyleSheet("background-color: #8b5cf6; border-radius: 2px;")
        lh2 = QLabel("User Variables")
        lh2.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        sub2 = QLabel("•  Personal cloud storage bound to your account")
        sub2.setStyleSheet("font-size: 11.5px; color: #6b6b74; margin-left: 6px;")
        h2.addWidget(bar2)
        h2.addWidget(lh2)
        h2.addWidget(sub2)
        h2.addStretch()
        c2_layout.addLayout(h2)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.inp_uvar_key = IconInputRow(SVG_KEY, placeholder="Key name")
        self.inp_uvar_val = IconInputRow(SVG_DATABASE, placeholder="Custom value to save or view")
        btn_get_uvar = make_ghost_btn("Get Value")
        btn_get_uvar.clicked.connect(self._handle_get_user_var)
        btn_set_uvar = make_primary_btn("Save Value")
        btn_set_uvar.clicked.connect(self._handle_set_user_var)

        row2.addWidget(self.inp_uvar_key, 2)
        row2.addWidget(self.inp_uvar_val, 3)
        row2.addWidget(btn_get_uvar, 1)
        row2.addWidget(btn_set_uvar, 1)
        c2_layout.addLayout(row2)
        layout.addWidget(card2)

        card3 = QFrame()
        card3.setProperty("class", "card")
        c3_layout = QVBoxLayout(card3)
        c3_layout.setContentsMargins(16, 14, 16, 14)
        c3_layout.setSpacing(10)

        h3 = QHBoxLayout()
        bar3 = QFrame()
        bar3.setFixedSize(3, 13)
        bar3.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        lh3 = QLabel("All User Cloud Variables")
        lh3.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        h3.addWidget(bar3)
        h3.addWidget(lh3)
        h3.addStretch()

        btn_fetch_all_uvars = make_ghost_btn("Fetch All Variables")
        btn_fetch_all_uvars.clicked.connect(self._handle_fetch_all_user_vars)
        h3.addWidget(btn_fetch_all_uvars)
        c3_layout.addLayout(h3)

        self.tbl_user_vars = QTableWidget(0, 2)
        self.tbl_user_vars.setHorizontalHeaderLabels(["KEY", "VALUE"])
        self.tbl_user_vars.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_user_vars.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl_user_vars.setFixedHeight(180)
        c3_layout.addWidget(self.tbl_user_vars)
        layout.addWidget(card3)

        layout.addStretch()
        return w

    def _handle_fetch_global_var(self):
        k = self.inp_var_key.text().strip()
        if not k:
            return
        def task():
            return self.night_auth.get_var(k)
        def on_done(ok, err, res):
            if ok and res is not None:
                self.inp_var_val.setText(str(res))
            else:
                self.inp_var_val.setText(f"Not found / {err}")
        run_async(task, on_done)

    def _handle_get_user_var(self):
        k = self.inp_uvar_key.text().strip()
        if not k:
            return
        def task():
            return self.night_auth.get_user_var(k)
        def on_done(ok, err, res):
            if ok and res is not None:
                self.inp_uvar_val.setText(str(res))
            else:
                self.inp_uvar_val.setText(f"Not found / {err}")
        run_async(task, on_done)

    def _handle_set_user_var(self):
        k = self.inp_uvar_key.text().strip()
        v = self.inp_uvar_val.text()
        if not k:
            return
        def task():
            return self.night_auth.set_user_var(k, v)
        def on_done(ok, err, res):
            if ok and res:
                QMessageBox.information(self, "NightAuth", f"Variable '{k}' saved successfully.")
                self._handle_fetch_all_user_vars()
            else:
                QMessageBox.critical(self, "NightAuth", f"Failed to save variable: {err}")
        run_async(task, on_done)

    def _handle_fetch_all_user_vars(self):
        def task():
            return self.night_auth.fetch_all_user_vars()
        def on_done(ok, err, res):
            if ok and isinstance(res, list):
                self.tbl_user_vars.setRowCount(len(res))
                for row, item in enumerate(res):
                    k = item.get("name") or item.get("key") or "—"
                    v = item.get("value") or "—"
                    k_item = QTableWidgetItem(str(k))
                    k_item.setFont(QFont("Consolas", 10))
                    v_item = QTableWidgetItem(str(v))
                    self.tbl_user_vars.setItem(row, 0, k_item)
                    self.tbl_user_vars.setItem(row, 1, v_item)
        run_async(task, on_done)

    def _build_chat_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        t = QLabel("Live Chat")
        t.setStyleSheet("font-size: 22px; font-weight: bold; color: #f4f4f5;")
        sub = QLabel("Real-time communication channel for this application.")
        sub.setStyleSheet("font-size: 12.5px; color: #6b6b74;")
        layout.addWidget(t)
        layout.addWidget(sub)

        bar_card = QFrame()
        bar_card.setProperty("class", "card")
        bc_layout = QHBoxLayout(bar_card)
        bc_layout.setContentsMargins(10, 8, 10, 8)
        bc_layout.setSpacing(10)

        self.inp_chat_room = IconInputRow(SVG_CHAT, placeholder="Enter room name (e.g. general, announcements)")
        self.inp_chat_room.setText("general")
        btn_join_room = make_primary_btn("Connect Room")
        btn_join_room.clicked.connect(self._handle_join_chat_room)

        self.lbl_room_badge = QLabel("●  Offline")
        self.lbl_room_badge.setStyleSheet("background-color: rgba(59, 130, 246, 0.12); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: bold;")

        bc_layout.addWidget(self.inp_chat_room, 1)
        bc_layout.addWidget(btn_join_room)
        bc_layout.addWidget(self.lbl_room_badge)
        layout.addWidget(bar_card)

        chat_card = QFrame()
        chat_card.setProperty("class", "card")
        chat_card.setFixedHeight(280)
        cc_layout = QVBoxLayout(chat_card)
        cc_layout.setContentsMargins(14, 12, 14, 12)

        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.chat_content = QWidget()
        self.chat_content.setStyleSheet("background: transparent;")
        self.chat_vbox = QVBoxLayout(self.chat_content)
        self.chat_vbox.setContentsMargins(0, 0, 0, 0)
        self.chat_vbox.setSpacing(8)
        self.chat_vbox.addStretch()

        self.chat_scroll.setWidget(self.chat_content)
        cc_layout.addWidget(self.chat_scroll)
        layout.addWidget(chat_card)

        inp_card = QFrame()
        inp_card.setProperty("class", "card")
        ic_layout = QHBoxLayout(inp_card)
        ic_layout.setContentsMargins(10, 6, 10, 6)
        ic_layout.setSpacing(10)

        self.inp_chat_msg = QLineEdit()
        self.inp_chat_msg.setPlaceholderText("Type your message and press Enter...")
        self.inp_chat_msg.setStyleSheet("QLineEdit { background: transparent; border: none; color: #f4f4f5; font-size: 13px; }")
        self.inp_chat_msg.returnPressed.connect(self._handle_send_chat)

        btn_send = make_primary_btn("Send")
        btn_send.clicked.connect(self._handle_send_chat)

        ic_layout.addWidget(self.inp_chat_msg, 1)
        ic_layout.addWidget(btn_send)
        layout.addWidget(inp_card)

        return w

    def _handle_join_chat_room(self):
        room = self.inp_chat_room.text().strip() or "general"
        self._current_chat_room = room
        self.lbl_room_badge.setText(f"●  {room}")
        self.lbl_room_badge.setStyleSheet("background-color: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: bold;")
        
        def task():
            return self.night_auth.get_chat_messages(channel=room)
        def on_done(ok, err, res):
            if ok and isinstance(res, list):
                while self.chat_vbox.count() > 1:
                    item = self.chat_vbox.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                for m in res:
                    author = getattr(m, "author", "User")
                    content = getattr(m, "message", "")
                    ts = getattr(m, "timestamp", "")
                    self._append_chat_bubble(author, content, ts)
        run_async(task, on_done)

    def _handle_send_chat(self):
        msg = self.inp_chat_msg.text().strip()
        if not msg:
            return
        room = self._current_chat_room
        self.inp_chat_msg.clear()
        def task():
            return self.night_auth.send_chat_message(msg, channel=room)
        def on_done(ok, err, res):
            if ok:
                user = getattr(self._current_user, "username", "Me")
                now = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")
                self._append_chat_bubble(user, msg, now)
        run_async(task, on_done)

    def _append_chat_bubble(self, author: str, content: str, timestamp: str):
        bubble = QFrame()
        bubble.setStyleSheet("background-color: #0E1017; border: 1px solid #1E2333; border-radius: 8px; padding: 8px 12px;")
        b_layout = QVBoxLayout(bubble)
        b_layout.setContentsMargins(10, 6, 10, 6)
        b_layout.setSpacing(2)

        hdr = QHBoxLayout()
        auth_lbl = QLabel(author)
        auth_lbl.setStyleSheet("font-size: 11.5px; font-weight: bold; color: #60A5FA;")
        time_lbl = QLabel(timestamp)
        time_lbl.setStyleSheet("font-size: 10px; color: #6b6b74;")
        hdr.addWidget(auth_lbl)
        hdr.addStretch()
        hdr.addWidget(time_lbl)
        b_layout.addLayout(hdr)

        msg_lbl = QLabel(content)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("font-size: 12.5px; color: #f4f4f5;")
        b_layout.addWidget(msg_lbl)

        self.chat_vbox.insertWidget(self.chat_vbox.count() - 1, bubble)
        QTimer.singleShot(50, lambda: self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum()))

    def _build_stats_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        t = QLabel("App Statistics")
        t.setStyleSheet("font-size: 22px; font-weight: bold; color: #f4f4f5;")
        sub = QLabel("Telemetry, active connections, and server ecosystem metrics.")
        sub.setStyleSheet("font-size: 12.5px; color: #6b6b74; margin-bottom: 10px;")
        layout.addWidget(t)
        layout.addWidget(sub)

        tiles = QGridLayout()
        tiles.setHorizontalSpacing(12)
        tiles.setVerticalSpacing(0)

        c1 = QFrame()
        c1.setProperty("class", "card-sm")
        cl1 = QVBoxLayout(c1)
        cl1.setContentsMargins(16, 14, 16, 14)
        l1 = QLabel("TOTAL USERS")
        l1.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #6b6b74;")
        self.lbl_stat_users = QLabel("—")
        self.lbl_stat_users.setStyleSheet("font-size: 20px; font-weight: bold; color: #3b82f6; margin-top: 4px;")
        cl1.addWidget(l1)
        cl1.addWidget(self.lbl_stat_users)
        tiles.addWidget(c1, 0, 0)

        c2 = QFrame()
        c2.setProperty("class", "card-sm")
        cl2 = QVBoxLayout(c2)
        cl2.setContentsMargins(16, 14, 16, 14)
        l2 = QLabel("ONLINE USERS")
        l2.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #6b6b74;")
        self.lbl_stat_online = QLabel("—")
        self.lbl_stat_online.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981; margin-top: 4px;")
        cl2.addWidget(l2)
        cl2.addWidget(self.lbl_stat_online)
        tiles.addWidget(c2, 0, 1)

        c3 = QFrame()
        c3.setProperty("class", "card-sm")
        cl3 = QVBoxLayout(c3)
        cl3.setContentsMargins(16, 14, 16, 14)
        l3 = QLabel("TOTAL LICENSES")
        l3.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #6b6b74;")
        self.lbl_stat_keys = QLabel("—")
        self.lbl_stat_keys.setStyleSheet("font-size: 20px; font-weight: bold; color: #f4f4f5; margin-top: 4px;")
        cl3.addWidget(l3)
        cl3.addWidget(self.lbl_stat_keys)
        tiles.addWidget(c3, 0, 2)

        c4 = QFrame()
        c4.setProperty("class", "card-sm")
        cl4 = QVBoxLayout(c4)
        cl4.setContentsMargins(16, 14, 16, 14)
        l4 = QLabel("APP VERSION")
        l4.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #6b6b74;")
        self.lbl_stat_ver = QLabel(NightAuthApp.version or "1.0")
        self.lbl_stat_ver.setStyleSheet("font-size: 20px; font-weight: bold; color: #8b5cf6; margin-top: 4px;")
        cl4.addWidget(l4)
        cl4.addWidget(self.lbl_stat_ver)
        tiles.addWidget(c4, 0, 3)

        layout.addLayout(tiles)

        sess_card = QFrame()
        sess_card.setProperty("class", "card")
        sc_layout = QVBoxLayout(sess_card)
        sc_layout.setContentsMargins(18, 16, 18, 16)
        sc_layout.setSpacing(12)

        sh = QHBoxLayout()
        bar = QFrame()
        bar.setFixedSize(3, 13)
        bar.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        sh_lbl = QLabel("Active User Sessions")
        sh_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        sh.addWidget(bar)
        sh.addWidget(sh_lbl)
        sh.addStretch()

        btn_ref_stats = make_ghost_btn("Refresh Statistics")
        btn_ref_stats.clicked.connect(self._refresh_stats)
        sh.addWidget(btn_ref_stats)
        sc_layout.addLayout(sh)

        self.list_sessions = QListWidget()
        self.list_sessions.setStyleSheet("""
            QListWidget {
                background-color: #0E1017;
                border: 1px solid #26262b;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                background-color: #121520;
                border: 1px solid #1F2433;
                border-radius: 6px;
                padding: 10px 12px;
                margin-bottom: 6px;
                color: #ffffff;
                font-weight: 600;
            }
        """)
        self.list_sessions.setFixedHeight(220)
        sc_layout.addWidget(self.list_sessions)
        layout.addWidget(sess_card)

        layout.addStretch()
        return w

    def _refresh_stats(self):
        ad = getattr(self.night_auth, "app", None) or getattr(self.night_auth, "app_data", None)
        if ad:
            self.lbl_stat_users.setText(str(getattr(ad, "total_users", "—")))
            self.lbl_stat_online.setText(str(getattr(ad, "online_users", "—")))
            self.lbl_stat_keys.setText(str(getattr(ad, "total_keys", "—")))
            self.lbl_stat_ver.setText(str(getattr(ad, "version", "1.0") or getattr(self.night_auth, "version", "1.0")))

        self.list_sessions.clear()
        u = getattr(self._current_user, "username", "Active User")
        self.list_sessions.addItem(f"●  {u}   (Current Active Session)")

        def fetch_live_stats():
            stats = self.night_auth.get_stats()
            online = self.night_auth.get_online_users()
            return stats, online

        def on_stats_done(ok, err, res):
            if ok and res:
                stats, online = res
                if stats:
                    self.lbl_stat_users.setText(str(stats.total_users))
                    self.lbl_stat_keys.setText(str(stats.total_licenses))
                    if stats.version:
                        self.lbl_stat_ver.setText(stats.version)
                if online is not None:
                    self.lbl_stat_online.setText(str(len(online)))
                    self.list_sessions.clear()
                    curr_user = getattr(self._current_user, "username", "")
                    if online:
                        for name in online:
                            if name == curr_user:
                                self.list_sessions.addItem(f"●  {name}   (Current Active Session)")
                            else:
                                self.list_sessions.addItem(f"●  {name}   (Active Session)")
                    else:
                        self.list_sessions.addItem(f"●  {curr_user or 'Active User'}   (Current Active Session)")
            self.lbl_status.setText("Active sessions and application telemetry refreshed.")

        run_async(fetch_live_stats, on_stats_done)

    def _build_security_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        t = QLabel("Account & Security")
        t.setStyleSheet("font-size: 22px; font-weight: bold; color: #f4f4f5;")
        sub = QLabel("Manage credentials, upgrades, and two-factor authentication.")
        sub.setStyleSheet("font-size: 12.5px; color: #6b6b74; margin-bottom: 4px;")
        layout.addWidget(t)
        layout.addWidget(sub)

        card_user = QFrame()
        card_user.setProperty("class", "card")
        cu_layout = QVBoxLayout(card_user)
        cu_layout.setContentsMargins(20, 18, 20, 18)
        cu_layout.setSpacing(10)

        uh = QHBoxLayout()
        bar1 = QFrame()
        bar1.setFixedSize(3, 13)
        bar1.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        uhl = QLabel("Change Username")
        uhl.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        uh.addWidget(bar1)
        uh.addWidget(uhl)
        uh.addStretch()
        cu_layout.addLayout(uh)

        u_hint = QLabel("This immediately terminates active sessions — you will be prompted to sign in again with the new username.")
        u_hint.setStyleSheet("font-size: 11.5px; color: #6b6b74;")
        cu_layout.addWidget(u_hint)

        row_u = QHBoxLayout()
        row_u.setSpacing(12)
        self.inp_new_user = IconInputRow(SVG_USER, placeholder="Enter new username")
        self.inp_new_user_pwd = IconInputRow(SVG_LOCK, placeholder="Confirm password", is_password=True)
        row_u.addWidget(self.inp_new_user)
        row_u.addWidget(self.inp_new_user_pwd)
        cu_layout.addLayout(row_u)

        btn_chg_user = make_primary_btn("Update Username")
        btn_chg_user.clicked.connect(self._handle_change_username)
        cu_layout.addWidget(btn_chg_user, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(card_user)

        card_2fa = QFrame()
        card_2fa.setProperty("class", "card")
        c2_layout = QVBoxLayout(card_2fa)
        c2_layout.setContentsMargins(20, 18, 20, 18)
        c2_layout.setSpacing(10)

        h2 = QHBoxLayout()
        bar2 = QFrame()
        bar2.setFixedSize(3, 13)
        bar2.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        h2l = QLabel("Two-Factor Authentication")
        h2l.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        h2.addWidget(bar2)
        h2.addWidget(h2l)
        h2.addStretch()

        self.lbl_2fa_status = QLabel("SET UP AVAILABLE")
        self.lbl_2fa_status.setStyleSheet("background-color: rgba(59, 130, 246, 0.12); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 5px; padding: 4px 8px; font-size: 9.5px; font-weight: bold;")
        h2.addWidget(self.lbl_2fa_status)
        c2_layout.addLayout(h2)

        desc_2fa = QLabel("Protect this account with an authenticator app (Google Authenticator, Authy, 1Password, etc.).")
        desc_2fa.setStyleSheet("font-size: 12px; color: #6b6b74;")
        c2_layout.addWidget(desc_2fa)

        btn_row_2fa = QHBoxLayout()
        btn_row_2fa.setSpacing(10)
        self.btn_setup_2fa = make_primary_btn("Set Up 2FA")
        self.btn_setup_2fa.clicked.connect(self._handle_setup_2fa)

        self.btn_disable_2fa = QPushButton("Disable 2FA")
        self.btn_disable_2fa.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_disable_2fa.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f43f5e;
                border: 1px solid #26262b;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 16px;
                min-height: 38px;
            }
            QPushButton:hover {
                background-color: rgba(244, 63, 94, 0.1);
                border: 1px solid #f43f5e;
            }
        """)
        self.btn_disable_2fa.clicked.connect(self._handle_disable_2fa)

        btn_row_2fa.addWidget(self.btn_setup_2fa)
        btn_row_2fa.addWidget(self.btn_disable_2fa)
        btn_row_2fa.addStretch()
        c2_layout.addLayout(btn_row_2fa)
        layout.addWidget(card_2fa)

        card_sec = QFrame()
        card_sec.setProperty("class", "card")
        cs_layout = QVBoxLayout(card_sec)
        cs_layout.setContentsMargins(20, 18, 20, 18)
        cs_layout.setSpacing(10)

        hs = QHBoxLayout()
        bar3 = QFrame()
        bar3.setFixedSize(3, 13)
        bar3.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        hsl = QLabel("Send Audit Log to Server")
        hsl.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        hs.addWidget(bar3)
        hs.addWidget(hsl)
        hs.addStretch()
        cs_layout.addLayout(hs)

        self.inp_audit_msg = IconInputRow(SVG_SHIELD, placeholder="Enter log message to store in dashboard audit trail...")
        cs_layout.addWidget(self.inp_audit_msg)

        btn_send_log = make_ghost_btn("Send Audit Log")
        btn_send_log.clicked.connect(self._handle_send_audit_log)
        cs_layout.addWidget(btn_send_log, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(card_sec)

        layout.addStretch()
        return w

    def _handle_change_username(self):
        nu = self.inp_new_user.text().strip()
        p = self.inp_new_user_pwd.text()
        if not nu or not p:
            QMessageBox.warning(self, "NightAuth", "Please fill in all fields.")
            return
        def task():
            return self.night_auth.change_username(nu, p)
        def on_done(ok, err, res):
            if ok and res:
                QMessageBox.information(self, "NightAuth", "Username updated! Please sign in with your new credentials.")
                self._action_logout()
            else:
                QMessageBox.critical(self, "NightAuth", f"Failed to change username: {err}")
        run_async(task, on_done)

    def _handle_setup_2fa(self):
        def task():
            return self.night_auth.setup_2fa()
        def on_done(ok, err, res):
            if ok and res:
                secret = getattr(res, "secret", "")
                uri = getattr(res, "uri", "")
                self._show_2fa_setup_dialog(secret, uri)
            else:
                QMessageBox.critical(self, "NightAuth", f"Failed to initiate 2FA: {err}")
        run_async(task, on_done)

    def _show_2fa_setup_dialog(self, secret: str, uri: str):
        dlg = QDialog(self)
        dlg.setWindowTitle("Two-Factor Authentication Setup")
        dlg.setFixedSize(480, 420)
        dlg.setStyleSheet(WPF_STYLESHEET)
        d_layout = QVBoxLayout(dlg)
        d_layout.setContentsMargins(24, 20, 24, 20)
        d_layout.setSpacing(12)

        hl = QLabel("Two-Factor Authentication Setup")
        hl.setStyleSheet("font-size: 16px; font-weight: bold; color: #f4f4f5;")
        dl = QLabel("Enter this secret key in your authenticator app:")
        dl.setStyleSheet("font-size: 12px; color: #6b6b74;")
        d_layout.addWidget(hl)
        d_layout.addWidget(dl)

        s_inp = IconInputRow(SVG_KEY, placeholder=secret)
        s_inp.setText(secret)
        s_inp.line_edit.setReadOnly(True)
        d_layout.addWidget(s_inp)

        cl = QLabel("CONFIRMATION CODE")
        cl.setStyleSheet("font-size: 10.5px; font-weight: bold; color: #a1a1aa; margin-top: 6px;")
        d_layout.addWidget(cl)

        c_inp = IconInputRow(SVG_LOCK, placeholder="6-digit code from app", max_length=6)
        d_layout.addWidget(c_inp)

        btn_conf = make_primary_btn("Confirm & Enable 2FA")

        def do_confirm():
            code = c_inp.text().strip()
            if len(code) != 6:
                return
            def task():
                return self.night_auth.confirm_2fa(code)
            def on_c_done(ok, err, res):
                if ok and res:
                    QMessageBox.information(dlg, "NightAuth", "Two-Factor Authentication enabled successfully!")
                    dlg.accept()
                else:
                    QMessageBox.critical(dlg, "NightAuth", f"Invalid code: {err}")
            run_async(task, on_c_done)

        btn_conf.clicked.connect(do_confirm)
        d_layout.addWidget(btn_conf)
        dlg.exec()

    def _handle_disable_2fa(self):
        pwd, ok1 = QLineEdit(), False
        dlg = QDialog(self)
        dlg.setWindowTitle("Disable 2FA")
        dlg.setFixedSize(420, 240)
        dlg.setStyleSheet(WPF_STYLESHEET)
        dl = QVBoxLayout(dlg)
        dl.setContentsMargins(20, 20, 20, 20)
        dl.setSpacing(10)

        hl = QLabel("Disable Two-Factor Authentication")
        hl.setStyleSheet("font-size: 15px; font-weight: bold; color: #f4f4f5;")
        dl.addWidget(hl)

        p_inp = IconInputRow(SVG_LOCK, placeholder="Enter account password", is_password=True)
        c_inp = IconInputRow(SVG_LOCK, placeholder="Current 6-digit 2FA code", max_length=6)
        dl.addWidget(p_inp)
        dl.addWidget(c_inp)

        btn_d = QPushButton("Disable 2FA")
        btn_d.setProperty("class", "primary-btn")
        btn_d.setStyleSheet("background-color: #ef4444;")
        btn_d.setCursor(Qt.CursorShape.PointingHandCursor)

        def do_dis():
            p = p_inp.text()
            c = c_inp.text().strip()
            if not p or not c:
                return
            def task():
                return self.night_auth.disable_2fa(p, c)
            def on_d_done(ok, err, res):
                if ok and res:
                    QMessageBox.information(dlg, "NightAuth", "Two-Factor Authentication disabled.")
                    dlg.accept()
                else:
                    QMessageBox.critical(dlg, "NightAuth", f"Failed to disable: {err}")
            run_async(task, on_d_done)

        btn_d.clicked.connect(do_dis)
        dl.addWidget(btn_d)
        dlg.exec()

    def _handle_send_audit_log(self):
        msg = self.inp_audit_msg.text().strip()
        if not msg:
            return
        def task():
            return self.night_auth.log(msg)
        def on_done(ok, err, res):
            if ok:
                QMessageBox.information(self, "NightAuth", "Audit log message delivered to dashboard.")
                self.inp_audit_msg.clear()
            else:
                QMessageBox.critical(self, "NightAuth", f"Failed to log: {err}")
        run_async(task, on_done)

    def _build_files_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        t = QLabel("Files & Webhooks")
        t.setStyleSheet("font-size: 22px; font-weight: bold; color: #f4f4f5;")
        sub = QLabel("Secure server asset distribution and cloud webhook dispatch.")
        sub.setStyleSheet("font-size: 12.5px; color: #6b6b74; margin-bottom: 4px;")
        layout.addWidget(t)
        layout.addWidget(sub)

        card1 = QFrame()
        card1.setProperty("class", "card")
        c1_layout = QVBoxLayout(card1)
        c1_layout.setContentsMargins(20, 18, 20, 18)
        c1_layout.setSpacing(10)

        h1 = QHBoxLayout()
        bar1 = QFrame()
        bar1.setFixedSize(3, 13)
        bar1.setStyleSheet("background-color: #3b82f6; border-radius: 2px;")
        h1l = QLabel("Protected Remote File Downloader")
        h1l.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        h1.addWidget(bar1)
        h1.addWidget(h1l)
        h1.addStretch()
        c1_layout.addLayout(h1)

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.inp_file_id = IconInputRow(SVG_DOWNLOAD, placeholder="File ID (e.g. 1)")
        btn_dl = make_primary_btn("Download File")
        btn_dl.clicked.connect(self._handle_download_file)

        row1.addWidget(self.inp_file_id, 2)
        row1.addWidget(btn_dl, 1)
        c1_layout.addLayout(row1)

        self.lbl_dl_status = QLabel("Protected binary payload downloads directly into memory.")
        self.lbl_dl_status.setStyleSheet("font-size: 11.5px; color: #6b6b74;")
        c1_layout.addWidget(self.lbl_dl_status)
        layout.addWidget(card1)

        card2 = QFrame()
        card2.setProperty("class", "card")
        c2_layout = QVBoxLayout(card2)
        c2_layout.setContentsMargins(20, 18, 20, 18)
        c2_layout.setSpacing(10)

        h2 = QHBoxLayout()
        bar2 = QFrame()
        bar2.setFixedSize(3, 13)
        bar2.setStyleSheet("background-color: #8b5cf6; border-radius: 2px;")
        h2l = QLabel("Webhook Trigger")
        h2l.setStyleSheet("font-size: 14px; font-weight: bold; color: #f4f4f5;")
        h2.addWidget(bar2)
        h2.addWidget(h2l)
        h2.addStretch()
        c2_layout.addLayout(h2)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.inp_hook_id = IconInputRow(SVG_WEBHOOK, placeholder="Webhook ID")
        self.inp_hook_body = IconInputRow(SVG_DATABASE, placeholder='Optional JSON payload (e.g. {"action":"ping"})')
        btn_hook = make_primary_btn("Trigger Webhook")
        btn_hook.clicked.connect(self._handle_trigger_webhook)

        row2.addWidget(self.inp_hook_id, 2)
        row2.addWidget(self.inp_hook_body, 3)
        row2.addWidget(btn_hook, 1)
        c2_layout.addLayout(row2)

        self.lbl_hook_status = QLabel("Server response will appear here...")
        self.lbl_hook_status.setStyleSheet("font-size: 11.5px; color: #6b6b74;")
        c2_layout.addWidget(self.lbl_hook_status)
        layout.addWidget(card2)

        layout.addStretch()
        return w

    def _handle_download_file(self):
        fid = self.inp_file_id.text().strip()
        if not fid:
            return
        self.lbl_dl_status.setText("Downloading...")
        def task():
            return self.night_auth.get_file(fid)
        def on_done(ok, err, res):
            if ok and res is not None:
                size = len(res) if isinstance(res, (bytes, bytearray)) else 0
                self.lbl_dl_status.setText(f"✓ Downloaded {size} bytes successfully into memory.")
                self.lbl_dl_status.setStyleSheet("font-size: 11.5px; color: #10b981;")
            else:
                self.lbl_dl_status.setText(f"Download failed: {err}")
                self.lbl_dl_status.setStyleSheet("font-size: 11.5px; color: #f43f5e;")
        run_async(task, on_done)

    def _handle_trigger_webhook(self):
        hid = self.inp_hook_id.text().strip()
        body_raw = self.inp_hook_body.text().strip()
        if not hid:
            return
        payload = {}
        if body_raw:
            try:
                payload = json.loads(body_raw)
            except Exception:
                payload = {"content": body_raw}
        def task():
            return self.night_auth.trigger_webhook(hid, payload)
        def on_done(ok, err, res):
            if ok:
                self.lbl_hook_status.setText(f"✓ Webhook executed successfully (Status: 200).")
                self.lbl_hook_status.setStyleSheet("font-size: 11.5px; color: #10b981;")
            else:
                self.lbl_hook_status.setText(f"Webhook execution failed: {err}")
                self.lbl_hook_status.setStyleSheet("font-size: 11.5px; color: #f43f5e;")
        run_async(task, on_done)

    def _init_app_handshake(self):
        if not self.night_auth.name or not self.night_auth.api_key:
            self.lbl_bound_app.setText("Unconfigured")
            self.lbl_telemetry_badge.setText("●  ZERO-TRUST TELEMETRY")
            self.btn_submit.setEnabled(False)
            return

        self.btn_submit.setEnabled(False)

        def task():
            try:
                self.night_auth.init()
                return self.night_auth.response.success, self.night_auth.response.message
            except Exception as e:
                return False, str(e)

        def on_done(ok, err, res):
            success = False
            msg = ""
            if ok and isinstance(res, tuple):
                success, msg = res
            elif ok:
                success = bool(getattr(self.night_auth.response, "success", False))
                msg = getattr(self.night_auth.response, "message", "")
            else:
                success = False
                msg = err or "Connection error"

            app_name = self.night_auth.name if self.night_auth.name else "Unconfigured"
            self.lbl_bound_app.setText(app_name)

            if success:
                self.lbl_telemetry_badge.setText("●  ZERO-TRUST TELEMETRY")
                self.btn_submit.setEnabled(True)
                self.lbl_auth_error.setVisible(False)
            else:
                self.lbl_telemetry_badge.setText("●  ZERO-TRUST TELEMETRY")
                if msg:
                    self.lbl_auth_error.setText(f"Handshake error: {msg}")
                    self.lbl_auth_error.setVisible(True)

        run_async(task, on_done)

    def _handle_event_invalidated(self, reason: str):
        QMessageBox.warning(self, "Session Invalidated", f"Your session was invalidated: {reason}")
        self._action_logout()

    def _handle_event_banned(self, reason: str):
        QMessageBox.critical(self, "Security Alert", f"Your account or device has been banned: {reason}")
        QApplication.instance().quit()

    def _handle_event_status(self, status: str):
        pass

    def _handle_event_version(self, version: str):
        pass

    def _handle_event_chat(self, msg_obj, room: str):
        if room == self._current_chat_room and msg_obj:
            author = getattr(msg_obj, "author", "User")
            content = getattr(msg_obj, "message", "")
            ts = getattr(msg_obj, "timestamp", "")
            self._append_chat_bubble(author, content, ts)

def main():
    app = QApplication(sys.argv)
    window = NightAuthDesktopApp()
    window.show()
    window.raise_()
    window.activateWindow()
    try:
        import ctypes
        hwnd = int(window.winId())
        ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception:
        pass
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
