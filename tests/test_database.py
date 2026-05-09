"""
数据库模块测试
"""

import os
import tempfile
import unittest
from datetime import datetime

from clipocr.config import Config
from clipocr.database import Database, ClipboardItem


class TestDatabase(unittest.TestCase):
    """数据库测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config(data_dir=self.temp_dir)
        self.db = Database(self.config)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_item(self):
        """测试添加条目"""
        item = ClipboardItem(
            content="测试内容",
            source="test",
            content_type="text"
        )
        
        item_id = self.db.add_item(item)
        self.assertIsNotNone(item_id)
        self.assertGreater(item_id, 0)
    
    def test_get_item(self):
        """测试获取条目"""
        # 添加条目
        item = ClipboardItem(
            content="测试获取",
            source="test"
        )
        item_id = self.db.add_item(item)
        
        # 获取条目
        retrieved = self.db.get_item(item_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.content, "测试获取")
        self.assertEqual(retrieved.source, "test")
    
    def test_get_items(self):
        """测试获取条目列表"""
        # 添加多个条目
        for i in range(5):
            item = ClipboardItem(
                content=f"内容{i}",
                source="test"
            )
            self.db.add_item(item)
        
        # 获取列表
        items = self.db.get_items(limit=10)
        self.assertEqual(len(items), 5)
    
    def test_update_item(self):
        """测试更新条目"""
        # 添加条目
        item = ClipboardItem(content="原始内容", source="test")
        item_id = self.db.add_item(item)
        
        # 更新
        success = self.db.update_item(item_id, is_favorite=True, tags="重要")
        self.assertTrue(success)
        
        # 验证
        updated = self.db.get_item(item_id)
        self.assertTrue(updated.is_favorite)
        self.assertEqual(updated.tags, "重要")
    
    def test_delete_item(self):
        """测试删除条目"""
        # 添加条目
        item = ClipboardItem(content="待删除", source="test")
        item_id = self.db.add_item(item)
        
        # 删除
        success = self.db.delete_item(item_id)
        self.assertTrue(success)
        
        # 验证
        deleted = self.db.get_item(item_id)
        self.assertIsNone(deleted)
    
    def test_search(self):
        """测试搜索"""
        # 添加条目
        self.db.add_item(ClipboardItem(content="Hello World", source="test"))
        self.db.add_item(ClipboardItem(content="Test Search", source="test"))
        
        # 搜索
        results = self.db.get_items(search="Hello")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "Hello World")
    
    def test_tags(self):
        """测试标签功能"""
        # 添加条目
        item = ClipboardItem(content="带标签", source="test")
        item_id = self.db.add_item(item)
        
        # 添加标签
        success = self.db.add_tags(item_id, ["标签1", "标签2"])
        self.assertTrue(success)
        
        # 验证
        updated = self.db.get_item(item_id)
        self.assertIn("标签1", updated.tags)
        self.assertIn("标签2", updated.tags)
        
        # 获取所有标签
        all_tags = self.db.get_all_tags()
        self.assertIn("标签1", all_tags)
        self.assertIn("标签2", all_tags)
    
    def test_statistics(self):
        """测试统计功能"""
        # 添加条目
        self.db.add_item(ClipboardItem(content="条目1", source="test"))
        self.db.add_item(ClipboardItem(content="条目2", source="test", ocr_text="OCR内容"))
        
        # 获取统计
        stats = self.db.get_statistics()
        self.assertEqual(stats["total_items"], 2)
        self.assertEqual(stats["ocr_items"], 1)


if __name__ == "__main__":
    unittest.main()
