import sys
import os
import subprocess
import threading
import logging
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

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
        "title": "Python Package Installer (Tkinter - Dark Mode)",
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
        "refresh_btn": "🔄 Refresh",
        "btn_debug_show": "🛠 Show Logs",
        "btn_debug_hide": "🛠 Hide Logs",
        "about_title": "About Program",
        "about_msg": "A modern desktop client designed to streamline pip operations. Built using Python and Tkinter.",
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
        "title": "Instalator Pakietów Python (Tkinter - Dark Mode)",
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
        "refresh_btn": "🔄 Odśwież",
        "btn_debug_show": "🛠 Pokaż Logi",
        "btn_debug_hide": "🛠 Ukryj Logi",
        "about_title": "O programie",
        "about_msg": "Nowoczesny klient okienkowy usprawniający zarządzanie pakietami pip. Stworzony w Pythonie i Tkinterze.",
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
    "version": "2.0.1",
    "author": "Sebastian Januchowski",
    "company": "polsoft.ITS(TM) Group",
    "github": "https://github.com/polsoft-IT",
    "email": "polsoft.its@mail.com",
    "description": "An advanced and lightweight desktop GUI wrapper for handling Python environment configurations and pip package control flows effortlessly."
}

def parse_pip_freeze_output(output):
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
    if not output:
        return ""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"


class AboutDialog(tk.Toplevel):
    def __init__(self, parent, lang_code):
        super().__init__(parent)
        self.lang_code = lang_code
        self.init_ui()

    def init_ui(self):
        lang = LANGUAGES[self.lang_code]
        self.title(lang["about_title"])
        self.geometry("480x420")
        self.resizable(False, False)
        self.configure(bg="#1e293b")
        self.transient(self.master)
        self.grab_set()

        lbl_logo = tk.Label(self, text="📦", font=("Segoe UI", 38), bg="#1e293b", fg="#f8fafc")
        lbl_logo.pack(pady=(20, 2))

        lbl_title = tk.Label(self, text=METADATA["name"], font=("Segoe UI", 14, "bold"), bg="#1e293b", fg="#f8fafc")
        lbl_title.pack()

        lbl_version = tk.Label(self, text=f"v{METADATA['version']}", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#94a3b8")
        lbl_version.pack(pady=(0, 5))

        lbl_desc = tk.Label(self, text=lang["about_msg"], font=("Segoe UI", 11), bg="#1e293b", fg="#cbd5e1", wraplength=420, justify="center")
        lbl_desc.pack(pady=(0, 15))

        meta_frame = tk.Frame(self, bg="#0f172a", bd=1, relief="solid")
        meta_frame.pack(fill="x", padx=25, pady=5)

        rows = [
            ("Author", METADATA["author"]),
            ("Company", METADATA["company"]),
            ("GitHub", METADATA["github"]),
            ("Email", METADATA["email"])
        ]

        for idx, (label_text, value_text) in enumerate(rows):
            lbl_key = tk.Label(meta_frame, text=f"{label_text}:", font=("Segoe UI", 10, "bold"), bg="#0f172a", fg="#94a3b8", anchor="w")
            lbl_key.grid(row=idx, column=0, sticky="w", padx=(15, 10), pady=4)

            is_link = "http" in value_text or "@" in value_text
            val_fg = "#38bdf8" if is_link else "#e2e8f0"
            lbl_val = tk.Label(meta_frame, text=value_text, font=("Segoe UI", 10), bg="#0f172a", fg=val_fg, anchor="w")
            lbl_val.grid(row=idx, column=1, sticky="w", padx=(0, 15), pady=4)

        btn_close = ttk.Button(self, text="OK", command=self.destroy)
        btn_close.pack(side="bottom", pady=20)


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg="#0f172a")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#0f172a")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class PackageRowTk(tk.Frame):
    def __init__(self, parent, package_name, is_installed, install_callback, current_lang, installed_version=""):
        super().__init__(parent, bg="#1e293b", bd=1, relief="solid", highlightthickness=0)
        self.package_name = package_name
        self.install_callback = install_callback
        self.current_lang = current_lang
        self.is_installed = is_installed
        self.installed_version = installed_version

        self.pack(fill="x", padx=10, pady=4, ipady=6)

        self.lbl_name = tk.Label(self, text=package_name, font=("Segoe UI", 11, "bold"), bg="#1e293b", fg="#f8fafc", anchor="w")
        self.lbl_name.pack(side="left", padx=15, fill="x", expand=True)

        self.lbl_status = tk.Label(self, font=("Segoe UI", 10, "bold"), bg="#1e293b", anchor="e")
        
        self.btn_install = ttk.Button(self, command=lambda: self.install_callback(self.package_name, self, "install"))
        self.btn_update = ttk.Button(self, command=lambda: self.install_callback(self.package_name, self, "upgrade"))
        self.btn_uninstall = ttk.Button(self, command=lambda: self.install_callback(self.package_name, self, "uninstall"))

        self.update_ui()

    def update_ui(self):
        lang = LANGUAGES[self.current_lang]
        self.btn_install.config(text=lang["install_btn"])
        self.btn_update.config(text=lang["update_btn"])
        self.btn_uninstall.config(text=lang["uninstall_btn"])

        self.btn_install.state(["!disabled"])
        self.btn_update.state(["!disabled"])
        self.btn_uninstall.state(["!disabled"])

        if self.is_installed:
            version_str = f" ({self.installed_version})" if self.installed_version else ""
            self.lbl_status.config(text=f"✓ {lang['installed']}{version_str}", fg="#4ade80")
            self.lbl_status.pack(side="left", padx=10)
            self.config(highlightbackground="#16a34a", highlightcolor="#16a34a", highlightthickness=1)
            
            self.btn_install.pack_forget()
            self.btn_update.pack(side="right", padx=5)
            self.btn_uninstall.pack(side="right", padx=(5, 15))
        else:
            self.lbl_status.pack_forget()
            self.config(highlightthickness=0)
            
            self.btn_update.pack_forget()
            self.btn_uninstall.pack_forget()
            self.btn_install.pack(side="right", padx=15)

    def set_loading(self, action):
        lang = LANGUAGES[self.current_lang]
        self.btn_install.state(["disabled"])
        self.btn_update.state(["disabled"])
        self.btn_uninstall.state(["disabled"])
        if action == "install":
            self.btn_install.config(text=lang["installing"])


class InstallerAppTk:
    def __init__(self, root):
        self.root = root
        self.current_lang = "EN"
        self.debug_visible = False
        self.python_executable = sys.executable
        self.search_filter = ""
        self.current_category = None
        self.zainstalowane_pakiety = {}

        self.init_styles()
        self.init_ui()
        self.refresh_installed_packages()

    def init_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Konfiguracja ciemnych stylów dla elementów Ttk
        self.style.configure(".", font=("Segoe UI", 10), background="#0f172a", foreground="#f8fafc")
        
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), background="#1e293b", foreground="#f8fafc", borderwidth=0, padding=6)
        self.style.map("TButton", background=[("hover", "#334155"), ("disabled", "#0f172a")], foreground=[("disabled", "#64748b")])
        
        self.style.configure("TScrollbar", background="#1e293b", troughcolor="#0f172a", borderwidth=0, arrowsize=12)
        self.style.map("TScrollbar", background=[("hover", "#334155")])
        
        self.style.configure("TProgressbar", background="#38bdf8", troughcolor="#1e293b", borderwidth=0)

    def init_ui(self):
        self.root.title(LANGUAGES[self.current_lang]["title"])
        self.root.geometry("980x720")
        self.root.minsize(850, 620)
        self.root.configure(bg="#0f172a")

        # Top Bar
        top_frame = tk.Frame(self.root, bg="#0f172a")
        top_frame.pack(fill="x", padx=20, pady=(15, 5))

        self.lbl_header = tk.Label(top_frame, text=LANGUAGES[self.current_lang]["header"], font=("Segoe UI", 16, "bold"), bg="#0f172a", fg="#f8fafc")
        self.lbl_header.pack(side="left")

        self.btn_about = ttk.Button(top_frame, text="ℹ️", width=4, command=self.show_about_dialog)
        self.btn_about.pack(side="right", padx=2)

        self.btn_lang = ttk.Button(top_frame, text="🌐 EN / PL", command=self.toggle_language)
        self.btn_lang.pack(side="right", padx=2)

        self.btn_toggle_debug = ttk.Button(top_frame, text=LANGUAGES[self.current_lang]["btn_debug_show"], command=self.toggle_debug_panel)
        self.btn_toggle_debug.pack(side="right", padx=2)

        self.btn_refresh = ttk.Button(top_frame, text=LANGUAGES[self.current_lang]["refresh_btn"], command=self.refresh_installed_packages)
        self.btn_refresh.pack(side="right", padx=2)

        # Search & Interpreter Bar
        search_frame = tk.Frame(self.root, bg="#0f172a")
        search_frame.pack(fill="x", padx=20, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_text)
        
        self.search_ctrl = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 10), bg="#1e293b", fg="#f8fafc", insertbackground="white", bd=1, relief="solid")
        self.search_ctrl.pack(side="left", fill="x", expand=True, padx=(0, 15), ipady=4)
        
        self.placeholder_text = LANGUAGES[self.current_lang]["search_placeholder"]
        self.search_var.set(self.placeholder_text)
        self.search_ctrl.config(fg="#64748b")
        self.search_ctrl.bind("<FocusIn>", self.clear_placeholder)
        self.search_ctrl.bind("<FocusOut>", self.set_placeholder)

        self.lbl_interpreter = tk.Label(search_frame, text=LANGUAGES[self.current_lang]["python_exec_label"], font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#94a3b8")
        self.lbl_interpreter.pack(side="left", padx=(0, 5))

        self.txt_interpreter = tk.Entry(search_frame, font=("Segoe UI", 10), bg="#0f172a", fg="#94a3b8", bd=1, relief="solid")
        self.txt_interpreter.insert(0, self.python_executable)
        self.txt_interpreter.config(state="readonly")
        self.txt_interpreter.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=4)

        self.btn_choose_python = ttk.Button(search_frame, text=LANGUAGES[self.current_lang]["choose_interpreter_btn"], command=self.choose_python_executable)
        self.btn_choose_python.pack(side="left")

        # Main Splitter Area
        self.pane = tk.PanedWindow(self.root, orient="horizontal", bd=0, bg="#334155", sashwidth=3)
        self.pane.pack(fill="both", expand=True, padx=20, pady=10)

        # Left panel: Categories
        left_panel = tk.Frame(self.pane, bg="#0f172a")
        self.lbl_cat = tk.Label(left_panel, text=LANGUAGES[self.current_lang]["categories"], font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#94a3b8")
        self.lbl_cat.pack(anchor="w", pady=(0, 2))
        
        self.category_list = tk.Listbox(left_panel, font=("Segoe UI", 10), bg="#1e293b", fg="#f8fafc", bd=1, relief="solid", highlightthickness=0, selectbackground="#38bdf8", selectforeground="#0f172a")
        self.category_list.pack(fill="both", expand=True)
        self.category_list.bind("<<ListboxSelect>>", self.on_category_select)
        
        self.pane.add(left_panel, width=260)

        # Right panel: Packages View
        right_panel = tk.Frame(self.pane, bg="#0f172a")
        self.lbl_right_header = tk.Label(right_panel, text=LANGUAGES[self.current_lang]["select_category"], font=("Segoe UI", 11, "bold"), bg="#0f172a", fg="#f8fafc")
        self.lbl_right_header.pack(anchor="w", pady=(0, 4))

        self.scroll_frame = ScrollableFrame(right_panel)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.pane.add(right_panel, width=660)

        # Debug Console
        self.debug_console = tk.Text(self.root, height=8, font=("Consolas", 10), bg="#1e293b", fg="#e2e8f0", insertbackground="white", bd=1, relief="solid")
        
        # Status Bar
        status_frame = tk.Frame(self.root, bg="#0f172a", bd=1, relief="flat")
        status_frame.pack(fill="x", side="bottom")

        self.lbl_status = tk.Label(status_frame, text=LANGUAGES[self.current_lang]["status_ready"], bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9))
        self.lbl_status.pack(side="left", padx=5, pady=4)

        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", length=160, mode="determinate")
        self.progress_bar.pack(side="right", padx=10, pady=4)

        self.update_category_listbox()

    def set_placeholder(self, event=None):
        if not self.search_var.get().strip():
            self.placeholder_text = LANGUAGES[self.current_lang]["search_placeholder"]
            self.search_var.set(self.placeholder_text)
            self.search_ctrl.config(fg="#64748b")

    def clear_placeholder(self, event=None):
        if self.search_var.get() == self.placeholder_text:
            self.search_var.set("")
            self.search_ctrl.config(fg="#f8fafc")

    def update_category_listbox(self):
        self.category_list.delete(0, tk.END)
        lang = LANGUAGES[self.current_lang]
        for cat_raw in BIBLIOTEKI.keys():
            translated_key = CATEGORY_MAP.get(cat_raw, cat_raw)
            display_name = lang.get(translated_key, cat_raw)
            self.category_list.insert(tk.END, display_name)

    def toggle_language(self):
        self.current_lang = "PL" if self.current_lang == "EN" else "EN"
        lang = LANGUAGES[self.current_lang]

        self.root.title(lang["title"])
        self.lbl_header.config(text=lang["header"])
        self.btn_refresh.config(text=lang["refresh_btn"])
        self.btn_toggle_debug.config(text=lang["btn_debug_hide"] if self.debug_visible else lang["btn_debug_show"])
        self.lbl_interpreter.config(text=lang["python_exec_label"])
        self.btn_choose_python.config(text=lang["choose_interpreter_btn"])
        self.lbl_cat.config(text=lang["categories"])

        if self.search_var.get() == self.placeholder_text or not self.search_var.get():
            self.placeholder_text = lang["search_placeholder"]
            self.search_var.set(self.placeholder_text)
            self.search_ctrl.config(fg="#64748b")

        self.update_category_listbox()
        self.refresh_package_view()

    def toggle_debug_panel(self):
        self.debug_visible = not self.debug_visible
        lang = LANGUAGES[self.current_lang]
        if self.debug_visible:
            self.debug_console.pack(fill="x", padx=20, pady=(0, 10), before=self.root.pack_slaves()[-1])
            self.btn_toggle_debug.config(text=lang["btn_debug_hide"])
        else:
            self.debug_console.pack_forget()
            self.btn_toggle_debug.config(text=lang["btn_debug_show"])

    def log_debug(self, text):
        self.debug_console.insert(tk.END, text + "\n")
        self.debug_console.see(tk.END)

    def refresh_installed_packages(self):
        self.log_debug("Scanning python environment packages...")
        
        def run_scan():
            try:
                result = subprocess.run([self.python_executable, "-m", "pip", "freeze"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace", check=True)
                self.zainstalowane_pakiety = parse_pip_freeze_output(result.stdout)
                self.log_debug(f"Scan complete. Found {len(self.zainstalowane_pakiety)} packages.")
                self.root.after(0, self.refresh_package_view)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(LANGUAGES[self.current_lang]["scan_error_title"], LANGUAGES[self.current_lang]["scan_error_msg"].format(str(e))))

        threading.Thread(target=run_scan, daemon=True).start()

    def on_category_select(self, event):
        selection = self.category_list.curselection()
        if selection:
            index = selection[0]
            self.current_category = list(BIBLIOTEKI.keys())[index]
            self.search_filter = ""
            self.refresh_package_view()

    def on_search_text(self, *args):
        val = self.search_var.get()
        if val != self.placeholder_text:
            self.search_filter = val.lower().strip()
            self.refresh_package_view()

    def choose_python_executable(self):
        file_filter = [("Python", "python.exe"), ("All Files", "*.*")] if sys.platform == "win32" else [("All Files", "*")]
        filename = filedialog.askopenfilename(title=LANGUAGES[self.current_lang]["choose_interpreter_title"], filetypes=file_filter)
        if filename:
            self.python_executable = filename
            self.txt_interpreter.config(state="normal")
            self.txt_interpreter.delete(0, tk.END)
            self.txt_interpreter.insert(0, filename)
            self.txt_interpreter.config(state="readonly")
            self.refresh_installed_packages()

    def show_about_dialog(self):
        AboutDialog(self.root, self.current_lang)

    def handle_package_action(self, package_name, row_widget, action):
        lang = LANGUAGES[self.current_lang]
        row_widget.set_loading(action)
        
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(10)

        if action == "install":
            self.lbl_status.config(text=lang["preparing"].format(package_name))
            cmd = [self.python_executable, "-m", "pip", "install", package_name]
        elif action == "upgrade":
            self.lbl_status.config(text=lang["preparing_upgrade"].format(package_name))
            cmd = [self.python_executable, "-m", "pip", "install", "--upgrade", package_name]
        elif action == "uninstall":
            self.lbl_status.config(text=lang["preparing_uninstall"].format(package_name))
            cmd = [self.python_executable, "-m", "pip", "uninstall", "-y", package_name]

        def run_pip():
            self.log_debug(f"Executing: {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace", check=True)
                self.root.after(0, lambda: self.on_action_finished(package_name, action, True, result.stdout))
            except subprocess.CalledProcessError as e:
                self.root.after(0, lambda: self.on_action_finished(package_name, action, False, e.stderr or e.stdout))

        threading.Thread(target=run_pip, daemon=True).start()

    def on_action_finished(self, package_name, action, success, output):
        lang = LANGUAGES[self.current_lang]
        self.log_debug(output)
        
        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate", value=0)

        self.refresh_installed_packages()
        
        if success:
            if action == "install":
                msg = lang["success_install_msg"].format(package_name)
                self.lbl_status.config(text=lang["success_install_status"].format(package_name))
            elif action == "upgrade":
                msg = lang["success_upgrade_msg"].format(package_name)
                self.lbl_status.config(text=lang["success_upgrade_status"].format(package_name))
            elif action == "uninstall":
                msg = lang["success_uninstall_msg"].format(package_name)
                self.lbl_status.config(text=lang["success_uninstall_status"].format(package_name))
            
            messagebox.showinfo(lang["success_title"], msg, parent=self.root)
        else:
            if action == "install":
                msg = lang["error_install_msg"].format(package_name, summarize_install_output(output))
                self.lbl_status.config(text=lang["error_install_status"].format(package_name))
            elif action == "upgrade":
                msg = lang["error_upgrade_msg"].format(package_name, summarize_install_output(output))
                self.lbl_status.config(text=lang["error_upgrade_status"].format(package_name))
            elif action == "uninstall":
                msg = lang["error_uninstall_msg"].format(package_name, summarize_install_output(output))
                self.lbl_status.config(text=lang["error_uninstall_status"].format(package_name))
            
            messagebox.showerror(lang["error_title"], msg, parent=self.root)

    def refresh_package_view(self):
        for widget in self.scroll_frame.scrollable_frame.winfo_children():
            widget.destroy()

        lang = LANGUAGES[self.current_lang]
        packages_to_show = []

        if self.search_filter and self.search_filter != self.placeholder_text.lower():
            prefix = "🔍 Wyniki dla: " if self.current_lang == "PL" else "🔍 Results for: "
            self.lbl_right_header.config(text=f"{prefix}'{self.search_filter}'")
            for cat, libs in BIBLIOTEKI.items():
                for lib in libs:
                    if self.search_filter in lib.lower() and lib not in packages_to_show:
                        packages_to_show.append(lib)
        elif self.current_category:
            translated_cat_key = CATEGORY_MAP.get(self.current_category, self.current_category)
            display_name = lang.get(translated_cat_key, self.current_category)
            self.lbl_right_header.config(text=f"{lang['libs_in']}{display_name}")
            packages_to_show = BIBLIOTEKI.get(self.current_category, [])
        else:
            self.lbl_right_header.config(text=lang["select_category"])
            return

        if not packages_to_show:
            lbl_empty = tk.Label(self.scroll_frame.scrollable_frame, text=lang["no_search_results"], font=("Segoe UI", 10, "italic"), bg="#0f172a", fg="#64748b")
            lbl_empty.pack(anchor="w", padx=15, pady=10)
            return

        for pkg in sorted(packages_to_show):
            is_installed = pkg.lower() in self.zainstalowane_pakiety
            version = self.zainstalowane_pakiety.get(pkg.lower(), "")
            PackageRowTk(self.scroll_frame.scrollable_frame, pkg, is_installed, self.handle_package_action, self.current_lang, version)


if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerAppTk(root)
    root.mainloop()