import json
import os
import sys
import subprocess
import threading
import webbrowser
import logging


# Basic logger for CLI and debugging
logger = logging.getLogger(__name__)
# Avoid configuring logging at import time so module is import-safe for tests.
logger.addHandler(logging.NullHandler())

try:
    import wx
except Exception:
    wx = None

HAS_WX = wx is not None


def resource_path(relative_path):
    """Return the absolute path to a resource, whether running frozen or not."""
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def parse_pip_freeze_output(output):
    """Parse output from `pip freeze` into a {package: version} dictionary."""
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
    """Collapse long pip output so the GUI remains responsive."""
    if not output:
        return ""

    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return "\n".join(lines)

    return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"


try:
    from wx import adv
    HyperlinkCtrl = adv.HyperlinkCtrl
except Exception:
    HyperlinkCtrl = None


# Maksymalnie rozszerzona lista bibliotek przypisanych do kategorii
BIBLIOTEKI = {
    "Kompilatory i Transpilatory": [
        "pyinstaller",
        "cx_Freeze",
        "nuitka",
        "py2exe",
        "cython",
        "pyarmor",
        "briefcase"
    ],
    "GUI (Interfejsy graficzne)": [
        "customtkinter",
        "PyQt6",
        "PySide6",
        "wxPython",
        "kivy",
        "flet",
        "PySimpleGUI",
        "dearpygui",
        "eel"
    ],
    "Gry i Multimedia (Games)": [
        "pygame",
        "arcade",
        "pyglet",
        "panda3d",
        "ursina",
        "pygame-zero",
        "renpy",
        "cocos2d"
    ],
    "Data Science i ML": [
        "numpy",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "scipy",
        "seaborn",
        "statsmodels",
        "xgboost",
        "lightgbm",
        "yellowbrick"
    ],
    "Web Scraping i API": [
        "requests",
        "beautifulsoup4",
        "scrapy",
        "selenium",
        "playwright",
        "httpx",
        "parsel",
        "undetected-chromedriver"
    ],
    "Frameworki Webowe": [
        "django",
        "flask",
        "fastapi",
        "tornado",
        "dash",
        "starlette",
        "sanic",
        "quart",
        "bottle",
        "jinja2"
    ],
    "Bazy Danych i ORM": [
        "sqlalchemy",
        "peewee",
        "alembic",
        "psycopg2-binary",
        "pymongo",
        "redis",
        "mysql-connector-python",
        "pymysql",
        "asyncpg",
        "motor"
    ],
    "Testowanie i QA": [
        "pytest",
        "unittest2",
        "tox",
        "coverage",
        "mock",
        "behave",
        "pytest-cov",
        "robotframework",
        "nose2",
        "hypothesis"
    ],
    "Obraz i Wideo": [
        "pillow",
        "opencv-python",
        "scikit-image",
        "moviepy",
        "imageio",
        "mediapipe",
        "pyvips",
        "pydub",
        "opencv-contrib-python"
    ],
    "Asynchroniczność i Współbieżność": [
        "asyncio",
        "trio",
        "twisted",
        "gevent",
        "aiohttp",
        "anyio",
        "httpx"
    ],
    "Kryptografia i Bezpieczeństwo": [
        "cryptography",
        "pyjwt",
        "passlib",
        "bcrypt",
        "paramiko",
        "pycryptodome",
        "argon2-cffi"
    ],
    "Automatyzacja i System": [
        "psutil",
        "click",
        "sh",
        "schedule",
        "watchdog",
        "pyautogui",
        "fabric",
        "invoke",
        "ansible"
    ],
    "Parsery i Formatowanie Danych": [
        "pydantic",
        "pyyaml",
        "toml",
        "lxml",
        "xmltodict",
        "ruamel.yaml",
        "csvkit",
        "xmlschema"
    ],
    "Terminale i CLI": [
        "rich",
        "textual",
        "typer",
        "prompt_toolkit",
        "blessed",
        "colorama",
        "docopt",
        "questionary"
    ],
    "Sztuczna Inteligencja i NLP": [
        "transformers",
        "spacy",
        "nltk",
        "gensim",
        "langchain",
        "openai",
        "torch",
        "torchvision",
        "torchaudio",
        "tensorflow",
        "keras",
        "sentence-transformers",
        "accelerate",
        "diffusers",
        "datasets",
        "tokenizers",
        "sentencepiece",
        "peft",
        "bitsandbytes",
        "onnxruntime",
        "optuna",
        "gradio",
        "fastai",
        "llama-cpp-python",
        "openllm",
        "wandb"
    ],
    "Obsługa Dokumentów i Plików": [
        "openpyxl",
        "pypdf",
        "python-docx",
        "python-pptx",
        "weasyprint",
        "xlsxwriter",
        "pdfplumber",
        "pdfminer.six",
        "python-magic"
    ],
    "Zaawansowana Wizualizacja": [
        "plotly",
        "bokeh",
        "altair",
        "pygal",
        "pydot",
        "folium",
        "geopandas",
        "streamlit"
    ],
    "Logowanie i Diagnostyka": [
        "loguru",
        "icecream",
        "structlog",
        "sentry-sdk",
        "memory-profiler",
        "python-json-logger",
        "logzero"
    ],
    "Sieć i Protokoły": [
        "scapy",
        "pyshark",
        "python-socketio",
        "dnspython",
        "netaddr",
        "websocket-client",
        "requests"
    ],
    "Generowanie Danych i Mock": [
        "faker",
        "hypothesis",
        "factory-boy",
        "mimesis",
        "model-bakery"
    ],
    "Chmura i Integracje": [
        "boto3",
        "google-cloud-storage",
        "azure-storage-blob",
        "kubernetes",
        "apache-libcloud",
        "google-auth",
        "azure-identity"
    ],
    "Grafika i Modele 3D": [
        "open3d",
        "trimesh",
        "pyopengl",
        "pyrender",
        "moderngl",
        "pywavefront"
    ]
}

# Słownik tłumaczeń
LANGUAGES = {
    "EN": {
        "title": "Python Package Installer (with Debug)",
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
        "success_msg": "Successfully installed {}!",
        "success_upgrade_msg": "Successfully upgraded {}!",
        "success_uninstall_msg": "Successfully uninstalled {}!",
        "success_status": "Success: Package '{}' installed successfully.",
        "success_upgrade_status": "Success: Package '{}' upgraded successfully.",
        "success_uninstall_status": "Success: Package '{}' uninstalled successfully.",
        "error_title": "Installation Error",
        "error_msg": "Failed to install {}.\nError:\n{}",
        "error_upgrade_msg": "Failed to upgrade {}.\nError:\n{}",
        "error_uninstall_msg": "Failed to uninstall {}.\nError:\n{}",
        "error_status": "Error installing package {}.",
        "error_upgrade_status": "Error upgrading package {}.",
        "error_uninstall_status": "Error uninstalling package {}.",
        "scan_error_title": "Error",
        "scan_error_msg": "Failed to scan packages: {}",
        "search_label": "Search:",
        "search_placeholder": "Search packages...",
        "python_exec_label": "Python Interpreter:",
        "choose_interpreter_btn": "Change Interpreter",
        "choose_interpreter_title": "Select Python Interpreter",
        "python_executable_filter": "Python executable|python.exe|All files|*.*",
        "update_btn": "Upgrade",
        "uninstall_btn": "Uninstall",
        "no_search_results": "No packages match your search.",
        "btn_refresh": "Refresh",
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
        "graphics3d_cat": "3D Graphics & Models",
        "refresh_btn": "Refresh",
        "btn_debug_show": "Show Debug Log",
        "btn_debug_hide": "Hide Debug Log",
        "debug_header": "--- Diagnostic Console (Debug) ---",
        "about_title": "About",
        "about_author": "Author",
        "about_company": "Company",
        "about_email": "Email",
        "about_github": "GitHub",
        "about_close": "Close"
    },
    "PL": {
        "title": "Instalator Pakietów Python (z Debugowaniem)",
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
        "success_msg": "Pomyślnie zainstalowano {}!",
        "success_upgrade_msg": "Pomyślnie zaktualizowano {}!",
        "success_uninstall_msg": "Pomyślnie odinstalowano {}!",
        "success_status": "Sukces: Zainstalowano pakiet '{}'.",
        "success_upgrade_status": "Sukces: Zaktualizowano pakiet '{}'.",
        "success_uninstall_status": "Sukces: Odinstalowano pakiet '{}'.",
        "error_title": "Błąd instalacji",
        "error_msg": "Nie udało się zainstalować {}.\nBłąd:\n{}",
        "error_upgrade_msg": "Nie udało się zaktualizować {}.\nBłąd:\n{}",
        "error_uninstall_msg": "Nie udało się odinstalować {}.\nBłąd:\n{}",
        "error_status": "Błąd instalacji pakietu {}.",
        "error_upgrade_status": "Błąd aktualizacji pakietu {}.",
        "error_uninstall_status": "Błąd odinstalowywania pakietu {}.",
        "scan_error_title": "Błąd",
        "scan_error_msg": "Nie udało się zeskanować pakietów: {}",
        "search_label": "Szukaj:",
        "search_placeholder": "Szukaj pakietów...",
        "python_exec_label": "Interpreter Pythona:",
        "choose_interpreter_btn": "Zmień interpreter",
        "choose_interpreter_title": "Wybierz interpreter Pythona",
        "python_executable_filter": "Plik wykonywalny Pythona|python.exe|Wszystkie pliki|*.*",
        "update_btn": "Aktualizuj",
        "uninstall_btn": "Odinstaluj",
        "no_search_results": "Brak pakietów pasujących do wyszukiwania.",
        "btn_refresh": "Odśwież",
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
        "graphics3d_cat": "Grafika i Modele 3D",
        "refresh_btn": "Odśwież",
        "btn_debug_show": "Pokaż Logi",
        "btn_debug_hide": "Ukryj Logi",
        "debug_header": "--- Konsola diagnostyczna (Debug) ---",
        "about_title": "O programie",
        "about_author": "Autor",
        "about_company": "Firma",
        "about_email": "E-mail",
        "about_github": "GitHub",
        "about_close": "Zamknij"
    }
}


# Odwzorowanie kluczy kategorii na ich przetłumaczone klucze ze słownika językowego
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

if wx is not None:
    # Kolory interfejsu (Modern Palette)
    COLOR_PRIMARY = wx.Colour(41, 128, 185)       # Elegancki niebieski
    COLOR_BG_LIGHT = wx.Colour(248, 249, 250)     # Bardzo jasny szary do tła paneli
    COLOR_BG_WHITE = wx.Colour(255, 255, 255)     # Czysta biel dla list i kart
    COLOR_TEXT_MAIN = wx.Colour(44, 62, 80)       # Ciemny grafit do tekstu
    COLOR_SUCCESS = wx.Colour(39, 174, 96)        # Przyjazna zieleń
    COLOR_TERMINAL_BG = wx.Colour(30, 30, 30)     # Ciemne tło konsoli
    COLOR_TERMINAL_FG = wx.Colour(240, 240, 240)  # Jasny tekst konsoli

    # Własne zdarzenia do bezpiecznej komunikacji między wątkami a wxPython
    EVT_STATUS_TYPE = wx.NewEventType()
    EVT_STATUS = wx.PyEventBinder(EVT_STATUS_TYPE, 1)
    EVT_SUCCESS_TYPE = wx.NewEventType()
    EVT_SUCCESS = wx.PyEventBinder(EVT_SUCCESS_TYPE, 1)
    EVT_ERROR_TYPE = wx.NewEventType()
    EVT_ERROR = wx.PyEventBinder(EVT_ERROR_TYPE, 1)
    EVT_DEBUG_TYPE = wx.NewEventType()
    EVT_DEBUG = wx.PyEventBinder(EVT_DEBUG_TYPE, 1)

    class StatusEvent(wx.PyEvent):
        def __init__(self, data):
            super().__init__()
            self.SetEventType(EVT_STATUS_TYPE)
            self.data = data

    class SuccessEvent(wx.PyEvent):
        def __init__(self, package_name, row_pane, action="install"):
            super().__init__()
            self.SetEventType(EVT_SUCCESS_TYPE)
            self.package_name = package_name
            self.row_pane = row_pane
            self.action = action

    class ErrorEvent(wx.PyEvent):
        def __init__(self, package_name, row_pane, error_msg, action="install"):
            super().__init__()
            self.SetEventType(EVT_ERROR_TYPE)
            self.package_name = package_name
            self.row_pane = row_pane
            self.error_msg = error_msg
            self.action = action

    class DebugEvent(wx.PyEvent):
        def __init__(self, text):
            super().__init__()
            self.SetEventType(EVT_DEBUG_TYPE)
            self.text = text

    class PackageRow(wx.Panel):
        """Pojedynczy wiersz reprezentujący pakiet."""
        def __init__(self, parent, package_name, is_installed, install_callback, current_lang, installed_version=""):
            super().__init__(parent, style=wx.BORDER_SIMPLE)
            self.package_name = package_name
            self.install_callback = install_callback
            self.current_lang = current_lang
            self.is_installed = is_installed
            self.installed_version = installed_version or ""

            self.SetBackgroundColour(COLOR_BG_WHITE)
            self.sizer = wx.BoxSizer(wx.HORIZONTAL)

            # Nazwa pakietu
            self.lbl_name = wx.StaticText(self, label=package_name)
            font = self.lbl_name.GetFont()
            font.SetPointSize(10)
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            self.lbl_name.SetFont(font)
            self.lbl_name.SetForegroundColour(COLOR_TEXT_MAIN)
            self.sizer.Add(self.lbl_name, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

            self.lbl_status = None
            self.btn_install = None
            self.btn_update = None
            self.btn_uninstall = None

            if self.is_installed:
                self.show_installed_label()
            else:
                self.show_install_button()

            self.SetSizer(self.sizer)

        def on_install_click(self, event):
            self.btn_install.Disable()
            self.btn_install.SetLabel(LANGUAGES[self.current_lang]["installing"])
            self.install_callback(self.package_name, self, action="install")

        def on_update_click(self, event):
            if self.btn_update:
                self.btn_update.Disable()
                self.btn_uninstall.Disable()
            self.install_callback(self.package_name, self, action="upgrade")

        def on_uninstall_click(self, event):
            if self.btn_uninstall:
                self.btn_uninstall.Disable()
                if self.btn_update:
                    self.btn_update.Disable()
            self.install_callback(self.package_name, self, action="uninstall")

        def show_installed_label(self):
            if self.btn_install:
                self.btn_install.Destroy()
                self.btn_install = None
            if self.btn_update:
                self.btn_update.Destroy()
                self.btn_update = None
            if self.btn_uninstall:
                self.btn_uninstall.Destroy()
                self.btn_uninstall = None
                
            label_text = f"✓ {LANGUAGES[self.current_lang]['installed']}"
            if self.installed_version:
                label_text += f" ({self.installed_version})"

            self.lbl_status = wx.StaticText(self, label=label_text)
            font = self.lbl_status.GetFont()
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            self.lbl_status.SetFont(font)
            self.lbl_status.SetForegroundColour(COLOR_SUCCESS)
            
            # Subtelna zmiana tła całej karty na jasnozielony
            self.SetBackgroundColour(wx.Colour(235, 247, 235))
            
            self.sizer.Add(self.lbl_status, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

            self.btn_update = wx.Button(self, label=LANGUAGES[self.current_lang]["update_btn"], size=(90, -1))
            self.btn_update.SetBackgroundColour(wx.Colour(41, 128, 185))
            self.btn_update.SetForegroundColour(wx.WHITE)
            self.btn_update.Bind(wx.EVT_BUTTON, self.on_update_click)
            self.sizer.Add(self.btn_update, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

            self.btn_uninstall = wx.Button(self, label=LANGUAGES[self.current_lang]["uninstall_btn"], size=(90, -1))
            self.btn_uninstall.SetBackgroundColour(wx.Colour(192, 57, 43))
            self.btn_uninstall.SetForegroundColour(wx.WHITE)
            self.btn_uninstall.Bind(wx.EVT_BUTTON, self.on_uninstall_click)
            self.sizer.Add(self.btn_uninstall, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

            self.Layout()
            self.Refresh()

        def show_install_button(self):
            if self.lbl_status:
                self.lbl_status.Destroy()
                self.lbl_status = None
            if self.btn_update:
                self.btn_update.Destroy()
                self.btn_update = None
            if self.btn_uninstall:
                self.btn_uninstall.Destroy()
                self.btn_uninstall = None

            self.btn_install = wx.Button(self, label=LANGUAGES[self.current_lang]["install_btn"], size=(100, -1))
            self.btn_install.SetBackgroundColour(COLOR_PRIMARY)
            self.btn_install.SetForegroundColour(wx.WHITE)
            self.btn_install.Bind(wx.EVT_BUTTON, self.on_install_click)
            
            self.sizer.Add(self.btn_install, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
            self.Layout()
            self.Refresh()

        def reset_button(self):
            if self.btn_install:
                self.btn_install.Enable()
                self.btn_install.SetLabel(LANGUAGES[self.current_lang]["install_btn"])
            if self.btn_update:
                self.btn_update.Enable()
                self.btn_update.SetLabel(LANGUAGES[self.current_lang]["update_btn"])
            if self.btn_uninstall:
                self.btn_uninstall.Enable()
                self.btn_uninstall.SetLabel(LANGUAGES[self.current_lang]["uninstall_btn"])
            if self.is_installed and not self.lbl_status:
                self.show_installed_label()
            elif not self.is_installed and not self.btn_install:
                self.show_install_button()

        def update_language(self, new_lang):
            self.current_lang = new_lang
            if self.lbl_status:
                label_text = f"✓ {LANGUAGES[new_lang]['installed']}"
                if self.installed_version:
                    label_text += f" ({self.installed_version})"
                self.lbl_status.SetLabel(label_text)
            if self.btn_install:
                if not self.btn_install.IsEnabled():
                    self.btn_install.SetLabel(LANGUAGES[new_lang]["installing"])
                else:
                    self.btn_install.SetLabel(LANGUAGES[new_lang]["install_btn"])
            if self.btn_update:
                self.btn_update.SetLabel(LANGUAGES[new_lang]["update_btn"])
            if self.btn_uninstall:
                self.btn_uninstall.SetLabel(LANGUAGES[new_lang]["uninstall_btn"])
            self.Layout()


    class InstallerFrame(wx.Frame):
        def __init__(self):
            # DOSTOSOWANE: Angielski ustawiony jako domyślny język standardowy ("EN")
            self.current_lang = "EN"
            self.debug_visible = False  # Log debugowania domyślnie schowany
            self.python_executable = sys.executable
            self.search_filter = ""
            self.current_category = None

            # Zoptymalizowany rozmiar okna głównego
            super().__init__(parent=None, title=LANGUAGES[self.current_lang]["title"], size=(880, 680))
            self.SetMinSize((800, 580))
            self.SetBackgroundColour(COLOR_BG_LIGHT)

            icon_path = resource_path("ppm.ico")
            if os.path.exists(icon_path):
                icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
                self.SetIcon(icon)
            else:
                icon_path = resource_path("ppm-ico.png")
                if os.path.exists(icon_path):
                    icon = wx.Icon(icon_path, wx.BITMAP_TYPE_PNG)
                    self.SetIcon(icon)

            # Skanowanie środowiska
            self.zainstalowane_pakiety = self.pobierz_zainstalowane_pakiety()

            # Powiązanie zdarzeń wątkowych
            self.Bind(EVT_STATUS, self.on_status_update)
            self.Bind(EVT_SUCCESS, self.on_install_success)
            self.Bind(EVT_ERROR, self.on_install_error)
            self.Bind(EVT_DEBUG, self.on_debug_write)

            self.init_ui()
            self.log_debug("Program started. Environment loaded successfully." if self.current_lang == "EN" else "Uruchomiono program. Wczytano pakiety systemowe.")
            self.Centre()

        def init_ui(self):
            self.panel = wx.Panel(self)
            self.panel.SetBackgroundColour(COLOR_BG_LIGHT)
            self.main_sizer = wx.BoxSizer(wx.VERTICAL)

            # Górny panel (Nagłówek + Przyciski EN/PL oraz Debug)
            top_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)

            self.header = wx.StaticText(self.panel, label=LANGUAGES[self.current_lang]["header"])
            font = self.header.GetFont()
            font.SetPointSize(16)
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            self.header.SetFont(font)
            self.header.SetForegroundColour(COLOR_TEXT_MAIN)
            top_bar_sizer.Add(self.header, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)

            # Przycisk przełączania logów
            self.btn_refresh = wx.Button(self.panel, label=LANGUAGES[self.current_lang]["refresh_btn"], size=(110, 32))
            self.btn_refresh.SetBackgroundColour(wx.Colour(52, 152, 219))
            self.btn_refresh.SetForegroundColour(wx.WHITE)
            self.btn_refresh.Bind(wx.EVT_BUTTON, self.refresh_installed_packages)
            top_bar_sizer.Add(self.btn_refresh, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

            self.btn_toggle_debug = wx.Button(self.panel, label=LANGUAGES[self.current_lang]["btn_debug_show"], size=(130, 32))
            self.btn_toggle_debug.SetBackgroundColour(wx.Colour(127, 140, 141))
            self.btn_toggle_debug.SetForegroundColour(wx.WHITE)
            self.btn_toggle_debug.Bind(wx.EVT_BUTTON, self.toggle_debug_panel)
            top_bar_sizer.Add(self.btn_toggle_debug, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

            # Przycisk języka
            self.btn_lang = wx.Button(self.panel, label="EN / PL", size=(85, 32))
            self.btn_lang.SetBackgroundColour(COLOR_PRIMARY)
            self.btn_lang.SetForegroundColour(wx.WHITE)
            self.btn_lang.Bind(wx.EVT_BUTTON, self.toggle_language)
            top_bar_sizer.Add(self.btn_lang, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

            # Przycisk About (ikona, bez etykiety)
            about_bitmap = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_TOOLBAR, (22, 22))
            self.btn_about = wx.BitmapButton(self.panel, bitmap=about_bitmap, size=(36, 32))
            self.btn_about.SetToolTip(LANGUAGES[self.current_lang]["about_title"])
            self.btn_about.Bind(wx.EVT_BUTTON, self.show_about_dialog)
            top_bar_sizer.Add(self.btn_about, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

            self.main_sizer.Add(top_bar_sizer, 0, wx.EXPAND)

            search_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.lbl_search = wx.StaticText(self.panel, label=LANGUAGES[self.current_lang]["search_label"])
            search_bar_sizer.Add(self.lbl_search, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 8)

            self.search_ctrl = wx.SearchCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
            self.search_ctrl.ShowSearchButton(True)
            self.search_ctrl.ShowCancelButton(True)
            self.search_ctrl.SetDescriptiveText(LANGUAGES[self.current_lang]["search_placeholder"])
            self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search_text)
            self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_search_clear)
            self.search_ctrl.SetMinSize((240, -1))
            search_bar_sizer.Add(self.search_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)

            self.lbl_interpreter = wx.StaticText(self.panel, label=LANGUAGES[self.current_lang]["python_exec_label"])
            search_bar_sizer.Add(self.lbl_interpreter, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

            self.txt_interpreter = wx.TextCtrl(self.panel, value=self.python_executable, style=wx.TE_READONLY)
            self.txt_interpreter.SetMinSize((260, -1))
            search_bar_sizer.Add(self.txt_interpreter, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

            self.btn_choose_python = wx.Button(self.panel, label=LANGUAGES[self.current_lang]["choose_interpreter_btn"], size=(140, 32))
            self.btn_choose_python.Bind(wx.EVT_BUTTON, self.choose_python_executable)
            search_bar_sizer.Add(self.btn_choose_python, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

            self.main_sizer.Add(search_bar_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

            # Splitter główny (Kategorie / Pakiety)
            splitter = wx.SplitterWindow(self.panel, style=wx.SP_LIVE_UPDATE | wx.SP_3D)
            self.main_sizer.Add(splitter, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

            # --- LEWA KOLUMNA: Kategorie ---
            left_panel = wx.Panel(splitter)
            left_panel.SetBackgroundColour(COLOR_BG_LIGHT)
            left_sizer = wx.BoxSizer(wx.VERTICAL)

            self.lbl_cat = wx.StaticText(left_panel, label=LANGUAGES[self.current_lang]["categories"])
            font_sub = self.lbl_cat.GetFont()
            font_sub.SetPointSize(11)
            font_sub.SetWeight(wx.FONTWEIGHT_BOLD)
            self.lbl_cat.SetFont(font_sub)
            self.lbl_cat.SetForegroundColour(COLOR_TEXT_MAIN)
            left_sizer.Add(self.lbl_cat, 0, wx.ALL, 8)

            # Stylowa lista kategorii
            self.category_list = wx.ListBox(left_panel, style=wx.LB_SINGLE)
            self.category_list.SetBackgroundColour(COLOR_BG_WHITE)
            self.category_list.SetForegroundColour(COLOR_TEXT_MAIN)
            font_list = self.category_list.GetFont()
            font_list.SetPointSize(10)
            self.category_list.SetFont(font_list)

            self.update_category_listbox()
            self.category_list.Bind(wx.EVT_LISTBOX, self.on_category_select)
            left_sizer.Add(self.category_list, 1, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)
            left_panel.SetSizer(left_sizer)

            # --- PRAWA KOLUMNA: Biblioteki ---
            self.right_panel = wx.Panel(splitter)
            self.right_panel.SetBackgroundColour(COLOR_BG_LIGHT)
            self.right_sizer = wx.BoxSizer(wx.VERTICAL)

            self.lbl_right_header = wx.StaticText(self.right_panel, label=LANGUAGES[self.current_lang]["select_category"])
            self.lbl_right_header.SetFont(font_sub)
            self.lbl_right_header.SetForegroundColour(COLOR_TEXT_MAIN)
            self.right_sizer.Add(self.lbl_right_header, 0, wx.ALL, 8)

            # Przewijana lista z pakietami
            self.scroll_window = wx.ScrolledWindow(self.right_panel, style=wx.VSCROLL)
            self.scroll_window.SetBackgroundColour(COLOR_BG_LIGHT)
            self.scroll_window.SetScrollRate(0, 10)
            self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
            self.scroll_window.SetSizer(self.scroll_sizer)

            self.right_sizer.Add(self.scroll_window, 1, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)
            self.right_panel.SetSizer(self.right_sizer)

            # Zoptymalizowany podział (Lewy panel: 260px, reszta dla prawego)
            splitter.SplitVertically(left_panel, self.right_panel, 260)

            # --- SEKCOJA DEBUGOWANIA ---
            self.debug_container = wx.Panel(self.panel)
            self.debug_container.SetBackgroundColour(COLOR_BG_LIGHT)
            self.debug_sizer = wx.BoxSizer(wx.VERTICAL)

            self.lbl_debug = wx.StaticText(self.debug_container, label=LANGUAGES[self.current_lang]["debug_header"])
            self.lbl_debug.SetFont(font_sub)
            self.lbl_debug.SetForegroundColour(COLOR_TEXT_MAIN)
            self.debug_sizer.Add(self.lbl_debug, 0, wx.TOP | wx.BOTTOM, 8)

            # Terminal
            self.txt_debug_log = wx.TextCtrl(
                self.debug_container,
                style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
            )
            self.txt_debug_log.SetBackgroundColour(COLOR_TERMINAL_BG)
            self.txt_debug_log.SetForegroundColour(COLOR_TERMINAL_FG)
            font_mono = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            self.txt_debug_log.SetFont(font_mono)
            self.txt_debug_log.SetMinSize((-1, 140))
            self.debug_sizer.Add(self.txt_debug_log, 1, wx.EXPAND | wx.BOTTOM, 5)
            self.debug_container.SetSizer(self.debug_sizer)

            # Domyślnie chowany panel logów
            self.debug_container.Show(False)
            self.main_sizer.Add(self.debug_container, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

            # Progress bar
            self.progress_bar = wx.Gauge(self.panel, range=100, style=wx.GA_HORIZONTAL, size=(-1, 6))
            self.progress_bar.SetBackgroundColour(COLOR_BG_LIGHT)
            self.main_sizer.Add(self.progress_bar, 0, wx.EXPAND | wx.ALL, 15)

            self.panel.SetSizer(self.main_sizer)

            # Status bar
            self.status_bar = self.CreateStatusBar()
            self.status_bar.SetStatusText(LANGUAGES[self.current_lang]["status_ready"])

            if BIBLIOTEKI:
                self.category_list.SetSelection(0)
                self.display_category_packages(list(BIBLIOTEKI.keys())[0])

        def log_debug(self, msg):
            """Dodaje bezpieczną wiadomość do okna debugowania."""
            wx.PostEvent(self, DebugEvent(msg))

        def on_search_text(self, event):
            self.search_filter = event.GetString().strip()
            if self.current_category is not None:
                self.display_category_packages(self.current_category)

        def on_search_clear(self, event):
            self.search_filter = ""
            self.search_ctrl.SetValue("")
            if self.current_category is not None:
                self.display_category_packages(self.current_category)

        def choose_python_executable(self, event):
            wildcard = LANGUAGES[self.current_lang]["python_executable_filter"]
            dlg = wx.FileDialog(
                self,
                LANGUAGES[self.current_lang]["choose_interpreter_title"],
                wildcard=wildcard,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            )
            if dlg.ShowModal() == wx.ID_OK:
                chosen_path = dlg.GetPath()
                self.python_executable = chosen_path
                self.txt_interpreter.SetValue(chosen_path)
                self.log_debug(f"[SYSTEM] Python interpreter switched to: {chosen_path}")
                self.refresh_installed_packages()
            dlg.Destroy()

        def on_debug_write(self, event):
            self.txt_debug_log.AppendText(event.text + "\n")

        def toggle_debug_panel(self, event):
            self.debug_visible = not self.debug_visible
            self.debug_container.Show(self.debug_visible)

            btn_label_key = "btn_debug_hide" if self.debug_visible else "btn_debug_show"
            self.btn_toggle_debug.SetLabel(LANGUAGES[self.current_lang][btn_label_key])

            self.panel.Layout()

        def show_about_dialog(self, event):
            about_text = wx.Dialog(self, title=LANGUAGES[self.current_lang]["about_title"], size=(360, 220))
            about_text.SetBackgroundColour(COLOR_BG_WHITE)

            main_sizer = wx.BoxSizer(wx.VERTICAL)
            title = wx.StaticText(about_text, label="polsoft.ITS™ Group")
            title_font = title.GetFont()
            title_font.SetPointSize(11)
            title_font.SetWeight(wx.FONTWEIGHT_BOLD)
            title.SetFont(title_font)
            title.SetForegroundColour(COLOR_TEXT_MAIN)
            main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 8)

            content_sizer = wx.BoxSizer(wx.HORIZONTAL)
            info_sizer = wx.BoxSizer(wx.VERTICAL)
            info_sizer.Add(wx.StaticText(about_text, label=f"{LANGUAGES[self.current_lang]['about_author']}: Sebastian Januchowski"), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
            info_sizer.Add(wx.StaticText(about_text, label=f"{LANGUAGES[self.current_lang]['about_company']}: polsoft.ITS™ Group"), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

            if HyperlinkCtrl is not None:
                email_link = HyperlinkCtrl(
                    about_text,
                    id=wx.ID_ANY,
                    label="polsoft.its@mail.com",
                    url="mailto:polsoft.its@mail.com"
                )
                github_link = HyperlinkCtrl(
                    about_text,
                    id=wx.ID_ANY,
                    label="https://github.com/polsoft-IT",
                    url="https://github.com/polsoft-IT"
                )
            else:
                email_link = wx.StaticText(about_text, label="polsoft.its@mail.com")
                email_link.SetForegroundColour(wx.BLUE)
                email_link.SetCursor(wx.Cursor(wx.CURSOR_HAND))
                email_link.Bind(wx.EVT_LEFT_DOWN, lambda event: webbrowser.open("mailto:polsoft.its@mail.com"))

                github_link = wx.StaticText(about_text, label="https://github.com/polsoft-IT")
                github_link.SetForegroundColour(wx.BLUE)
                github_link.SetCursor(wx.Cursor(wx.CURSOR_HAND))
                github_link.Bind(wx.EVT_LEFT_DOWN, lambda event: webbrowser.open("https://github.com/polsoft-IT"))

            info_sizer.Add(email_link, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
            info_sizer.Add(github_link, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

            icon_file = resource_path("ppm-ico.png")
            if os.path.exists(icon_file):
                img = wx.Image(icon_file, wx.BITMAP_TYPE_PNG)
                img = img.Rescale(72, 72)
                icon_bitmap = img.ConvertToBitmap()
                icon_ctrl = wx.StaticBitmap(about_text, bitmap=icon_bitmap)
                content_sizer.Add(info_sizer, 1, wx.EXPAND | wx.ALL, 4)
                content_sizer.Add(icon_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
            else:
                content_sizer.Add(info_sizer, 1, wx.EXPAND | wx.ALL, 4)

            main_sizer.Add(content_sizer, 0, wx.EXPAND | wx.ALL, 4)

            close_btn = wx.Button(about_text, wx.ID_OK, label=LANGUAGES[self.current_lang]["about_close"])
            main_sizer.Add(close_btn, 0, wx.ALL | wx.ALIGN_CENTER, 6)

            about_text.SetSizer(main_sizer)
            about_text.Centre()
            about_text.ShowModal()
            about_text.Destroy()

        def update_category_listbox(self):
            current_selection = self.category_list.GetSelection()
            self.category_list.Clear()
            for raw_kat in BIBLIOTEKI.keys():
                translated_key = CATEGORY_MAP.get(raw_kat, raw_kat)
                translated_name = LANGUAGES[self.current_lang].get(translated_key, raw_kat)
                self.category_list.Append(translated_name)

            if current_selection != wx.NOT_FOUND:
                self.category_list.SetSelection(current_selection)

        def pobierz_zainstalowane_pakiety(self):
            try:
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                wynik = subprocess.run(
                    [self.python_executable, "-m", "pip", "list", "--format=json", "--disable-pip-version-check"],
                    capture_output=True,
                    text=True,
                    check=True,
                    startupinfo=startupinfo
                )
                dane = json.loads(wynik.stdout)
                pakiety = {pakiet["name"].lower(): pakiet.get("version", "") for pakiet in dane if pakiet.get("name")}
                return pakiety
            except Exception:
                try:
                    # Fallback dla środowisk, gdzie format JSON może nie być obsługiwany
                    startupinfo = None
                    if sys.platform == "win32":
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    wynik = subprocess.run(
                        [self.python_executable, "-m", "pip", "freeze", "--disable-pip-version-check"],
                        capture_output=True,
                        text=True,
                        check=True,
                        startupinfo=startupinfo
                    )
                    pakiety = parse_pip_freeze_output(wynik.stdout)
                    return pakiety
                except Exception as exc:
                    try:
                        # Ostateczny fallback bez użycia pip
                        import importlib.metadata as importlib_metadata
                        pakiety = {dist.metadata["Name"].lower(): dist.version for dist in importlib_metadata.distributions() if dist.metadata and dist.metadata.get("Name")}
                        return pakiety
                    except Exception:
                        wx.MessageBox(
                            LANGUAGES[self.current_lang]["scan_error_msg"].format(exc),
                            LANGUAGES[self.current_lang]["scan_error_title"],
                            wx.OK | wx.ICON_ERROR
                        )
                        return {}

        def refresh_installed_packages(self, event=None):
            self.status_bar.SetStatusText(LANGUAGES[self.current_lang]["refresh_btn"] + "...")
            self.log_debug("[SYSTEM] Refreshing installed package database.")
            self.zainstalowane_pakiety = self.pobierz_zainstalowane_pakiety()
            selection_idx = self.category_list.GetSelection()
            if selection_idx != wx.NOT_FOUND:
                raw_category_name = list(BIBLIOTEKI.keys())[selection_idx]
                self.display_category_packages(raw_category_name)
            self.status_bar.SetStatusText(LANGUAGES[self.current_lang]["status_ready"])
            self.log_debug("[SYSTEM] Installed package database refreshed.")

        def on_category_select(self, event):
            selection_idx = self.category_list.GetSelection()
            if selection_idx != wx.NOT_FOUND:
                raw_category_name = list(BIBLIOTEKI.keys())[selection_idx]
                self.display_category_packages(raw_category_name)

        def display_category_packages(self, raw_category_name):
            self.current_category = raw_category_name
            translated_key = CATEGORY_MAP.get(raw_category_name, raw_category_name)
            translated_name = LANGUAGES[self.current_lang].get(translated_key, raw_category_name)

            self.lbl_right_header.SetLabel(f"{LANGUAGES[self.current_lang]['libs_in']}{translated_name}")
            # Clear existing items
            for child in self.scroll_window.GetChildren():
                child.Destroy()
            self.scroll_sizer.Clear(True)

            pakiety = BIBLIOTEKI.get(raw_category_name, [])
            search_filter = self.search_filter.lower() if self.search_filter else None
            for pkg in pakiety:
                if search_filter and search_filter not in pkg.lower():
                    continue
                pkg_key = pkg.lower()
                installed_version = self.zainstalowane_pakiety.get(pkg_key, "")
                is_installed = bool(installed_version)
                row = PackageRow(
                    self.scroll_window,
                    pkg,
                    is_installed,
                    self.start_installation,
                    self.current_lang,
                    installed_version=installed_version
                )
                self.scroll_sizer.Add(row, 0, wx.EXPAND | wx.BOTTOM, 6)

            if search_filter and self.scroll_sizer.GetItemCount() == 0:
                no_results = wx.StaticText(self.scroll_window, label=LANGUAGES[self.current_lang]["no_search_results"])
                no_results.SetForegroundColour(COLOR_TEXT_MAIN)
                self.scroll_sizer.Add(no_results, 0, wx.ALL, 10)

            self.scroll_window.Layout()
            self.scroll_sizer.FitInside(self.scroll_window)
            self.right_panel.Layout()

        def toggle_language(self, event):
            self.current_lang = "PL" if self.current_lang == "EN" else "EN"

            self.SetTitle(LANGUAGES[self.current_lang]["title"])
            self.header.SetLabel(LANGUAGES[self.current_lang]["header"])
            self.lbl_cat.SetLabel(LANGUAGES[self.current_lang]["categories"])
            self.lbl_debug.SetLabel(LANGUAGES[self.current_lang]["debug_header"])

            # Aktualizacja etykiety przycisku debugowania
            btn_label_key = "btn_debug_hide" if self.debug_visible else "btn_debug_show"
            self.btn_refresh.SetLabel(LANGUAGES[self.current_lang]["refresh_btn"])
            self.btn_toggle_debug.SetLabel(LANGUAGES[self.current_lang][btn_label_key])
            self.btn_about.SetToolTip(LANGUAGES[self.current_lang]["about_title"])

            self.update_category_listbox()

            selection_idx = self.category_list.GetSelection()
            if selection_idx != wx.NOT_FOUND:
                raw_category_name = list(BIBLIOTEKI.keys())[selection_idx]
                translated_key = CATEGORY_MAP.get(raw_category_name, raw_category_name)
                translated_name = LANGUAGES[self.current_lang].get(translated_key, raw_category_name)
                self.lbl_right_header.SetLabel(f"{LANGUAGES[self.current_lang]['libs_in']}{translated_name}")
            else:
                self.lbl_right_header.SetLabel(LANGUAGES[self.current_lang]["select_category"])

            for child in self.scroll_window.GetChildren():
                if isinstance(child, PackageRow):
                    child.update_language(self.current_lang)

            current_status = self.status_bar.GetStatusText()
            if current_status in [LANGUAGES["EN"]["status_ready"], LANGUAGES["PL"]["status_ready"]]:
                self.status_bar.SetStatusText(LANGUAGES[self.current_lang]["status_ready"])

            self.panel.Layout()

        def start_installation(self, package_name, row_pane, action="install"):
            self.progress_bar.Pulse()
            if action == "upgrade":
                self.status_bar.SetStatusText(LANGUAGES[self.current_lang]["preparing_upgrade"].format(package_name))
            elif action == "uninstall":
                self.status_bar.SetStatusText(LANGUAGES[self.current_lang]["preparing_uninstall"].format(package_name))
            else:
                self.status_bar.SetStatusText(LANGUAGES[self.current_lang]["preparing"].format(package_name))

            if self.current_lang == "EN":
                if action == "upgrade":
                    log_msg = f"[SYSTEM] Starting upgrade for package: {package_name}"
                elif action == "uninstall":
                    log_msg = f"[SYSTEM] Starting uninstall for package: {package_name}"
                else:
                    log_msg = f"[SYSTEM] Starting installation for package: {package_name}"
            else:
                if action == "upgrade":
                    log_msg = f"[SYSTEM] Rozpoczynanie procesu aktualizacji pakietu: {package_name}"
                elif action == "uninstall":
                    log_msg = f"[SYSTEM] Rozpoczynanie procesu odinstalowywania pakietu: {package_name}"
                else:
                    log_msg = f"[SYSTEM] Rozpoczynanie procesu instalacji pakietu: {package_name}"
            self.log_debug(log_msg)

            thread = threading.Thread(
                target=self._watek_instalacji,
                args=(package_name, row_pane, action),
                daemon=True
            )
            thread.start()

        def _watek_instalacji(self, package_name, row_pane, action="install"):
            try:
                startupinfo = None
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                if action == "upgrade":
                    cmd = [self.python_executable, "-m", "pip", "install", "--upgrade", package_name, "--disable-pip-version-check"]
                elif action == "uninstall":
                    cmd = [self.python_executable, "-m", "pip", "uninstall", "-y", package_name, "--disable-pip-version-check"]
                else:
                    cmd = [self.python_executable, "-m", "pip", "install", package_name, "--disable-pip-version-check"]

                proces = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    startupinfo=startupinfo
                )

                output_lines = []
                status_update_counter = 0
                while True:
                    linia = proces.stdout.readline()
                    if not linia and proces.poll() is not None:
                        break
                    if linia:
                        czysta_linia = linia.strip()
                        if czysta_linia:
                            output_lines.append(czysta_linia)
                            if status_update_counter % 8 == 0:
                                self.log_debug(f"[{package_name}] {czysta_linia}")
                                wx.PostEvent(self, StatusEvent(f"[{package_name}] {czysta_linia[:70]}..."))
                            status_update_counter += 1

                proces.wait()
                pelny_output = "\n".join(output_lines).strip()

                if proces.returncode == 0:
                    wx.PostEvent(self, SuccessEvent(package_name, row_pane, action=action))
                else:
                    blad = pelny_output or "Unknown installation error."
                    err_prefix = "[SYSTEM ERROR] " if self.current_lang == "EN" else "[BŁĄD SYSTEMU] "
                    self.log_debug(f"{err_prefix}{blad}")
                    wx.PostEvent(self, ErrorEvent(package_name, row_pane, blad, action=action))

            except Exception as e:
                err_prefix = "[CRITICAL EXCEPTION] " if self.current_lang == "EN" else "[WYJĄTEK CRITICAL] "
                self.log_debug(f"{err_prefix}{str(e)}")
                wx.PostEvent(self, ErrorEvent(package_name, row_pane, str(e)))

        # --- OBSŁUGA ZDARZEŃ WĄTKOWYCH ---

        def on_status_update(self, event):
            self.status_bar.SetStatusText(event.data)

        def on_install_success(self, event):
            self.progress_bar.SetValue(100)

            if event.action == "uninstall":
                self.zainstalowane_pakiety.pop(event.package_name.lower(), None)
                event.row_pane.is_installed = False
                event.row_pane.installed_version = ""
                event.row_pane.show_install_button()
                status_text = LANGUAGES[self.current_lang]["success_uninstall_status"].format(event.package_name)
                message = LANGUAGES[self.current_lang]["success_uninstall_msg"].format(event.package_name)
                log_msg = f"[SYSTEM] Package '{event.package_name}' was successfully uninstalled." if self.current_lang == "EN" else f"[SYSTEM] Pakiet '{event.package_name}' został pomyślnie odinstalowany."
            else:
                self.zainstalowane_pakiety = self.pobierz_zainstalowane_pakiety()
                pkg_key = event.package_name.lower()
                event.row_pane.installed_version = self.zainstalowane_pakiety.get(pkg_key, "")
                event.row_pane.is_installed = True
                event.row_pane.show_installed_label()
                if event.action == "upgrade":
                    status_text = LANGUAGES[self.current_lang]["success_upgrade_status"].format(event.package_name)
                    message = LANGUAGES[self.current_lang]["success_upgrade_msg"].format(event.package_name)
                    log_msg = f"[SYSTEM] Package '{event.package_name}' was successfully upgraded." if self.current_lang == "EN" else f"[SYSTEM] Pakiet '{event.package_name}' został pomyślnie zaktualizowany."
                else:
                    status_text = LANGUAGES[self.current_lang]["success_status"].format(event.package_name)
                    message = LANGUAGES[self.current_lang]["success_msg"].format(event.package_name)
                    log_msg = f"[SYSTEM] Success: Package '{event.package_name}' has been successfully installed." if self.current_lang == "EN" else f"[SYSTEM] Sukces: Pakiet '{event.package_name}' został pomyślnie zainstalowany."

            self.status_bar.SetStatusText(status_text)
            self.log_debug(log_msg)
            wx.MessageBox(
                message,
                LANGUAGES[self.current_lang]["success_title"],
                wx.OK | wx.ICON_INFORMATION
            )
            self.progress_bar.SetValue(0)

        def on_install_error(self, event):
            self.progress_bar.SetValue(0)
            event.row_pane.reset_button()

            if event.action == "upgrade":
                status_text = LANGUAGES[self.current_lang]["error_upgrade_status"].format(event.package_name)
                error_message = LANGUAGES[self.current_lang]["error_upgrade_msg"].format(event.package_name, event.error_msg)
                log_msg = f"[SYSTEM] Error upgrading package '{event.package_name}'." if self.current_lang == "EN" else f"[SYSTEM] Błąd aktualizacji pakietu '{event.package_name}'."
            elif event.action == "uninstall":
                status_text = LANGUAGES[self.current_lang]["error_uninstall_status"].format(event.package_name)
                error_message = LANGUAGES[self.current_lang]["error_uninstall_msg"].format(event.package_name, event.error_msg)
                log_msg = f"[SYSTEM] Error uninstalling package '{event.package_name}'." if self.current_lang == "EN" else f"[SYSTEM] Błąd odinstalowywania pakietu '{event.package_name}'."
            else:
                status_text = LANGUAGES[self.current_lang]["error_status"].format(event.package_name)
                error_message = LANGUAGES[self.current_lang]["error_msg"].format(event.package_name, event.error_msg)
                log_msg = f"[SYSTEM] Error installing package '{event.package_name}'." if self.current_lang == "EN" else f"[SYSTEM] Błąd instalacji pakietu '{event.package_name}'."

            self.status_bar.SetStatusText(status_text)
            self.log_debug(log_msg)
            wx.MessageBox(
                error_message,
                LANGUAGES[self.current_lang]["error_title"],
                wx.OK | wx.ICON_ERROR
            )


def _cli_list_categories():
    for kat in BIBLIOTEKI.keys():
        print(kat)
        logger.debug("Listed category: %s", kat)


def _cli_list_packages(category=None):
    if category is None:
        for kat, pakiety in BIBLIOTEKI.items():
            print(f"{kat}:")
            for p in pakiety:
                print(f"  - {p}")
            print()
    else:
        # Accept raw category keys or translated category names (PL/EN), case-insensitive
        raw_category = None
        cat_lower = category.lower()
        # direct match
        for raw_k in BIBLIOTEKI.keys():
            if raw_k.lower() == cat_lower:
                raw_category = raw_k
                break
        # translated name match (search both EN and PL)
        if raw_category is None:
            for raw_k in BIBLIOTEKI.keys():
                translated_key = CATEGORY_MAP.get(raw_k, raw_k)
                for lang in LANGUAGES.keys():
                    translated_name = LANGUAGES[lang].get(translated_key, "")
                    if translated_name and translated_name.lower() == cat_lower:
                        raw_category = raw_k
                        break
                if raw_category:
                    break

        pakiety = BIBLIOTEKI.get(raw_category)
        if not pakiety:
            print(f"Unknown category: {category}")
            return
        for p in pakiety:
            print(p)
            logger.debug("Listed package: %s (category=%s)", p, raw_category)


def _cli_scan_installed(python_exec=None):
    python_exec = python_exec or sys.executable
    try:
        proc = subprocess.run(
            [python_exec, "-m", "pip", "list", "--format=json", "--disable-pip-version-check"],
            capture_output=True, text=True, check=True
        )
        data = json.loads(proc.stdout)
        for pkg in data:
            print(f"{pkg.get('name')}: {pkg.get('version')}")
    except Exception:
        logger.exception("Failed to scan installed packages using pip.")
        print("Failed to scan installed packages using pip.")


def main(argv=None):
    import argparse
    # Configure basic logging only when running as program
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Python Package Manager - CLI fallback")
    parser.add_argument("--list-categories", action="store_true", help="List available categories")
    parser.add_argument("--list-packages", nargs="?", const="__ALL__", help="List packages (optionally by category)")
    parser.add_argument("--scan-installed", action="store_true", help="Scan and print installed packages")
    parser.add_argument("--gui", action="store_true", help="Force GUI mode (requires wxPython)")
    parser.add_argument("--no-gui", action="store_true", help="Force CLI mode even if wxPython is available")
    parser.add_argument("--version", action="store_true", help="Print program version and exit")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose (DEBUG) logging")
    args = parser.parse_args(argv)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    try:
        if args.version:
            try:
                with open(os.path.join(os.path.dirname(__file__), "version.txt"), "r", encoding="utf-8") as vf:
                    ver = vf.read().strip()
            except Exception:
                ver = "unknown"
            print(ver)
            return 0

        if args.list_categories:
            _cli_list_categories()
            return 0

        if args.list_packages is not None:
            if args.list_packages == "__ALL__":
                _cli_list_packages()
            else:
                _cli_list_packages(args.list_packages)
            return 0

        if args.scan_installed:
            _cli_scan_installed()
            return 0

        # Default behavior: if no CLI action requested, run GUI when available
        no_cli_flags = not (args.list_categories or (args.list_packages is not None) or args.scan_installed or args.verbose or args.gui or args.version)
        if no_cli_flags and HAS_WX and not args.no_gui:
            logger.debug("No CLI flags provided — launching GUI by default")
            app = wx.App(False)
            frame = InstallerFrame()
            frame.Show()
            app.MainLoop()
            return 0

        # If --gui explicitly requested, also launch GUI (even if other flags present we prioritize explicit GUI)
        if HAS_WX and args.gui:
            logger.debug("--gui provided — launching GUI")
            app = wx.App(False)
            frame = InstallerFrame()
            frame.Show()
            app.MainLoop()
            return 0

        # Otherwise fall back to CLI messages
        if not HAS_WX:
            print("wxPython is not available. Use --list-categories, --list-packages or --scan-installed for CLI mode.")
        return 0
    except Exception as exc:
        logger.exception("Unhandled exception in main")
        return 1


if __name__ == "__main__":
    sys.exit(main())