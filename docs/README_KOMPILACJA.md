# Instrukcja kompilacji PPM na Windows 11

<p align="center">
  <img src="https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black" alt="Linux">
  <img src="https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white" alt="macOS">
</p>

## Wymagania wstępne
1. **Python 3.8+** zainstalowany i dodany do PATH
2. Dostęp do internetu (do instalacji bibliotek)

## Szybka kompilacja (automatyczna)
1. Upewnij się, że znajdujesz się w folderze z plikiem `ppm.py`
2. Kliknij dwukrotnie plik `build.bat`
3. Poczekaj na zakończenie kompilacji
4. Skompilowany plik `ppm.exe` znajdziesz w folderze `dist`

## Kompilacja ręczna
Jeśli chcesz skompilować ręcznie, wykonaj poniższe kroki:

1. **Zainstaluj zależności:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Skompiluj za pomocą PyInstaller:**
   ```bash
   pyinstaller --clean ppm.spec
   ```

## Dodatkowe uwagi
- Jeśli masz plik ikony `ppm.ico`, umieść go w tym samym folderze - zostanie on automatycznie użyty
- Aplikacja jest kompilowana jako **jedno plikowe EXE** (bez dodatkowych folderów)
- Domyślnie aplikacja nie pokazuje okna konsoli (`console=False` w `ppm.spec`)
