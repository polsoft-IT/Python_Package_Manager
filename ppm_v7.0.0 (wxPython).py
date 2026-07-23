"""
Python Package Manager - wxPython Version
A modern graphical package manager and installer for Python environments.
"""

import sys
import os
import subprocess
import threading
import wx
from typing import Dict, List, Optional, Callable, Any

# Program Metadata
METADATA = {
    "name": "Python Package Installer",
    "version": "5.0.0",
    "author": "Sebastian Januchowski",
    "company": "polsoft.ITS(TM) Group",
    "github": "https://github.com/polsoft-IT",
    "email": "polsoft.its@mail.com",
    "description": "A modern graphical package manager and installer for Python environments."
}

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
        "title": "Python Package Installer (wxPython Modern)",
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
        "choose_interpreter_btn": "Browse Path",
        "choose_interpreter_title": "Select Python Interpreter",
        "update_btn": "Upgrade",
        "uninstall_btn": "Uninstall",
        "no_search_results": "No packages match your search.",
        "btn_refresh": "Refresh",
        "refresh_btn": "Refresh",
        "btn_install_file": "Install from File",
        "btn_install_all": "Install All",
        "btn_uninstall_all": "Uninstall All",
        "btn_update_all": "Update All",
        "btn_debug_show": "Log's",
        "btn_debug_hide": "Hide",
        "btn_save_logs": "Save",
        "save_logs_success": "Logs saved successfully!",
        "save_logs_error": "Failed to save logs: {}",
        "about_title": "About",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "acknowledgements_title": "Acknowledgements",
        "acknowledgements_text": "Special thanks to Google and the global Python Community for providing open-source tools, developer resources, and rich ecosystems that made the development of this software possible.",
        "cat_names": {
            "compilers": "Compilers & Transpilers", "gui": "GUI (Graphical Interfaces)", "games": "Games & Multimedia",
            "data_science": "Data Science & Analysis", "scraping": "Web Scraping", "web_frameworks": "Web Development",
            "databases": "Database & ORM", "testing": "Testing & Quality Assurance", "image_video": "Image & Video Processing",
            "async": "Async & Concurrency", "security": "Security & Cryptography", "automation": "Automation & Scripting",
            "parsers": "Data Parsing", "cli": "CLI & Terminal", "ai_nlp": "AI & NLP", "documents": "Document Processing",
            "visualization": "Data Visualization", "logging": "Logging & Monitoring", "network": "Networking",
            "mocking": "Mocking & Testing", "cloud": "Cloud Services", "graphics_3d": "3D Graphics"
        }
    },
    "PL": {
        "title": "Instalator Pakietów Python (wxPython Modern)",
        "header": "Menedżer Pakietów Python",
        "categories": "Kategorie",
        "select_category": "Wybierz kategorię z menu po lewej stronie",
        "libs_in": "Biblioteki w: ",
        "installed": "Zainstalowany",
        "install_btn": "Zainstaluj",
        "installing": "Instalowanie...",
        "status_ready": "Gotowy",
        "preparing": "Przygotowywanie instalacji {}...",
        "preparing_upgrade": "Przygotowywanie aktualizacji {}...",
        "preparing_uninstall": "Przygotowywanie odinstalowania {}...",
        "success_title": "Sukces",
        "success_install_msg": "Pomyślnie zainstalowano {}!",
        "success_upgrade_msg": "Pomyślnie zaktualizowano {}!",
        "success_uninstall_msg": "Pomyślnie odinstalowano {}!",
        "success_install_status": "Sukces: Pakiet '{}' zainstalowany pomyślnie.",
        "success_upgrade_status": "Sukces: Pakiet '{}' zaktualizowany pomyślnie.",
        "success_uninstall_status": "Sukces: Pakiet '{}' odinstalowany pomyślnie.",
        "error_title": "Błąd instalacji",
        "error_install_msg": "Nie udało się zainstalować {}.\nBłąd:\n{}",
        "error_upgrade_msg": "Nie udało się zaktualizować {}.\nBłąd:\n{}",
        "error_uninstall_msg": "Nie udało się odinstalować {}.\nBłąd:\n{}",
        "error_install_status": "Błąd instalacji pakietu {}.",
        "error_upgrade_status": "Błąd aktualizacji pakietu {}.",
        "error_uninstall_status": "Błąd odinstalowania pakietu {}.",
        "scan_error_title": "Błąd",
        "scan_error_msg": "Nie udało się przeskanować pakietów: {}",
        "search_label": "Szukaj:",
        "search_placeholder": "Wpisz nazwę pakietu...",
        "python_exec_label": "Interpreter:",
        "choose_interpreter_btn": "Przeglądaj",
        "choose_interpreter_title": "Wybierz interpreter Pythona",
        "update_btn": "Aktualizuj",
        "uninstall_btn": "Odinstaluj",
        "no_search_results": "Brak pakietów pasujących do wyszukiwania.",
        "btn_refresh": "Odśwież",
        "refresh_btn": "Odśwież",
        "btn_install_file": "Instaluj z pliku",
        "btn_install_all": "Zainstaluj wszystkie",
        "btn_uninstall_all": "Odinstaluj wszystkie",
        "btn_update_all": "Zaktualizuj wszystkie",
        "btn_debug_show": "Logi",
        "btn_debug_hide": "Ukryj",
        "btn_save_logs": "Zapisz",
        "save_logs_success": "Logi zostały pomyślnie zapisane!",
        "save_logs_error": "Nie udało się zapisać logów: {}",
        "about_title": "O programie",
        "theme_light": "Jasny",
        "theme_dark": "Ciemny",
        "acknowledgements_title": "Podziękowania",
        "acknowledgements_text": "Szczególne podziękowania dla firmy Google oraz globalnej Społeczności Pythona za udostępnienie narzędzi open-source, zasobów programistycznych i bogatych ekosystemów, które umożliwiły zbudowanie tego programu.",
        "cat_names": {
            "compilers": "Kompilatory i Transpilatory", "gui": "GUI (Interfejsy Graficzne)", "games": "Gry i Multimedia",
            "data_science": "Data Science i Analiza", "scraping": "Web Scraping", "web_frameworks": "Tworzenie Web",
            "databases": "Bazy Danych i ORM", "testing": "Testowanie i QA", "image_video": "Przetwarzanie Obrazu i Video",
            "async": "Async i Współbieżność", "security": "Bezpieczeństwo i Kryptografia", "automation": "Automatyzacja i Skrypty",
            "parsers": "Parsowanie Danych", "cli": "CLI i Terminal", "ai_nlp": "AI i NLP", "documents": "Przetwarzanie Dokumentów",
            "visualization": "Wizualizacja Danych", "logging": "Logowanie i Monitorowanie", "network": "Sieci",
            "mocking": "Mockowanie i Testowanie", "cloud": "Usługi Chmurowe", "graphics_3d": "Grafika 3D"
        }
    }
}

THEME_CONFIG = {
    "light": {
        "bg": "#f8f9fa",
        "fg": "#212529",
        "card_bg": "#ffffff",
        "card_installed": "#d4edda",
        "card_installed_border": "#28a745",
        "border": "#dee2e6",
        "text_muted": "#6c757d",
        "accent": "#007bff",
        "accent_hover": "#0056b3",
        "success": "#28a745",
        "success_hover": "#218838",
        "danger": "#dc3545",
        "danger_hover": "#c82333",
        "warning": "#ffc107",
        "warning_hover": "#e0a800",
        "header_bg": "#343a40",
        "header_fg": "#ffffff",
        "button_bg": "#007bff",
        "button_fg": "#ffffff",
        "button_hover": "#0056b3",
        "shadow": "rgba(0, 0, 0, 0.1)"
    },
    "dark": {
        "bg": "#121212",
        "fg": "#e0e0e0",
        "card_bg": "#1e1e1e",
        "card_installed": "#1b5e20",
        "card_installed_border": "#4caf50",
        "border": "#333333",
        "text_muted": "#b0b0b0",
        "accent": "#bb86fc",
        "accent_hover": "#9965f4",
        "success": "#03dac6",
        "success_hover": "#01a895",
        "danger": "#cf6679",
        "danger_hover": "#b00020",
        "warning": "#ffb74d",
        "warning_hover": "#ff9800",
        "header_bg": "#1f1f1f",
        "header_fg": "#ffffff",
        "button_bg": "#bb86fc",
        "button_fg": "#121212",
        "button_hover": "#9965f4",
        "shadow": "rgba(0, 0, 0, 0.3)"
    }
}


def run_subprocess_with_timeout(cmd, timeout=300):
    """Run subprocess with timeout."""
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                   text=True, universal_newlines=True)
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode == 0, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def parse_pip_freeze_output(output: str) -> Dict[str, str]:
    """Parse pip freeze output to get installed packages."""
    packages = {}
    for line in output.split('\n'):
        line = line.strip()
        if '==' in line:
            name, version = line.split('==', 1)
            packages[name.lower()] = version
    return packages


def summarize_install_output(output: str) -> str:
    """Summarize pip install output for error messages."""
    if "ERROR: Could not find a version" in output:
        return "Package not found or incompatible"
    elif "ERROR: Permission denied" in output:
        return "Permission denied - try running as administrator"
    elif "ERROR: Could not install packages" in output:
        return "Dependency conflict or installation error"
    elif "already satisfied" in output:
        return "Package already installed"
    else:
        lines = output.split('\n')
        for line in lines:
            if 'ERROR' in line:
                return line.strip()
        return "Installation failed"


class PackageRowPanel(wx.Panel):
    """Panel representing a single package row with buttons."""
    
    def __init__(self, parent, package_name: str, is_installed: bool, 
                 install_callback: Callable, current_lang: str, theme_mode: str, 
                 installed_version: str = "", is_pending: bool = False):
        super().__init__(parent)
        
        self.package_name = package_name
        self.install_callback = install_callback
        self.current_lang = current_lang
        self.theme_mode = theme_mode
        self.is_installed = is_installed
        self.installed_version = installed_version
        self.is_pending = is_pending
        
        self.colors = THEME_CONFIG[theme_mode]
        self.SetBackgroundColour(self.colors["card_installed"] if is_installed else self.colors["card_bg"])
        
        # Add border
        if is_installed:
            self.SetWindowStyleFlag(wx.BORDER_SIMPLE)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create widgets for the package row."""
        colors = self.colors
        lang = LANGUAGES[self.current_lang]
        
        # Main sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Package name (left side)
        name_label = wx.StaticText(self, label=self.package_name)
        name_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        name_label.SetForegroundColour(colors["fg"])
        sizer.Add(name_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 12)
        
        # Status (left side)
        if self.is_installed:
            version_str = f" v{self.installed_version}" if self.installed_version else ""
            status_label = wx.StaticText(self, label=f"✓ {lang['installed']}{version_str}")
            status_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            status_label.SetForegroundColour(colors["success"])
            sizer.Add(status_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 12)
        
        # Spacer to push buttons to the right
        sizer.AddStretchSpacer(1)
        
        # Buttons (right side)
        if self.is_installed:
            update_btn = wx.Button(self, label=lang["update_btn"], size=(95, 32))
            update_btn.SetBackgroundColour(colors["success"])
            update_btn.SetForegroundColour(wx.WHITE)
            update_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            update_btn.Bind(wx.EVT_BUTTON, lambda e: self.install_callback(self.package_name, self, "upgrade"))
            sizer.Add(update_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 6)
            
            uninstall_btn = wx.Button(self, label=lang["uninstall_btn"], size=(115, 32))
            uninstall_btn.SetBackgroundColour(colors["danger"])
            uninstall_btn.SetForegroundColour(wx.WHITE)
            uninstall_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            uninstall_btn.Bind(wx.EVT_BUTTON, lambda e: self.install_callback(self.package_name, self, "uninstall"))
            sizer.Add(uninstall_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 6)
        else:
            install_btn = wx.Button(self, label=lang["install_btn"], size=(95, 32))
            install_btn.SetBackgroundColour(colors["button_bg"])
            install_btn.SetForegroundColour(colors["button_fg"])
            install_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            install_btn.Bind(wx.EVT_BUTTON, lambda e: self.install_callback(self.package_name, self, "install"))
            sizer.Add(install_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 6)
        
        self.SetSizer(sizer)
    
    def update_state(self, is_installed: bool, installed_version: str = ""):
        """Update the installation state."""
        self.is_installed = is_installed
        self.installed_version = installed_version
        
        self.SetBackgroundColour(self.colors["card_installed"] if is_installed else self.colors["card_bg"])
        self.Refresh()
        
        # Recreate widgets
        self.DestroyChildren()
        self._create_widgets()
        self.Layout()
    
    def update_language(self, lang: str):
        """Update language."""
        self.current_lang = lang
        self.DestroyChildren()
        self._create_widgets()
        self.Layout()
    
    def cleanup(self):
        """Clean up resources."""
        self.Destroy()


class InstallerAppWx(wx.Frame):
    """Main application class using wxPython."""
    
    def __init__(self):
        super().__init__(None, title=LANGUAGES["EN"]["title"], size=(980, 714))
        
        self.current_lang = "EN"
        self.theme_mode = "dark"
        self.python_executable = sys.executable
        self.installed_packages = {}
        self.current_category_id = None
        self.search_filter = ""
        self.debug_visible = False
        self.pending_installations: List[Dict[str, str]] = []
        self._running = True
        self.package_rows = {}
        
        self._setup_ui()
        self._apply_theme()
        
        # Start scanning for installed packages
        self.refresh_installed_packages()
        
        self.Centre()
        self.Show()
    
    def _setup_ui(self):
        """Setup the user interface."""
        lang = LANGUAGES[self.current_lang]
        colors = THEME_CONFIG[self.theme_mode]
        
        # Main panel
        main_panel = wx.Panel(self)
        main_panel.SetBackgroundColour(colors["bg"])
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header panel
        header_panel = wx.Panel(main_panel)
        header_panel.SetBackgroundColour(colors["header_bg"])
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        header = wx.StaticText(header_panel, label=lang["header"])
        header.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        header.SetForegroundColour(colors["header_fg"])
        header_sizer.Add(header, 0, wx.ALL, 20)
        
        header_panel.SetSizer(header_sizer)
        main_sizer.Add(header_panel, 0, wx.EXPAND | wx.BOTTOM, 2)
        
        # Top bar
        top_bar = wx.Panel(main_panel)
        top_bar.SetBackgroundColour(colors["card_bg"])
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_refresh = wx.Button(top_bar, label=lang["refresh_btn"], size=(105, 38))
        self._style_button(self.btn_refresh, colors["button_bg"], colors["button_fg"])
        self.btn_refresh.Bind(wx.EVT_BUTTON, self.refresh_installed_packages)
        top_sizer.Add(self.btn_refresh, 0, wx.ALL, 10)
        
        self.btn_install_file = wx.Button(top_bar, label=lang["btn_install_file"], size=(155, 38))
        self._style_button(self.btn_install_file, colors["accent"], colors["button_fg"])
        self.btn_install_file.Bind(wx.EVT_BUTTON, self.install_from_file)
        top_sizer.Add(self.btn_install_file, 0, wx.ALL, 10)
        
        self.btn_debug = wx.Button(top_bar, label=lang["btn_debug_show"], size=(85, 38))
        self._style_button(self.btn_debug, colors["warning"], colors["button_fg"])
        self.btn_debug.Bind(wx.EVT_BUTTON, self.toggle_debug_panel)
        top_sizer.Add(self.btn_debug, 0, wx.ALL, 10)
        
        self.btn_theme = wx.Button(top_bar, label=lang["theme_light"], size=(105, 38))
        self._style_button(self.btn_theme, colors["text_muted"], colors["button_fg"])
        self.btn_theme.Bind(wx.EVT_BUTTON, self.toggle_theme)
        top_sizer.Add(self.btn_theme, 0, wx.ALL, 10)
        
        self.btn_lang = wx.Button(top_bar, label=self.current_lang, size=(55, 38))
        self._style_button(self.btn_lang, colors["text_muted"], colors["button_fg"])
        self.btn_lang.Bind(wx.EVT_BUTTON, self.toggle_language)
        top_sizer.Add(self.btn_lang, 0, wx.ALL, 10)
        
        self.btn_about = wx.Button(top_bar, label=lang["about_title"], size=(85, 38))
        self._style_button(self.btn_about, colors["text_muted"], colors["button_fg"])
        self.btn_about.Bind(wx.EVT_BUTTON, self.show_about_dialog)
        top_sizer.Add(self.btn_about, 0, wx.ALL, 10)
        
        top_bar.SetSizer(top_sizer)
        main_sizer.Add(top_bar, 0, wx.ALL | wx.EXPAND, 10)
        
        # Search bar
        search_bar = wx.Panel(main_panel)
        search_bar.SetBackgroundColour(colors["card_bg"])
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        search_label = wx.StaticText(search_bar, label=lang["search_label"])
        search_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        search_label.SetForegroundColour(colors["fg"])
        search_sizer.Add(search_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        self.search_ctrl = wx.TextCtrl(search_bar, size=(300, 30), style=wx.BORDER_SIMPLE)
        self.search_ctrl.SetBackgroundColour(colors["bg"])
        self.search_ctrl.SetForegroundColour(colors["fg"])
        self.search_ctrl.Bind(wx.EVT_TEXT, self._on_search_text)
        search_sizer.Add(self.search_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)
        
        interp_label = wx.StaticText(search_bar, label=lang["python_exec_label"])
        interp_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        interp_label.SetForegroundColour(colors["fg"])
        search_sizer.Add(interp_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        self.interp_ctrl = wx.TextCtrl(search_bar, value=self.python_executable, size=(300, 30), 
                                       style=wx.TE_READONLY | wx.BORDER_SIMPLE)
        self.interp_ctrl.SetBackgroundColour(colors["bg"])
        self.interp_ctrl.SetForegroundColour(colors["text_muted"])
        search_sizer.Add(self.interp_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)
        
        btn_choose_interp = wx.Button(search_bar, label=lang["choose_interpreter_btn"], size=(120, 30))
        self._style_button(btn_choose_interp, colors["accent"], colors["button_fg"])
        btn_choose_interp.Bind(wx.EVT_BUTTON, self.choose_python_executable)
        search_sizer.Add(btn_choose_interp, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)
        
        search_bar.SetSizer(search_sizer)
        main_sizer.Add(search_bar, 0, wx.ALL | wx.EXPAND, 8)
        
        # Workspace (splitter)
        self.workspace = wx.SplitterWindow(main_panel, style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        self.workspace.SetBackgroundColour(colors["bg"])
        
        # Left panel - Categories
        left_panel = wx.Panel(self.workspace)
        left_panel.SetBackgroundColour(colors["card_bg"])
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        cat_label = wx.StaticText(left_panel, label=lang["categories"])
        cat_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        cat_label.SetForegroundColour(colors["fg"])
        left_sizer.Add(cat_label, 0, wx.ALL, 10)
        
        self.category_list = wx.ListBox(left_panel, choices=list(lang["cat_names"].values()), 
                                       style=wx.LB_SINGLE | wx.BORDER_SIMPLE | wx.VSCROLL)
        self.category_list.SetBackgroundColour(colors["bg"])
        self.category_list.SetForegroundColour(colors["fg"])
        self.category_list.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.category_list.Bind(wx.EVT_LISTBOX, self._on_category_select)
        left_sizer.Add(self.category_list, 1, wx.ALL | wx.EXPAND, 10)
        
        left_panel.SetSizer(left_sizer)
        
        # Right panel - Packages
        right_panel = wx.Panel(self.workspace)
        right_panel.SetBackgroundColour(colors["card_bg"])
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.lbl_right_header = wx.StaticText(right_panel, label=lang["select_category"])
        self.lbl_right_header.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.lbl_right_header.SetForegroundColour(colors["fg"])
        right_sizer.Add(self.lbl_right_header, 0, wx.ALL, 10)
        
        # Package list with scrollable panel
        self.package_scrolled = wx.ScrolledWindow(right_panel, style=wx.VSCROLL)
        self.package_scrolled.SetBackgroundColour(colors["bg"])
        self.package_scrolled.SetScrollRate(0, 20)
        self.package_scrolled.EnableScrolling(True, True)
        self.package_scrolled.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self.package_content = wx.Panel(self.package_scrolled)
        self.package_content.SetBackgroundColour(colors["bg"])
        self.package_sizer = wx.BoxSizer(wx.VERTICAL)
        self.package_content.SetSizer(self.package_sizer)
        self.package_scrolled.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.package_scrolled.GetSizer().Add(self.package_content, 1, wx.EXPAND)
        right_sizer.Add(self.package_scrolled, 1, wx.ALL | wx.EXPAND, 10)
        
        # Batch buttons
        batch_buttons = wx.Panel(right_panel)
        batch_buttons.SetBackgroundColour(colors["card_bg"])
        batch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_install_all = wx.Button(batch_buttons, label=lang["btn_install_all"], size=(135, 38))
        self._style_button(self.btn_install_all, colors["success"], colors["button_fg"])
        self.btn_install_all.Bind(wx.EVT_BUTTON, self.install_all_packages)
        batch_sizer.Add(self.btn_install_all, 0, wx.ALL, 10)
        
        self.btn_uninstall_all = wx.Button(batch_buttons, label=lang["btn_uninstall_all"], size=(135, 38))
        self._style_button(self.btn_uninstall_all, colors["danger"], colors["button_fg"])
        self.btn_uninstall_all.Bind(wx.EVT_BUTTON, self.uninstall_all_packages)
        batch_sizer.Add(self.btn_uninstall_all, 0, wx.ALL, 10)
        
        self.btn_update_all = wx.Button(batch_buttons, label=lang["btn_update_all"], size=(135, 38))
        self._style_button(self.btn_update_all, colors["accent"], colors["button_fg"])
        self.btn_update_all.Bind(wx.EVT_BUTTON, self.update_all_packages)
        batch_sizer.Add(self.btn_update_all, 0, wx.ALL, 10)
        
        batch_buttons.SetSizer(batch_sizer)
        right_sizer.Add(batch_buttons, 0, wx.ALL | wx.CENTER, 12)
        
        right_panel.SetSizer(right_sizer)
        
        self.workspace.SplitVertically(left_panel, right_panel, 180)
        self.workspace.SetMinimumPaneSize(150)
        self.workspace.SetSashGravity(0.15)
        
        main_sizer.Add(self.workspace, 1, wx.ALL | wx.EXPAND, 8)
        
        # Status bar with progress bar
        status_panel = wx.Panel(main_panel)
        status_panel.SetBackgroundColour(colors["header_bg"])
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.status_bar = wx.StaticText(status_panel, label=lang["status_ready"])
        self.status_bar.SetForegroundColour(colors["header_fg"])
        self.status_bar.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        status_sizer.Add(self.status_bar, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        status_sizer.AddStretchSpacer(1)
        
        self.progress_bar = wx.Gauge(status_panel, range=100, size=(250, 22), style=wx.GA_HORIZONTAL)
        self.progress_bar.SetBackgroundColour(colors["bg"])
        self.progress_bar.SetValue(0)
        status_sizer.Add(self.progress_bar, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 12)
        
        status_panel.SetSizer(status_sizer)
        main_sizer.Add(status_panel, 0, wx.EXPAND)
        
        # Debug console (hidden by default)
        self.debug_panel = wx.Panel(main_panel)
        self.debug_panel.SetBackgroundColour(colors["card_bg"])
        debug_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.debug_console = wx.TextCtrl(self.debug_panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 150))
        self.debug_console.SetBackgroundColour(colors["bg"])
        self.debug_console.SetForegroundColour(colors["fg"])
        self.debug_console.SetFont(wx.Font(9, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        debug_sizer.Add(self.debug_console, 1, wx.ALL | wx.EXPAND, 10)
        
        self.debug_panel.SetSizer(debug_sizer)
        self.debug_panel.Hide()
        main_sizer.Add(self.debug_panel, 0, wx.ALL | wx.EXPAND, 8)
        
        main_panel.SetSizer(main_sizer)
    
    def _style_button(self, button, bg_color, fg_color):
        """Style a button with custom colors."""
        button.SetBackgroundColour(bg_color)
        button.SetForegroundColour(fg_color)
        button.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        button.SetWindowStyleFlag(wx.BORDER_NONE)
    
    def _apply_theme(self):
        """Apply theme colors to the UI."""
        colors = THEME_CONFIG[self.theme_mode]
        lang = LANGUAGES[self.current_lang]
        
        # Rebuild UI with new theme
        self.DestroyChildren()
        self._setup_ui()
        self.Layout()
        self.Refresh()
    
    def refresh_installed_packages(self, event=None):
        """Scan for installed packages."""
        def run_scan():
            cmd = [self.python_executable, "-m", "pip", "freeze"]
            success, stdout, stderr = run_subprocess_with_timeout(cmd, timeout=60)
            if success:
                self.installed_packages = parse_pip_freeze_output(stdout)
                wx.CallAfter(self._refresh_package_view)
            else:
                wx.CallAfter(wx.MessageBox, f"Failed to scan packages: {stderr}", "Error", wx.OK | wx.ICON_ERROR)
        
        threading.Thread(target=run_scan, daemon=True).start()
    
    def _on_category_select(self, event):
        """Handle category selection."""
        selection = self.category_list.GetSelection()
        if selection != wx.NOT_FOUND:
            self.search_filter = ""
            self.search_ctrl.Clear()
            cat_keys = list(LANGUAGES[self.current_lang]["cat_names"].keys())
            if selection < len(cat_keys):
                self.current_category_id = cat_keys[selection]
            self._refresh_package_view()
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel/touchpad scrolling."""
        rotation = event.GetWheelRotation()
        delta = rotation // event.GetWheelDelta()
        lines_per_delta = event.GetLinesPerAction()
        
        # Calculate scroll amount
        scroll_amount = delta * lines_per_delta * 20
        
        # Get current scroll position
        x, y = self.package_scrolled.GetScrollPos(wx.HORIZONTAL), self.package_scrolled.GetScrollPos(wx.VERTICAL)
        
        # Update scroll position
        new_y = max(0, y - scroll_amount)
        self.package_scrolled.Scroll(x, new_y)
        
        event.Skip()
    
    def _on_search_text(self, event):
        """Handle search text input."""
        self.search_filter = self.search_ctrl.GetValue().lower().strip()
        if self.search_filter:
            self.category_list.SetSelection(wx.NOT_FOUND)
            self.current_category_id = None
        self._refresh_package_view()
    
    def _refresh_package_view(self):
        """Refresh the package view based on current category or search filter."""
        lang = LANGUAGES[self.current_lang]
        
        # Clean up existing package rows
        for row in self.package_rows.values():
            row.cleanup()
        self.package_rows.clear()
        
        self.package_sizer.Clear(delete_windows=True)
        
        packages_to_show = []
        
        if self.search_filter:
            self.lbl_right_header.SetLabel(f"{lang['search_label']} '{self.search_filter}'")
            for cat_id, libs in BIBLIOTEKI.items():
                for lib in libs:
                    if self.search_filter in lib.lower() and lib not in packages_to_show:
                        packages_to_show.append(lib)
        elif self.current_category_id:
            translated_cat_name = lang["cat_names"].get(self.current_category_id, self.current_category_id)
            self.lbl_right_header.SetLabel(f"{lang['libs_in']}{translated_cat_name}")
            packages_to_show = BIBLIOTEKI.get(self.current_category_id, [])
        else:
            self.lbl_right_header.SetLabel(lang["select_category"])
            return
        
        if not packages_to_show:
            no_res = wx.StaticText(self.package_content, label=lang["no_search_results"])
            self.package_sizer.Add(no_res, 0, wx.ALL, 10)
            self.package_content.Layout()
            self.package_scrolled.FitInside()
            self.package_scrolled.SetVirtualSize(self.package_content.GetBestSize())
            self.package_scrolled.Layout()
            return
        
        # Display packages
        for pkg in packages_to_show:
            is_installed = pkg.lower() in self.installed_packages
            version = self.installed_packages.get(pkg.lower(), "")
            row = PackageRowPanel(self.package_content, pkg, is_installed, self._handle_package_action, 
                             self.current_lang, self.theme_mode, version)
            self.package_rows[pkg] = row
            self.package_sizer.Add(row, 0, wx.ALL | wx.EXPAND, 5)
        
        self.package_content.Layout()
        self.package_scrolled.FitInside()
        self.package_scrolled.SetVirtualSize(self.package_content.GetBestSize())
        self.package_scrolled.Layout()
        self.package_scrolled.Scroll(0, 0)
    
    def _handle_package_action(self, package_name: str, row_widget, action: str):
        """Handle package action (install/upgrade/uninstall)."""
        lang = LANGUAGES[self.current_lang]
        
        if action == "install":
            cmd = [self.python_executable, "-m", "pip", "install", package_name]
            status_text = lang["preparing"].format(package_name)
        elif action == "upgrade":
            cmd = [self.python_executable, "-m", "pip", "install", "--upgrade", package_name]
            status_text = lang["preparing_upgrade"].format(package_name)
        elif action == "uninstall":
            cmd = [self.python_executable, "-m", "pip", "uninstall", "-y", package_name]
            status_text = lang["preparing_uninstall"].format(package_name)
        else:
            return
        
        # Show progress bar
        wx.CallAfter(self._show_progress, status_text)
        
        def run_pip():
            success, stdout, stderr = run_subprocess_with_timeout(cmd, timeout=300)
            wx.CallAfter(self._hide_progress)
            if success:
                wx.CallAfter(wx.MessageBox, lang[f"success_{action}_msg"].format(package_name), 
                             lang["success_title"], wx.OK | wx.ICON_INFORMATION)
                wx.CallAfter(self.refresh_installed_packages)
            else:
                error_msg = summarize_install_output(stderr)
                wx.CallAfter(wx.MessageBox, lang[f"error_{action}_msg"].format(package_name, error_msg), 
                             lang["error_title"], wx.OK | wx.ICON_ERROR)
        
        threading.Thread(target=run_pip, daemon=True).start()
    
    def _show_progress(self, status_text: str):
        """Show progress bar with status text."""
        self.status_bar.SetLabel(status_text)
        self.progress_bar.SetValue(0)
        self.progress_bar.Pulse()
        self.Layout()
    
    def _hide_progress(self):
        """Hide progress bar and reset status."""
        lang = LANGUAGES[self.current_lang]
        self.status_bar.SetLabel(lang["status_ready"])
        self.progress_bar.SetValue(0)
        self.Layout()
    
    def install_from_file(self, event=None):
        """Parse packages from a file and display them."""
        lang = LANGUAGES[self.current_lang]
        
        wildcard = "Requirements files (requirements*.txt)|requirements*.txt|" \
                   "Setup files (setup.py)|setup.py|" \
                   "PyProject files (pyproject.toml)|pyproject.toml|" \
                   "Conda environment files (environment*.yml)|environment*.yml|" \
                   "All files (*.*)|*.*"
        
        dialog = wx.FileDialog(self, "Select dependency file", wildcard=wildcard, 
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        
        file_path = dialog.GetPath()
        dialog.Destroy()
        
        file_name = os.path.basename(file_path)
        
        # Detect file format and parse accordingly
        file_type = self._detect_file_format(file_path, file_name)
        
        if file_type == "requirements":
            packages = self._parse_requirements_file(file_path)
        elif file_type == "setup":
            packages = self._parse_setup_file(file_path)
        elif file_type == "pyproject":
            packages = self._parse_pyproject_file(file_path)
        elif file_type == "conda":
            wx.MessageBox("Conda environment files require conda. Please use conda directly.", 
                         "Warning", wx.OK | wx.ICON_WARNING)
            return
        else:
            wx.MessageBox(f"Unsupported file format: {file_name}", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        if not packages:
            wx.MessageBox("No packages found in the selected file.", "Info", wx.OK | wx.ICON_INFORMATION)
            return
        
        # Store pending installations
        self.pending_installations = packages
        self._display_pending_installations(file_name)
    
    def _detect_file_format(self, file_path: str, file_name: str) -> str:
        """Detect the format of the dependency file."""
        file_lower = file_name.lower()
        
        if file_lower.startswith("requirements") and file_lower.endswith(".txt"):
            return "requirements"
        elif file_lower == "setup.py":
            return "setup"
        elif file_lower == "pyproject.toml":
            return "pyproject"
        elif file_lower.startswith("environment") and (file_lower.endswith(".yml") or file_lower.endswith(".yaml")):
            return "conda"
        
        return "unknown"
    
    def _parse_requirements_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse requirements.txt file."""
        packages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('-r'):
                        continue
                    pkg_name = line
                    version = ""
                    for op in ['==', '>=', '<=', '~=', '>', '<', '!=']:
                        if op in line:
                            parts = line.split(op)
                            pkg_name = parts[0].strip()
                            version = op + parts[1].strip()
                            break
                    packages.append({"name": pkg_name, "version": version})
        except Exception as e:
            wx.MessageBox(f"Error parsing requirements.txt: {e}", "Error", wx.OK | wx.ICON_ERROR)
        return packages
    
    def _parse_setup_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse setup.py file."""
        packages = []
        try:
            dir_name = os.path.basename(os.path.dirname(file_path))
            if dir_name:
                packages.append({"name": dir_name, "version": ""})
        except Exception as e:
            wx.MessageBox(f"Error parsing setup.py: {e}", "Error", wx.OK | wx.ICON_ERROR)
        return packages
    
    def _parse_pyproject_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse pyproject.toml file."""
        packages = []
        try:
            dir_name = os.path.basename(os.path.dirname(file_path))
            if dir_name:
                packages.append({"name": dir_name, "version": ""})
        except Exception as e:
            wx.MessageBox(f"Error parsing pyproject.toml: {e}", "Error", wx.OK | wx.ICON_ERROR)
        return packages
    
    def _display_pending_installations(self, file_name: str):
        """Display pending installations."""
        lang = LANGUAGES[self.current_lang]
        self.lbl_right_header.SetLabel(f"Packages from: {file_name}")
        
        # Clean up existing package rows
        for row in self.package_rows.values():
            row.cleanup()
        self.package_rows.clear()
        
        self.package_sizer.Clear(delete_windows=True)
        
        # Display packages
        for pkg in self.pending_installations:
            pkg_name = pkg["name"]
            version = pkg["version"]
            is_installed = pkg_name.lower() in self.installed_packages
            row = PackageRowPanel(self.package_content, pkg_name, is_installed, self._handle_package_action, 
                             self.current_lang, self.theme_mode, version, is_pending=True)
            self.package_rows[pkg_name] = row
            self.package_sizer.Add(row, 0, wx.ALL | wx.EXPAND, 5)
        
        self.package_content.Layout()
        self.package_scrolled.FitInside()
        self.package_scrolled.SetVirtualSize(self.package_content.GetBestSize())
        self.package_scrolled.Layout()
        self.package_scrolled.Scroll(0, 0)
    
    def install_all_packages(self, event=None):
        """Install all pending packages."""
        if not self.pending_installations:
            return
        
        for pkg in self.pending_installations:
            pkg_name = pkg["name"]
            self._handle_package_action(pkg_name, None, "install")
    
    def uninstall_all_packages(self, event=None):
        """Uninstall all currently displayed packages."""
        if not self.package_rows:
            return
        
        for pkg_name, row in list(self.package_rows.items()):
            if row.is_installed:
                self._handle_package_action(pkg_name, row, "uninstall")
    
    def update_all_packages(self, event=None):
        """Update all currently displayed packages."""
        if not self.package_rows:
            return
        
        for pkg_name, row in list(self.package_rows.items()):
            if row.is_installed:
                self._handle_package_action(pkg_name, row, "upgrade")
    
    def toggle_debug_panel(self, event):
        """Toggle debug panel visibility."""
        self.debug_visible = not self.debug_visible
        lang = LANGUAGES[self.current_lang]
        self.btn_debug.SetLabel(lang["btn_debug_hide"] if self.debug_visible else lang["btn_debug_show"])
        self.debug_panel.Show(self.debug_visible)
        self.Layout()
    
    def toggle_theme(self, event):
        """Toggle between light and dark theme."""
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        lang = LANGUAGES[self.current_lang]
        self.btn_theme.SetLabel(lang["theme_light"] if self.theme_mode == "dark" else lang["theme_dark"])
        self._apply_theme()
    
    def toggle_language(self, event):
        """Toggle between English and Polish."""
        self.current_lang = "PL" if self.current_lang == "EN" else "EN"
        lang = LANGUAGES[self.current_lang]
        
        self.SetTitle(lang["title"])
        self.btn_refresh.SetLabel(lang["refresh_btn"])
        self.btn_install_file.SetLabel(lang["btn_install_file"])
        self.btn_debug.SetLabel(lang["btn_debug_hide"] if self.debug_visible else lang["btn_debug_show"])
        self.btn_theme.SetLabel(lang["theme_light"] if self.theme_mode == "dark" else lang["theme_dark"])
        self.btn_lang.SetLabel(self.current_lang)
        self.btn_about.SetLabel(lang["about_title"])
        self.status_bar.SetLabel(lang["status_ready"])
        
        # Update category list
        self.category_list.Clear()
        for cat_name in lang["cat_names"].values():
            self.category_list.Append(cat_name)
        
        self._refresh_package_view()
    
    def choose_python_executable(self, event=None):
        """Choose Python interpreter."""
        wildcard = "Python Executable (python.exe)|python.exe|All files (*.*)|*.*"
        
        dialog = wx.FileDialog(self, LANGUAGES[self.current_lang]["choose_interpreter_title"], 
                               wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        
        file_path = dialog.GetPath()
        dialog.Destroy()
        
        self.python_executable = file_path
        self.interp_ctrl.SetValue(file_path)
        self.refresh_installed_packages()
    
    def show_about_dialog(self, event):
        """Show the about dialog."""
        lang = LANGUAGES[self.current_lang]
        
        about_text = (
            f"{METADATA['name']}\n"
            f"Version: {METADATA['version']}\n"
            f"Description: {METADATA['description']}\n\n"
            f"Author: {METADATA['author']}\n"
            f"Company: {METADATA['company']}\n"
            f"GitHub: {METADATA['github']}\n"
            f"E-mail: {METADATA['email']}\n\n"
            f"--- {lang['acknowledgements_title']} ---\n"
            f"{lang['acknowledgements_text']}"
        )
        
        wx.MessageBox(about_text, lang["about_title"], wx.OK | wx.ICON_INFORMATION)


if __name__ == "__main__":
    app = wx.App(False)
    frame = InstallerAppWx()
    app.MainLoop()
