"""
剪贴板管理模块
"""

import time
import threading
from typing import Callable, Optional, List
from datetime import datetime

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

from .database import Database, ClipboardItem
from .config import Config


class ClipboardManager:
    """剪贴板管理器"""
    
    def __init__(self, config: Config, database: Database):
        self.config = config
        self.db = database
        self._last_content = ""
        self._running = False
        self._listener_thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[ClipboardItem], None]] = []
        
        if not PYPERCLIP_AVAILABLE:
            print("警告: pyperclip 模块不可用，剪贴板功能将受限")
    
    def start_listening(self) -> None:
        """开始监听剪贴板变化"""
        if self._running:
            return
        
        self._running = True
        self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listener_thread.start()
    
    def stop_listening(self) -> None:
        """停止监听剪贴板变化"""
        self._running = False
        if self._listener_thread:
            self._listener_thread.join(timeout=1.0)
    
    def _listen_loop(self) -> None:
        """监听循环"""
        while self._running:
            try:
                if PYPERCLIP_AVAILABLE:
                    current_content = pyperclip.paste()
                    
                    # 检查内容是否变化
                    if current_content and current_content != self._last_content:
                        self._last_content = current_content
                        self._handle_new_content(current_content, "clipboard")
                        
            except Exception:
                pass
            
            time.sleep(self.config.clipboard_polling_interval)
    
    def _handle_new_content(self, content: str, source: str) -> Optional[ClipboardItem]:
        """处理新内容"""
        if not content or len(content.strip()) == 0:
            return None
        
        # 检查是否可能是敏感信息（简单启发式）
        if self.config.exclude_sensitive and self._is_sensitive(content):
            return None
        
        item = ClipboardItem(
            content=content,
            source=source,
            content_type="text"
        )
        
        item_id = self.db.add_item(item)
        if item_id:
            item.id = item_id
            
            # 触发回调
            for callback in self._callbacks:
                try:
                    callback(item)
                except Exception:
                    pass
            
            return item
        
        return None
    
    def _is_sensitive(self, content: str) -> bool:
        """检查内容是否可能是敏感信息"""
        # 简单启发式：检测可能的密码、密钥等
        sensitive_patterns = [
            "password", "passwd", "pwd",
            "secret", "token", "api_key", "apikey",
            "private_key", "privatekey",
            "-----BEGIN", "-----END"
        ]
        
        content_lower = content.lower()
        for pattern in sensitive_patterns:
            if pattern in content_lower:
                return True
        
        return False
    
    def add_callback(self, callback: Callable[[ClipboardItem], None]) -> None:
        """添加新内容回调"""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[ClipboardItem], None]) -> None:
        """移除回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def copy_to_clipboard(self, content: str) -> bool:
        """复制内容到剪贴板"""
        if not PYPERCLIP_AVAILABLE:
            return False
        
        try:
            pyperclip.copy(content)
            self._last_content = content
            return True
        except Exception:
            return False
    
    def get_history(
        self, 
        limit: int = 100, 
        search: Optional[str] = None,
        favorites_only: bool = False
    ) -> List[ClipboardItem]:
        """获取剪贴板历史"""
        return self.db.get_items(
            limit=limit,
            search=search,
            favorites_only=favorites_only
        )
    
    def add_manual_entry(self, content: str, tags: Optional[List[str]] = None) -> Optional[int]:
        """手动添加条目"""
        item = ClipboardItem(
            content=content,
            source="manual",
            tags=",".join(tags) if tags else ""
        )
        return self.db.add_item(item)
    
    def toggle_favorite(self, item_id: int) -> bool:
        """切换收藏状态"""
        item = self.db.get_item(item_id)
        if item:
            return self.db.update_item(item_id, is_favorite=not item.is_favorite)
        return False
    
    def delete_item(self, item_id: int) -> bool:
        """删除条目"""
        return self.db.delete_item(item_id)
    
    def add_tags(self, item_id: int, tags: List[str]) -> bool:
        """为条目添加标签"""
        return self.db.add_tags(item_id, tags)
    
    def search_items(self, query: str, limit: int = 50) -> List[ClipboardItem]:
        """搜索条目"""
        return self.db.get_items(limit=limit, search=query)
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        return self.db.get_statistics()
