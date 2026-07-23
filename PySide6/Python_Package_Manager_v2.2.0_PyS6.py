import sys
import os
import subprocess
import logging
import shutil
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QScrollArea,
    QMessageBox, QFileDialog, QSplitter, QTextEdit, QProgressBar,
    QFrame, QDialog
)
from PySide6.QtGui import QFont, QIcon

# Konfiguracja logowania
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# --- MAPOWANIE KATEGORII JĘZYKOWYCH ---
CATEGORY_MAP = {
    "Kompilatory i Transpilatory": "cat_compilers",
    "GUI (Interfejsy graficzne)": "cat_gui",
    "Gry i Multimedia (Games)": "cat_games",
    "Data Science i ML": "cat_datascience",
    "Web Scraping i API": "cat_scraping",
    "Frameworki Webowe": "cat_web",
    "Bazy Danych i ORM": "cat_db",
    "Testowanie i QA": "cat_testing",
    "Obraz i Wideo": "cat_media",
    "Asynchroniczność i Współbieżność": "cat_async",
    "Kryptografia i Bezpieczeństwo": "cat_crypto",
    "Automatyzacja i System": "cat_automation",
    "Parsery i Formatowanie Danych": "cat_parsers",
    "Terminale i CLI": "cat_cli",
    "Sztuczna Inteligencja i NLP": "cat_ai",
    "Obsługa Dokumentów i Plików": "cat_docs",
    "Zaawansowana Wizualizacja": "cat_viz",
    "Logowanie i Diagnostyka": "cat_logging",
    "Sieć i Protokoły": "cat_network",
    "Generowanie Danych i Mock": "cat_mock",
    "Chmura i Integracje": "cat_cloud",
    "Grafika i Modele 3D": "cat_3d"
}

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
        "title": "Python Package Installer (PySide6)",
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
        "search_placeholder": "🔍 Search packages...",
        "python_exec_label": "Python Interpreter:",
        "choose_interpreter_btn": "Browse...",
        "choose_interpreter_title": "Select Python Interpreter",
        "update_btn": "Upgrade",
        "uninstall_btn": "Uninstall",
        "no_search_results": "No packages match your search.",
        "refresh_btn": "🔄 Refresh",
        "btn_debug_show": "🛠 Show Logs",
        "btn_debug_hide": "🛠 Hide Logs",
        "about_title": "About Program",
        "about_msg": "A modern desktop client designed to streamline pip operations. Built using Python and PySide6.",
        "cat_compilers": "Compilers & Transpilers",
        "cat_gui": "GUI Frameworks",
        "cat_games": "Games & Multimedia",
        "cat_datascience": "Data Science & ML",
        "cat_scraping": "Web Scraping & APIs",
        "cat_web": "Web Frameworks",
        "cat_db": "Databases & ORMs",
        "cat_testing": "Testing & QA",
        "cat_media": "Image & Video",
        "cat_async": "Async & Concurrency",
        "cat_crypto": "Cryptography & Security",
        "cat_automation": "Automation & OS",
        "cat_parsers": "Parsers & Serialization",
        "cat_cli": "Terminal & CLIs",
        "cat_ai": "Artificial Intelligence & NLP",
        "cat_docs": "Documents & File Parsing",
        "cat_viz": "Advanced Visualization",
        "cat_logging": "Logging & Diagnostics",
        "cat_network": "Networking & Protocols",
        "cat_mock": "Data Generation & Mocking",
        "cat_cloud": "Cloud Integrations",
        "cat_3d": "3D Graphics & Modeling"
    },
    "PL": {
        "title": "Instalator Pakietów Python (PySide6)",
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
        "search_placeholder": "🔍 Szukaj pakietów...",
        "python_exec_label": "Interpreter Pythona:",
        "choose_interpreter_btn": "Przeglądaj...",
        "choose_interpreter_title": "Wybierz interpreter Pythona",
        "update_btn": "Aktualizuj",
        "uninstall_btn": "Odinstaluj",
        "no_search_results": "Brak pakietów pasujących do wyszukiwania.",
        "refresh_btn": "🔄 Odśwież",
        "btn_debug_show": "🛠 Pokaż Logi",
        "btn_debug_hide": "🛠 Ukryj Logi",
        "about_title": "O programie",
        "about_msg": "Nowoczesny klient okienkowy usprawniający zarządzanie pakietami pip. Stworzony w Pythonie i PySide6.",
        "cat_compilers": "Kompilatory i Transpilatory",
        "cat_gui": "GUI (Interfejsy graficzne)",
        "cat_games": "Gry i Multimedia (Games)",
        "cat_datascience": "Data Science i ML",
        "cat_scraping": "Web Scraping i API",
        "cat_web": "Frameworki Webowe",
        "cat_db": "Bazy Danych i ORM",
        "cat_testing": "Testowanie i QA",
        "cat_media": "Obraz i Wideo",
        "cat_async": "Asynchroniczność i Współbieżność",
        "cat_crypto": "Kryptografia i Bezpieczeństwo",
        "cat_automation": "Automatyzacja i System",
        "cat_parsers": "Parsery i Formatowanie Danych",
        "cat_cli": "Terminale i CLI",
        "cat_ai": "Sztuczna Inteligencja i NLP",
        "cat_docs": "Obsługa Dokumentów i Plików",
        "cat_viz": "Zaawansowana Wizualizacja",
        "cat_logging": "Logowanie i Diagnostyka",
        "cat_network": "Sieć i Protokoły",
        "cat_mock": "Generowanie Danych i Mock",
        "cat_cloud": "Chmura i Integracje",
        "cat_3d": "Grafika i Modele 3D"
    }
}

METADATA = {
    "name": "Python Package Manager",
    "version": "2.2.0",
    "author": "Sebastian Januchowski",
    "company": "polsoft.ITS(TM) Group",
    "github": "https://github.com/polsoft-IT",
    "email": "polsoft.its@mail.com"
}

# --- ARKUSZE STYLÓW QSS DLA MOTYWÓW ---
QSS_THEMES = {
    "dark": """
        QWidget {
            background-color: #000000;
            color: #ffffff;
            font-family: "Segoe UI";
            font-size: 13px;
        }
        QFrame#packageRow {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 6px;
        }
        QFrame#packageRow[installed="true"] {
            border: 1px solid #00aa44;
        }
        QListWidget {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 4px;
        }
        QListWidget::item:selected {
            background-color: #ffffff;
            color: #000000;
        }
        QLineEdit {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 5px;
            color: #ffffff;
        }
        QPushButton {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2d2d2d;
        }
        QPushButton:disabled {
            color: #888888;
            background-color: #121212;
        }
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #333333;
            font-family: "Consolas";
        }
        QScrollBar:vertical {
            background-color: #000000;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background-color: #2d2d2d;
            border-radius: 6px;
        }
        QSplitter::handle {
            background-color: #2d2d2d;
        }
    """,
    "light": """
        QWidget {
            background-color: #f3f4f6;
            color: #1f2937;
            font-family: "Segoe UI";
            font-size: 13px;
        }
        QFrame#packageRow {
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 6px;
        }
        QFrame#packageRow[installed="true"] {
            border: 1px solid #16a34a;
        }
        QListWidget {
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 4px;
        }
        QListWidget::item:selected {
            background-color: #1f2937;
            color: #ffffff;
        }
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            padding: 5px;
            color: #1f2937;
        }
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #e5e7eb;
        }
        QPushButton:disabled {
            color: #9ca3af;
            background-color: #f3f4f6;
        }
        QTextEdit {
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            font-family: "Consolas";
        }
        QScrollBar:vertical {
            background-color: #f3f4f6;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background-color: #d1d5db;
            border-radius: 6px;
        }
        QSplitter::handle {
            background-color: #d1d5db;
        }
    """
}

def parse_pip_freeze_output(output):
    packages = {}
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("-e ") or " @ " in line:
            continue
        if "==" in line:
            pkg, version = line.split("==", 1)
            packages[pkg.strip().lower()] = version.strip()
        else:
            packages[line.lower()] = ""
    return packages


def find_system_python():
    """Find the system Python interpreter, especially when the app is frozen."""
    # If not frozen, just return sys.executable
    if not getattr(sys, "frozen", False):
        return sys.executable
    
    # Try common Python locations on Windows
    possible_paths = [
        # Python from Microsoft Store
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "python.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "python3.exe"),
        # Python installed for all users
        r"C:\Python312\python.exe",
        r"C:\Python311\python.exe",
        r"C:\Python310\python.exe",
        r"C:\Python39\python.exe",
        r"C:\Python38\python.exe",
        # Python in Program Files
        r"C:\Program Files\Python312\python.exe",
        r"C:\Program Files\Python311\python.exe",
        r"C:\Program Files\Python310\python.exe",
        r"C:\Program Files\Python39\python.exe",
        r"C:\Program Files\Python38\python.exe",
        # Python in Program Files (x86)
        r"C:\Program Files (x86)\Python312\python.exe",
        r"C:\Program Files (x86)\Python311\python.exe",
        r"C:\Program Files (x86)\Python310\python.exe",
        r"C:\Program Files (x86)\Python39\python.exe",
        r"C:\Program Files (x86)\Python38\python.exe",
    ]
    
    # Also try using 'python' or 'python3' from PATH
    try:
        python_from_path = shutil.which("python")
        if python_from_path:
            possible_paths.insert(0, python_from_path)
        python3_from_path = shutil.which("python3")
        if python3_from_path:
            possible_paths.insert(0, python3_from_path)
    except Exception:
        pass
    
    # Check each path
    for path in possible_paths:
        if os.path.exists(path):
            # Test if it's a valid Python interpreter
            try:
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                result = subprocess.run(
                    [path, "-c", "import sys; print(sys.executable)"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    startupinfo=startupinfo
                )
                if result.returncode == 0:
                    return path
            except Exception:
                continue
    
    # If nothing found, return sys.executable as a last resort
    return sys.executable

# --- WĄTKI PROCESÓW (ASYNCHRONICZNOŚĆ QT) ---
class WorkerThread(QThread):
    finished_signal = Signal(bool, str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace", check=True, startupinfo=startupinfo)
            self.finished_signal.emit(True, result.stdout)
        except subprocess.CalledProcessError as e:
            self.finished_signal.emit(False, e.stderr or e.stdout)
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class AboutDialog(QDialog):
    def __init__(self, parent, lang_code):
        super().__init__(parent)
        lang = LANGUAGES[lang_code]
        self.setWindowTitle(lang["about_title"])
        self.setFixedSize(460, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        logo = QLabel("📦")
        logo.setFont(QFont("Segoe UI", 36))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        title = QLabel(METADATA["name"])
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        version = QLabel(f"v{METADATA['version']}")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        desc = QLabel(lang["about_msg"])
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        meta_frame = QFrame()
        meta_frame.setFrameShape(QFrame.StyledPanel)
        meta_layout = QVBoxLayout(meta_frame)
        
        rows = [
            (f"<b>Author:</b> {METADATA['author']}"),
            (f"<b>Company:</b> {METADATA['company']}"),
            (f"<b>GitHub:</b> <a href='{METADATA['github']}' style='color:#00adb5;'>{METADATA['github']}</a>"),
            (f"<b>Email:</b> {METADATA['email']}")
        ]
        for row in rows:
            lbl = QLabel(row)
            lbl.setOpenExternalLinks(True)
            meta_layout.addWidget(lbl)
            
        layout.addWidget(meta_frame)
        
        btn_close = QPushButton("OK")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, 0, Qt.AlignCenter)


class PackageRowWidget(QFrame):
    def __init__(self, package_name, is_installed, version, action_callback, lang_code, theme):
        super().__init__()
        self.setObjectName("packageRow")
        self.package_name = package_name
        self.is_installed = is_installed
        self.version = version
        self.action_callback = action_callback
        self.lang_code = lang_code
        self.theme = theme
        
        self.setProperty("installed", "true" if is_installed else "false")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        
        self.lbl_name = QLabel(self.package_name)
        self.lbl_name.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(self.lbl_name, 1)
        
        self.lbl_status = QLabel()
        layout.addWidget(self.lbl_status)
        
        self.btn_action = QPushButton()
        self.btn_action.clicked.connect(lambda: self.action_callback(self.package_name, self, "install"))
        layout.addWidget(self.btn_action)
        
        self.btn_update = QPushButton()
        self.btn_update.clicked.connect(lambda: self.action_callback(self.package_name, self, "upgrade"))
        layout.addWidget(self.btn_update)
        
        self.btn_uninstall = QPushButton()
        self.btn_uninstall.clicked.connect(lambda: self.action_callback(self.package_name, self, "uninstall"))
        layout.addWidget(self.btn_uninstall)
        
        self.update_lang_and_state()

    def update_lang_and_state(self):
        lang = LANGUAGES[self.lang_code]
        
        self.btn_action.setText(lang["install_btn"])
        self.btn_update.setText(lang["update_btn"])
        self.btn_uninstall.setText(lang["uninstall_btn"])
        
        self.btn_action.setEnabled(True)
        self.btn_update.setEnabled(True)
        self.btn_uninstall.setEnabled(True)
        
        if self.is_installed:
            v_str = f" ({self.version})" if self.version else ""
            self.lbl_status.setText(f"✓ {lang['installed']}{v_str}")
            color = "#00ff66" if self.theme == "dark" else "#16a34a"
            self.lbl_status.setStyleSheet(f"color: {color}; font-weight: bold; margin-right: 10px;")
            self.lbl_status.show()
            
            self.btn_action.hide()
            self.btn_update.show()
            self.btn_uninstall.show()
        else:
            self.lbl_status.hide()
            self.btn_update.hide()
            self.btn_uninstall.hide()
            self.btn_action.show()

    def set_loading(self, action):
        lang = LANGUAGES[self.lang_code]
        self.btn_action.setEnabled(False)
        self.btn_update.setEnabled(False)
        self.btn_uninstall.setEnabled(False)
        if action == "install":
            self.btn_action.setText(lang["installing"])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "EN"
        self.current_theme = "dark"
        self.python_executable = find_system_python()
        self.search_filter = ""
        self.current_category = None
        self.zainstalowane_pakiety = {}
        
        self.init_ui()
        self.refresh_installed_packages()

    def init_ui(self):
        self.resize(1000, 720)
        self.setMinimumSize(850, 620)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 15, 20, 15)
        
        # --- Top Bar ---
        top_layout = QHBoxLayout()
        self.lbl_header = QLabel()
        self.lbl_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        top_layout.addWidget(self.lbl_header, 1)
        
        self.btn_refresh = QPushButton()
        self.btn_refresh.clicked.connect(self.refresh_installed_packages)
        top_layout.addWidget(self.btn_refresh)
        
        self.btn_toggle_debug = QPushButton()
        self.btn_toggle_debug.clicked.connect(self.toggle_debug_panel)
        top_layout.addWidget(self.btn_toggle_debug)
        
        self.btn_lang = QPushButton("🌐 EN / PL")
        self.btn_lang.clicked.connect(self.toggle_language)
        top_layout.addWidget(self.btn_lang)
        
        self.btn_theme = QPushButton("🌙 / ☀️")
        self.btn_theme.clicked.connect(self.toggle_theme)
        top_layout.addWidget(self.btn_theme)
        
        self.btn_about = QPushButton("ℹ️")
        self.btn_about.setFixedWidth(40)
        self.btn_about.clicked.connect(self.show_about_dialog)
        top_layout.addWidget(self.btn_about)
        
        main_layout.addLayout(top_layout)
        
        # --- Search & Interpreter Bar ---
        search_layout = QHBoxLayout()
        self.search_ctrl = QLineEdit()
        self.search_ctrl.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_ctrl, 3)
        
        self.lbl_interpreter = QLabel()
        self.lbl_interpreter.setStyleSheet("color: #888888; font-weight: bold;")
        search_layout.addWidget(self.lbl_interpreter)
        
        self.txt_interpreter = QLineEdit(self.python_executable)
        self.txt_interpreter.setReadOnly(True)
        search_layout.addWidget(self.txt_interpreter, 3)
        
        self.btn_choose_python = QPushButton()
        self.btn_choose_python.clicked.connect(self.choose_python_executable)
        search_layout.addWidget(self.btn_choose_python)
        
        main_layout.addLayout(search_layout)
        
        # --- Splitter (Główna przestrzeń pracy) ---
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Panel Lewy (Kategorie)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_cat = QLabel()
        self.lbl_cat.setStyleSheet("color: #888888; font-weight: bold;")
        left_layout.addWidget(self.lbl_cat)
        
        self.category_list = QListWidget()
        self.category_list.itemSelectionChanged.connect(self.on_category_select)
        left_layout.addWidget(self.category_list)
        self.splitter.addWidget(left_widget)
        
        # Panel Prawy (Biblioteki)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_right_header = QLabel()
        self.lbl_right_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        right_layout.addWidget(self.lbl_right_header)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        right_layout.addWidget(self.scroll_area)
        self.splitter.addWidget(right_widget)
        
        self.splitter.setSizes([260, 680])
        main_layout.addWidget(self.splitter, 1)
        
        # --- Debug Console ---
        self.debug_console = QTextEdit()
        self.debug_console.setReadOnly(True)
        self.debug_console.hide()
        main_layout.addWidget(self.debug_console)
        
        # --- Status Bar ---
        status_layout = QHBoxLayout()
        self.lbl_status = QLabel()
        status_layout.addWidget(self.lbl_status, 1)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(160)
        self.progress_bar.setTextVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(status_layout)
        
        self.update_ui_texts()
        self.apply_theme()

    def update_ui_texts(self):
        lang = LANGUAGES[self.current_lang]
        
        self.setWindowTitle(lang["title"])
        self.lbl_header.setText(lang["header"])
        self.btn_refresh.setText(lang["refresh_btn"])
        self.btn_toggle_debug.setText(lang["btn_debug_hide"] if self.debug_console.isVisible() else lang["btn_debug_show"])
        self.search_ctrl.setPlaceholderText(lang["search_placeholder"])
        self.lbl_interpreter.setText(lang["python_exec_label"])
        self.btn_choose_python.setText(lang["choose_interpreter_btn"])
        self.lbl_cat.setText(lang["categories"])
        
        self.lbl_status.setText(lang["status_ready"])
        
        # Aktualizacja listy kategorii
        self.category_list.blockSignals(True)
        current_row = self.category_list.currentRow()
        self.category_list.clear()
        for cat_raw in BIBLIOTEKI.keys():
            translated_key = CATEGORY_MAP.get(cat_raw, cat_raw)
            self.category_list.addItem(lang.get(translated_key, cat_raw))
        if current_row >= 0:
            self.category_list.setCurrentRow(current_row)
        self.category_list.blockSignals(False)
        
        self.refresh_package_view()

    def apply_theme(self):
        self.setStyleSheet(QSS_THEMES[self.current_theme])

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()
        self.refresh_package_view()

    def toggle_language(self):
        self.current_lang = "PL" if self.current_lang == "EN" else "EN"
        self.update_ui_texts()

    def toggle_debug_panel(self):
        if self.debug_console.isVisible():
            self.debug_console.hide()
        else:
            self.debug_console.show()
        self.update_ui_texts()

    def log_debug(self, text):
        self.debug_console.append(text)

    def refresh_installed_packages(self):
        self.log_debug("Scanning python environment packages...")
        self.progress_bar.setRange(0, 0) # Mode Indeterminate
        
        cmd = [self.python_executable, "-m", "pip", "freeze"]
        self.scan_thread = WorkerThread(cmd)
        self.scan_thread.finished_signal.connect(self.on_scan_finished)
        self.scan_thread.start()

    @Slot(bool, str)
    def on_scan_finished(self, success, output):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        if success:
            self.zainstalowane_pakiety = parse_pip_freeze_output(output)
            self.log_debug(f"Scan complete. Found {len(self.zainstalowane_pakiety)} packages.")
            self.refresh_package_view()
        else:
            lang = LANGUAGES[self.current_lang]
            QMessageBox.critical(self, lang["scan_error_title"], lang["scan_error_msg"].format(output))

    def on_category_select(self):
        current_row = self.category_list.currentRow()
        if current_row >= 0:
            self.current_category = list(BIBLIOTEKI.keys())[current_row]
            self.search_filter = ""
            self.search_ctrl.clear()
            self.refresh_package_view()

    def on_search_text_changed(self, text):
        self.search_filter = text.lower().strip()
        self.refresh_package_view()

    def choose_python_executable(self):
        lang = LANGUAGES[self.current_lang]
        file_filter = "Python (python.exe)" if sys.platform == "win32" else "All Files (*)"
        filename, _ = QFileDialog.getOpenFileName(self, lang["choose_interpreter_title"], "", file_filter)
        if filename:
            self.python_executable = filename
            self.txt_interpreter.setText(filename)
            self.refresh_installed_packages()

    def show_about_dialog(self):
        dialog = AboutDialog(self, self.current_lang)
        dialog.exec()

    def handle_package_action(self, package_name, row_widget, action):
        lang = LANGUAGES[self.current_lang]
        row_widget.set_loading(action)
        self.progress_bar.setRange(0, 0)
        
        if action == "install":
            self.lbl_status.setText(lang["preparing"].format(package_name))
            cmd = [self.python_executable, "-m", "pip", "install", package_name]
        elif action == "upgrade":
            self.lbl_status.setText(lang["preparing_upgrade"].format(package_name))
            cmd = [self.python_executable, "-m", "pip", "install", "--upgrade", package_name]
        elif action == "uninstall":
            self.lbl_status.setText(lang["preparing_uninstall"].format(package_name))
            cmd = [self.python_executable, "-m", "pip", "uninstall", "-y", package_name]

        self.action_thread = WorkerThread(cmd)
        self.action_thread.finished_signal.connect(lambda success, output: self.on_action_finished(package_name, action, success, output))
        self.action_thread.start()

    def on_action_finished(self, package_name, action, success, output):
        lang = LANGUAGES[self.current_lang]
        self.log_debug(output)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        if success:
            msg_map = {
                "install": "success_install_msg",
                "upgrade": "success_upgrade_msg",
                "uninstall": "success_uninstall_msg"
            }
            status_map = {
                "install": "success_install_status",
                "upgrade": "success_upgrade_status",
                "uninstall": "success_uninstall_status"
            }
            QMessageBox.information(self, lang["success_title"], lang[msg_map[action]].format(package_name))
            self.lbl_status.setText(lang[status_map[action]].format(package_name))
        else:
            err_map = {
                "install": "error_install_msg",
                "upgrade": "error_upgrade_msg",
                "uninstall": "error_uninstall_msg"
            }
            err_status = {
                "install": "error_install_status",
                "upgrade": "error_upgrade_status",
                "uninstall": "error_uninstall_status"
            }
            # Ograniczenie wyświetlania zbyt długich logów błędu
            lines = [line.strip() for line in output.splitlines() if line.strip()][-8:]
            short_err = "\n".join(lines)
            QMessageBox.critical(self, lang["error_title"], lang[err_map[action]].format(package_name, short_err))
            self.lbl_status.setText(lang[err_status[action]].format(package_name))
            
        self.refresh_installed_packages()

    def refresh_package_view(self):
        # Czyszczenie starego widoku scrolla
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        lang = LANGUAGES[self.current_lang]
        packages_to_show = []
        
        if self.search_filter:
            prefix = "🔍 Wyniki dla: " if self.current_lang == "PL" else "🔍 Results for: "
            self.lbl_right_header.setText(f"{prefix}'{self.search_filter}'")
            for cat, libs in BIBLIOTEKI.items():
                for lib in libs:
                    if self.search_filter in lib.lower() and lib not in packages_to_show:
                        packages_to_show.append(lib)
        elif self.current_category:
            translated_cat_key = CATEGORY_MAP.get(self.current_category, self.current_category)
            self.lbl_right_header.setText(f"{lang['libs_in']}{lang.get(translated_cat_key, self.current_category)}")
            packages_to_show = BIBLIOTEKI.get(self.current_category, [])
        else:
            self.lbl_right_header.setText(lang["select_category"])
            return
            
        if not packages_to_show:
            empty_lbl = QLabel(lang["no_search_results"])
            empty_lbl.setStyleSheet("color: #888888; font-style: italic; padding: 10px;")
            self.scroll_layout.addWidget(empty_lbl)
            return
            
        for pkg in sorted(packages_to_show):
            is_installed = pkg.lower() in self.zainstalowane_pakiety
            version = self.zainstalowane_pakiety.get(pkg.lower(), "")
            row = PackageRowWidget(pkg, is_installed, version, self.handle_package_action, self.current_lang, self.current_theme)
            self.scroll_layout.addWidget(row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())