"""
配置管理模块
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Config:
    """应用配置类"""
    
    # 数据存储路径
    data_dir: str = ""
    
    # 数据库配置
    db_name: str = "clipocr.db"
    
    # 剪贴板监听配置
    clipboard_polling_interval: float = 0.5  # 秒
    max_history_items: int = 1000
    
    # OCR配置
    ocr_language: str = "chi_sim+eng"  # 默认中文简体+英文
    ocr_dpi: int = 300
    ocr_psm: int = 6  # 页面分割模式
    
    # TUI配置
    tui_theme: str = "default"
    tui_page_size: int = 20
    
    # 快捷键配置 (可选)
    hotkey_screenshot: str = "ctrl+shift+s"
    hotkey_show_ui: str = "ctrl+shift+v"
    
    # 隐私配置
    auto_cleanup_days: int = 30  # 自动清理天数，0表示不清理
    exclude_sensitive: bool = True  # 排除敏感信息（如密码）
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.data_dir:
            # 默认数据目录
            self.data_dir = os.path.join(
                Path.home(), 
                ".config" if os.name != 'nt' else "AppData/Roaming",
                "clipocr"
            )
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
    
    @property
    def db_path(self) -> str:
        """获取数据库路径"""
        return os.path.join(self.data_dir, self.db_name)
    
    @property
    def config_path(self) -> str:
        """获取配置文件路径"""
        return os.path.join(self.data_dir, "config.json")
    
    def save(self) -> None:
        """保存配置到文件"""
        config_dict = asdict(self)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls) -> "Config":
        """从文件加载配置"""
        # 先创建默认配置获取路径
        default_config = cls()
        
        if os.path.exists(default_config.config_path):
            try:
                with open(default_config.config_path, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                return cls(**config_dict)
            except Exception:
                pass
        
        # 返回默认配置并保存
        default_config.save()
        return default_config
    
    def update(self, **kwargs) -> None:
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
