#!/usr/bin/env python3
"""
构建脚本 - 用于打包ClipOCR
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def run_command(cmd, cwd=None):
    """运行命令"""
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False
    if result.stdout:
        print(result.stdout)
    return True


def clean_build():
    """清理构建目录"""
    print("🧹 清理构建目录...")
    dirs_to_remove = ['build', 'dist', '*.egg-info', '__pycache__']
    for pattern in dirs_to_remove:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  删除: {path}")


def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    return run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])


def build_wheel():
    """构建wheel包"""
    print("🔨 构建Wheel包...")
    return run_command([sys.executable, '-m', 'pip', 'install', 'wheel', 'build']) and \
           run_command([sys.executable, '-m', 'build', '--wheel'])


def build_executable():
    """使用PyInstaller构建可执行文件"""
    print("🔨 构建可执行文件...")
    
    # 检查PyInstaller
    result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'pyinstaller'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("安装 PyInstaller...")
        if not run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller']):
            return False
    
    # 构建命令
    system = platform.system()
    exe_name = "clipocr.exe" if system == "Windows" else "clipocr"
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', exe_name,
        '--clean',
        '--noconfirm',
        '--hidden-import', 'PIL',
        '--hidden-import', 'pytesseract',
        '--hidden-import', 'rich',
        '--hidden-import', 'textual',
        '--hidden-import', 'pyperclip',
        'clipocr/cli.py'
    ]
    
    if run_command(cmd):
        print(f"✅ 可执行文件已生成: dist/{exe_name}")
        return True
    return False


def create_release_package():
    """创建发布包"""
    print("📦 创建发布包...")
    
    system = platform.system().lower()
    arch = platform.machine().lower()
    version = "1.0.0"
    
    package_name = f"clipocr-v{version}-{system}-{arch}"
    package_dir = Path(f"dist/{package_name}")
    
    # 创建目录
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制文件
    files_to_copy = [
        ('README.md', 'README.md'),
        ('LICENSE', 'LICENSE'),
        ('requirements.txt', 'requirements.txt'),
    ]
    
    # 复制可执行文件
    exe_name = "clipocr.exe" if system == "windows" else "clipocr"
    exe_path = Path(f"dist/{exe_name}")
    if exe_path.exists():
        shutil.copy2(exe_path, package_dir / exe_name)
    
    # 复制其他文件
    for src, dst in files_to_copy:
        if Path(src).exists():
            shutil.copy2(src, package_dir / dst)
    
    # 创建压缩包
    archive_path = f"dist/{package_name}"
    shutil.make_archive(archive_path, 'zip', package_dir)
    
    print(f"✅ 发布包已创建: {archive_path}.zip")
    return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ClipOCR 构建脚本')
    parser.add_argument('--clean', action='store_true', help='清理构建目录')
    parser.add_argument('--wheel', action='store_true', help='构建Wheel包')
    parser.add_argument('--exe', action='store_true', help='构建可执行文件')
    parser.add_argument('--all', action='store_true', help='执行完整构建')
    parser.add_argument('--release', action='store_true', help='创建发布包')
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if not any([args.clean, args.wheel, args.exe, args.all, args.release]):
        parser.print_help()
        return 0
    
    # 切换到项目根目录
    os.chdir(Path(__file__).parent.parent)
    
    success = True
    
    if args.clean or args.all:
        clean_build()
    
    if args.wheel or args.all:
        success = success and install_dependencies() and build_wheel()
    
    if args.exe or args.all:
        success = success and build_executable()
    
    if args.release and success:
        success = success and create_release_package()
    
    if success:
        print("\n✅ 构建成功！")
        return 0
    else:
        print("\n❌ 构建失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
