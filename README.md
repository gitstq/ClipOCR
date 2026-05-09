<div align="center">

# 🚀 ClipOCR

**轻量级剪贴板历史与OCR截图智能管理引擎**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/gitstq/ClipOCR)

[English](README_EN.md) | [繁體中文](README_TW.md)

</div>

---

## 🎉 项目介绍

ClipOCR 是一款**零依赖、离线优先、隐私保护**的剪贴板历史管理与OCR截图文字识别工具。它将剪贴板历史记录与OCR截图识别功能完美结合，帮助开发者高效管理复制历史，快速提取截图中的文字内容。

### 💡 核心亮点

- 🔒 **零依赖设计** - 纯Python实现，无需复杂依赖
- 🌐 **离线优先** - 所有数据本地存储，无需联网
- 🔐 **隐私保护** - 敏感信息自动过滤，数据不出本地
- 🎯 **OCR集成** - 截图即识别，支持多语言
- 🖥️ **TUI界面** - 美观的终端交互界面
- ⚡ **轻量高效** - 资源占用低，响应迅速

---

## ✨ 核心特性

### 📋 剪贴板历史管理
- ✅ **自动监听** - 后台自动记录剪贴板变化
- ✅ **历史检索** - 支持关键词搜索、标签筛选
- ✅ **收藏功能** - 重要内容一键收藏
- ✅ **智能标签** - 自定义标签分类管理
- ✅ **数据导出** - JSON格式导入导出

### 🔍 OCR截图识别
- ✅ **截图识别** - 一键截图并提取文字
- ✅ **多语言支持** - 支持中英日韩等多国语言
- ✅ **批量处理** - 支持批量图片识别
- ✅ **文件识别** - 支持本地图片文件识别
- ✅ **结果保存** - 识别结果自动存入历史

### 🖥️ TUI交互界面
- ✅ **美观界面** - 基于Textual的现代化TUI
- ✅ **快捷键支持** - 丰富的键盘快捷键
- ✅ **实时预览** - 内容详情实时展示
- ✅ **统计面板** - 使用情况一目了然

### 🛠️ 开发者友好
- ✅ **CLI命令** - 完整的命令行接口
- ✅ **配置灵活** - 丰富的配置选项
- ✅ **跨平台** - 支持Windows/macOS/Linux
- ✅ **易于扩展** - 模块化设计，易于二次开发

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Tesseract OCR (可选，OCR功能需要)

### 安装方式

#### 方式一：pip安装

```bash
pip install clipocr
```

#### 方式二：源码安装

```bash
git clone https://github.com/gitstq/ClipOCR.git
cd ClipOCR
pip install -r requirements.txt
pip install -e .
```

#### 方式三：安装脚本

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/gitstq/ClipOCR/main/scripts/install.sh | bash
```

**Windows:**
```powershell
# 下载并运行 install.bat
```

### 安装Tesseract OCR

OCR功能需要安装Tesseract：

- **Windows**: [下载安装包](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract tesseract-lang`
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- **其他Linux**: 参考 [Tesseract文档](https://github.com/tesseract-ocr/tesseract)

---

## 📖 使用指南

### 启动TUI界面

```bash
clipocr
```

### 常用命令

```bash
# 后台监听剪贴板
clipocr --listen

# 截图并OCR识别
clipocr screenshot

# 列出历史记录
clipocr list

# 搜索条目
clipocr search "关键词"

# 复制指定ID的内容
clipocr copy 123

# 收藏条目
clipocr favorite 123

# 删除条目
clipocr delete 123

# 显示统计信息
clipocr stats

# 导出数据
clipocr export backup.json

# 导入数据
clipocr import backup.json
```

### TUI快捷键

| 快捷键 | 功能 |
|--------|------|
| `q` | 退出程序 |
| `r` | 刷新数据 |
| `s` | 截图OCR |
| `f` | 收藏/取消收藏 |
| `c` | 复制到剪贴板 |
| `d` | 删除条目 |
| `t` | 添加标签 |
| `/` | 聚焦搜索框 |

---

## 💡 设计思路与迭代规划

### 技术选型

- **Python 3.8+**: 现代Python特性，广泛兼容
- **SQLite**: 轻量级本地数据库，零配置
- **Textual**: 现代化TUI框架，界面美观
- **Pillow**: 图像处理，截图功能
- **Pytesseract**: OCR文字识别

### 设计理念

1. **隐私优先**: 所有数据本地存储，不上传云端
2. **简洁高效**: 功能聚焦，操作流畅
3. **可扩展性**: 模块化架构，易于扩展
4. **跨平台**: 一套代码，多平台运行

### 后续迭代计划

- [ ] 支持图片剪贴板内容
- [ ] 云同步功能（可选）
- [ ] 更多OCR引擎支持
- [ ] 插件系统
- [ ] Web界面
- [ ] 移动端支持

---

## 📦 打包与部署

### 构建Wheel包

```bash
python scripts/build.py --wheel
```

### 构建可执行文件

```bash
# 安装PyInstaller
pip install pyinstaller

# 构建
python scripts/build.py --exe

# 完整发布包
python scripts/build.py --all --release
```

### 运行测试

```bash
python -m pytest tests/
```

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 提交规范

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

- [Textual](https://github.com/Textualize/textual) - TUI框架
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR引擎
- [Rich](https://github.com/Textualize/rich) - 终端美化

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**

[GitHub](https://github.com/gitstq/ClipOCR) | [Issues](https://github.com/gitstq/ClipOCR/issues) | [Releases](https://github.com/gitstq/ClipOCR/releases)

</div>
