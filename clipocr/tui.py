"""
TUI交互界面模块 - 使用Textual库
"""

from typing import List, Optional
from datetime import datetime

try:
    from textual.app import App, ComposeResult
    from textual.widgets import (
        Header, Footer, DataTable, Input, Button, 
        Static, Label, ListView, ListItem, TextArea,
        TabbedContent, TabPane, Markdown
    )
    from textual.containers import Horizontal, Vertical, Container
    from textual.reactive import reactive
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    # 创建占位类
    class App:
        pass
    class ComposeResult:
        pass

from .database import Database, ClipboardItem
from .clipboard_manager import ClipboardManager
from .ocr_engine import OCREngine
from .config import Config


class ClipOCRApp(App):
    """ClipOCR TUI应用"""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    #search-input {
        width: 100%;
        margin-bottom: 1;
    }
    
    #content-table {
        width: 100%;
        height: 60%;
        border: solid green;
    }
    
    #detail-panel {
        width: 100%;
        height: 30%;
        border: solid blue;
        padding: 1;
    }
    
    #stats-panel {
        width: 100%;
        height: auto;
        background: $surface-darken-1;
        padding: 1;
    }
    
    .button-bar {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    
    Button {
        margin-right: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("r", "refresh", "刷新"),
        Binding("s", "screenshot", "截图OCR"),
        Binding("f", "toggle_favorite", "收藏"),
        Binding("d", "delete", "删除"),
        Binding("c", "copy", "复制"),
        Binding("t", "add_tag", "添加标签"),
        Binding("/", "focus_search", "搜索"),
    ]
    
    def __init__(self, config: Config, db: Database, clipboard: ClipboardManager, ocr: OCREngine):
        if not TEXTUAL_AVAILABLE:
            raise ImportError("Textual库不可用，无法启动TUI界面")
        
        super().__init__()
        self.config = config
        self.db = db
        self.clipboard = clipboard
        self.ocr = ocr
        self.current_items: List[ClipboardItem] = []
        self.selected_item: Optional[ClipboardItem] = None
    
    def compose(self) -> ComposeResult:
        """构建UI"""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            # 统计面板
            with Static(id="stats-panel"):
                yield Label("📊 加载统计信息...")
            
            # 搜索输入框
            yield Input(placeholder="🔍 搜索剪贴板内容...", id="search-input")
            
            # 数据表格
            yield DataTable(id="content-table")
            
            # 详情面板
            with Static(id="detail-panel"):
                yield Label("选择条目查看详情")
            
            # 按钮栏
            with Horizontal(classes="button-bar"):
                yield Button("📸 截图OCR", id="btn-screenshot", variant="primary")
                yield Button("⭐ 收藏", id="btn-favorite")
                yield Button("📋 复制", id="btn-copy")
                yield Button("🏷️ 标签", id="btn-tag")
                yield Button("🗑️ 删除", id="btn-delete", variant="error")
                yield Button("🔄 刷新", id="btn-refresh")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """应用挂载时"""
        self.title = "ClipOCR - 剪贴板历史与OCR管理"
        
        # 初始化表格
        table = self.query_one("#content-table", DataTable)
        table.add_columns("ID", "类型", "内容预览", "标签", "⭐", "时间")
        table.cursor_type = "row"
        
        # 加载数据
        self.refresh_data()
        self.update_stats()
    
    def refresh_data(self, search: Optional[str] = None) -> None:
        """刷新数据"""
        table = self.query_one("#content-table", DataTable)
        table.clear()
        
        self.current_items = self.db.get_items(
            limit=self.config.tui_page_size,
            search=search
        )
        
        for item in self.current_items:
            content_preview = item.content[:50] + "..." if len(item.content) > 50 else item.content
            content_preview = content_preview.replace("\n", " ")
            
            favorite_mark = "⭐" if item.is_favorite else ""
            
            table.add_row(
                str(item.id),
                item.content_type,
                content_preview,
                item.tags or "",
                favorite_mark,
                item.updated_at[:16] if item.updated_at else ""
            )
    
    def update_stats(self) -> None:
        """更新统计信息"""
        stats = self.db.get_statistics()
        stats_label = self.query_one("#stats-panel", Static)
        stats_text = (
            f"📊 总计: {stats['total_items']} | "
            f"⭐ 收藏: {stats['favorite_items']} | "
            f"🔍 OCR: {stats['ocr_items']} | "
            f"📅 今日: {stats['today_items']}"
        )
        stats_label.update(stats_text)
    
    def on_data_table_row_selected(self, event) -> None:
        """表格行选中事件"""
        if event.row_key:
            row_index = int(event.row_key.value)
            if 0 <= row_index < len(self.current_items):
                self.selected_item = self.current_items[row_index]
                self.update_detail_panel()
    
    def update_detail_panel(self) -> None:
        """更新详情面板"""
        detail = self.query_one("#detail-panel", Static)
        
        if not self.selected_item:
            detail.update("选择条目查看详情")
            return
        
        item = self.selected_item
        content = f"""
📋 **内容详情**

**ID:** {item.id}
**类型:** {item.content_type}
**来源:** {item.source}
**标签:** {item.tags or '无'}
**收藏:** {'⭐ 是' if item.is_favorite else '否'}
**创建时间:** {item.created_at}
**更新时间:** {item.updated_at}

---

**完整内容:**
```
{item.content}
```
"""
        
        if item.ocr_text:
            content += f"""

**OCR识别结果:**
```
{item.ocr_text}
```
"""
        
        detail.update(content)
    
    def on_input_changed(self, event) -> None:
        """搜索输入变化"""
        if event.input.id == "search-input":
            self.refresh_data(search=event.value if event.value else None)
    
    def on_button_pressed(self, event) -> None:
        """按钮点击事件"""
        button_id = event.button.id
        
        if button_id == "btn-screenshot":
            self.action_screenshot()
        elif button_id == "btn-favorite":
            self.action_toggle_favorite()
        elif button_id == "btn-copy":
            self.action_copy()
        elif button_id == "btn-tag":
            self.action_add_tag()
        elif button_id == "btn-delete":
            self.action_delete()
        elif button_id == "btn-refresh":
            self.action_refresh()
    
    def action_refresh(self) -> None:
        """刷新动作"""
        self.refresh_data()
        self.update_stats()
        self.notify("数据已刷新", severity="information")
    
    def action_screenshot(self) -> None:
        """截图OCR动作"""
        if not self.ocr.is_available:
            self.notify("OCR功能不可用，请检查依赖", severity="error")
            return
        
        self.notify("正在截图并识别...", severity="information")
        
        try:
            item = self.ocr.capture_and_recognize()
            if item:
                self.notify(f"OCR识别成功！ID: {item.id}", severity="success")
                self.refresh_data()
                self.update_stats()
            else:
                self.notify("未识别到文字", severity="warning")
        except Exception as e:
            self.notify(f"截图OCR失败: {str(e)}", severity="error")
    
    def action_toggle_favorite(self) -> None:
        """切换收藏动作"""
        if not self.selected_item:
            self.notify("请先选择条目", severity="warning")
            return
        
        success = self.db.update_item(
            self.selected_item.id, 
            is_favorite=not self.selected_item.is_favorite
        )
        
        if success:
            self.selected_item.is_favorite = not self.selected_item.is_favorite
            self.notify("收藏状态已更新", severity="success")
            self.refresh_data()
            self.update_detail_panel()
    
    def action_copy(self) -> None:
        """复制动作"""
        if not self.selected_item:
            self.notify("请先选择条目", severity="warning")
            return
        
        content = self.selected_item.ocr_text or self.selected_item.content
        if self.clipboard.copy_to_clipboard(content):
            self.notify("已复制到剪贴板", severity="success")
        else:
            self.notify("复制失败", severity="error")
    
    def action_add_tag(self) -> None:
        """添加标签动作"""
        if not self.selected_item:
            self.notify("请先选择条目", severity="warning")
            return
        
        # 简化实现：直接添加一个示例标签
        # 完整实现应该弹出输入框
        self.db.add_tags(self.selected_item.id, ["重要"])
        self.notify("标签已添加", severity="success")
        self.refresh_data()
    
    def action_delete(self) -> None:
        """删除动作"""
        if not self.selected_item:
            self.notify("请先选择条目", severity="warning")
            return
        
        self.db.delete_item(self.selected_item.id)
        self.notify("条目已删除", severity="success")
        self.selected_item = None
        self.refresh_data()
        self.update_stats()
        self.update_detail_panel()
    
    def action_focus_search(self) -> None:
        """聚焦搜索框"""
        self.query_one("#search-input", Input).focus()


class SimpleTUI:
    """简单TUI界面（当Textual不可用时使用）"""
    
    def __init__(self, config: Config, db: Database, clipboard: ClipboardManager, ocr: OCREngine):
        self.config = config
        self.db = db
        self.clipboard = clipboard
        self.ocr = ocr
    
    def run(self) -> None:
        """运行简单命令行界面"""
        print("\n" + "="*60)
        print("🚀 ClipOCR - 轻量级剪贴板历史与OCR截图智能管理引擎")
        print("="*60)
        print("\n📋 可用命令:")
        print("  list    - 显示剪贴板历史")
        print("  search  - 搜索条目")
        print("  ocr     - 截图并识别文字")
        print("  copy    - 复制指定ID的内容")
        print("  fav     - 收藏/取消收藏")
        print("  del     - 删除条目")
        print("  stats   - 显示统计信息")
        print("  export  - 导出数据")
        print("  quit    - 退出程序")
        print("-"*60)
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "quit" or command == "q":
                    print("👋 再见！")
                    break
                
                elif command == "list" or command == "l":
                    self._list_items()
                
                elif command == "search" or command == "s":
                    query = input("搜索关键词: ").strip()
                    self._list_items(search=query)
                
                elif command == "ocr" or command == "o":
                    self._do_ocr()
                
                elif command == "copy" or command == "c":
                    item_id = input("条目ID: ").strip()
                    self._copy_item(item_id)
                
                elif command == "fav" or command == "f":
                    item_id = input("条目ID: ").strip()
                    self._toggle_favorite(item_id)
                
                elif command == "del" or command == "d":
                    item_id = input("条目ID: ").strip()
                    self._delete_item(item_id)
                
                elif command == "stats":
                    self._show_stats()
                
                elif command == "export" or command == "e":
                    filepath = input("导出文件路径: ").strip()
                    self._export_data(filepath)
                
                else:
                    print("❌ 未知命令，请重试")
            
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
    
    def _list_items(self, search: Optional[str] = None) -> None:
        """列出条目"""
        items = self.db.get_items(limit=20, search=search)
        
        if not items:
            print("📭 暂无条目")
            return
        
        print(f"\n{'ID':<6}{'类型':<10}{'⭐':<4}{'内容预览':<40}{'时间'}")
        print("-"*80)
        
        for item in items:
            fav = "⭐" if item.is_favorite else ""
            preview = item.content[:35] + "..." if len(item.content) > 35 else item.content
            preview = preview.replace("\n", " ")
            time_str = item.updated_at[5:16] if item.updated_at else ""
            
            print(f"{item.id:<6}{item.content_type:<10}{fav:<4}{preview:<40}{time_str}")
    
    def _do_ocr(self) -> None:
        """执行OCR"""
        if not self.ocr.is_available:
            print("❌ OCR功能不可用")
            return
        
        print("📸 正在截图并识别...")
        item = self.ocr.capture_and_recognize()
        
        if item:
            print(f"✅ 识别成功！ID: {item.id}")
            print(f"📝 识别内容:\n{item.ocr_text[:200]}...")
        else:
            print("❌ 识别失败或未识别到文字")
    
    def _copy_item(self, item_id: str) -> None:
        """复制条目"""
        try:
            item = self.db.get_item(int(item_id))
            if item:
                content = item.ocr_text or item.content
                if self.clipboard.copy_to_clipboard(content):
                    print("✅ 已复制到剪贴板")
                else:
                    print("❌ 复制失败")
            else:
                print("❌ 条目不存在")
        except ValueError:
            print("❌ 无效的ID")
    
    def _toggle_favorite(self, item_id: str) -> None:
        """切换收藏"""
        try:
            item = self.db.get_item(int(item_id))
            if item:
                self.db.update_item(item.id, is_favorite=not item.is_favorite)
                print("✅ 收藏状态已更新")
            else:
                print("❌ 条目不存在")
        except ValueError:
            print("❌ 无效的ID")
    
    def _delete_item(self, item_id: str) -> None:
        """删除条目"""
        try:
            confirm = input("确认删除? (y/n): ").strip().lower()
            if confirm == 'y':
                self.db.delete_item(int(item_id))
                print("✅ 已删除")
            else:
                print("已取消")
        except ValueError:
            print("❌ 无效的ID")
    
    def _show_stats(self) -> None:
        """显示统计"""
        stats = self.db.get_statistics()
        print(f"\n📊 统计信息:")
        print(f"  总计条目: {stats['total_items']}")
        print(f"  收藏条目: {stats['favorite_items']}")
        print(f"  OCR条目:  {stats['ocr_items']}")
        print(f"  今日新增: {stats['today_items']}")
    
    def _export_data(self, filepath: str) -> None:
        """导出数据"""
        if self.db.export_data(filepath):
            print(f"✅ 数据已导出到: {filepath}")
        else:
            print("❌ 导出失败")


def run_tui(config: Config, db: Database, clipboard: ClipboardManager, ocr: OCREngine) -> None:
    """运行TUI界面"""
    if TEXTUAL_AVAILABLE:
        try:
            app = ClipOCRApp(config, db, clipboard, ocr)
            app.run()
        except Exception as e:
            print(f"TUI启动失败，切换到简单模式: {e}")
            simple = SimpleTUI(config, db, clipboard, ocr)
            simple.run()
    else:
        simple = SimpleTUI(config, db, clipboard, ocr)
        simple.run()
