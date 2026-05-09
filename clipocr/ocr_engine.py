"""
OCR截图文字识别模块
"""

import os
import io
import tempfile
from typing import Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

from .database import Database, ClipboardItem
from .config import Config


@dataclass
class OCRResult:
    """OCR识别结果"""
    text: str
    confidence: float
    language: str
    image_path: Optional[str] = None


class OCREngine:
    """OCR引擎"""
    
    # 支持的语言
    LANGUAGES = {
        "chi_sim": "简体中文",
        "chi_tra": "繁体中文",
        "eng": "English",
        "jpn": "日本語",
        "kor": "한국어",
        "fra": "Français",
        "deu": "Deutsch",
        "spa": "Español",
        "rus": "Русский",
    }
    
    def __init__(self, config: Config, database: Database):
        self.config = config
        self.db = database
        
        self._available = PIL_AVAILABLE and PYTESSERACT_AVAILABLE
        
        if not PIL_AVAILABLE:
            print("警告: Pillow 模块不可用，截图功能将受限")
        if not PYTESSERACT_AVAILABLE:
            print("警告: pytesseract 模块不可用，OCR功能将受限")
        
        # 检查tesseract是否安装
        if PYTESSERACT_AVAILABLE:
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                print("警告: Tesseract OCR 未安装，OCR功能将不可用")
                print("请安装 Tesseract: https://github.com/tesseract-ocr/tesseract")
                self._available = False
    
    @property
    def is_available(self) -> bool:
        """检查OCR是否可用"""
        return self._available
    
    def capture_screenshot(self) -> Optional[Image.Image]:
        """捕获全屏截图"""
        if not PIL_AVAILABLE:
            return None
        
        try:
            # 尝试使用ImageGrab (Windows/macOS)
            screenshot = ImageGrab.grab()
            return screenshot
        except Exception:
            # Linux系统可能需要其他方式
            try:
                import subprocess
                # 使用gnome-screenshot或类似工具
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                temp_file.close()
                
                result = subprocess.run(
                    ['gnome-screenshot', '-f', temp_file.name],
                    capture_output=True
                )
                
                if result.returncode == 0:
                    image = Image.open(temp_file.name)
                    os.unlink(temp_file.name)
                    return image
                else:
                    os.unlink(temp_file.name)
            except Exception:
                pass
        
        return None
    
    def recognize_image(self, image: Image.Image, language: Optional[str] = None) -> OCRResult:
        """识别图片中的文字"""
        if not self._available:
            return OCRResult(
                text="OCR功能不可用，请检查依赖安装",
                confidence=0.0,
                language=""
            )
        
        lang = language or self.config.ocr_language
        
        try:
            # 预处理图片以提高识别率
            processed_image = self._preprocess_image(image)
            
            # 执行OCR
            text = pytesseract.image_to_string(
                processed_image,
                lang=lang,
                config=f'--psm {self.config.ocr_psm}'
            )
            
            # 获取置信度
            data = pytesseract.image_to_data(
                processed_image,
                lang=lang,
                output_type=pytesseract.Output.DICT
            )
            
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence / 100.0,
                language=lang
            )
            
        except Exception as e:
            return OCRResult(
                text=f"OCR识别失败: {str(e)}",
                confidence=0.0,
                language=lang
            )
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """预处理图片以提高OCR准确率"""
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 调整DPI
        image.info['dpi'] = (self.config.ocr_dpi, self.config.ocr_dpi)
        
        return image
    
    def capture_and_recognize(self, language: Optional[str] = None) -> Optional[ClipboardItem]:
        """截图并识别文字"""
        # 捕获截图
        screenshot = self.capture_screenshot()
        if not screenshot:
            return None
        
        # 识别文字
        result = self.recognize_image(screenshot, language)
        
        if result.text:
            # 保存截图到临时文件
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.png', 
                delete=False,
                dir=self.config.data_dir
            )
            screenshot.save(temp_file.name)
            temp_file.close()
            
            # 创建条目
            item = ClipboardItem(
                content=f"[截图] {result.text[:50]}..." if len(result.text) > 50 else f"[截图] {result.text}",
                source="screenshot",
                content_type="ocr",
                ocr_text=result.text,
                tags=f"ocr,{result.language}"
            )
            
            item_id = self.db.add_item(item)
            if item_id:
                item.id = item_id
                return item
        
        return None
    
    def recognize_from_file(self, image_path: str, language: Optional[str] = None) -> Optional[ClipboardItem]:
        """从文件识别图片"""
        if not os.path.exists(image_path):
            return None
        
        try:
            image = Image.open(image_path)
            result = self.recognize_image(image, language)
            
            if result.text:
                item = ClipboardItem(
                    content=f"[图片] {result.text[:50]}..." if len(result.text) > 50 else f"[图片] {result.text}",
                    source="file",
                    content_type="ocr",
                    ocr_text=result.text,
                    tags=f"ocr,{result.language}"
                )
                
                item_id = self.db.add_item(item)
                if item_id:
                    item.id = item_id
                    return item
            
        except Exception:
            pass
        
        return None
    
    def get_supported_languages(self) -> List[Tuple[str, str]]:
        """获取支持的语言列表"""
        if not self._available:
            return []
        
        try:
            # 获取已安装的语言包
            installed = pytesseract.get_languages()
            return [
                (code, name) 
                for code, name in self.LANGUAGES.items() 
                if code in installed
            ]
        except Exception:
            return list(self.LANGUAGES.items())
    
    def batch_recognize(self, image_paths: List[str], language: Optional[str] = None) -> List[ClipboardItem]:
        """批量识别图片"""
        results = []
        for path in image_paths:
            item = self.recognize_from_file(path, language)
            if item:
                results.append(item)
        return results
