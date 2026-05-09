<div align="center">

# 🚀 ClipOCR

**Lightweight Clipboard History & OCR Screenshot Intelligent Management Engine**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/gitstq/ClipOCR)

[简体中文](README.md) | [繁體中文](README_TW.md)

</div>

---

## 🎉 Introduction

ClipOCR is a **zero-dependency, offline-first, privacy-focused** clipboard history manager and OCR screenshot text recognition tool. It perfectly combines clipboard history recording with OCR screenshot recognition, helping developers efficiently manage copy history and quickly extract text from screenshots.

### 💡 Key Highlights

- 🔒 **Zero Dependency** - Pure Python implementation, no complex dependencies
- 🌐 **Offline First** - All data stored locally, no internet required
- 🔐 **Privacy Protection** - Automatic sensitive information filtering, data never leaves your machine
- 🎯 **OCR Integration** - Screenshot and recognize instantly, multi-language support
- 🖥️ **TUI Interface** - Beautiful terminal interactive interface
- ⚡ **Lightweight & Efficient** - Low resource usage, fast response

---

## ✨ Core Features

### 📋 Clipboard History Management
- ✅ **Auto Listen** - Background automatic clipboard change recording
- ✅ **History Search** - Support keyword search and tag filtering
- ✅ **Favorites** - One-click favorite for important content
- ✅ **Smart Tags** - Custom tag classification management
- ✅ **Data Export** - JSON format import/export

### 🔍 OCR Screenshot Recognition
- ✅ **Screenshot Recognition** - One-click screenshot and text extraction
- ✅ **Multi-language Support** - Support Chinese, English, Japanese, Korean and more
- ✅ **Batch Processing** - Support batch image recognition
- ✅ **File Recognition** - Support local image file recognition
- ✅ **Result Saving** - Recognition results automatically saved to history

### 🖥️ TUI Interactive Interface
- ✅ **Beautiful Interface** - Modern TUI based on Textual
- ✅ **Shortcut Support** - Rich keyboard shortcuts
- ✅ **Real-time Preview** - Content details displayed in real-time
- ✅ **Statistics Panel** - Usage statistics at a glance

### 🛠️ Developer Friendly
- ✅ **CLI Commands** - Complete command line interface
- ✅ **Flexible Configuration** - Rich configuration options
- ✅ **Cross-platform** - Support Windows/macOS/Linux
- ✅ **Easy to Extend** - Modular design, easy to customize

---

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- Tesseract OCR (optional, required for OCR features)

### Installation

#### Method 1: pip install

```bash
pip install clipocr
```

#### Method 2: Source install

```bash
git clone https://github.com/gitstq/ClipOCR.git
cd ClipOCR
pip install -r requirements.txt
pip install -e .
```

#### Method 3: Install script

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/gitstq/ClipOCR/main/scripts/install.sh | bash
```

**Windows:**
```powershell
# Download and run install.bat
```

### Install Tesseract OCR

OCR features require Tesseract installation:

- **Windows**: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract tesseract-lang`
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- **Other Linux**: See [Tesseract docs](https://github.com/tesseract-ocr/tesseract)

---

## 📖 Usage Guide

### Launch TUI Interface

```bash
clipocr
```

### Common Commands

```bash
# Background clipboard listening
clipocr --listen

# Screenshot and OCR
clipocr screenshot

# List history
clipocr list

# Search entries
clipocr search "keyword"

# Copy content by ID
clipocr copy 123

# Favorite entry
clipocr favorite 123

# Delete entry
clipocr delete 123

# Show statistics
clipocr stats

# Export data
clipocr export backup.json

# Import data
clipocr import backup.json
```

### TUI Shortcuts

| Shortcut | Function |
|----------|----------|
| `q` | Quit program |
| `r` | Refresh data |
| `s` | Screenshot OCR |
| `f` | Toggle favorite |
| `c` | Copy to clipboard |
| `d` | Delete entry |
| `t` | Add tag |
| `/` | Focus search box |

---

## 💡 Design Philosophy & Roadmap

### Tech Stack

- **Python 3.8+**: Modern Python features, wide compatibility
- **SQLite**: Lightweight local database, zero configuration
- **Textual**: Modern TUI framework, beautiful interface
- **Pillow**: Image processing, screenshot functionality
- **Pytesseract**: OCR text recognition

### Design Principles

1. **Privacy First**: All data stored locally, no cloud upload
2. **Simple & Efficient**: Focused features, smooth operation
3. **Extensibility**: Modular architecture, easy to extend
4. **Cross-platform**: One codebase, multiple platforms

### Roadmap

- [ ] Support image clipboard content
- [ ] Cloud sync (optional)
- [ ] More OCR engine support
- [ ] Plugin system
- [ ] Web interface
- [ ] Mobile support

---

## 📦 Packaging & Deployment

### Build Wheel Package

```bash
python scripts/build.py --wheel
```

### Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build
python scripts/build.py --exe

# Full release package
python scripts/build.py --all --release
```

### Run Tests

```bash
python -m pytest tests/
```

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

### Commit Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tool related

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [Textual](https://github.com/Textualize/textual) - TUI framework
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [Rich](https://github.com/Textualize/rich) - Terminal styling

---

<div align="center">

**⭐ If this project helps you, please give it a Star!**

[GitHub](https://github.com/gitstq/ClipOCR) | [Issues](https://github.com/gitstq/ClipOCR/issues) | [Releases](https://github.com/gitstq/ClipOCR/releases)

</div>
