#!/bin/bash
# ClipOCR 安装脚本 (Linux/macOS)

set -e

echo "🚀 ClipOCR 安装脚本"
echo "=================="

# 检测操作系统
OS=$(uname -s)
ARCH=$(uname -m)

echo "📋 检测到系统: $OS $ARCH"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python版本: $PYTHON_VERSION"

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境? (y/n): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 安装依赖
echo "📦 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 检查Tesseract OCR
echo "🔍 检查 Tesseract OCR..."
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  警告: 未找到 Tesseract OCR"
    echo "   OCR功能需要 Tesseract，请根据您的系统安装:"
    echo ""
    
    case $OS in
        Linux)
            if command -v apt-get &> /dev/null; then
                echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim"
            elif command -v yum &> /dev/null; then
                echo "   CentOS/RHEL: sudo yum install tesseract tesseract-langpack-chi_sim"
            elif command -v pacman &> /dev/null; then
                echo "   Arch: sudo pacman -S tesseract tesseract-data-chi_sim"
            fi
            ;;
        Darwin)
            echo "   macOS: brew install tesseract tesseract-lang"
            ;;
    esac
    
    echo ""
    echo "   更多信息: https://github.com/tesseract-ocr/tesseract"
else
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
    echo "✅ Tesseract: $TESSERACT_VERSION"
fi

# 安装ClipOCR
echo "📦 安装 ClipOCR..."
pip install -e .

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p ~/.config/clipocr

echo ""
echo "✅ 安装完成！"
echo ""
echo "🎉 使用方式:"
echo "   clipocr              # 启动TUI界面"
echo "   clipocr --listen     # 后台监听剪贴板"
echo "   clipocr screenshot   # 截图OCR"
echo "   clipocr --help       # 查看帮助"
echo ""
