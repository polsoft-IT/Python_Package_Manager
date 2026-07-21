import json
import os
import sys
import subprocess
import logging
import shutil
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QScrollArea,
    QSplitter, QTextEdit, QMessageBox, QFileDialog, QFrame, QDialog,
    QGridLayout, QProgressBar
)
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

# Konfiguracja logowania
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# --- NOWOCZESNY CIEMNY STYL INTERFEJSU (DARK QSS) ---
STYLESHEET = """
QMainWindow {
    background-color: #1e1e24;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #e1e2e6;
}
QLabel#HeaderLabel {
    font-size: 20px;
    font-weight: bold;
    color: #f1f2f6;
    padding-bottom: 5px;
}
QLineEdit {
    background-color: #2d2d35;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    selection-background-color: #3498db;
}
QLineEdit:focus {
    border: 1px solid #3498db;
}
QPushButton {
    background-color: #3f3f46;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
    color: #ffffff;
}
QPushButton:hover {
    background-color: #52525b;
}
QPushButton:disabled {
    background-color: #27272a;
    color: #71717a;
}
QPushButton#PrimaryBtn {
    background-color: #3498db;
    color: white;
}
QPushButton#PrimaryBtn:hover {
    background-color: #2980b9;
}
QPushButton#DangerBtn {
    background-color: #e74c3c;
    color: white;
}
QPushButton#DangerBtn:hover {
    background-color: #c0392b;
}
QPushButton#AccentBtn {
    background-color: #2ecc71;
    color: white;
}
QPushButton#AccentBtn:hover {
    background-color: #27ae60;
}
QListWidget {
    background-color: #2d2d35;
    border: 1px solid #3f3f46;
    border-radius: 8px;
    padding: 5px;
    color: #e1e2e6;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin-bottom: 2px;
}
QListWidget::item:hover {
    background-color: #3f3f46;
}
QListWidget::item:selected {
    background-color: #3498db;
    color: white;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QProgressBar {
    border: 1px solid #3f3f46;
    border-radius: 4px;
    background-color: #2d2d35;
    text-align: center;
    color: white;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #3498db;
    border-radius: 3px;
}
"""

def parse_pip_freeze_output(output):
    """Parsuje dane wyjściowe z `pip freeze` do słownika {pakiet: wersja}."""
    packages = {}
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("-e ") and "#egg=" in line:
            pkg = line.split("#egg=", 1)[-1].strip()
            version = ""
        elif " @ " in line:
            pkg = line.split(" @ ", 1)[0].strip()
            version = ""
        elif "==" in line:
            pkg, version = line.split("==", 1)
            pkg = pkg.strip()
            version = version.strip()
        else:
            pkg = line
            version = ""

        if pkg:
            packages[pkg.lower()] = version

    return packages


def summarize_install_output(output, max_lines=8):
    """Skraca długie logi instalacji pip."""
    if not output:
        return ""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"


def find_system_python():
    """Find the system Python interpreter, especially when the app is frozen."""
    if not getattr(sys, "frozen", False):
        return sys.executable
    
    possible_paths = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "python.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "python3.exe"),
        r"C:\Python312\python.exe",
        r"C:\Python311\python.exe",
        r"C:\Python310\python.exe",
        r"C:\Python39\python.exe",
        r"C:\Python38\python.exe",
        r"C:\Program Files\Python312\python.exe",
        r"C:\Program Files\Python311\python.exe",
        r"C:\Program Files\Python310\python.exe",
        r"C:\Program Files\Python39\python.exe",
        r"C:\Program Files\Python38\python.exe",
        r"C:\Program Files (x86)\Python312\python.exe",
        r"C:\Program Files (x86)\Python311\python.exe",
        r"C:\Program Files (x86)\Python310\python.exe",
        r"C:\Program Files (x86)\Python39\python.exe",
        r"C:\Program Files (x86)\Python38\python.exe",
    ]
    
    try:
        python_from_path = shutil.which("python")
        if python_from_path:
            possible_paths.insert(0, python_from_path)
        python3_from_path = shutil.which("python3")
        if python3_from_path:
            possible_paths.insert(0, python3_from_path)
    except Exception:
        pass
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                result = subprocess.run([path, "-c", "import sys; print(sys.executable)"], 
                                        capture_output=True, text=True, timeout=5, startupinfo=startupinfo)
                if result.returncode == 0:
                    return path
            except Exception:
                continue
    return sys.executable


# Słownik z bibliotekami podzielonymi na kategorie
BIBLIOTEKI = {
    "Kompilatory i Transpilatory": ["pyinstaller", "cx_Freeze", "nuitka", "py2exe", "cython", "pyarmor", "briefcase"],
    "GUI (Interfejsy graficzne)": ["customtkinter", "PyQt6", "PySide6", "wxPython", "kivy", "flet", "PySimpleGUI", "dearpygui", "eel"],
    "Gry i Multimedia (Games)": ["pygame", "arcade", "pyglet", "panda3d", "ursina", "pygame-zero", "renpy", "cocos2d"],
    "Data Science i ML": ["numpy", "pandas", "matplotlib", "scikit-learn", "scipy", "seaborn", "statsmodels", "xgboost", "lightgbm", "yellowbrick"],
    "Web Scraping i API": ["requests", "beautifulsoup4", "scrapy", "selenium", "playwright", "httpx", "parsel", "undetected-chromedriver"],
    "Frameworki Webowe": ["django", "flask", "fastapi", "tornado", "dash", "starlette", "sanic", "quart", "bottle", "jinja2"],
    "Bazy Danych i ORM": ["sqlalchemy", "peewee", "alembic", "psycopg2-binary", "pymongo", "redis", "mysql-connector-python", "pymysql", "asyncpg", "motor"],
    "Testowanie i QA": ["pytest", "unittest2", "tox", "coverage", "mock", "behave", "pytest-cov", "robotframework", "nose2", "hypothesis"],
    "Obraz i Wideo": ["pillow", "opencv-python", "scikit-image", "moviepy", "imageio", "mediapipe", "pyvips", "pydub", "opencv-contrib-python"],
    "Asynchroniczność i Współbieżność": ["asyncio", "trio", "twisted", "gevent", "aiohttp", "anyio", "httpx"],
    "Kryptografia i Bezpieczeństwo": ["cryptography", "pyjwt", "passlib", "bcrypt", "paramiko", "pycryptodome", "argon2-cffi"],
    "Automatyzacja i System": ["psutil", "click", "sh", "schedule", "watchdog", "pyautogui", "fabric", "invoke", "ansible"],
    "Parsery i Formatowanie Danych": ["pydantic", "pyyaml", "toml", "lxml", "xmltodict", "ruamel.yaml", "csvkit", "xmlschema"],
    "Terminale i CLI": ["rich", "textual", "typer", "prompt_toolkit", "blessed", "colorama", "docopt", "questionary"],
    "Sztuczna Inteligencja i NLP": ["transformers", "spacy", "nltk", "gensim", "langchain", "openai", "torch", "torchvision", "torchaudio", "tensorflow", "keras", "sentence-transformers", "accelerate", "diffusers", "datasets", "tokenizers", "sentencepiece", "peft", "bitsandbytes", "onnxruntime", "optuna", "gradio", "fastai", "llama-cpp-python", "openllm", "wandb"],
    "Obsługa Dokumentów i Plików": ["openpyxl", "pypdf", "python-docx", "python-pptx", "weasyprint", "xlsxwriter", "pdfplumber", "pdfminer.six", "python-magic"],
    "Zaawansowana Wizualizacja": ["plotly", "bokeh", "altair", "pygal", "pydot", "folium", "geopandas", "streamlit"],
    "Logowanie i Diagnostyka": ["loguru", "icecream", "structlog", "sentry-sdk", "memory-profiler", "python-json-logger", "logzero"],
    "Sieć i Protokoły": ["scapy", "pyshark", "python-socketio", "dnspython", "netaddr", "websocket-client", "requests"],
    "Generowanie Danych i Mock": ["faker", "hypothesis", "factory-boy", "mimesis", "model-bakery"],
    "Chmura i Integracje": ["boto3", "google-cloud-storage", "azure-storage-blob", "kubernetes", "apache-libcloud", "google-auth", "azure-identity"],
    "Grafika i Modele 3D": ["open3d", "trimesh", "pyopengl", "pyrender", "moderngl", "pywavefront"]
}

LANGUAGES = {
    "EN": {
        "title": "Python Package Installer (PyQt6)",
        "header": "Python Package Manager",
        "categories": "Categories",
        "select_category": "Select a category from the list on the left",
        "libs_in": "Libraries in: ",
        "installed": "Installed",
        "install_btn": "Install",
        "installing": "Installing...",
        "status_ready": "Ready",
        "preparing": "Preparing to install {}...",
        "preparing_upgrade": "Preparing to upgrade {}...",
        "preparing_uninstall": "Preparing to uninstall {}...",
        "success_title": "Success",
        "success_install_msg": "Successfully installed {}!",
        "success_upgrade_msg": "Successfully upgraded {}!",
        "success_uninstall_msg": "Successfully uninstalled {}!",
        "success_install_status": "Success: Package '{}' installed successfully.",
        "success_upgrade_status": "Success: Package '{}' upgraded successfully.",
        "success_uninstall_status": "Success: Package '{}' uninstalled successfully.",
        "error_title": "Operation Error",
        "error_install_msg": "Failed to install {}.\nError:\n{}",
        "error_upgrade_msg": "Failed to upgrade {}.\nError:\n{}",
        "error_uninstall_msg": "Failed to uninstall {}.\nError:\n{}",
        "error_install_status": "Error installing package {}.",
        "error_upgrade_status": "Error upgrading package {}.",
        "error_uninstall_status": "Error uninstalling package {}.",
        "scan_error_title": "Error",
        "scan_error_msg": "Failed to scan packages: {}",
        "search_label": "Search:",
        "search_placeholder": "🔍 Search packages...",
        "python_exec_label": "Python Interpreter:",
        "choose_interpreter_btn": "Browse...",
        "choose_interpreter_title": "Select Python Interpreter",
        "update_btn": "Upgrade",
        "uninstall_btn": "Uninstall",
        "no_search_results": "No packages match your search.",
        "btn_refresh": "Refresh",
        "refresh_btn": "🔄 Refresh",
        "btn_debug_show": "🛠 Show Logs",
        "btn_debug_hide": "🛠 Hide Logs",
        "about_title": "About Program",
        "about_msg": "A modern desktop client designed to streamline pip operations. Built using Python and PyQt6.",
        "compilers_cat": "Compilers & Transpilers",
        "gui_cat": "GUI (Graphical Interfaces)",
        "games_cat": "Games & Multimedia",
        "datascience_cat": "Data Science & Machine Learning",
        "scraping_cat": "Web Scraping & APIs",
        "web_cat": "Web Frameworks",
        "db_cat": "Databases & ORM",
        "testing_cat": "Testing & QA",
        "media_cat": "Image & Video Processing",
        "async_cat": "Async & Concurrency",
        "crypto_cat": "Cryptography & Security",
        "auto_cat": "Automation & System",
        "parsers_cat": "Parsers & Data Formats",
        "cli_cat": "Terminals & CLI",
        "ai_cat": "AI & Natural Language (NLP)",
        "docs_cat": "Documents & File Formats",
        "viz_cat": "Advanced Visualization",
        "log_cat": "Logging & Diagnostics",
        "net_cat": "Network & Protocols",
        "mock_cat": "Data Generation & Mocking",
        "cloud_cat": "Cloud & Integrations",
        "graphics3d_cat": "3D Graphics & Models"
    },
    "PL": {
        "title": "Instalator Pakietów Python (PyQt6)",
        "header": "Menedżer Pakietów Python",
        "categories": "Kategorie",
        "select_category": "Wybierz kategorię z listy po lewej",
        "libs_in": "Biblioteki w: ",
        "installed": "Zainstalowano",
        "install_btn": "Instaluj",
        "installing": "Instalacja...",
        "status_ready": "Gotowy",
        "preparing": "Przygotowanie do instalacji {}...",
        "preparing_upgrade": "Przygotowanie do aktualizacji {}...",
        "preparing_uninstall": "Przygotowanie do odinstalowania {}...",
        "success_title": "Sukces",
        "success_install_msg": "Pomyślnie zainstalowano {}!",
        "success_upgrade_msg": "Pomyślnie zaktualizowano {}!",
        "success_uninstall_msg": "Pomyślnie odinstalowano {}!",
        "success_install_status": "Sukces: Zainstalowano pakiet '{}'.",
        "success_upgrade_status": "Sukces: Zaktualizowano pakiet '{}'.",
        "success_uninstall_status": "Sukces: Odinstalowano pakiet '{}'.",
        "error_title": "Błąd operacji",
        "error_install_msg": "Nie udało się zainstalować {}.\nBłąd:\n{}",
        "error_upgrade_msg": "Nie udało się zaktualizować {}.\nBłąd:\n{}",
        "error_uninstall_msg": "Nie udało się odinstalować {}.\nBłąd:\n{}",
        "error_install_status": "Błąd instalacji pakietu {}.",
        "error_upgrade_status": "Błąd aktualizacji pakietu {}.",
        "error_uninstall_status": "Błąd odinstalowywania pakietu {}.",
        "scan_error_title": "Błąd",
        "scan_error_msg": "Nie udało się zeskanować pakietów: {}",
        "search_label": "Szukaj:",
        "search_placeholder": "🔍 Szukaj pakietów...",
        "python_exec_label": "Interpreter Pythona:",
        "choose_interpreter_btn": "Przeglądaj...",
        "choose_interpreter_title": "Wybierz interpreter Pythona",
        "update_btn": "Aktualizuj",
        "uninstall_btn": "Odinstaluj",
        "no_search_results": "Brak pakietów pasujących do wyszukiwania.",
        "btn_refresh": "Odśwież",
        "refresh_btn": "🔄 Odśwież",
        "btn_debug_show": "🛠 Pokaż Logi",
        "btn_debug_hide": "🛠 Ukryj Logi",
        "about_title": "O programie",
        "about_msg": "Nowoczesny klient okienkowy usprawniający zarządzanie pakietami pip. Stworzony w Pythonie i PyQt6.",
        "compilers_cat": "Kompilatory i Transpilatory",
        "gui_cat": "GUI (Interfejsy graficzne)",
        "games_cat": "Gry i Multimedia (Games)",
        "datascience_cat": "Analiza danych i ML",
        "scraping_cat": "Pobieranie danych (Scraping)",
        "web_cat": "Frameworki Webowe (Strony WWW)",
        "db_cat": "Bazy danych i ORM",
        "testing_cat": "Testowanie i QA",
        "media_cat": "Przetwarzanie obrazu i wideo",
        "async_cat": "Asynchroniczność i współbieżność",
        "crypto_cat": "Kryptografia i bezpieczeństwo",
        "auto_cat": "Automatyzacja i system",
        "parsers_cat": "Parsery i formaty danych",
        "cli_cat": "Aplikacje Terminalowe i CLI",
        "ai_cat": "Sztuczna Inteligencja i NLP",
        "docs_cat": "Obsługa Dokumentów i Plików",
        "viz_cat": "Zaawansowana Wizualizacja",
        "log_cat": "Logowanie i Diagnostyka",
        "net_cat": "Sieć i Protokoły",
        "mock_cat": "Generowanie Danych i Mock",
        "cloud_cat": "Chmura i Integracje",
        "graphics3d_cat": "Grafika i Modele 3D"
    }
}

CATEGORY_MAP = {
    "Kompilatory i Transpilatory": "compilers_cat",
    "GUI (Interfejsy graficzne)": "gui_cat",
    "Gry i Multimedia (Games)": "games_cat",
    "Data Science i ML": "datascience_cat",
    "Web Scraping i API": "scraping_cat",
    "Frameworki Webowe": "web_cat",
    "Bazy Danych i ORM": "db_cat",
    "Testowanie i QA": "testing_cat",
    "Obraz i Wideo": "media_cat",
    "Asynchroniczność i Współbieżność": "async_cat",
    "Kryptografia i Bezpieczeństwo": "crypto_cat",
    "Automatyzacja i System": "auto_cat",
    "Parsery i Formatowanie Danych": "parsers_cat",
    "Terminale i CLI": "cli_cat",
    "Sztuczna Inteligencja i NLP": "ai_cat",
    "Obsługa Dokumentów i Plików": "docs_cat",
    "Zaawansowana Wizualizacja": "viz_cat",
    "Logowanie i Diagnostyka": "log_cat",
    "Sieć i Protokoły": "net_cat",
    "Generowanie Danych i Mock": "mock_cat",
    "Chmura i Integracje": "cloud_cat",
    "Grafika i Modele 3D": "graphics3d_cat"
}

# --- METADANE APLIKACJI ---
METADATA = {
    "name": "Python Package Manager",
    "version": "2.0.1",
    "author": "Sebastian Januchowski",
    "company": "polsoft.ITS(TM) Group",
    "github": "https://github.com/polsoft-IT",
    "email": "polsoft.its@mail.com",
    "description": "An advanced and lightweight desktop GUI wrapper for handling Python environment configurations and pip package control flows effortlessly."
}


class AboutDialog(QDialog):
    def __init__(self, parent, lang_code):
        super().__init__(parent)
        self.lang_code = lang_code
        self.init_ui()

    def init_ui(self):
        lang = LANGUAGES[self.lang_code]
        self.setWindowTitle(lang["about_title"])
        self.setFixedSize(460, 360)
        self.setStyleSheet("background-color: #1e1e24; color: #e1e2e6;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)

        lbl_logo = QLabel("📦", self)
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("font-size: 38px; margin-bottom: 2px;")
        layout.addWidget(lbl_logo)

        lbl_title = QLabel(METADATA["name"], self)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(lbl_title)

        lbl_version = QLabel(f"v{METADATA['version']}", self)
        lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_version.setStyleSheet("font-size: 11px; color: #9ca3af; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(lbl_version)

        lbl_desc = QLabel(lang["about_msg"], self)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #cbd5e1; font-size: 12px; margin-bottom: 12px;")
        layout.addWidget(lbl_desc)

        meta_frame = QFrame(self)
        meta_frame.setStyleSheet("background-color: #2d2d35; border: 1px solid #3f3f46; border-radius: 6px; padding: 10px;")
        
        meta_grid = QGridLayout(meta_frame)
        meta_grid.setHorizontalSpacing(15)
        meta_grid.setVerticalSpacing(6)
        meta_grid.setContentsMargins(12, 10, 12, 10)

        rows = [
            ("Author", METADATA["author"]),
            ("Company", METADATA["company"]),
            ("GitHub", METADATA["github"]),
            ("Email", METADATA["email"])
        ]

        for idx, (label_text, value_text) in enumerate(rows):
            lbl_key = QLabel(f"<b>{label_text}:</b>", self)
            lbl_key.setStyleSheet("color: #94a3b8; font-size: 12px;")
            lbl_key.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            lbl_val = QLabel(value_text, self)
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            if "http" in value_text or "@" in value_text:
                lbl_val.setStyleSheet("color: #3498db; font-size: 12px;")
            else:
                lbl_val.setStyleSheet("color: #f1f2f6; font-size: 12px;")
                
            meta_grid.addWidget(lbl_key, idx, 0)
            meta_grid.addWidget(lbl_val, idx, 1)

        layout.addWidget(meta_frame)
        layout.addStretch()

        btn_close = QPushButton("OK", self)
        btn_close.setObjectName("PrimaryBtn")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class PipWorker(QThread):
    """Wykonuje operacje PIP w osobnym wątku, zapobiegając zamarzaniu GUI."""
    status_signal = pyqtSignal(str)
    debug_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str, str, bool, str)

    def __init__(self, python_exec, package_name, action):
        super().__init__()
        self.python_exec = python_exec
        self.package_name = package_name
        self.action = action

    def run(self):
        if self.action == "install":
            cmd = [self.python_exec, "-m", "pip", "install", self.package_name]
        elif self.action == "upgrade":
            cmd = [self.python_exec, "-m", "pip", "install", "--upgrade", self.package_name]
        elif self.action == "uninstall":
            cmd = [self.python_exec, "-m", "pip", "uninstall", "-y", self.package_name]
        else:
            return

        self.debug_signal.emit(f"Executing: {' '.join(cmd)}")
        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace", check=True, startupinfo=startupinfo)
            self.finished_signal.emit(self.package_name, self.action, True, result.stdout)
        except subprocess.CalledProcessError as e:
            self.finished_signal.emit(self.package_name, self.action, False, e.stderr or e.stdout)


class PackageRow(QFrame):
    """Pojedynczy wiersz reprezentujący pakiet na liście."""
    def __init__(self, parent, package_name, is_installed, install_callback, current_lang, installed_version=""):
        super().__init__(parent)
        self.package_name = package_name
        self.install_callback = install_callback
        self.current_lang = current_lang
        self.is_installed = is_installed
        self.installed_version = installed_version

        self.setObjectName("PackageRow")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 8, 15, 8)

        self.lbl_name = QLabel(package_name, self)
        self.lbl_name.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        self.layout.addWidget(self.lbl_name, 1)

        self.lbl_status = QLabel(self)
        self.layout.addWidget(self.lbl_status)

        self.btn_install = QPushButton(self)
        self.btn_install.setObjectName("PrimaryBtn")
        self.btn_install.clicked.connect(lambda: self.install_callback(self.package_name, self, "install"))
        self.layout.addWidget(self.btn_install)

        self.btn_update = QPushButton(self)
        self.btn_update.setObjectName("AccentBtn")
        self.btn_update.clicked.connect(lambda: self.install_callback(self.package_name, self, "upgrade"))
        self.layout.addWidget(self.btn_update)

        self.btn_uninstall = QPushButton(self)
        self.btn_uninstall.setObjectName("DangerBtn")
        self.btn_uninstall.clicked.connect(lambda: self.install_callback(self.package_name, self, "uninstall"))
        self.layout.addWidget(self.btn_uninstall)

        self.update_ui()

    def update_ui(self):
        lang = LANGUAGES[self.current_lang]
        self.btn_install.setText(lang["install_btn"])
        self.btn_update.setText(lang["update_btn"])
        self.btn_uninstall.setText(lang["uninstall_btn"])

        self.btn_install.setEnabled(True)
        self.btn_update.setEnabled(True)
        self.btn_uninstall.setEnabled(True)

        if self.is_installed:
            version_str = f" ({self.installed_version})" if self.installed_version else ""
            self.lbl_status.setText(f"✓ {lang['installed']}{version_str}")
            self.lbl_status.setStyleSheet("color: #2ecc71; font-weight: bold; margin-right: 10px;")
            self.setStyleSheet("QFrame#PackageRow { background-color: #2d2d35; border: 1px solid #2ecc71; border-radius: 8px; }")
            self.lbl_status.show()
            self.btn_install.hide()
            self.btn_update.show()
            self.btn_uninstall.show()
        else:
            self.lbl_status.hide()
            self.btn_install.show()
            self.btn_update.hide()
            self.btn_uninstall.hide()
            self.setStyleSheet("QFrame#PackageRow { background-color: #2d2d35; border: 1px solid #3f3f46; border-radius: 8px; }")

    def set_loading(self, action):
        lang = LANGUAGES[self.current_lang]
        self.btn_install.setEnabled(False)
        self.btn_update.setEnabled(False)
        self.btn_uninstall.setEnabled(False)
        if action == "install":
            self.btn_install.setText(lang["installing"])


class InstallerFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "EN"
        self.debug_visible = False
        self.python_executable = find_system_python()
        self.search_filter = ""
        self.current_category = None
        self.zainstalowane_pakiety = {}
        self.active_workers = []  # Zapobiega usuwaniu wątków przez Garbage Collector

        self.init_ui()
        self.refresh_installed_packages()

    def init_ui(self):
        self.setWindowTitle(LANGUAGES[self.current_lang]["title"])
        self.resize(950, 720)
        self.setMinimumSize(850, 620)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # --- GÓRNY PANEL ---
        top_bar = QHBoxLayout()
        self.lbl_header = QLabel(LANGUAGES[self.current_lang]["header"], self)
        self.lbl_header.setObjectName("HeaderLabel")
        top_bar.addWidget(self.lbl_header, 1)

        self.btn_refresh = QPushButton(LANGUAGES[self.current_lang]["refresh_btn"], self)
        self.btn_refresh.clicked.connect(self.refresh_installed_packages)
        top_bar.addWidget(self.btn_refresh)

        self.btn_toggle_debug = QPushButton(LANGUAGES[self.current_lang]["btn_debug_show"], self)
        self.btn_toggle_debug.clicked.connect(self.toggle_debug_panel)
        top_bar.addWidget(self.btn_toggle_debug)

        self.btn_lang = QPushButton("🌐 EN / PL", self)
        self.btn_lang.clicked.connect(self.toggle_language)
        top_bar.addWidget(self.btn_lang)

        self.btn_about = QPushButton("ℹ️", self)
        self.btn_about.setFixedWidth(40)
        self.btn_about.clicked.connect(self.show_about_dialog)
        top_bar.addWidget(self.btn_about)

        self.main_layout.addLayout(top_bar)

        # --- PANEL WYSZUKIWANIA I INTERPRETERA ---
        search_bar = QHBoxLayout()
        search_bar.setSpacing(10)

        self.search_ctrl = QLineEdit(self)
        self.search_ctrl.setPlaceholderText(LANGUAGES[self.current_lang]["search_placeholder"])
        self.search_ctrl.textChanged.connect(self.on_search_text)
        search_bar.addWidget(self.search_ctrl, 2)

        self.lbl_interpreter = QLabel(LANGUAGES[self.current_lang]["python_exec_label"], self)
        self.lbl_interpreter.setStyleSheet("font-weight: 600; color: #9ca3af;")
        search_bar.addWidget(self.lbl_interpreter)

        self.txt_interpreter = QLineEdit(self.python_executable, self)
        self.txt_interpreter.setReadOnly(True)
        self.txt_interpreter.setStyleSheet("background-color: #2d2d35; color: #9ca3af;")
        search_bar.addWidget(self.txt_interpreter, 3)

        self.btn_choose_python = QPushButton(LANGUAGES[self.current_lang]["choose_interpreter_btn"], self)
        self.btn_choose_python.clicked.connect(self.choose_python_executable)
        search_bar.addWidget(self.btn_choose_python)

        self.main_layout.addLayout(search_bar)

        # --- GŁÓWNY SPLITTER WIDOKU ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #3f3f46; width: 2px; }")
        self.main_layout.addWidget(self.splitter, 1)

        # Lewo: Kategorie
        self.left_widget = QWidget(self)
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setContentsMargins(0, 0, 5, 0)
        self.lbl_cat = QLabel(LANGUAGES[self.current_lang]["categories"], self)
        self.lbl_cat.setStyleSheet("font-weight: bold; color: #9ca3af; text-transform: uppercase; font-size: 11px;")
        left_layout.addWidget(self.lbl_cat)

        self.category_list = QListWidget(self)
        self.category_list.itemClicked.connect(self.on_category_select)
        left_layout.addWidget(self.category_list)
        self.splitter.addWidget(self.left_widget)

        # Prawo: Przewijana lista pakietów
        self.right_widget = QWidget(self)
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(5, 0, 0, 0)
        self.lbl_right_header = QLabel(LANGUAGES[self.current_lang]["select_category"], self)
        self.lbl_right_header.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 14px;")
        self.right_layout.addWidget(self.lbl_right_header)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.right_layout.addWidget(self.scroll_area)
        self.splitter.addWidget(self.right_widget)

        self.splitter.setSizes([280, 670])

        # --- KONSOLA DIAGNOSTYCZNA ---
        self.debug_console = QTextEdit(self)
        self.debug_console.setReadOnly(True)
        self.debug_console.setStyleSheet("background-color: #121214; color: #f5f6fa; font-family: 'Consolas', monospace; border-radius: 6px; padding: 10px; border: 1px solid #3f3f46;")
        self.debug_console.hide()
        self.main_layout.addWidget(self.debug_console, 0)

        # --- PASY STATUSU I PROGRESU ---
        self.statusBar().setStyleSheet("background-color: #1e1e24; border-top: 1px solid #3f3f46; color: #9ca3af; padding: 3px;")
        self.statusBar().showMessage(LANGUAGES[self.current_lang]["status_ready"])
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedWidth(160)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.statusBar().addPermanentWidget(self.progress_bar)

        self.update_category_listbox()

    def update_category_listbox(self):
        self.category_list.clear()
        lang = LANGUAGES[self.current_lang]
        for cat_raw in BIBLIOTEKI.keys():
            translated_key = CATEGORY_MAP.get(cat_raw, cat_raw)
            display_name = lang.get(translated_key, cat_raw)
            self.category_list.addItem(display_name)

    def toggle_language(self):
        self.current_lang = "PL" if self.current_lang == "EN" else "EN"
        lang = LANGUAGES[self.current_lang]

        self.setWindowTitle(lang["title"])
        self.lbl_header.setText(lang["header"])
        self.btn_refresh.setText(lang["refresh_btn"])
        self.btn_toggle_debug.setText(lang["btn_debug_hide"] if self.debug_visible else lang["btn_debug_show"])
        self.search_ctrl.setPlaceholderText(lang["search_placeholder"])
        self.lbl_interpreter.setText(lang["python_exec_label"])
        self.btn_choose_python.setText(lang["choose_interpreter_btn"])
        self.lbl_cat.setText(lang["categories"])

        self.update_category_listbox()
        self.refresh_package_view()

    def toggle_debug_panel(self):
        self.debug_visible = not self.debug_visible
        lang = LANGUAGES[self.current_lang]
        if self.debug_visible:
            self.debug_console.show()
            self.btn_toggle_debug.setText(lang["btn_debug_hide"])
            self.main_layout.setStretchFactor(self.debug_console, 1)
        else:
            self.debug_console.hide()
            self.btn_toggle_debug.setText(lang["btn_debug_show"])
            self.main_layout.setStretchFactor(self.debug_console, 0)

    def log_debug(self, text):
        self.debug_console.append(text)

    def refresh_installed_packages(self):
        self.log_debug("Scanning python environment packages...")
        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run([self.python_executable, "-m", "pip", "freeze"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace", check=True, startupinfo=startupinfo)
            self.zainstalowane_pakiety = parse_pip_freeze_output(result.stdout)
            self.log_debug(f"Scan complete. Found {len(self.zainstalowane_pakiety)} packages.")
            self.refresh_package_view()
        except Exception as e:
            QMessageBox.critical(self, LANGUAGES[self.current_lang]["scan_error_title"], LANGUAGES[self.current_lang]["scan_error_msg"].format(str(e)))

    def on_category_select(self, item):
        index = self.category_list.row(item)
        self.current_category = list(BIBLIOTEKI.keys())[index]
        self.refresh_package_view()

    def on_search_text(self, text):
        self.search_filter = text.lower().strip()
        self.refresh_package_view()

    def refresh_package_view(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        lang = LANGUAGES[self.current_lang]

        if self.search_filter:
            prefix = "🔍 Wyniki dla: " if self.current_lang == "PL" else "🔍 Results for: "
            self.lbl_right_header.setText(f"{prefix}'{self.search_filter}'")
            packages_to_show = []
            for cat, libs in BIBLIOTEKI.items():
                for lib in libs:
                    if self.search_filter in lib.lower() and lib not in packages_to_show:
                        packages_to_show.append(lib)
        elif self.current_category:
            translated_cat_key = CATEGORY_MAP.get(self.current_category, self.current_category)
            translated_cat_name = lang.get(translated_cat_key, self.current_category)
            self.lbl_right_header.setText(f"{lang['libs_in']}{translated_cat_name}")
            packages_to_show = BIBLIOTEKI[self.current_category]
        else:
            self.lbl_right_header.setText(lang["select_category"])
            return

        if not packages_to_show:
            empty_lbl = QLabel(lang["no_search_results"], self)
            empty_lbl.setStyleSheet("color: #9ca3af; font-style: italic; padding: 20px;")
            self.scroll_layout.addWidget(empty_lbl)
            return

        for pkg in packages_to_show:
            is_installed = pkg.lower() in self.zainstalowane_pakiety
            version = self.zainstalowane_pakiety.get(pkg.lower(), "")
            row = PackageRow(self.scroll_content, pkg, is_installed, self.handle_package_action, self.current_lang, version)
            self.scroll_layout.addWidget(row)

    def choose_python_executable(self):
        file_path, _ = QFileDialog.getOpenFileName(self, LANGUAGES[self.current_lang]["choose_interpreter_title"], "", "Python Executable (python.exe python);;All Files (*)")
        if file_path:
            self.python_executable = file_path
            self.txt_interpreter.setText(file_path)
            self.refresh_installed_packages()

    def set_controls_enabled(self, enabled: bool):
        """Blokuje kontrolki na czas operacji instalacji, zapobiegając race condition."""
        self.central_widget.setEnabled(enabled)

    def handle_package_action(self, package_name, row_widget, action):
        lang = LANGUAGES[self.current_lang]
        if action == "install":
            status_text = lang["preparing"].format(package_name)
        elif action == "upgrade":
            status_text = lang["preparing_upgrade"].format(package_name)
        else:
            status_text = lang["preparing_uninstall"].format(package_name)

        self.statusBar().showMessage(status_text)
        row_widget.set_loading(action)
        self.set_controls_enabled(False)

        self.progress_bar.setRange(0, 0)

        # Tworzenie bezpiecznego i trwałego obiektu wątku
        worker = PipWorker(self.python_executable, package_name, action)
        worker.debug_signal.connect(self.log_debug)
        worker.finished_signal.connect(self.on_pip_action_finished)
        
        self.active_workers.append(worker)  # Zachowanie silnej referencji wątku
        worker.start()

    def on_pip_action_finished(self, package_name, action, success, output_or_error):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.set_controls_enabled(True)

        lang = LANGUAGES[self.current_lang]
        self.log_debug(output_or_error)

        if success:
            self.statusBar().showMessage(lang[f"success_{action}_status"].format(package_name))
            QMessageBox.information(self, lang["success_title"], lang[f"success_{action}_msg"].format(package_name))
        else:
            self.statusBar().showMessage(lang[f"error_{action}_status"].format(package_name))
            summary = summarize_install_output(output_or_error)
            QMessageBox.critical(self, lang["error_title"], lang[f"error_{action}_msg"].format(package_name, summary))

        # Czyszczenie wątków z pamięci podręcznej
        sender_worker = self.sender()
        if sender_worker in self.active_workers:
            self.active_workers.remove(sender_worker)

        self.refresh_installed_packages()
        self.progress_bar.setValue(0)

    def show_about_dialog(self):
        dialog = AboutDialog(self, self.current_lang)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    frame = InstallerFrame()
    frame.show()
    sys.exit(app.exec())