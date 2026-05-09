"""
数据存储模块 - SQLite数据库管理
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

from .config import Config


@dataclass
class ClipboardItem:
    """剪贴板条目数据类"""
    id: Optional[int] = None
    content: str = ""
    content_hash: str = ""
    content_type: str = "text"  # text, image, ocr
    source: str = "clipboard"  # clipboard, screenshot, manual
    ocr_text: Optional[str] = None
    tags: str = ""  # 逗号分隔的标签
    is_favorite: bool = False
    is_deleted: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.content_hash is None and self.content:
            self.content_hash = self._compute_hash(self.content)
    
    @staticmethod
    def _compute_hash(content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()


class Database:
    """SQLite数据库管理类"""
    
    def __init__(self, config: Config):
        self.config = config
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = sqlite3.connect(self.config.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self) -> None:
        """初始化数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建剪贴板历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    content_hash TEXT UNIQUE NOT NULL,
                    content_type TEXT DEFAULT 'text',
                    source TEXT DEFAULT 'clipboard',
                    ocr_text TEXT,
                    tags TEXT DEFAULT '',
                    is_favorite INTEGER DEFAULT 0,
                    is_deleted INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_hash 
                ON clipboard_history(content_hash)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON clipboard_history(created_at DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ocr_text 
                ON clipboard_history(ocr_text)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags 
                ON clipboard_history(tags)
            """)
            
            # 创建统计表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    items_added INTEGER DEFAULT 0,
                    items_deleted INTEGER DEFAULT 0,
                    ocr_performed INTEGER DEFAULT 0
                )
            """)
    
    def add_item(self, item: ClipboardItem) -> Optional[int]:
        """添加剪贴板条目"""
        item.content_hash = ClipboardItem._compute_hash(item.content)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM clipboard_history WHERE content_hash = ?",
                (item.content_hash,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有条目时间戳
                cursor.execute(
                    """UPDATE clipboard_history 
                       SET updated_at = CURRENT_TIMESTAMP 
                       WHERE id = ?""",
                    (existing['id'],)
                )
                return existing['id']
            
            # 插入新条目
            cursor.execute("""
                INSERT INTO clipboard_history 
                (content, content_hash, content_type, source, ocr_text, tags, 
                 is_favorite, is_deleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                item.content, item.content_hash, item.content_type,
                item.source, item.ocr_text, item.tags,
                1 if item.is_favorite else 0,
                1 if item.is_deleted else 0
            ))
            
            return cursor.lastrowid
    
    def get_item(self, item_id: int) -> Optional[ClipboardItem]:
        """获取单个条目"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM clipboard_history WHERE id = ? AND is_deleted = 0",
                (item_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return self._row_to_item(row)
            return None
    
    def get_items(
        self, 
        limit: int = 100, 
        offset: int = 0,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        favorites_only: bool = False,
        source: Optional[str] = None
    ) -> List[ClipboardItem]:
        """获取条目列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM clipboard_history WHERE is_deleted = 0"
            params = []
            
            if search:
                query += " AND (content LIKE ? OR ocr_text LIKE ?)"
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern])
            
            if tags:
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
                query += " AND (" + " OR ".join(tag_conditions) + ")"
            
            if favorites_only:
                query += " AND is_favorite = 1"
            
            if source:
                query += " AND source = ?"
                params.append(source)
            
            query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_item(row) for row in rows]
    
    def update_item(self, item_id: int, **kwargs) -> bool:
        """更新条目"""
        allowed_fields = ['content', 'ocr_text', 'tags', 'is_favorite', 'is_deleted']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        # 转换布尔值
        if 'is_favorite' in updates:
            updates['is_favorite'] = 1 if updates['is_favorite'] else 0
        if 'is_deleted' in updates:
            updates['is_deleted'] = 1 if updates['is_deleted'] else 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            set_clause += ", updated_at = CURRENT_TIMESTAMP"
            
            query = f"UPDATE clipboard_history SET {set_clause} WHERE id = ?"
            params = list(updates.values()) + [item_id]
            
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_item(self, item_id: int, soft_delete: bool = True) -> bool:
        """删除条目"""
        if soft_delete:
            return self.update_item(item_id, is_deleted=True)
        else:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM clipboard_history WHERE id = ?",
                    (item_id,)
                )
                return cursor.rowcount > 0
    
    def add_tags(self, item_id: int, tags: List[str]) -> bool:
        """为条目添加标签"""
        item = self.get_item(item_id)
        if not item:
            return False
        
        existing_tags = set(item.tags.split(",")) if item.tags else set()
        existing_tags.update(tags)
        new_tags = ",".join(sorted(existing_tags))
        
        return self.update_item(item_id, tags=new_tags)
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT tags FROM clipboard_history WHERE is_deleted = 0"
            )
            rows = cursor.fetchall()
            
            all_tags = set()
            for row in rows:
                if row['tags']:
                    all_tags.update(row['tags'].split(","))
            
            return sorted(list(all_tags))
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取统计信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 总条目数
            cursor.execute(
                "SELECT COUNT(*) as count FROM clipboard_history WHERE is_deleted = 0"
            )
            total_items = cursor.fetchone()['count']
            
            # 收藏数
            cursor.execute(
                "SELECT COUNT(*) as count FROM clipboard_history WHERE is_favorite = 1 AND is_deleted = 0"
            )
            favorite_items = cursor.fetchone()['count']
            
            # OCR条目数
            cursor.execute(
                "SELECT COUNT(*) as count FROM clipboard_history WHERE ocr_text IS NOT NULL AND is_deleted = 0"
            )
            ocr_items = cursor.fetchone()['count']
            
            # 今日新增
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                """SELECT COUNT(*) as count FROM clipboard_history 
                   WHERE date(created_at) = ? AND is_deleted = 0""",
                (today,)
            )
            today_items = cursor.fetchone()['count']
            
            return {
                "total_items": total_items,
                "favorite_items": favorite_items,
                "ocr_items": ocr_items,
                "today_items": today_items,
            }
    
    def cleanup_old_items(self, days: int) -> int:
        """清理旧条目"""
        if days <= 0:
            return 0
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """DELETE FROM clipboard_history 
                   WHERE date(created_at) < ? AND is_favorite = 0""",
                (cutoff_date,)
            )
            return cursor.rowcount
    
    def _row_to_item(self, row: sqlite3.Row) -> ClipboardItem:
        """将数据库行转换为ClipboardItem"""
        return ClipboardItem(
            id=row['id'],
            content=row['content'],
            content_hash=row['content_hash'],
            content_type=row['content_type'],
            source=row['source'],
            ocr_text=row['ocr_text'],
            tags=row['tags'],
            is_favorite=bool(row['is_favorite']),
            is_deleted=bool(row['is_deleted']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def export_data(self, filepath: str) -> bool:
        """导出数据到JSON文件"""
        try:
            items = self.get_items(limit=10000)
            data = {
                "export_date": datetime.now().isoformat(),
                "items": [
                    {
                        "content": item.content,
                        "content_type": item.content_type,
                        "source": item.source,
                        "ocr_text": item.ocr_text,
                        "tags": item.tags,
                        "is_favorite": item.is_favorite,
                        "created_at": item.created_at,
                    }
                    for item in items
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def import_data(self, filepath: str) -> int:
        """从JSON文件导入数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for item_data in data.get("items", []):
                item = ClipboardItem(
                    content=item_data.get("content", ""),
                    content_type=item_data.get("content_type", "text"),
                    source=item_data.get("source", "import"),
                    ocr_text=item_data.get("ocr_text"),
                    tags=item_data.get("tags", ""),
                    is_favorite=item_data.get("is_favorite", False),
                )
                if self.add_item(item):
                    imported_count += 1
            
            return imported_count
        except Exception:
            return 0
