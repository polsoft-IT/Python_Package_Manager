# Python Package Manager

![Screenshot](screenshot.png)

<p align="center">
  <img src="https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black" alt="Linux">
  <img src="https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white" alt="macOS">
</p>

A modern, bilingual (EN/PL) Python package manager with an optional graphical user interface (wxPython) and a robust CLI fallback.

<!-- TOC -->
- [About](#about)
- [Screenshot](#screenshot)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Tests](#tests)
- [Contributing](#contributing)
- [License](#license)
<!-- /TOC -->

## About

`Python Package Manager` helps you browse popular Python libraries grouped into categories, detect which are installed in the active environment and install/upgrade/uninstall them. The GUI is optional — the program is import-safe and provides a full-featured CLI.

## Screenshot

Place a screenshot image at `screenshot.png` (or update the path below). The image above should appear directly under the project title when viewed on GitHub.

## Features

- GUI (wxPython) with categorized library browser and install buttons
- Threaded `pip` operations to keep the UI responsive
- CLI fallback with commands: `--list-categories`, `--list-packages`, `--scan-installed`
- `--verbose` to enable debug logging, `--no-gui` to force CLI mode, `--version` to show version
- Multi-language UI (English / Polish)

## Installation

1. Clone the repo:

```bash
git clone https://github.com/polsoft-IT/python-package-manager.git
cd python-package-manager
```

2. (Optional) Create and activate a virtualenv:

```bash
python -m venv .venv
\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS / Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

CLI examples:

```bash
# List categories
python python_package_manager.py --list-categories

# List packages (all)
python python_package_manager.py --list-packages

# List packages by category (accepts PL/EN translations)
python python_package_manager.py --list-packages "GUI (Interfejsy graficzne)"

# Scan installed packages
python python_package_manager.py --scan-installed

# Force CLI even if wx is available
python python_package_manager.py --no-gui --list-categories

# Show program version
python python_package_manager.py --version

# Verbose output
python python_package_manager.py --verbose --scan-installed
```

GUI:

```bash
# Launch GUI if wxPython is installed
python python_package_manager.py

# Force GUI (if available)
python python_package_manager.py --gui
```

## Tests

Run unit and integration tests:

```bash
python -m unittest discover -v tests
```

## Contributing

1. Fork the repo and create a feature branch
2. Run tests locally
3. Open a pull request describing your changes

## License

Add a `LICENSE` file to indicate the project license. If unspecified, treat as proprietary by default.

---

Author: Sebastian Januchowski — polsoft.ITS™ Group
Contact: polsoft.its@mail.com