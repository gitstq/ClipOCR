@echo off
chcp 65001 >nul
REM ClipOCR 安装脚本 (Windows)

echo 🚀 ClipOCR 安装脚本
echo ==================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.8+
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo ✅ Python版本: %PYTHON_VERSION%

REM 检查是否需要虚拟环境
set /p create_venv="是否创建虚拟环境? (y/n): "
if /i "%create_venv%"=="y" (
    echo 📦 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM 安装依赖
echo 📦 安装依赖...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 检查Tesseract
echo 🔍 检查 Tesseract OCR...
where tesseract >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告: 未找到 Tesseract OCR
    echo    OCR功能需要 Tesseract，请下载安装:
    echo    https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo    安装后请将 Tesseract 添加到系统 PATH
) else (
    for /f "tokens=*" %%a in ('tesseract --version 2^>^&1 ^| findstr "tesseract"') do (
        echo ✅ Tesseract: %%a
    )
)

REM 安装ClipOCR
echo 📦 安装 ClipOCR...
pip install -e .

REM 创建数据目录
echo 📁 创建数据目录...
if not exist "%APPDATA%\clipocr" mkdir "%APPDATA%\clipocr"

echo.
echo ✅ 安装完成！
echo.
echo 🎉 使用方式:
echo    clipocr              启动TUI界面
echo    clipocr --listen     后台监听剪贴板
echo    clipocr screenshot   截图OCR
echo    clipocr --help       查看帮助
echo.

pause
