# PrismPaper 

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

**PrismPaper** is a lightning-fast, multithreaded desktop application that organizes your wallpapers by their dominant color. Built with **PyQt6** and **K-Means Clustering**.

##  Features

* **Smart Color Detection:** Uses K-Means clustering to find the *true* vibrant color, ignoring muddy averages.
* **Selective Sorting:** Choose to sort specific colors (e.g., "Only Red images") or process everything.
* **Selective Accuracy** Control the accuracy of the sorting system , higher accuracy means improved color classification precision - Better detection of dominant colors with stricter filtering
* **Selective Power Mode** _Low Power_ (CPUs <= 2 Cores & RAM < 4 GB & Laptop battery unplugged ) , _Performance_ (Take advantage of full System power), _Auto_ (Automatically detect System ressorces).

* **Multithreaded Processing:** Sorts thousands of images in seconds using parallel processing.
* **Real-time Stats:** Precise progress tracking, time elapsed, and estimated time remaining.

## 🛠️ Full Installation Guide


## 1. Install System Prerequisites

### Windows
1.  Download and install **Python 3.10+** from [python.org](https://www.python.org/downloads/).
    * *Important:* Check the box **"Add Python to PATH"** during installation.
2.  Download and install **Git** from [git-scm.com](https://git-scm.com/download/win).

### Linux (Arch / CachyOS / Manjaro)
```bash
sudo pacman -S python git base-devel
```
### Linux (Ubuntu / Debian / Mint)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```
### Linux (Fedora)
```bash
sudo dnf install python3 python3-pip git
```
## 2. Clone the Repository
Run this in your terminal (PowerShell, CMD, or Terminal):
```bash
git clone https://github.com/jugurthq47/PrismPaper.git
cd PrismPaper
```

## 3. Set Up Virtual Environment
This step isolates the project dependencies from your system.

### Windows (PowerShell)
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```
### Windows (Command Prompt / CMD)
```bash
python -m venv venv
venv\Scripts\activate.bat
```
### Linux / macOS (Bash or Zsh)
```bash
python3 -m venv venv
source venv/bin/activate
```
### Linux (Fish Shell)
```bash
python3 -m venv venv
source venv/bin/activate.fish
```

## 4. Install Dependencies
```bash
pip install -r requirements.txt pyinstaller
```
## 5. Run the Application
```bash
python main.py
```
Note for Linux users on Wayland (Hyprland/Sway): If the window looks blurry or has scaling issues, run:
```bash
QT_QPA_PLATFORM=xcb python main.py
```
## 6. Build Standalone Executable (Optional)
Create a single file that runs without Python installed.

### Windows Build
```bash
Pyinstaller --noconsole --onefile --icon=assets/icon.ico --add-data "assets;assets" --name PrismPaper main.py
```
### Linux Build
```bash
Pyinstaller --noconsole --onefile --icon=assets/icon.ico --add-data "assets:assets" --name PrismPaper main.py
```
The executable file will appear in the /dist folder.
