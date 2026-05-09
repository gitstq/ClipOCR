"""
ClipOCR - 轻量级剪贴板历史与OCR截图智能管理引擎

一个零依赖、离线优先的剪贴板历史管理与OCR截图文字识别工具。
支持多语言OCR、智能标签分类、TUI交互界面。

Author: gitstq
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .clipboard_manager import ClipboardManager
from .ocr_engine import OCREngine
from .database import Database
from .config import Config

__all__ = [
    "ClipboardManager",
    "OCREngine", 
    "Database",
    "Config",
]
