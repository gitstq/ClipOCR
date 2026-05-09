<div align="center">

# 🚀 ClipOCR

**輕量級剪貼簿歷史與OCR截圖智能管理引擎**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/gitstq/ClipOCR)

[简体中文](README.md) | [English](README_EN.md)

</div>

---

## 🎉 專案介紹

ClipOCR 是一款**零依賴、離線優先、隱私保護**的剪貼簿歷史管理與OCR截圖文字識別工具。它將剪貼簿歷史記錄與OCR截圖識別功能完美結合，幫助開發者高效管理複製歷史，快速提取截圖中的文字內容。

### 💡 核心亮點

- 🔒 **零依賴設計** - 純Python實現，無需複雜依賴
- 🌐 **離線優先** - 所有數據本地存儲，無需連網
- 🔐 **隱私保護** - 敏感信息自動過濾，數據不出本地
- 🎯 **OCR集成** - 截圖即識別，支援多語言
- 🖥️ **TUI界面** - 美觀的終端互動界面
- ⚡ **輕量高效** - 資源佔用低，響應迅速

---

## ✨ 核心特性

### 📋 剪貼簿歷史管理
- ✅ **自動監聽** - 後台自動記錄剪貼簿變化
- ✅ **歷史檢索** - 支援關鍵詞搜索、標籤篩選
- ✅ **收藏功能** - 重要內容一鍵收藏
- ✅ **智能標籤** - 自定義標籤分類管理
- ✅ **數據導出** - JSON格式導入導出

### 🔍 OCR截圖識別
- ✅ **截圖識別** - 一鍵截圖並提取文字
- ✅ **多語言支援** - 支援中英日韓等多國語言
- ✅ **批量處理** - 支援批量圖片識別
- ✅ **文件識別** - 支援本地圖片文件識別
- ✅ **結果保存** - 識別結果自動存入歷史

### 🖥️ TUI互動界面
- ✅ **美觀界面** - 基於Textual的現代化TUI
- ✅ **快捷鍵支援** - 豐富的鍵盤快捷鍵
- ✅ **實時預覽** - 內容詳情實時展示
- ✅ **統計面板** - 使用情況一目了然

### 🛠️ 開發者友好
- ✅ **CLI命令** - 完整的命令行接口
- ✅ **配置靈活** - 豐富的配置選項
- ✅ **跨平台** - 支援Windows/macOS/Linux
- ✅ **易於擴展** - 模組化設計，易於二次開發

---

## 🚀 快速開始

### 環境要求

- Python 3.8 或更高版本
- Tesseract OCR (可選，OCR功能需要)

### 安裝方式

#### 方式一：pip安裝

```bash
pip install clipocr
```

#### 方式二：原始碼安裝

```bash
git clone https://github.com/gitstq/ClipOCR.git
cd ClipOCR
pip install -r requirements.txt
pip install -e .
```

#### 方式三：安裝腳本

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/gitstq/ClipOCR/main/scripts/install.sh | bash
```

**Windows:**
```powershell
# 下載並執行 install.bat
```

### 安裝Tesseract OCR

OCR功能需要安裝Tesseract：

- **Windows**: [下載安裝包](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract tesseract-lang`
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- **其他Linux**: 參考 [Tesseract文檔](https://github.com/tesseract-ocr/tesseract)

---

## 📖 使用指南

### 啟動TUI界面

```bash
clipocr
```

### 常用命令

```bash
# 後台監聽剪貼簿
clipocr --listen

# 截圖並OCR識別
clipocr screenshot

# 列出歷史記錄
clipocr list

# 搜索條目
clipocr search "關鍵詞"

# 複製指定ID的內容
clipocr copy 123

# 收藏條目
clipocr favorite 123

# 刪除條目
clipocr delete 123

# 顯示統計信息
clipocr stats

# 導出數據
clipocr export backup.json

# 導入數據
clipocr import backup.json
```

### TUI快捷鍵

| 快捷鍵 | 功能 |
|--------|------|
| `q` | 退出程式 |
| `r` | 刷新數據 |
| `s` | 截圖OCR |
| `f` | 收藏/取消收藏 |
| `c` | 複製到剪貼簿 |
| `d` | 刪除條目 |
| `t` | 添加標籤 |
| `/` | 聚焦搜索框 |

---

## 💡 設計思路與迭代規劃

### 技術選型

- **Python 3.8+**: 現代Python特性，廣泛兼容
- **SQLite**: 輕量級本地數據庫，零配置
- **Textual**: 現代化TUI框架，界面美觀
- **Pillow**: 圖像處理，截圖功能
- **Pytesseract**: OCR文字識別

### 設計理念

1. **隱私優先**: 所有數據本地存儲，不上傳雲端
2. **簡潔高效**: 功能聚焦，操作流暢
3. **可擴展性**: 模組化架構，易於擴展
4. **跨平台**: 一套代碼，多平台運行

### 後續迭代計劃

- [ ] 支援圖片剪貼簿內容
- [ ] 雲同步功能（可選）
- [ ] 更多OCR引擎支援
- [ ] 插件系統
- [ ] Web界面
- [ ] 移動端支援

---

## 📦 打包與部署

### 構建Wheel包

```bash
python scripts/build.py --wheel
```

### 構建可執行文件

```bash
# 安裝PyInstaller
pip install pyinstaller

# 構建
python scripts/build.py --exe

# 完整發布包
python scripts/build.py --all --release
```

### 執行測試

```bash
python -m pytest tests/
```

---

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

### 提交規範

- `feat:` 新功能
- `fix:` 修復問題
- `docs:` 文檔更新
- `refactor:` 代碼重構
- `test:` 測試相關
- `chore:` 構建/工具相關

---

## 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

## 🙏 致謝

- [Textual](https://github.com/Textualize/textual) - TUI框架
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR引擎
- [Rich](https://github.com/Textualize/rich) - 終端美化

---

<div align="center">

**⭐ 如果這個專案對你有幫助，請給個Star支持一下！**

[GitHub](https://github.com/gitstq/ClipOCR) | [Issues](https://github.com/gitstq/ClipOCR/issues) | [Releases](https://github.com/gitstq/ClipOCR/releases)

</div>
