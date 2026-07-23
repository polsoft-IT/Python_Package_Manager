import json
import os
import sys
import subprocess
import logging
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QScrollArea,
    QSplitter, QTextEdit, QMessageBox, QFileDialog, QFrame, QProgressBar
)
from PyQt6.QtGui import QFont, QColor, QPalette

# Metadane programu
METADATA = {
    "name"       : "Python Package Installer",
    "version"    : "3.0.5",
    "author"     : "Sebastian Januchowski",
    "company"    : "polsoft.ITS(TM) Group",
    "github"     : "https://github.com/polsoft-IT",
    "email"      : "polsoft.its@mail.com",
    "description": "Nowoczesny, graficzny menedżer i instalator pakietów dla środowisk Python."
}

# Konfiguracja logowania
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Nowoczesny arkusz stylów CSS (QSS) dla Dark Mode
DARK_STYLE = """
QMainWindow {
    background-color: #121214;
}
QWidget {
    color: #e1e1e6;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
}
QLabel#HeaderLabel {
    color: #ffffff;
    font-weight: 700;
    font-size: 20px;
}
QLineEdit {
    background-color: #202024;
    border: 1px solid #323238;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e1e1e6;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #00adb5;
}
QLineEdit[readOnly="true"] {
    color: #8d8d99;
    background-color: #1c1c1e;
}
QListWidget {
    background-color: #202024;
    border: 1px solid #323238;
    border-radius: 8px;
    padding: 5px;
}
QListWidget::item {
    padding: 10px 12px;
    border-radius: 6px;
    margin-bottom: 2px;
    color: #c4c4cc;
}
QListWidget::item:hover {
    background-color: #29292e;
    color: #ffffff;
}
QListWidget::item:selected {
    background-color: #00adb5;
    color: #ffffff;
    font-weight: bold;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QPushButton {
    font-weight: 600;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
}
QPushButton:disabled {
    background-color: #29292e !important;
    color: #7c7c8a !important;
}
QPushButton#BtnInstall { background-color: #00adb5; color: #ffffff; }
QPushButton#BtnInstall:hover { background-color: #00cbd3; }
QPushButton#BtnUpdate { background-color: #2b7a78; color: #ffffff; }
QPushButton#BtnUpdate:hover { background-color: #3aafa9; }
QPushButton#BtnUninstall { background-color: #e04343; color: #ffffff; }
QPushButton#BtnUninstall:hover { background-color: #f05454; }

PackageRow {
    background-color: #202024;
    border: 1px solid #323238;
    border-radius: 8px;
}
PackageRow[installed="true"] {
    background-color: #172220;
    border: 1px solid #1f3a35;
}
QScrollBar:vertical {
    border: none;
    background: #121214;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #323238;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #00adb5;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QSplitter::handle { background-color: transparent; }
"""

# Poprawiony jasny motyw
LIGHT_STYLE = """
QMainWindow {
    background-color: #f8fafc;
}
QWidget {
    color: #475569;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
}
QLabel#HeaderLabel {
    color: #0284c7;
    font-weight: 700;
    font-size: 21px;
    background-color: transparent;
}
QLabel#RightHeaderLabel {
    color: #475569;
    background-color: transparent;
}
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 14px;
    color: #475569;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #38bdf8;
    background-color: #ffffff;
}
QLineEdit[readOnly="true"] {
    color: #94a3b8;
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
}
QListWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 6px;
}
QListWidget::item {
    padding: 11px 14px;
    border-radius: 6px;
    margin-bottom: 3px;
    color: #64748b;
    background-color: #ffffff;
}
QListWidget::item:hover {
    background-color: #f1f5f9;
    color: #0284c7;
}
QListWidget::item:selected {
    background-color: #0ea5e9;
    color: #ffffff;
    font-weight: 600;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollArea QWidget {
    background-color: transparent;
}
QPushButton {
    font-weight: 600;
    border-radius: 7px;
    padding: 9px 16px;
    font-size: 13px;
    border: 1px solid transparent;
}
QPushButton:disabled {
    background-color: #f8fafc !important;
    color: #cbd5e1 !important;
    border: 1px solid #e2e8f0 !important;
}

QPushButton#BtnInstall { background-color: #38bdf8; color: #ffffff; }
QPushButton#BtnInstall:hover { background-color: #0ea5e9; }
QPushButton#BtnUpdate { background-color: #34d399; color: #ffffff; }
QPushButton#BtnUpdate:hover { background-color: #10b981; }
QPushButton#BtnUninstall { background-color: #f87171; color: #ffffff; }
QPushButton#BtnUninstall:hover { background-color: #ef4444; }

PackageRow {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}
PackageRow QLabel {
    color: #475569;
    background-color: transparent;
}
PackageRow[installed="true"] {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
}

QScrollBar:vertical {
    border: none;
    background: #f8fafc;
    width: 9px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #e2e8f0;
    min-height: 25px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #cbd5e1;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QSplitter { background-color: transparent; }
QSplitter::handle { background-color: transparent; }
"""

def parse_pip_freeze_output(output):
    """Parsuje dane wyjściowe z `pip freeze` do słownika {pakiet: wersja}."""
    packages = {}
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
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


BIBLIOTEKI = {
    "compilers": ["pyinstaller", "cx_Freeze", "nuitka", "py2exe", "cython", "pyarmor", "briefcase"],
    "gui": ["customtkinter", "PyQt6", "PySide6", "wxPython", "kivy", "flet", "PySimpleGUI", "dearpygui", "eel"],
    "games": ["pygame", "arcade", "pyglet", "panda3d", "ursina", "pygame-zero", "renpy", "cocos2d"],
    "data_science": ["numpy", "pandas", "matplotlib", "scikit-learn", "scipy", "seaborn", "statsmodels", "xgboost", "lightgbm", "yellowbrick"],
    "scraping": ["requests", "beautifulsoup4", "scrapy", "selenium", "playwright", "httpx", "parsel", "undetected-chromedriver"],
    "web_frameworks": ["django", "flask", "fastapi", "tornado", "dash", "starlette", "sanic", "quart", "bottle", "jinja2"],
    "databases": ["sqlalchemy", "peewee", "alembic", "psycopg2-binary", "pymongo", "redis", "mysql-connector-python", "pymysql", "asyncpg", "motor"],
    "testing": ["pytest", "unittest2", "tox", "coverage", "mock", "behave", "pytest-cov", "robotframework", "nose2", "hypothesis"],
    "image_video": ["pillow", "opencv-python", "scikit-image", "moviepy", "imageio", "mediapipe", "pyvips", "pydub", "opencv-contrib-python"],
    "async": ["asyncio", "trio", "twisted", "gevent", "aiohttp", "anyio", "httpx"],
    "security": ["cryptography", "pyjwt", "passlib", "bcrypt", "paramiko", "pycryptodome", "argon2-cffi"],
    "automation": ["psutil", "click", "sh", "schedule", "watchdog", "pyautogui", "fabric", "invoke", "ansible"],
    "parsers": ["pydantic", "pyyaml", "toml", "lxml", "xmltodict", "ruamel.yaml", "csvkit", "xmlschema"],
    "cli": ["rich", "textual", "typer", "prompt_toolkit", "blessed", "colorama", "docopt", "questionary"],
    "ai_nlp": ["transformers", "spacy", "nltk", "gensim", "langchain", "openai", "torch", "torchvision", "torchaudio", "tensorflow", "keras", "sentence-transformers", "accelerate", "diffusers", "datasets", "tokenizers", "sentencepiece", "peft", "bitsandbytes", "onnxruntime", "optuna", "gradio", "fastai", "llama-cpp-python", "openllm", "wandb"],
    "documents": ["openpyxl", "pypdf", "python-docx", "python-pptx", "weasyprint", "xlsxwriter", "pdfplumber", "pdfminer.six", "python-magic"],
    "visualization": ["plotly", "bokeh", "altair", "pygal", "pydot", "folium", "geopandas", "streamlit"],
    "logging": ["loguru", "icecream", "structlog", "sentry-sdk", "memory-profiler", "python-json-logger", "logzero"],
    "network": ["scapy", "pyshark", "python-socketio", "dnspython", "netaddr", "websocket-client", "requests"],
    "mocking": ["faker", "hypothesis", "factory-boy", "mimesis", "model-bakery"],
    "cloud": ["boto3", "google-cloud-storage", "azure-storage-blob", "kubernetes", "apache-libcloud", "google-auth", "azure-identity"],
    "graphics_3d": ["open3d", "trimesh", "pyopengl", "pyrender", "moderngl", "pywavefront"]
}

LANGUAGES = {
    "EN": {
        "title": "Python Package Installer (PyQt6 Modern)",
        "header": "Python Package Manager",
        "categories": "Categories",
        "select_category": "Select a category from the left menu",
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
        "error_title": "Installation Error",
        "error_install_msg": "Failed to install {}.\nError:\n{}",
        "error_upgrade_msg": "Failed to upgrade {}.\nError:\n{}",
        "error_uninstall_msg": "Failed to uninstall {}.\nError:\n{}",
        "error_install_status": "Error installing package {}.",
        "error_upgrade_status": "Error upgrading package {}.",
        "error_uninstall_status": "Error uninstalling package {}.",
        "scan_error_title": "Error",
        "scan_error_msg": "Failed to scan packages: {}",
        "search_label": "Search:",
        "search_placeholder": "Type to search packages...",
        "python_exec_label": "Interpreter:",
        "choose_interpreter_btn": "Change Path",
        "choose_interpreter_title": "Select Python Interpreter",
        "update_btn": "Upgrade",
        "uninstall_btn": "Uninstall",
        "no_search_results": "No packages match your search.",
        "btn_refresh": "Refresh",
        "refresh_btn": "Refresh",
        "btn_debug_show": "Show Logs",
        "btn_debug_hide": "Hide Logs",
        "btn_save_logs": "Save Logs",
        "save_logs_success": "Logs saved successfully!",
        "save_logs_error": "Failed to save logs: {}",
        "about_title": "About",
        "theme_light": "Theme: Light",
        "theme_dark": "Theme: Dark",
        "acknowledgements_title": "Acknowledgements",
        "acknowledgements_text": "Special thanks to <b>Google</b> and the global <b>Python Community</b> for providing open-source tools, developer resources, and rich ecosystems that made the development of this software possible.",
        "cat_names": {
            "compilers": "Compilers & Transpilers", "gui": "GUI (Graphical Interfaces)", "games": "Games & Multimedia",
            "data_science": "Data Science & ML", "scraping": "Web Scraping & APIs", "web_frameworks": "Web Frameworks",
            "databases": "Databases & ORMs", "testing": "Testing & QA", "image_video": "Image & Video Processing",
            "async": "Asynchrony & Concurrency", "security": "Cryptography & Security", "automation": "Automation & System",
            "parsers": "Parsers & Data Formats", "cli": "Terminals & CLI", "ai_nlp": "Artificial Intelligence & NLP",
            "documents": "Document & File Management", "visualization": "Advanced Visualization", "logging": "Logging & Diagnostics",
            "network": "Network & Protocols", "mocking": "Data Generation & Mocking", "cloud": "Cloud & Integrations",
            "graphics_3d": "3D Graphics & Models"
        }
    },
    "PL": {
        "title": "Instalator Pakietów Python (PyQt6 Modern)",
        "header": "Menedżer Pakietów Python",
        "categories": "Kategorie",
        "select_category": "Wybierz kategorię z menu po lewej",
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
        "search_placeholder": "Wpisz nazwę pakietu...",
        "python_exec_label": "Interpreter:",
        "choose_interpreter_btn": "Zmień ścieżkę",
        "choose_interpreter_title": "Wybierz interpreter Pythona",
        "update_btn": "Aktualizuj",
        "uninstall_btn": "Odinstaluj",
        "no_search_results": "Brak pakietów pasujących do wyszukiwania.",
        "btn_refresh": "Odśwież",
        "refresh_btn": "Odśwież",
        "btn_debug_show": "Pokaż Logi",
        "btn_debug_hide": "Ukryj Logi",
        "btn_save_logs": "Zapisz Logi",
        "save_logs_success": "Logi zostały pomyślnie zapisane!",
        "save_logs_error": "Nie udało się zapisać logów: {}",
        "about_title": "O programie",
        "theme_light": "Motyw: Jasny",
        "theme_dark": "Motyw: Ciemny",
        "acknowledgements_title": "Podziękowania",
        "acknowledgements_text": "Szczególne podziękowania dla firmy <b>Google</b> oraz globalnej <b>Społeczności Pythona</b> za udostępnienie narzędzi open-source, zasobów programistycznych i bogatych ekosystemów, które umożliwiły zbudowanie tego programu.",
        "cat_names": {
            "compilers": "Kompilatory i Transpilatory", "gui": "GUI (Interfejsy graficzne)", "games": "Gry i Multimedia (Games)",
            "data_science": "Data Science i ML", "scraping": "Web Scraping i API", "web_frameworks": "Frameworki Webowe",
            "databases": "Bazy Danych i ORM", "testing": "Testowanie i QA", "image_video": "Obraz i Wideo",
            "async": "Asynchroniczność i Współbieżność", "security": "Kryptografia i Bezpieczeństwo", "automation": "Automatyzacja i System",
            "parsers": "Parsers i Formatowanie Danych", "cli": "Terminale i CLI", "ai_nlp": "Sztuczna Inteligencja i NLP",
            "documents": "Obsługa Dokumentów i Plików", "visualization": "Zaawansowana Wizualizacja", "logging": "Logowanie i Diagnostyka",
            "network": "Sieć i Protokoły", "mocking": "Generowanie Danych i Mock", "cloud": "Chmura i Integracje",
            "graphics_3d": "Grafika i Modele 3D"
        }
    }
}


class PipWorker(QThread):
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
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.finished_signal.emit(self.package_name, self.action, True, result.stdout)
        except subprocess.CalledProcessError as e:
            self.finished_signal.emit(self.package_name, self.action, False, e.stderr or e.stdout)


class PackageRow(QFrame):
    def __init__(self, parent, package_name, is_installed, install_callback, current_lang, theme_mode, installed_version=""):
        super().__init__(parent)
        self.package_name = package_name
        self.install_callback = install_callback
        self.current_lang = current_lang
        self.theme_mode = theme_mode
        self.is_installed = is_installed
        self.installed_version = installed_version

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        self.layout.setSpacing(10)

        self.lbl_name = QLabel(package_name, self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        self.lbl_name.setFont(font)
        self.layout.addWidget(self.lbl_name, 1)

        self.lbl_status = QLabel(self)
        self.layout.addWidget(self.lbl_status)

        self.btn_install = QPushButton(self)
        self.btn_install.setObjectName("BtnInstall")
        self.btn_install.clicked.connect(lambda: self.install_callback(self.package_name, self, "install"))
        self.layout.addWidget(self.btn_install)

        self.btn_update = QPushButton(self)
        self.btn_update.setObjectName("BtnUpdate")
        self.btn_update.clicked.connect(lambda: self.install_callback(self.package_name, self, "upgrade"))
        self.layout.addWidget(self.btn_update)

        self.btn_uninstall = QPushButton(self)
        self.btn_uninstall.setObjectName("BtnUninstall")
        self.btn_uninstall.clicked.connect(lambda: self.install_callback(self.package_name, self, "uninstall"))
        self.layout.addWidget(self.btn_uninstall)

        self.update_ui()

    def update_ui(self):
        lang = LANGUAGES[self.current_lang]
        self.btn_install.setText(lang["install_btn"])
        self.btn_update.setText(lang["update_btn"])
        self.btn_uninstall.setText(lang["uninstall_btn"])

        if self.is_installed:
            self.setProperty("installed", "true")
            version_str = f" v{self.installed_version}" if self.installed_version else ""
            self.lbl_status.setText(f"✓ {lang['installed']}{version_str}")
            
            color = "#00adb5" if self.theme_mode == "dark" else "#10b981"
            self.lbl_status.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; background-color: transparent;")
            self.lbl_status.show()
            self.btn_install.hide()
            self.btn_update.show()
            self.btn_uninstall.show()
        else:
            self.setProperty("installed", "false")
            self.lbl_status.hide()
            self.btn_install.show()
            self.btn_update.hide()
            self.btn_uninstall.hide()
        
        self.style().unpolish(self)
        self.style().polish(self)

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
        self.theme_mode = "dark"
        self.debug_visible = False
        self.python_executable = sys.executable
        self.search_filter = ""
        self.current_category_id = None
        self.zainstalowane_pakiety = {}

        self.init_ui()
        self.refresh_installed_packages()

    def init_ui(self):
        self.setStyleSheet(DARK_STYLE)
        self.setWindowTitle(LANGUAGES[self.current_lang]["title"])
        self.resize(1000, 750)
        self.setMinimumSize(850, 650)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # --- GÓRNY PANEL (TOP BAR) ---
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

        self.btn_save_logs = QPushButton(LANGUAGES[self.current_lang]["btn_save_logs"], self)
        self.btn_save_logs.clicked.connect(self.save_logs_to_file)
        top_bar.addWidget(self.btn_save_logs)

        self.btn_theme = QPushButton(LANGUAGES[self.current_lang]["theme_dark"], self)
        self.btn_theme.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.btn_theme)

        self.btn_lang = QPushButton("EN / PL", self)
        self.btn_lang.clicked.connect(self.toggle_language)
        top_bar.addWidget(self.btn_lang)

        self.btn_about = QPushButton("ℹ", self)
        self.btn_about.clicked.connect(self.show_about_dialog)
        top_bar.addWidget(self.btn_about)

        self.main_layout.addLayout(top_bar)

        # --- PANEL WYSZUKIWANIA I INTERPRETERA ---
        search_bar = QHBoxLayout()
        search_bar.setSpacing(10)
        
        self.lbl_search = QLabel(LANGUAGES[self.current_lang]["search_label"], self)
        search_bar.addWidget(self.lbl_search)

        self.search_ctrl = QLineEdit(self)
        self.search_ctrl.setPlaceholderText(LANGUAGES[self.current_lang]["search_placeholder"])
        self.search_ctrl.textChanged.connect(self.on_search_text)
        search_bar.addWidget(self.search_ctrl, 2)

        self.lbl_interpreter = QLabel(LANGUAGES[self.current_lang]["python_exec_label"], self)
        search_bar.addWidget(self.lbl_interpreter)

        self.txt_interpreter = QLineEdit(self.python_executable, self)
        self.txt_interpreter.setReadOnly(True)
        search_bar.addWidget(self.txt_interpreter, 3)

        self.btn_choose_python = QPushButton(LANGUAGES[self.current_lang]["choose_interpreter_btn"], self)
        self.btn_choose_python.clicked.connect(self.choose_python_executable)
        search_bar.addWidget(self.btn_choose_python)

        self.main_layout.addLayout(search_bar)

        # --- GŁÓWNY SPLITTER WIDOKU ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.main_layout.addWidget(self.splitter, 1)

        # Lewo: Kategorie
        self.left_widget = QWidget(self)
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_cat = QLabel(LANGUAGES[self.current_lang]["categories"], self)
        font_sub = QFont()
        font_sub.setBold(True)
        font_sub.setPointSize(11)
        self.lbl_cat.setFont(font_sub)
        self.lbl_cat.setObjectName("SubHeaderLabel")
        left_layout.addWidget(self.lbl_cat)

        self.category_list = QListWidget(self)
        self.category_list.itemClicked.connect(self.on_category_select)
        left_layout.addWidget(self.category_list)
        self.splitter.addWidget(self.left_widget)

        # Prawo: Lista Pakietów
        self.right_widget = QWidget(self)
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_right_header = QLabel(LANGUAGES[self.current_lang]["select_category"], self)
        self.lbl_right_header.setObjectName("RightHeaderLabel")
        self.lbl_right_header.setFont(font_sub)
        self.right_layout.addWidget(self.lbl_right_header)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setContentsMargins(0, 0, 5, 0)
        self.scroll_area.setWidget(self.scroll_content)
        self.right_layout.addWidget(self.scroll_area)
        self.splitter.addWidget(self.right_widget)

        self.splitter.setSizes([280, 680])

        # --- KONSOLA DIAGNOSTYCZNA ---
        self.debug_console = QTextEdit(self)
        self.debug_console.setReadOnly(True)
        self.debug_console.hide()
        self.main_layout.addWidget(self.debug_console, 0)

        # --- CENTROWANY PROGRESS BAR W STATUS BARZE ---
        self.status_progress_container = QWidget(self)
        progress_layout = QHBoxLayout(self.status_progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()  
        
        progress_layout.addWidget(self.progress_bar)
        self.statusBar().addPermanentWidget(self.status_progress_container, 1) 

        # --- ETYKIETA AUTORA W STATUS BARZE ---
        self.lbl_author_watermark = QLabel("Sebastian Januchowski", self)
        font_watermark = QFont()
        font_watermark.setFamily("Segoe UI")
        font_watermark.setPointSize(9)
        font_watermark.setWeight(QFont.Weight.Medium)
        self.lbl_author_watermark.setFont(font_watermark)
        self.lbl_author_watermark.setContentsMargins(0, 0, 10, 0)
        self.statusBar().addPermanentWidget(self.lbl_author_watermark, 0)

        self.update_button_colors()
        self.statusBar().showMessage(LANGUAGES[self.current_lang]["status_ready"])
        self.update_category_listbox()

    def update_category_listbox(self):
        selected_id = self.current_category_id
        self.category_list.clear()
        translations = LANGUAGES[self.current_lang]["cat_names"]
        
        for cat_id in BIBLIOTEKI.keys():
            display_name = translations.get(cat_id, cat_id)
            self.category_list.addItem(display_name)
            item = self.category_list.item(self.category_list.count() - 1)
            item.setData(Qt.ItemDataRole.UserRole, cat_id)
            
            if cat_id == selected_id:
                self.category_list.setCurrentItem(item)

    def toggle_theme(self):
        if self.theme_mode == "dark":
            self.theme_mode = "light"
            self.setStyleSheet(LIGHT_STYLE)
            self.btn_theme.setText(LANGUAGES[self.current_lang]["theme_light"])
        else:
            self.theme_mode = "dark"
            self.setStyleSheet(DARK_STYLE)
            self.btn_theme.setText(LANGUAGES[self.current_lang]["theme_dark"])
        
        self.update_button_colors()
        self.refresh_package_view()

    def update_button_colors(self):
        if self.theme_mode == "dark":
            btn_style = "background-color: #323238; color: #ffffff;"
            accent_style = "background-color: #2b7a78; color: white;"
            console_style = "background-color: #121214; border: 1px solid #323238; color: #a4a4a4; font-family: 'Consolas', monospace; border-radius: 6px; padding: 8px;"
            status_style = "color: #8d8d99; border-top: 1px solid #202024; padding-top: 4px;"
            cat_lbl_style = "color: #8d8d99; margin-bottom: 5px; background-color: transparent;"
            watermark_style = "color: rgba(255, 255, 255, 0.18); background-color: transparent;"
            progress_style = """
                QProgressBar { background-color: #202024; border: 1px solid #323238; border-radius: 6px; }
                QProgressBar::chunk { background-color: #00adb5; border-radius: 5px; }
            """
        else:
            btn_style = "background-color: #ffffff; border: 1px solid #e2e8f0; color: #64748b;"
            accent_style = "background-color: #38bdf8; color: white; border: none;"
            console_style = "background-color: #ffffff; border: 1px solid #e2e8f0; color: #64748b; font-family: 'Consolas', monospace; border-radius: 8px; padding: 10px;"
            status_style = "color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 6px; background-color: #f8fafc;"
            cat_lbl_style = "color: #64748b; margin-bottom: 5px; background-color: transparent;"
            watermark_style = "color: rgba(71, 85, 105, 0.25); background-color: transparent;"
            progress_style = """
                QProgressBar { background-color: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 6px; }
                QProgressBar::chunk { background-color: #0ea5e9; border-radius: 5px; }
            """

        self.btn_refresh.setStyleSheet(btn_style)
        self.btn_toggle_debug.setStyleSheet(btn_style)
        self.btn_save_logs.setStyleSheet(btn_style)
        self.btn_theme.setStyleSheet(btn_style)
        self.btn_lang.setStyleSheet(btn_style)
        self.btn_about.setStyleSheet(btn_style)
        self.btn_choose_python.setStyleSheet(accent_style)
        self.debug_console.setStyleSheet(console_style)
        self.statusBar().setStyleSheet(status_style)
        self.lbl_cat.setStyleSheet(cat_lbl_style)
        self.lbl_right_header.setStyleSheet(cat_lbl_style)
        self.lbl_author_watermark.setStyleSheet(watermark_style)
        self.progress_bar.setStyleSheet(progress_style)

    def toggle_language(self):
        self.current_lang = "PL" if self.current_lang == "EN" else "EN"
        lang = LANGUAGES[self.current_lang]

        self.setWindowTitle(lang["title"])
        self.lbl_header.setText(lang["header"])
        self.btn_refresh.setText(lang["refresh_btn"])
        self.btn_toggle_debug.setText(lang["btn_debug_hide"] if self.debug_visible else lang["btn_debug_show"])
        self.btn_save_logs.setText(lang["btn_save_logs"])
        self.btn_theme.setText(lang["theme_light"] if self.theme_mode == "light" else lang["theme_dark"])
        self.lbl_search.setText(lang["search_label"])
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

    def save_logs_to_file(self):
        lang = LANGUAGES[self.current_lang]
        logs_text = self.debug_console.toPlainText()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            lang["btn_save_logs"], 
            "installer_logs.txt", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(logs_text)
                QMessageBox.information(self, lang["success_title"], lang["save_logs_success"])
            except Exception as e:
                QMessageBox.critical(self, lang["scan_error_title"], lang["save_logs_error"].format(str(e)))

    def refresh_installed_packages(self):
        self.log_debug("Scanning python environment packages...")
        try:
            result = subprocess.run([self.python_executable, "-m", "pip", "freeze"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.zainstalowane_pakiety = parse_pip_freeze_output(result.stdout)
            
            self.log_debug(f"Scan complete. Found {len(self.zainstalowane_pakiety)} packages:")
            self.log_debug("----------------------------------------")
            if self.zainstalowane_pakiety:
                for pkg_name, pkg_version in sorted(self.zainstalowane_pakiety.items()):
                    version_info = f"=={pkg_version}" if pkg_version else " (editable/direct URL)"
                    self.log_debug(f" -> {pkg_name}{version_info}")
            else:
                self.log_debug(" (No packages found in this environment)")
            self.log_debug("----------------------------------------")

            self.refresh_package_view()
        except Exception as e:
            QMessageBox.critical(self, LANGUAGES[self.current_lang]["scan_error_title"], LANGUAGES[self.current_lang]["scan_error_msg"].format(str(e)))

    def on_category_select(self, item):
        self.current_category_id = item.data(Qt.ItemDataRole.UserRole)
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
        cat_lbl_style = "color: #8d8d99; margin-bottom: 5px; background-color: transparent;" if self.theme_mode == "dark" else "color: #64748b; margin-bottom: 5px; background-color: transparent;"

        if self.search_filter:
            self.lbl_right_header.setText(f"{lang['search_label']} '{self.search_filter}'")
            packages_to_show = []
            for cat_id, libs in BIBLIOTEKI.items():
                for lib in libs:
                    if self.search_filter in lib.lower() and lib not in packages_to_show:
                        packages_to_show.append(lib)
        elif self.current_category_id:
            translated_cat_name = lang["cat_names"].get(self.current_category_id, self.current_category_id)
            self.lbl_right_header.setText(f"{lang['libs_in']}{translated_cat_name}")
            packages_to_show = BIBLIOTEKI[self.current_category_id]
        else:
            self.lbl_right_header.setText(lang["select_category"])
            return

        self.lbl_right_header.setStyleSheet(cat_lbl_style)

        if not packages_to_show:
            no_res_lbl = QLabel(lang["no_search_results"], self)
            no_res_lbl.setStyleSheet("color: #94a3b8; font-style: italic; padding: 10px; background-color: transparent;")
            self.scroll_layout.addWidget(no_res_lbl)
            return

        for pkg in packages_to_show:
            is_installed = pkg.lower() in self.zainstalowane_pakiety
            version = self.zainstalowane_pakiety.get(pkg.lower(), "")
            row = PackageRow(self.scroll_content, pkg, is_installed, self.handle_package_action, self.current_lang, self.theme_mode, version)
            self.scroll_layout.addWidget(row)

    def choose_python_executable(self):
        file_path, _ = QFileDialog.getOpenFileName(self, LANGUAGES[self.current_lang]["choose_interpreter_title"], "", "Python Executable (python.exe python);;All Files (*)")
        if file_path:
            self.python_executable = file_path
            self.txt_interpreter.setText(file_path)
            self.refresh_installed_packages()

    def handle_package_action(self, package_name, row_widget, action):
        lang = LANGUAGES[self.current_lang]
        if action == "install":
            status_text = lang["preparing"].format(package_name)
        elif action == "upgrade":
            status_text = lang["preparing_upgrade"].format(package_name)
        else:
            status_text = lang["preparing_uninstall"].format(package_name)

        self.statusBar().showMessage(status_text)
        self.progress_bar.show()  
        row_widget.set_loading(action)

        worker = PipWorker(self.python_executable, package_name, action)
        worker.debug_signal.connect(self.log_debug)
        worker.finished_signal.connect(self.on_pip_action_finished)
        row_widget.worker = worker
        worker.start()

    def on_pip_action_finished(self, package_name, action, success, output_or_error):
        lang = LANGUAGES[self.current_lang]
        self.log_debug(output_or_error)
        self.progress_bar.hide()  

        if success:
            self.statusBar().showMessage(lang[f"success_{action}_status"].format(package_name))
            QMessageBox.information(self, lang["success_title"], lang[f"success_{action}_msg"].format(package_name))
        else:
            self.statusBar().showMessage(lang[f"error_{action}_status"].format(package_name))
            summary = summarize_install_output(output_or_error)
            QMessageBox.critical(self, lang["error_title"], lang[f"error_{action}_msg"].format(package_name, summary))

        self.refresh_installed_packages()

    def show_about_dialog(self):
        """Wyświetla okno o programie zawierające zintegrowane podziękowania."""
        lang = LANGUAGES[self.current_lang]
        accent_color = "#00adb5" if self.theme_mode == "dark" else "#0284c7"
        
        about_html = (
            f"<h3><span style='color: {accent_color};'>{METADATA['name']}</span></h3>"
            f"<b>Wersja:</b> {METADATA['version']}<br>"
            f"<b>Opis:</b> {METADATA['description']}<br><br>"
            f"<b>Autor:</b> {METADATA['author']}<br>"
            f"<b>Firma:</b> {METADATA['company']}<br>"
            f"<b>GitHub:</b> <a href='{METADATA['github']}' style='color: {accent_color};'>{METADATA['github']}</a><br>"
            f"<b>E-mail:</b> <a href='mailto:{METADATA['email']}' style='color: {accent_color};'>{METADATA['email']}</a>"
            f"<br><br>"
            f"<hr style='border: 0; border-top: 1px solid rgba(128, 128, 128, 0.3);'>"
            f"<h4><span style='color: {accent_color};'>{lang['acknowledgements_title']}</span></h4>"
            f"<p style='line-height: 1.4; font-size: 12px;'>{lang['acknowledgements_text']}</p>"
        )
        
        QMessageBox.about(self, lang["about_title"], about_html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    frame = InstallerFrame()
    frame.show()
    sys.exit(app.exec())