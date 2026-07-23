import sys
import os
import subprocess
import threading
import queue
import time
import ast
import re
from tkinter import messagebox, filedialog
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from typing import Dict, List, Optional, Callable, Any

# Check if PIL/Pillow is available
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

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

# Timeout constants for subprocess operations
TIMEOUT_PIP_ACTION = 300  # 5 minutes for install/upgrade/uninstall
TIMEOUT_PIP_SCAN = 60    # 1 minute for pip freeze scan
TIMEOUT_PIP_FILE = 600   # 10 minutes for installing from files (requirements.txt, setup.py, etc.)
TIMEOUT_PYTHON_VALIDATE = 10  # 10 seconds for Python version validation

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
        "title": "Python Package Installer (Tkinter Modern)",
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
        "title": "Instalator Pakietów Python (Tkinter Modern)",
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

THEME_CONFIG = {
    "dark": {
        "bg": "#121214", "fg": "#e1e1e6", "bg_entry": "#202024", "border": "#323238",
        "accent": "#00adb5", "accent_hover": "#00cbd3", "card_bg": "#202024",
        "card_installed": "#172220", "card_installed_border": "#1f3a35", "text_muted": "#8d8d99"
    },
    "light": {
        "bg": "#f8fafc", "fg": "#475569", "bg_entry": "#ffffff", "border": "#e2e8f0",
        "accent": "#0ea5e9", "accent_hover": "#38bdf8", "card_bg": "#ffffff",
        "card_installed": "#f0fdf4", "card_installed_border": "#bbf7d0", "text_muted": "#94a3b8"
    }
}


def parse_pip_freeze_output(output: str) -> Dict[str, str]:
    """Parse pip freeze output into a dictionary of package names to versions."""
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
            pkg, version = pkg.strip(), version.strip()
        else:
            pkg, version = line, ""
        if pkg:
            packages[pkg.lower()] = version
    return packages


def summarize_install_output(output: str, max_lines: int = 8) -> str:
    """Summarize installation output to prevent overwhelming error messages."""
    if not output:
        return ""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"


def run_subprocess_with_timeout(cmd: List[str], timeout: int = 300) -> tuple[bool, str, str]:
    """Run subprocess with timeout and proper error handling."""
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        return True, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        return False, e.stdout or "", e.stderr or str(e)
    except FileNotFoundError:
        return False, "", f"Python executable not found: {cmd[0]}"
    except Exception as e:
        return False, "", str(e)


class ThreadSafeQueue:
    """Thread-safe queue for UI updates from background threads."""
    
    def __init__(self):
        self._queue = queue.Queue()
        self._lock = threading.Lock()
    
    def put(self, item: Any):
        with self._lock:
            self._queue.put(item)
    
    def get(self, timeout: float = 0.1) -> Optional[Any]:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def empty(self) -> bool:
        with self._lock:
            return self._queue.empty()


class PackageRowTk(tk.Frame):
    """Widget representing a single package in the list."""
    
    def __init__(self, parent, package_name: str, is_installed: bool, 
                 install_callback: Callable, current_lang: str, theme_mode: str, 
                 installed_version: str = "", is_pending: bool = False):
        self.colors = THEME_CONFIG[theme_mode]
        bg_color = self.colors["card_installed"] if is_installed else self.colors["card_bg"]
        highlight_color = self.colors["card_installed_border"] if is_installed else self.colors["border"]
        
        super().__init__(parent, bg=bg_color, highlightbackground=highlight_color, 
                        highlightthickness=1, bd=0)
        
        self.package_name = package_name
        self.install_callback = install_callback
        self.current_lang = current_lang
        self.theme_mode = theme_mode
        self.is_installed = is_installed
        self.installed_version = installed_version
        self.is_pending = is_pending
        self._widgets = []
        
        self.pack(fill="x", pady=5, padx=8)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all child widgets."""
        colors = self.colors
        bg_color = colors["card_installed"] if self.is_installed else colors["card_bg"]
        
        # Package Name
        self.lbl_name = tk.Label(self, text=self.package_name, fg=colors["fg"], 
                                bg=bg_color, font=("Segoe UI", 11, "bold"), anchor="w")
        self.lbl_name.pack(side="left", padx=15, pady=12, fill="x", expand=True)
        self._widgets.append(self.lbl_name)
        
        # Installation Status
        self.lbl_status = tk.Label(self, bg=bg_color)
        self.lbl_status.pack(side="left", padx=10)
        self._widgets.append(self.lbl_status)
        
        # Buttons
        lang = LANGUAGES[self.current_lang]
        
        self.btn_install = ttk.Button(self, text=lang["install_btn"], style="Accent.TButton", 
                                     cursor="hand2", command=lambda: self.trigger_action("install"))
        
        self.btn_update = ttk.Button(self, text=lang["update_btn"], style="Success.TButton", 
                                    cursor="hand2", command=lambda: self.trigger_action("upgrade"))
        
        self.btn_uninstall = ttk.Button(self, text=lang["uninstall_btn"], style="Danger.TButton", 
                                       cursor="hand2", command=lambda: self.trigger_action("uninstall"))
        
        self._update_ui_state()
    
    def _update_ui_state(self):
        """Update UI based on installation state."""
        lang = LANGUAGES[self.current_lang]
        colors = self.colors
        bg_color = colors["card_installed"] if self.is_installed else colors["card_bg"]
        
        # Update background
        self.configure(bg=bg_color, highlightbackground=colors["card_installed_border"] if self.is_installed else colors["border"])
        
        for widget in self._widgets:
            if isinstance(widget, tk.Label):
                widget.configure(bg=bg_color)
        
        if self.is_installed:
            version_str = f" v{self.installed_version}" if self.installed_version else ""
            status_color = "#00adb5" if self.theme_mode == "dark" else "#10b981"
            self.lbl_status.config(text=f"✓ {lang['installed']}{version_str}", 
                                  fg=status_color, font=("Segoe UI", 10, "bold"))
            self.lbl_status.pack(side="left", padx=10)
            
            self.btn_install.pack_forget()
            self.btn_update.pack(side="right", padx=6, pady=8)
            self.btn_uninstall.pack(side="right", padx=6, pady=8)
        elif self.is_pending:
            # For pending installations from file, show install button
            self.lbl_status.pack_forget()
            self.btn_update.pack_forget()
            self.btn_uninstall.pack_forget()
            self.btn_install.pack(side="right", padx=12, pady=8)
        else:
            self.lbl_status.pack_forget()
            self.btn_update.pack_forget()
            self.btn_uninstall.pack_forget()
            self.btn_install.pack(side="right", padx=12, pady=8)
    
    def update_state(self, is_installed: bool, installed_version: str = ""):
        """Update the installation state of this package row."""
        self.is_installed = is_installed
        self.installed_version = installed_version
        self._update_ui_state()
    
    def update_theme(self, theme_mode: str):
        """Update the theme of this widget."""
        self.theme_mode = theme_mode
        self.colors = THEME_CONFIG[theme_mode]
        self._update_ui_state()
    
    def update_language(self, current_lang: str):
        """Update the language of this widget."""
        self.current_lang = current_lang
        lang = LANGUAGES[current_lang]
        self.btn_install.config(text=lang["install_btn"])
        self.btn_update.config(text=lang["update_btn"])
        self.btn_uninstall.config(text=lang["uninstall_btn"])
        self._update_ui_state()
    
    def trigger_action(self, action: str):
        """Trigger an action (install/upgrade/uninstall)."""
        if action == "install":
            self.btn_install.config(text=LANGUAGES[self.current_lang]["installing"], state="disabled")
        else:
            self.btn_update.config(state="disabled")
            self.btn_uninstall.config(state="disabled")
        self.install_callback(self.package_name, self, action)
    
    def cleanup(self):
        """Clean up resources."""
        for widget in self._widgets:
            widget.destroy()
        self.btn_install.destroy()
        self.btn_update.destroy()
        self.btn_uninstall.destroy()
        self.destroy()


class InstallerAppTk(tk.Tk):
    """Main application class for Python Package Installer."""
    
    def __init__(self):
        super().__init__()
        
        # State
        self.current_lang = "EN"
        self.theme_mode = "dark"
        self.debug_visible = False
        self.python_executable = sys.executable
        self.search_filter = ""
        self.current_category_id = None
        self.installed_packages: Dict[str, str] = {}
        self.package_rows: Dict[str, PackageRowTk] = {}
        self._running = True
        self.pending_installations: List[Dict[str, str]] = []  # List of packages to install from file
        
        # Thread-safe communication
        self._ui_queue = ThreadSafeQueue()
        
        # Setup window
        self.title(LANGUAGES[self.current_lang]["title"])
        self.geometry("1040x780")
        self.minsize(900, 680)
        
        # Set custom icon with improved quality using PIL
        if PIL_AVAILABLE:
            try:
                # Load icon using PIL for better quality
                icon_image = Image.open("ppm-ico.ico")
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.iconphoto(False, icon_photo)
            except Exception:
                try:
                    # Fallback to standard iconbitmap
                    self.iconbitmap("ppm-ico.ico")
                except Exception:
                    pass  # Fallback to default icon if .ico file not found
        else:
            try:
                # Fallback to standard iconbitmap
                self.iconbitmap("ppm-ico.ico")
            except Exception:
                pass  # Fallback to default icon if .ico file not found
        
        # Setup styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Initialize UI
        self._init_ui()
        
        # Start UI update checker
        self._check_ui_queue()
        
        # Initial package scan
        self.refresh_installed_packages()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _init_ui(self):
        """Initialize the user interface."""
        colors = THEME_CONFIG[self.theme_mode]
        self.configure(bg=colors["bg"])
        
        # Top Bar
        self._create_top_bar()
        
        # Search & Interpreter Bar
        self._create_search_bar()
        
        # Main Workspace
        self._create_workspace()
        
        # Debug Console
        self._create_debug_console()
        
        # Status Bar
        self._create_status_bar()
        
        # Apply theme
        self._apply_theme_styles()
        
        # Update category list
        self._update_category_listbox()
    
    def _create_top_bar(self):
        """Create the top toolbar."""
        colors = THEME_CONFIG[self.theme_mode]
        
        self.top_bar = tk.Frame(self, bg=colors["bg"])
        self.top_bar.pack(fill="x", padx=25, pady=15)
        
        self.lbl_header = tk.Label(self.top_bar, text=LANGUAGES[self.current_lang]["header"], 
                                  fg=colors["fg"], bg=colors["bg"], font=("Segoe UI", 18, "bold"))
        self.lbl_header.pack(side="left")
        
        self.top_buttons = tk.Frame(self.top_bar, bg=colors["bg"])
        self.top_buttons.pack(side="right")
        
        self.btn_refresh = ttk.Button(self.top_buttons, text=LANGUAGES[self.current_lang]["refresh_btn"], 
                                     style="Secondary.TButton", cursor="hand2", command=self.refresh_installed_packages)
        self.btn_refresh.pack(side="left", padx=4)
        
        self.btn_install_file = ttk.Button(self.top_buttons, text=LANGUAGES[self.current_lang]["btn_install_file"], 
                                          style="Secondary.TButton", cursor="hand2", command=self.install_from_file)
        self.btn_install_file.pack(side="left", padx=4)
        
        self.btn_toggle_debug = ttk.Button(self.top_buttons, text=LANGUAGES[self.current_lang]["btn_debug_show"], 
                                          style="Secondary.TButton", cursor="hand2", command=self.toggle_debug_panel)
        self.btn_toggle_debug.pack(side="left", padx=4)
        
        self.btn_theme = ttk.Button(self.top_buttons, text=LANGUAGES[self.current_lang]["theme_dark"], 
                                   style="Secondary.TButton", cursor="hand2", command=self.toggle_theme)
        self.btn_theme.pack(side="left", padx=4)
        
        self.btn_lang = ttk.Button(self.top_buttons, text=self.current_lang, style="Secondary.TButton", 
                                  cursor="hand2", command=self.toggle_language)
        self.btn_lang.pack(side="left", padx=4)
        
        self.btn_about = ttk.Button(self.top_buttons, text="ℹ", width=3, style="Secondary.TButton", 
                                   cursor="hand2", command=self.show_about_dialog)
        self.btn_about.pack(side="left", padx=4)
    
    def _create_search_bar(self):
        """Create the search and interpreter bar."""
        colors = THEME_CONFIG[self.theme_mode]
        
        self.search_bar = tk.Frame(self, bg=colors["bg"])
        self.search_bar.pack(fill="x", padx=25, pady=5)
        
        self.lbl_search = tk.Label(self.search_bar, text=LANGUAGES[self.current_lang]["search_label"], 
                                  fg=colors["fg"], bg=colors["bg"], font=("Segoe UI", 10, "bold"))
        self.lbl_search.pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._on_search_text())
        
        self.search_ctrl = tk.Entry(self.search_bar, textvariable=self.search_var, font=("Segoe UI", 10), 
                                   bd=0, highlightthickness=1, relief="solid", width=28)
        self.search_ctrl.pack(side="left", fill="y", expand=False, padx=(0, 25), ipady=4)
        
        self.lbl_interpreter = tk.Label(self.search_bar, text=LANGUAGES[self.current_lang]["python_exec_label"], 
                                       fg=colors["fg"], bg=colors["bg"], font=("Segoe UI", 10, "bold"))
        self.lbl_interpreter.pack(side="left", padx=(0, 5))
        
        self.txt_interpreter = tk.Entry(self.search_bar, font=("Segoe UI", 10), bd=0, 
                                       highlightthickness=1, relief="solid")
        self.txt_interpreter.insert(0, self.python_executable)
        self.txt_interpreter.config(state="readonly")
        self.txt_interpreter.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        self.btn_choose_python = ttk.Button(self.search_bar, text=LANGUAGES[self.current_lang]["choose_interpreter_btn"], 
                                           style="Accent.TButton", cursor="hand2", command=self.choose_python_executable)
        self.btn_choose_python.pack(side="left")
    
    def _create_workspace(self):
        """Create the main workspace with category list and package view."""
        colors = THEME_CONFIG[self.theme_mode]
        
        self.workspace = tk.PanedWindow(self, orient="horizontal", bd=0, sashwidth=6, bg=colors["bg"])
        self.workspace.pack(fill="both", expand=True, padx=25, pady=15)
        
        # Left Panel - Categories
        self.left_panel = tk.Frame(self.workspace, bg=colors["bg"])
        self.lbl_cat = tk.Label(self.left_panel, text=LANGUAGES[self.current_lang]["categories"], 
                               font=("Segoe UI", 12, "bold"), bg=colors["bg"])
        self.lbl_cat.pack(anchor="w", pady=(0, 8))
        
        self.category_list = tk.Listbox(self.left_panel, font=("Segoe UI", 10), bd=0, 
                                      highlightthickness=1, relief="solid", selectmode="single", activestyle="none")
        self.category_list.pack(fill="both", expand=True)
        self.category_list.bind("<<ListboxSelect>>", self._on_category_select)
        
        self.workspace.add(self.left_panel, width=280)
        
        # Right Panel - Packages
        self.right_panel = tk.Frame(self.workspace, bg=colors["bg"])
        self.lbl_right_header = tk.Label(self.right_panel, text=LANGUAGES[self.current_lang]["select_category"], 
                                        font=("Segoe UI", 12, "bold"), bg=colors["bg"])
        self.lbl_right_header.pack(anchor="w", pady=(0, 8))
        
        self.canvas = tk.Canvas(self.right_panel, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=self.canvas.yview)
        self.scroll_content = tk.Frame(self.canvas)
        
        self.scroll_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame_id, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Batch operation buttons (inside scroll_content, below the list)
        self.batch_buttons_frame = tk.Frame(self.scroll_content, bg=colors["bg"])
        
        self.btn_install_all = ttk.Button(self.batch_buttons_frame, text=LANGUAGES[self.current_lang]["btn_install_all"], 
                                         style="Accent.TButton", cursor="hand2", command=self.install_all_packages)
        self.btn_install_all.pack(side="left", padx=5)
        
        self.btn_uninstall_all = ttk.Button(self.batch_buttons_frame, text=LANGUAGES[self.current_lang]["btn_uninstall_all"], 
                                            style="Danger.TButton", cursor="hand2", command=self.uninstall_all_packages)
        self.btn_uninstall_all.pack(side="left", padx=5)
        
        self.btn_update_all = ttk.Button(self.batch_buttons_frame, text=LANGUAGES[self.current_lang]["btn_update_all"], 
                                        style="Success.TButton", cursor="hand2", command=self.update_all_packages)
        self.btn_update_all.pack(side="left", padx=5)
        
        self.workspace.add(self.right_panel)
    
    def _create_debug_console(self):
        """Create the debug console for logs."""
        colors = THEME_CONFIG[self.theme_mode]
        
        self.debug_frame = tk.Frame(self, bg=colors["bg"])
        
        self.debug_console = scrolledtext.ScrolledText(self.debug_frame, font=("Consolas", 9), height=10, 
                                                      bd=0, highlightthickness=1, relief="solid", state="disabled")
        self.debug_console.pack(side="left", fill="both", expand=True)
        
        self.btn_save_logs = ttk.Button(self.debug_frame, text="💾", width=2,
                                        style="Secondary.TButton", cursor="hand2", command=self.save_logs_to_file)
        self.btn_save_logs.pack(side="right", padx=2, pady=2)
    
    def _create_status_bar(self):
        """Create the status bar."""
        colors = THEME_CONFIG[self.theme_mode]
        
        self.status_bar = tk.Frame(self, bd=0, height=26)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.lbl_status_text = tk.Label(self.status_bar, text=LANGUAGES[self.current_lang]["status_ready"], 
                                       anchor="w", font=("Segoe UI", 9, "bold"))
        self.lbl_status_text.pack(side="left", fill="x", expand=True, padx=10, pady=2)
        
        self.progress_bar = ttk.Progressbar(self.status_bar, mode="indeterminate", length=160)
        
        self.lbl_author_watermark = tk.Label(self.status_bar, text="Sebastian Januchowski", 
                                            font=("Segoe UI", 9, "italic"), anchor="e")
        self.lbl_author_watermark.pack(side="right", padx=15, pady=2)
    
    def _apply_theme_styles(self):
        """Apply theme styles to all widgets."""
        colors = THEME_CONFIG[self.theme_mode]
        
        # Main window
        self.configure(bg=colors["bg"])
        
        # Frames
        self.top_bar.configure(bg=colors["bg"])
        self.top_buttons.configure(bg=colors["bg"])
        self.search_bar.configure(bg=colors["bg"])
        self.left_panel.configure(bg=colors["bg"])
        self.right_panel.configure(bg=colors["bg"])
        self.workspace.configure(bg=colors["bg"])
        self.canvas.configure(bg=colors["bg"])
        self.scroll_content.configure(bg=colors["bg"])
        self.status_bar.configure(bg=colors["bg_entry"])
        
        # Labels
        self.lbl_header.configure(fg=colors["fg"], bg=colors["bg"])
        self.lbl_search.configure(fg=colors["fg"], bg=colors["bg"])
        self.lbl_interpreter.configure(fg=colors["fg"], bg=colors["bg"])
        self.lbl_cat.configure(fg=colors["fg"], bg=colors["bg"])
        self.lbl_right_header.configure(fg=colors["fg"], bg=colors["bg"])
        self.lbl_status_text.configure(fg=colors["accent"] if self.theme_mode == "dark" else colors["fg"], 
                                      bg=colors["bg_entry"])
        self.lbl_author_watermark.configure(fg=colors["text_muted"], bg=colors["bg_entry"])
        
        # Entries
        self.search_ctrl.configure(bg=colors["bg_entry"], fg=colors["fg"], insertbackground=colors["fg"], 
                                   highlightbackground=colors["border"], highlightcolor=colors["accent"])
        self.txt_interpreter.configure(bg=colors["bg_entry"], fg=colors["text_muted"], 
                                      highlightbackground=colors["border"], highlightcolor=colors["border"])
        
        # Listbox
        self.category_list.configure(bg=colors["bg_entry"], fg=colors["fg"], selectbackground=colors["accent"], 
                                    selectforeground="#121214" if self.theme_mode == "light" else "white", 
                                    highlightbackground=colors["border"], highlightcolor=colors["accent"])
        
        # Debug console
        self.debug_console.configure(bg=colors["bg_entry"], fg=colors["text_muted"] if self.theme_mode == "dark" else colors["fg"], 
                                     highlightbackground=colors["border"], highlightcolor=colors["border"])
        
        # Button styles
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=(10, 5), borderwidth=1, focuscolor="none")
        
        if self.theme_mode == "dark":
            self.style.configure("Accent.TButton", background=colors["accent"], foreground="white", bordercolor=colors["border"])
            self.style.map("Accent.TButton", background=[("active", colors["accent_hover"])])
            
            self.style.configure("Secondary.TButton", background="#202024", foreground="#e1e1e6", bordercolor="#323238")
            self.style.map("Secondary.TButton", background=[("active", "#323238")])
            
            self.style.configure("Success.TButton", background="#1b4d3e", foreground="#a7f3d0", bordercolor="#1f3a35")
            self.style.map("Success.TButton", background=[("active", "#22c55e")])
            
            self.style.configure("Danger.TButton", background="#4c1d1d", foreground="#fca5a5", bordercolor="#3f1d1d")
            self.style.map("Danger.TButton", background=[("active", "#ef4444")])
            
            self.style.configure("TProgressbar", thickness=8, troughcolor="#202024", background="#00adb5", bordercolor="#323238")
        else:
            self.style.configure("Accent.TButton", background=colors["accent"], foreground="white", bordercolor=colors["border"])
            self.style.map("Accent.TButton", background=[("active", colors["accent_hover"])])
            
            self.style.configure("Secondary.TButton", background="#ffffff", foreground="#475569", bordercolor="#e2e8f0")
            self.style.map("Secondary.TButton", background=[("active", "#f1f5f9")])
            
            self.style.configure("Success.TButton", background="#bbf7d0", foreground="#166534", bordercolor="#86efac")
            self.style.map("Success.TButton", background=[("active", "#4ade80")])
            
            self.style.configure("Danger.TButton", background="#fee2e2", foreground="#991b1b", bordercolor="#fca5a5")
            self.style.map("Danger.TButton", background=[("active", "#f87171")])
            
            self.style.configure("TProgressbar", thickness=8, troughcolor="#e2e8f0", background="#0ea5e9", bordercolor="#cbd5e1")
        
        # Update existing package rows
        for row in self.package_rows.values():
            row.update_theme(self.theme_mode)
    
    def _update_category_listbox(self):
        """Update the category listbox with current language."""
        current_selection = self.category_list.curselection()
        selected_cat_id = None
        if current_selection:
            cat_keys = list(BIBLIOTEKI.keys())
            if current_selection[0] < len(cat_keys):
                selected_cat_id = cat_keys[current_selection[0]]
        
        self.category_list.delete(0, tk.END)
        translations = LANGUAGES[self.current_lang]["cat_names"]
        
        for idx, cat_id in enumerate(BIBLIOTEKI.keys()):
            display_name = translations.get(cat_id, cat_id)
            self.category_list.insert(tk.END, display_name)
            if cat_id == selected_cat_id or cat_id == self.current_category_id:
                self.category_list.selection_set(idx)
    
    def _check_ui_queue(self):
        """Check for UI updates from background threads and process them."""
        if not self._running:
            return
        
        while True:
            item = self._ui_queue.get(timeout=0.01)
            if item is None:
                break
            
            action = item.get("action")
            data = item.get("data", {})
            
            if action == "log":
                self._log_debug(data.get("text", ""))
            elif action == "scan_complete":
                self.installed_packages = data.get("packages", {})
                self._log_debug(f"Scan complete. Found {len(self.installed_packages)} packages.")
                self._log_debug("Installed packages:")
                for pkg_name, version in sorted(self.installed_packages.items()):
                    version_str = f"=={version}" if version else ""
                    self._log_debug(f"  {pkg_name}{version_str}")
                self.lbl_status_text.config(text=LANGUAGES[self.current_lang]["status_ready"])
                self._refresh_package_view()
            elif action == "scan_failed":
                self._log_debug(f"Scan failed: {data.get('error', '')}")
                self._refresh_package_view()
            elif action == "pip_complete":
                self._on_pip_action_finished(data.get("package_name"), data.get("action"), 
                                            True, data.get("output"))
            elif action == "pip_failed":
                self._on_pip_action_finished(data.get("package_name"), data.get("action"), 
                                            False, data.get("error"))
        
        self.after(100, self._check_ui_queue)
    
    def _log_debug(self, text: str):
        """Add text to the debug console."""
        self.debug_console.config(state="normal")
        self.debug_console.insert(tk.END, text + "\n")
        self.debug_console.see(tk.END)
        self.debug_console.config(state="disabled")
    
    def _on_close(self):
        """Handle window close event."""
        self._running = False
        
        # Clean up package rows
        for row in self.package_rows.values():
            row.cleanup()
        self.package_rows.clear()
        
        self.destroy()
        sys.exit(0)
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.btn_theme.config(text=LANGUAGES[self.current_lang]["theme_light"] if self.theme_mode == "light" 
                             else LANGUAGES[self.current_lang]["theme_dark"])
        self._apply_theme_styles()
        self._refresh_package_view()
    
    def toggle_language(self):
        """Toggle between English and Polish."""
        self.current_lang = "PL" if self.current_lang == "EN" else "EN"
        lang = LANGUAGES[self.current_lang]
        
        self.title(lang["title"])
        self.lbl_header.config(text=lang["header"])
        self.btn_refresh.config(text=lang["refresh_btn"])
        self.btn_install_file.config(text=lang["btn_install_file"])
        self.btn_install_all.config(text=lang["btn_install_all"])
        self.btn_uninstall_all.config(text=lang["btn_uninstall_all"])
        self.btn_update_all.config(text=lang["btn_update_all"])
        self.btn_toggle_debug.config(text=lang["btn_debug_hide"] if self.debug_visible else lang["btn_debug_show"])
        self.btn_theme.config(text=lang["theme_light"] if self.theme_mode == "light" else lang["theme_dark"])
        self.btn_lang.config(text=self.current_lang)
        self.lbl_search.config(text=lang["search_label"])
        self.lbl_interpreter.config(text=lang["python_exec_label"])
        self.btn_choose_python.config(text=lang["choose_interpreter_btn"])
        self.lbl_cat.config(text=lang["categories"])
        self.lbl_status_text.config(text=lang["status_ready"])
        
        self._update_category_listbox()
        
        # Update existing package rows
        for row in self.package_rows.values():
            row.update_language(self.current_lang)
        
        self._refresh_package_view()
    
    def toggle_debug_panel(self):
        """Toggle visibility of the debug console."""
        self.debug_visible = not self.debug_visible
        lang = LANGUAGES[self.current_lang]
        if self.debug_visible:
            self.debug_frame.pack(before=self.status_bar, fill="x", padx=25, pady=5)
            self.btn_toggle_debug.config(text=lang["btn_debug_hide"])
        else:
            self.debug_frame.pack_forget()
            self.btn_toggle_debug.config(text=lang["btn_debug_show"])
    
    def save_logs_to_file(self):
        """Save debug logs to a file."""
        lang = LANGUAGES[self.current_lang]
        logs_text = self.debug_console.get("1.0", tk.END).strip()
        
        file_path = filedialog.asksaveasfilename(
            title=lang["btn_save_logs"],
            defaultextension=".txt",
            initialfile="installer_logs.txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(logs_text)
                messagebox.showinfo(lang["success_title"], lang["save_logs_success"])
            except Exception as e:
                messagebox.showerror(lang["scan_error_title"], lang["save_logs_error"].format(str(e)))
    
    def install_from_file(self):
        """Parse packages from a file and display them for individual installation."""
        lang = LANGUAGES[self.current_lang]
        
        file_path = filedialog.askopenfilename(
            title="Select dependency file",
            filetypes=[
                ("Requirements files", "requirements*.txt"),
                ("Setup files", "setup.py"),
                ("PyProject files", "pyproject.toml"),
                ("Conda environment files", "environment*.yml"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        file_name = os.path.basename(file_path)
        self._log_debug(f"Selected file: {file_name}")
        
        # Detect file format and parse accordingly
        file_type = self._detect_file_format(file_path, file_name)
        
        if file_type == "requirements":
            packages = self._parse_requirements_file(file_path)
        elif file_type == "setup":
            packages = self._parse_setup_file(file_path)
        elif file_type == "pyproject":
            packages = self._parse_pyproject_file(file_path)
        elif file_type == "conda":
            messagebox.showwarning("Warning", "Conda environment files require conda. Please use conda directly.")
            return
        else:
            messagebox.showerror("Error", f"Unsupported file format: {file_name}")
            return
        
        if not packages:
            messagebox.showinfo("Info", "No packages found in the selected file.")
            return
        
        # Store pending installations
        self.pending_installations = packages
        self._log_debug(f"Parsed {len(packages)} packages from file")
        
        # Display in right panel
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
        
        # Try to detect by content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for requirements.txt format
            if any(line.strip() and not line.strip().startswith('#') for line in content.split('\n')[:10]):
                if any('==' in line or '>=' in line or '<=' in line or '~=' in line for line in content.split('\n')):
                    return "requirements"
            
            # Check for setup.py
            if "setup(" in content or "from setuptools import setup" in content:
                return "setup"
            
            # Check for pyproject.toml
            if "[tool.poetry]" in content or "[build-system]" in content or "[project]" in content:
                return "pyproject"
                
        except Exception:
            pass
        
        return "unknown"
    
    def _parse_requirements_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse requirements.txt file and return list of packages."""
        packages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    # Skip -r includes
                    if line.startswith('-r') or line.startswith('--requirement'):
                        continue
                    # Extract package name and version
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
            self._log_debug(f"Error parsing requirements.txt: {e}")
        return packages
    
    def _parse_setup_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse setup.py file and return package name."""
        packages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse as AST to extract setup() arguments
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # Check if it's a setup() call
                        if isinstance(node.func, ast.Name) and node.func.id == 'setup':
                            for keyword in node.keywords:
                                if keyword.arg == 'name':
                                    if isinstance(keyword.value, ast.Constant):
                                        packages.append({"name": keyword.value.value, "version": ""})
                                        return packages
                                    elif isinstance(keyword.value, ast.Str):
                                        packages.append({"name": keyword.value.s, "version": ""})
                                        return packages
            except Exception:
                pass
            
            # Fallback to regex parsing
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                packages.append({"name": name_match.group(1), "version": ""})
            else:
                # Final fallback to directory name
                dir_name = os.path.basename(os.path.dirname(file_path))
                if dir_name:
                    packages.append({"name": dir_name, "version": ""})
        except Exception as e:
            self._log_debug(f"Error parsing setup.py: {e}")
        return packages
    
    def _parse_pyproject_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse pyproject.toml file and return package name."""
        packages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to extract name from [project] section (PEP 621)
            name_match = re.search(r'\[project\][\s\S]*?name\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            if name_match:
                packages.append({"name": name_match.group(1), "version": ""})
                return packages
            
            # Try to extract name from [tool.poetry] section
            name_match = re.search(r'\[tool\.poetry\][\s\S]*?name\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            if name_match:
                packages.append({"name": name_match.group(1), "version": ""})
                return packages
            
            # Try to extract name from [tool.setuptools] section
            name_match = re.search(r'\[tool\.setuptools\][\s\S]*?name\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            if name_match:
                packages.append({"name": name_match.group(1), "version": ""})
                return packages
            
            # Final fallback to directory name
            dir_name = os.path.basename(os.path.dirname(file_path))
            if dir_name:
                packages.append({"name": dir_name, "version": ""})
        except Exception as e:
            self._log_debug(f"Error parsing pyproject.toml: {e}")
        return packages
    
    def _display_pending_installations(self, file_name: str):
        """Display parsed packages in right panel with install buttons."""
        lang = LANGUAGES[self.current_lang]
        colors = THEME_CONFIG[self.theme_mode]
        
        # Clear current view
        self.current_category_id = None
        self.search_filter = ""
        self.search_ctrl.delete(0, tk.END)
        
        # Update header
        self.lbl_right_header.config(text=f"Packages from: {file_name}")
        
        # Clear existing package rows
        for row in self.package_rows.values():
            row.cleanup()
        self.package_rows.clear()
        
        # Clear widgets but preserve batch_buttons_frame
        for widget in self.scroll_content.winfo_children():
            if widget != self.batch_buttons_frame:
                widget.destroy()
        
        # Display each package with install button
        for pkg in self.pending_installations:
            pkg_name = pkg["name"]
            version = pkg["version"]
            is_installed = pkg_name.lower() in self.installed_packages
            
            row = PackageRowTk(self.scroll_content, pkg_name, is_installed, 
                             self._handle_pending_installation, self.current_lang, 
                             self.theme_mode, version, is_pending=True)
            self.package_rows[pkg_name] = row
        
        # Show batch buttons for pending installations at the bottom
        self.batch_buttons_frame.pack(anchor="center", pady=(15, 5))
        
        # Enable/disable buttons based on installed packages in the list
        installed_count = sum(1 for pkg in self.pending_installations if pkg["name"].lower() in self.installed_packages)
        self.btn_install_all.config(state="normal")
        self.btn_uninstall_all.config(state="normal" if installed_count > 0 else "disabled")
        self.btn_update_all.config(state="normal" if installed_count > 0 else "disabled")
    
    def _execute_pip_action(self, package_name: str, action: str):
        """Execute pip install/upgrade/uninstall action in background thread."""
        if action == "install":
            cmd = [self.python_executable, "-m", "pip", "install", package_name]
        elif action == "upgrade":
            cmd = [self.python_executable, "-m", "pip", "install", "--upgrade", package_name]
        elif action == "uninstall":
            cmd = [self.python_executable, "-m", "pip", "uninstall", "-y", package_name]
        else:
            return
        
        self._ui_queue.put({"action": "log", "data": {"text": f"Executing: {' '.join(cmd)}"}})
        
        success, stdout, stderr = run_subprocess_with_timeout(cmd, timeout=TIMEOUT_PIP_ACTION)
        
        if success:
            self._ui_queue.put({"action": "pip_complete", "data": {
                "package_name": package_name,
                "action": action,
                "output": stdout
            }})
        else:
            self._ui_queue.put({"action": "pip_failed", "data": {
                "package_name": package_name,
                "action": action,
                "error": stderr
            }})

    def _handle_pending_installation(self, package_name: str, row_widget: PackageRowTk, action: str):
        """Handle installation/uninstallation/upgrade of a single package from pending list."""
        lang = LANGUAGES[self.current_lang]
        
        if action == "install":
            status_text = lang["preparing"].format(package_name)
        elif action == "upgrade":
            status_text = lang["preparing_upgrade"].format(package_name)
        elif action == "uninstall":
            status_text = lang["preparing_uninstall"].format(package_name)
        else:
            return
        
        self.lbl_status_text.config(text=status_text)
        self.progress_bar.pack(side="right", padx=25)
        self.progress_bar.start(10)
        
        threading.Thread(target=self._execute_pip_action, args=(package_name, action), daemon=True).start()
    
    def install_all_packages(self):
        """Install all pending packages from the list."""
        if not self.pending_installations:
            return
        
        lang = LANGUAGES[self.current_lang]
        self._log_debug(f"Installing {len(self.pending_installations)} packages...")
        
        # Install packages one by one (including already installed ones)
        for pkg in self.pending_installations:
            pkg_name = pkg["name"]
            self._handle_pending_installation(pkg_name, None, "install")
    
    def uninstall_all_packages(self):
        """Uninstall all currently displayed packages."""
        if not self.package_rows:
            return
        
        lang = LANGUAGES[self.current_lang]
        self._log_debug(f"Uninstalling {len(self.package_rows)} packages...")
        
        for pkg_name, row in list(self.package_rows.items()):
            if row.is_installed:
                # Check if this is a pending installation or regular package
                if row.is_pending:
                    self._handle_pending_installation(pkg_name, row, "uninstall")
                else:
                    self._handle_package_action(pkg_name, row, "uninstall")
    
    def update_all_packages(self):
        """Update all currently displayed packages."""
        if not self.package_rows:
            return
        
        lang = LANGUAGES[self.current_lang]
        self._log_debug(f"Updating {len(self.package_rows)} packages...")
        
        for pkg_name, row in list(self.package_rows.items()):
            if row.is_installed:
                # Check if this is a pending installation or regular package
                if row.is_pending:
                    self._handle_pending_installation(pkg_name, row, "upgrade")
                else:
                    self._handle_package_action(pkg_name, row, "upgrade")
    
    def _install_from_requirements(self, file_path: str):
        """Install packages from requirements.txt file."""
        lang = LANGUAGES[self.current_lang]
        self._log_debug(f"Installing from requirements file: {file_path}")
        self.lbl_status_text.config(text="Installing from requirements file...")
        
        def run_install():
            cmd = [self.python_executable, "-m", "pip", "install", "-r", file_path]
            self._ui_queue.put({"action": "log", "data": {"text": f"Executing: {' '.join(cmd)}"}})
            
            success, stdout, stderr = run_subprocess_with_timeout(cmd, timeout=TIMEOUT_PIP_FILE)
            
            if success:
                self._ui_queue.put({"action": "log", "data": {"text": "Installation completed successfully."}})
                self._ui_queue.put({"action": "scan_complete", "data": {"packages": {}}})
            else:
                self._ui_queue.put({"action": "log", "data": {"text": f"Installation failed: {stderr}"}})
                self._ui_queue.put({"action": "scan_failed", "data": {"error": stderr}})
        
        threading.Thread(target=run_install, daemon=True).start()
    
    def _install_from_setup(self, file_path: str):
        """Install package from setup.py file."""
        lang = LANGUAGES[self.current_lang]
        self._log_debug(f"Installing from setup.py file: {file_path}")
        self.lbl_status_text.config(text="Installing from setup.py...")
        
        def run_install():
            # Install in editable mode from the directory containing setup.py
            dir_path = os.path.dirname(file_path)
            if not dir_path:
                dir_path = "."
            
            cmd = [self.python_executable, "-m", "pip", "install", "-e", dir_path]
            self._ui_queue.put({"action": "log", "data": {"text": f"Executing: {' '.join(cmd)}"}})
            
            success, stdout, stderr = run_subprocess_with_timeout(cmd, timeout=TIMEOUT_PIP_FILE)
            
            if success:
                self._ui_queue.put({"action": "log", "data": {"text": "Installation completed successfully."}})
                self._ui_queue.put({"action": "scan_complete", "data": {"packages": {}}})
            else:
                self._ui_queue.put({"action": "log", "data": {"text": f"Installation failed: {stderr}"}})
                self._ui_queue.put({"action": "scan_failed", "data": {"error": stderr}})
        
        threading.Thread(target=run_install, daemon=True).start()
    
    def _install_from_pyproject(self, file_path: str):
        """Install package from pyproject.toml file."""
        lang = LANGUAGES[self.current_lang]
        self._log_debug(f"Installing from pyproject.toml file: {file_path}")
        self.lbl_status_text.config(text="Installing from pyproject.toml...")
        
        def run_install():
            # Install in editable mode from the directory containing pyproject.toml
            dir_path = os.path.dirname(file_path)
            if not dir_path:
                dir_path = "."
            
            cmd = [self.python_executable, "-m", "pip", "install", "-e", dir_path]
            self._ui_queue.put({"action": "log", "data": {"text": f"Executing: {' '.join(cmd)}"}})
            
            success, stdout, stderr = run_subprocess_with_timeout(cmd, timeout=TIMEOUT_PIP_FILE)
            
            if success:
                self._ui_queue.put({"action": "log", "data": {"text": "Installation completed successfully."}})
                self._ui_queue.put({"action": "scan_complete", "data": {"packages": {}}})
            else:
                self._ui_queue.put({"action": "log", "data": {"text": f"Installation failed: {stderr}"}})
                self._ui_queue.put({"action": "scan_failed", "data": {"error": stderr}})
        
        threading.Thread(target=run_install, daemon=True).start()
    
    def refresh_installed_packages(self):
        """Refresh the list of installed packages by running pip freeze."""
        self._log_debug("Scanning python environment packages...")
        self.lbl_status_text.config(text="Scanning packages...")
        
        def run_scan():
            cmd = [self.python_executable, "-m", "pip", "freeze"]
            success, stdout, stderr = run_subprocess_with_timeout(cmd, timeout=TIMEOUT_PIP_SCAN)
            
            if success:
                packages = parse_pip_freeze_output(stdout)
                self._ui_queue.put({"action": "scan_complete", "data": {"packages": packages}})
            else:
                self._ui_queue.put({"action": "scan_failed", "data": {"error": stderr}})
        
        threading.Thread(target=run_scan, daemon=True).start()
    
    def _on_category_select(self, event):
        """Handle category selection from the listbox."""
        selection = self.category_list.curselection()
        if selection:
            self.search_filter = ""
            self.search_ctrl.delete(0, tk.END)
            cat_keys = list(BIBLIOTEKI.keys())
            if selection[0] < len(cat_keys):
                self.current_category_id = cat_keys[selection[0]]
            self._refresh_package_view()
    
    def _on_search_text(self):
        """Handle search text input."""
        self.search_filter = self.search_ctrl.get().lower().strip()
        if self.search_filter:
            self.category_list.selection_clear(0, tk.END)
            self.current_category_id = None
        self._refresh_package_view()
    
    def _refresh_package_view(self):
        """Refresh the package view based on current category or search filter."""
        # Clean up existing package rows
        for row in self.package_rows.values():
            row.cleanup()
        self.package_rows.clear()
        
        for widget in self.scroll_content.winfo_children():
            if widget != self.batch_buttons_frame:
                widget.destroy()
        
        lang = LANGUAGES[self.current_lang]
        packages_to_show = []
        
        # Hide batch buttons by default for regular views
        self.batch_buttons_frame.pack_forget()
        
        if self.search_filter:
            self.lbl_right_header.config(text=f"{lang['search_label']} '{self.search_filter}'")
            for cat_id, libs in BIBLIOTEKI.items():
                for lib in libs:
                    if self.search_filter in lib.lower() and lib not in packages_to_show:
                        packages_to_show.append(lib)
        elif self.current_category_id:
            translated_cat_name = lang["cat_names"].get(self.current_category_id, self.current_category_id)
            self.lbl_right_header.config(text=f"{lang['libs_in']}{translated_cat_name}")
            packages_to_show = BIBLIOTEKI.get(self.current_category_id, [])
        else:
            self.lbl_right_header.config(text=lang["select_category"])
            return
        
        if not packages_to_show:
            no_res_lbl = tk.Label(self.scroll_content, text=lang["no_search_results"], 
                                 fg=THEME_CONFIG[self.theme_mode]["text_muted"], 
                                 bg=THEME_CONFIG[self.theme_mode]["bg"], font=("Segoe UI", 10, "italic"))
            no_res_lbl.pack(anchor="w", padx=15, pady=15)
            return
        
        for pkg in packages_to_show:
            is_installed = pkg.lower() in self.installed_packages
            version = self.installed_packages.get(pkg.lower(), "")
            row = PackageRowTk(self.scroll_content, pkg, is_installed, self._handle_package_action, 
                             self.current_lang, self.theme_mode, version)
            self.package_rows[pkg] = row
        
        # Show batch buttons for regular views if there are installed packages
        installed_count = sum(1 for row in self.package_rows.values() if row.is_installed)
        if installed_count > 0:
            self.batch_buttons_frame.pack(anchor="center", pady=(15, 5))
            self.btn_install_all.config(state="disabled")
            self.btn_uninstall_all.config(state="normal")
            self.btn_update_all.config(state="normal")
    
    def choose_python_executable(self):
        """Open file dialog to choose Python interpreter."""
        file_path = filedialog.askopenfilename(
            title=LANGUAGES[self.current_lang]["choose_interpreter_title"],
            filetypes=[("Python Executable", "python.exe python"), ("All Files", "*.*")]
        )
        if file_path:
            # Validate the Python executable
            success, stdout, stderr = run_subprocess_with_timeout([file_path, "--version"], timeout=TIMEOUT_PYTHON_VALIDATE)
            if success and stdout:
                self._log_debug(f"Validated Python interpreter: {file_path} - {stdout.strip()}")
                self.python_executable = file_path
                self.txt_interpreter.config(state="normal")
                self.txt_interpreter.delete(0, tk.END)
                self.txt_interpreter.insert(0, file_path)
                self.txt_interpreter.config(state="readonly")
                self.refresh_installed_packages()
            else:
                error_msg = stderr if stderr else "Unknown error"
                messagebox.showerror("Error", f"Invalid Python interpreter:\n{error_msg}\n\nPlease select a valid Python executable.")
    
    def _handle_package_action(self, package_name: str, row_widget: PackageRowTk, action: str):
        """Handle package install/upgrade/uninstall action."""
        lang = LANGUAGES[self.current_lang]
        status_text = lang[f"preparing" if action == "install" else f"preparing_{action}"].format(package_name)
        
        self.lbl_status_text.config(text=status_text)
        self.progress_bar.pack(side="right", padx=25)
        self.progress_bar.start(10)
        
        threading.Thread(target=self._execute_pip_action, args=(package_name, action), daemon=True).start()
    
    def _on_pip_action_finished(self, package_name: str, action: str, success: bool, output_or_error: str):
        """Handle completion of pip action."""
        lang = LANGUAGES[self.current_lang]
        self._log_debug(output_or_error)
        
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        
        if success:
            self.lbl_status_text.config(text=lang[f"success_{action}_status"].format(package_name))
            messagebox.showinfo(lang["success_title"], lang[f"success_{action}_msg"].format(package_name))
        else:
            self.lbl_status_text.config(text=lang[f"error_{action}_status"].format(package_name))
            summary = summarize_install_output(output_or_error)
            messagebox.showerror(lang["error_title"], lang[f"error_{action}_msg"].format(package_name, summary))
        
        # Re-enable buttons and refresh
        self.refresh_installed_packages()
    
    def show_about_dialog(self):
        """Show the about dialog with high-quality icon."""
        lang = LANGUAGES[self.current_lang]
        colors = THEME_CONFIG[self.theme_mode]
        
        # Create custom about dialog
        about_window = tk.Toplevel(self)
        about_window.title(lang["about_title"])
        about_window.geometry("350x380")
        about_window.configure(bg=colors["bg"])
        about_window.resizable(False, False)
        
        # Center the dialog on screen
        about_window.transient(self)
        about_window.grab_set()
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (350 // 2)
        y = (about_window.winfo_screenheight() // 2) - (380 // 2)
        about_window.geometry(f"350x380+{x}+{y}")
        
        # Main container for centering
        main_frame = tk.Frame(about_window, bg=colors["bg"])
        main_frame.pack(fill="both", expand=True)
        
        # Content frame (centered)
        content_frame = tk.Frame(main_frame, bg=colors["bg"])
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Load and display icon
        if PIL_AVAILABLE:
            try:
                icon_image = Image.open("ppm-ico.ico")
                # Resize for better display in dialog
                icon_image = icon_image.resize((48, 48), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                about_window.iconphoto(False, icon_photo)
                
                icon_label = tk.Label(content_frame, image=icon_photo, bg=colors["bg"])
                icon_label.image = icon_photo  # Keep reference
                icon_label.pack(pady=(0, 8))
            except Exception:
                pass  # Fallback if icon loading fails
        
        # About text using regular Text widget without scrollbar
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
        
        text_widget = tk.Text(content_frame, font=("Segoe UI", 9), 
                             bg=colors["bg"], fg=colors["fg"],
                             bd=0, highlightthickness=0, wrap="word",
                             height=8, width=36)
        text_widget.tag_configure("center", justify="center")
        text_widget.insert("1.0", about_text, "center")
        text_widget.config(state="disabled")
        text_widget.pack(pady=(0, 10))
        
        # Close button
        close_btn = ttk.Button(content_frame, text="Close", style="Accent.TButton", 
                               cursor="hand2", command=about_window.destroy)
        close_btn.pack(pady=(0, 2))


if __name__ == "__main__":
    app = InstallerAppTk()
    app.mainloop()
