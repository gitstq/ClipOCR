"""
命令行接口模块
"""

import os
import sys
import argparse
from typing import Optional, List

from .config import Config
from .database import Database
from .clipboard_manager import ClipboardManager
from .ocr_engine import OCREngine
from .tui import run_tui, TEXTUAL_AVAILABLE


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="clipocr",
        description="🚀 ClipOCR - 轻量级剪贴板历史与OCR截图智能管理引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  clipocr                          # 启动TUI界面
  clipocr --listen                 # 后台监听剪贴板
  clipocr screenshot               # 截图并OCR识别
  clipocr list                     # 列出历史记录
  clipocr search "关键词"          # 搜索条目
  clipocr copy 123                 # 复制ID为123的内容
  clipocr export backup.json       # 导出数据

更多信息: https://github.com/gitstq/ClipOCR
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s 1.0.0"
    )
    
    parser.add_argument(
        "--config", 
        type=str,
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        help="数据存储目录"
    )
    
    parser.add_argument(
        "--listen",
        action="store_true",
        help="后台监听剪贴板变化"
    )
    
    parser.add_argument(
        "--no-tui",
        action="store_true",
        help="不使用TUI界面，使用命令行模式"
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # screenshot 命令
    screenshot_parser = subparsers.add_parser(
        "screenshot",
        aliases=["shot", "s"],
        help="截图并OCR识别"
    )
    screenshot_parser.add_argument(
        "--lang", "-l",
        type=str,
        default=None,
        help="OCR语言 (默认: chi_sim+eng)"
    )
    screenshot_parser.add_argument(
        "--file", "-f",
        type=str,
        help="识别指定图片文件"
    )
    
    # list 命令
    list_parser = subparsers.add_parser(
        "list",
        aliases=["ls", "l"],
        help="列出剪贴板历史"
    )
    list_parser.add_argument(
        "--limit", "-n",
        type=int,
        default=20,
        help="显示条目数量 (默认: 20)"
    )
    list_parser.add_argument(
        "--favorites", "-f",
        action="store_true",
        help="仅显示收藏"
    )
    
    # search 命令
    search_parser = subparsers.add_parser(
        "search",
        aliases=["find", "q"],
        help="搜索剪贴板历史"
    )
    search_parser.add_argument(
        "query",
        type=str,
        help="搜索关键词"
    )
    search_parser.add_argument(
        "--limit", "-n",
        type=int,
        default=20,
        help="显示条目数量 (默认: 20)"
    )
    
    # copy 命令
    copy_parser = subparsers.add_parser(
        "copy",
        aliases=["cp", "c"],
        help="复制指定条目到剪贴板"
    )
    copy_parser.add_argument(
        "id",
        type=int,
        help="条目ID"
    )
    
    # delete 命令
    delete_parser = subparsers.add_parser(
        "delete",
        aliases=["del", "d", "rm"],
        help="删除指定条目"
    )
    delete_parser.add_argument(
        "id",
        type=int,
        help="条目ID"
    )
    delete_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="强制删除，不确认"
    )
    
    # favorite 命令
    favorite_parser = subparsers.add_parser(
        "favorite",
        aliases=["fav", "star"],
        help="收藏/取消收藏条目"
    )
    favorite_parser.add_argument(
        "id",
        type=int,
        help="条目ID"
    )
    
    # tag 命令
    tag_parser = subparsers.add_parser(
        "tag",
        aliases=["t"],
        help="为条目添加标签"
    )
    tag_parser.add_argument(
        "id",
        type=int,
        help="条目ID"
    )
    tag_parser.add_argument(
        "tags",
        nargs="+",
        help="标签列表"
    )
    
    # stats 命令
    stats_parser = subparsers.add_parser(
        "stats",
        aliases=["stat", "st"],
        help="显示统计信息"
    )
    
    # export 命令
    export_parser = subparsers.add_parser(
        "export",
        aliases=["e", "ex"],
        help="导出数据到JSON文件"
    )
    export_parser.add_argument(
        "filepath",
        type=str,
        help="导出文件路径"
    )
    
    # import 命令
    import_parser = subparsers.add_parser(
        "import",
        aliases=["im"],
        help="从JSON文件导入数据"
    )
    import_parser.add_argument(
        "filepath",
        type=str,
        help="导入文件路径"
    )
    
    # config 命令
    config_parser = subparsers.add_parser(
        "config",
        help="配置管理"
    )
    config_parser.add_argument(
        "--set",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="设置配置项"
    )
    config_parser.add_argument(
        "--get",
        metavar="KEY",
        help="获取配置项"
    )
    config_parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有配置"
    )
    
    return parser


def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 ClipOCR - 轻量级剪贴板历史与OCR截图智能管理引擎 v1.0.0   ║
║                                                              ║
║   零依赖 · 离线优先 · 隐私保护 · 多语言OCR                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def cmd_screenshot(args, config: Config, db: Database, ocr: OCREngine) -> int:
    """截图命令"""
    if not ocr.is_available:
        print("❌ OCR功能不可用，请安装依赖:")
        print("   pip install Pillow pytesseract")
        print("   并安装 Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        return 1
    
    if args.file:
        # 识别指定文件
        print(f"📄 正在识别图片: {args.file}")
        item = ocr.recognize_from_file(args.file, language=args.lang)
    else:
        # 截图识别
        print("📸 请准备截图...")
        item = ocr.capture_and_recognize(language=args.lang)
    
    if item:
        print(f"✅ 识别成功！已保存到历史记录 (ID: {item.id})")
        print(f"📝 识别内容预览:")
        preview = item.ocr_text[:200] + "..." if len(item.ocr_text) > 200 else item.ocr_text
        print(f"   {preview}")
        return 0
    else:
        print("❌ 识别失败或未识别到文字")
        return 1


def cmd_list(args, config: Config, db: Database) -> int:
    """列表命令"""
    items = db.get_items(
        limit=args.limit,
        favorites_only=args.favorites
    )
    
    if not items:
        print("📭 暂无条目")
        return 0
    
    print(f"\n{'ID':<6}{'类型':<10}{'⭐':<4}{'内容预览':<45}{'更新时间'}")
    print("-"*85)
    
    for item in items:
        fav = "⭐" if item.is_favorite else ""
        preview = item.content[:40] + "..." if len(item.content) > 40 else item.content
        preview = preview.replace("\n", " ")
        time_str = item.updated_at[5:16] if item.updated_at else ""
        
        print(f"{item.id:<6}{item.content_type:<10}{fav:<4}{preview:<45}{time_str}")
    
    print(f"\n共 {len(items)} 条记录")
    return 0


def cmd_search(args, config: Config, db: Database) -> int:
    """搜索命令"""
    items = db.get_items(limit=args.limit, search=args.query)
    
    if not items:
        print(f"📭 未找到包含 '{args.query}' 的条目")
        return 0
    
    print(f"\n🔍 搜索 '{args.query}' 的结果:")
    print(f"{'ID':<6}{'类型':<10}{'⭐':<4}{'内容预览':<45}{'更新时间'}")
    print("-"*85)
    
    for item in items:
        fav = "⭐" if item.is_favorite else ""
        preview = item.content[:40] + "..." if len(item.content) > 40 else item.content
        preview = preview.replace("\n", " ")
        time_str = item.updated_at[5:16] if item.updated_at else ""
        
        print(f"{item.id:<6}{item.content_type:<10}{fav:<4}{preview:<45}{time_str}")
    
    print(f"\n共找到 {len(items)} 条记录")
    return 0


def cmd_copy(args, config: Config, db: Database, clipboard: ClipboardManager) -> int:
    """复制命令"""
    item = db.get_item(args.id)
    
    if not item:
        print(f"❌ 条目 ID {args.id} 不存在")
        return 1
    
    content = item.ocr_text or item.content
    if clipboard.copy_to_clipboard(content):
        print(f"✅ 已复制 ID {args.id} 的内容到剪贴板")
        preview = content[:100] + "..." if len(content) > 100 else content
        print(f"   内容: {preview}")
        return 0
    else:
        print("❌ 复制失败")
        return 1


def cmd_delete(args, config: Config, db: Database) -> int:
    """删除命令"""
    item = db.get_item(args.id)
    
    if not item:
        print(f"❌ 条目 ID {args.id} 不存在")
        return 1
    
    if not args.force:
        preview = item.content[:50] + "..." if len(item.content) > 50 else item.content
        confirm = input(f"确认删除条目 {args.id}? (内容: {preview}) [y/N]: ")
        if confirm.lower() != 'y':
            print("已取消")
            return 0
    
    if db.delete_item(args.id):
        print(f"✅ 已删除条目 ID {args.id}")
        return 0
    else:
        print("❌ 删除失败")
        return 1


def cmd_favorite(args, config: Config, db: Database) -> int:
    """收藏命令"""
    item = db.get_item(args.id)
    
    if not item:
        print(f"❌ 条目 ID {args.id} 不存在")
        return 1
    
    new_status = not item.is_favorite
    if db.update_item(args.id, is_favorite=new_status):
        status = "收藏" if new_status else "取消收藏"
        print(f"✅ 已{status}条目 ID {args.id}")
        return 0
    else:
        print("❌ 操作失败")
        return 1


def cmd_tag(args, config: Config, db: Database) -> int:
    """标签命令"""
    item = db.get_item(args.id)
    
    if not item:
        print(f"❌ 条目 ID {args.id} 不存在")
        return 1
    
    if db.add_tags(args.id, args.tags):
        print(f"✅ 已为条目 ID {args.id} 添加标签: {', '.join(args.tags)}")
        return 0
    else:
        print("❌ 添加标签失败")
        return 1


def cmd_stats(args, config: Config, db: Database) -> int:
    """统计命令"""
    stats = db.get_statistics()
    
    print("\n📊 ClipOCR 统计信息")
    print("="*40)
    print(f"📋 总条目数:     {stats['total_items']}")
    print(f"⭐ 收藏条目:     {stats['favorite_items']}")
    print(f"🔍 OCR识别条目:  {stats['ocr_items']}")
    print(f"📅 今日新增:     {stats['today_items']}")
    print("="*40)
    
    # 显示所有标签
    tags = db.get_all_tags()
    if tags:
        print(f"\n🏷️  标签列表: {', '.join(tags)}")
    
    return 0


def cmd_export(args, config: Config, db: Database) -> int:
    """导出命令"""
    if db.export_data(args.filepath):
        print(f"✅ 数据已导出到: {args.filepath}")
        return 0
    else:
        print("❌ 导出失败")
        return 1


def cmd_import(args, config: Config, db: Database) -> int:
    """导入命令"""
    if not os.path.exists(args.filepath):
        print(f"❌ 文件不存在: {args.filepath}")
        return 1
    
    count = db.import_data(args.filepath)
    if count > 0:
        print(f"✅ 成功导入 {count} 条记录")
        return 0
    else:
        print("❌ 导入失败或未找到有效数据")
        return 1


def cmd_config(args, config: Config) -> int:
    """配置命令"""
    if args.list:
        print("\n⚙️  当前配置:")
        print(f"  数据目录: {config.data_dir}")
        print(f"  数据库: {config.db_name}")
        print(f"  OCR语言: {config.ocr_language}")
        print(f"  最大历史: {config.max_history_items}")
        print(f"  监听间隔: {config.clipboard_polling_interval}s")
        print(f"  自动清理: {config.auto_cleanup_days}天")
    
    elif args.get:
        value = getattr(config, args.get, None)
        if value is not None:
            print(f"{args.get} = {value}")
        else:
            print(f"❌ 未知配置项: {args.get}")
            return 1
    
    elif args.set:
        key, value = args.set
        try:
            # 尝试转换为适当类型
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit():
                value = float(value)
            elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            
            config.update(**{key: value})
            print(f"✅ 已设置 {key} = {value}")
        except Exception as e:
            print(f"❌ 设置失败: {e}")
            return 1
    
    return 0


def main():
    """主入口函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 加载配置
    config = Config.load()
    
    # 应用命令行配置覆盖
    if args.data_dir:
        config.data_dir = args.data_dir
        config.save()
    
    # 初始化数据库
    db = Database(config)
    
    # 初始化剪贴板管理器
    clipboard = ClipboardManager(config, db)
    
    # 初始化OCR引擎
    ocr = OCREngine(config, db)
    
    # 处理命令
    if args.command == "screenshot" or args.command == "shot" or args.command == "s":
        return cmd_screenshot(args, config, db, ocr)
    
    elif args.command == "list" or args.command == "ls" or args.command == "l":
        return cmd_list(args, config, db)
    
    elif args.command == "search" or args.command == "find" or args.command == "q":
        return cmd_search(args, config, db)
    
    elif args.command == "copy" or args.command == "cp" or args.command == "c":
        return cmd_copy(args, config, db, clipboard)
    
    elif args.command == "delete" or args.command == "del" or args.command == "d" or args.command == "rm":
        return cmd_delete(args, config, db)
    
    elif args.command == "favorite" or args.command == "fav" or args.command == "star":
        return cmd_favorite(args, config, db)
    
    elif args.command == "tag" or args.command == "t":
        return cmd_tag(args, config, db)
    
    elif args.command == "stats" or args.command == "stat" or args.command == "st":
        return cmd_stats(args, config, db)
    
    elif args.command == "export" or args.command == "e" or args.command == "ex":
        return cmd_export(args, config, db)
    
    elif args.command == "import" or args.command == "im":
        return cmd_import(args, config, db)
    
    elif args.command == "config":
        return cmd_config(args, config)
    
    else:
        # 无命令或监听模式
        if args.listen:
            print_banner()
            print("👂 正在监听剪贴板变化...")
            print("按 Ctrl+C 停止\n")
            
            clipboard.start_listening()
            
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 停止监听")
                clipboard.stop_listening()
                return 0
        
        else:
            # 启动TUI界面
            print_banner()
            
            if args.no_tui or not TEXTUAL_AVAILABLE:
                # 简单命令行模式
                from .tui import SimpleTUI
                simple = SimpleTUI(config, db, clipboard, ocr)
                simple.run()
            else:
                # TUI模式
                run_tui(config, db, clipboard, ocr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
