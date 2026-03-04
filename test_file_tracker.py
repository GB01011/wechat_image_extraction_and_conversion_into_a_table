# -*- coding: utf-8 -*-
"""
文件跟踪功能测试脚本

功能：
- 测试文件不重复处理
- 测试新文件被正确识别
- 测试文件状态跟踪记录
"""

import json
from pathlib import Path
from src.logger import logger
from src.file_tracker import FileTracker
from src.wechat_listener import LocalFileListener


def test_file_tracker():
    """测试文件跟踪功能"""
    
    logger.info("=" * 60)
    logger.info("🧪 开始测试文件跟踪功能")
    logger.info("=" * 60)
    
    # 测试 1：初始化文件跟踪器
    logger.info("\n[测试 1] 初始化文件跟踪器")
    logger.info("-" * 60)
    
    tracker = FileTracker()
    stats = tracker.get_stats()
    
    logger.info(f"✓ 文件跟踪器初始化成功")
    logger.info(f"  总文件数: {stats['total']}")
    logger.info(f"  成功: {stats['success']}")
    logger.info(f"  失败: {stats['failed']}")
    logger.info(f"  跳过: {stats['skipped']}")
    
    # 测试 2：标记文件为已处理
    logger.info("\n[测试 2] 标记文件为已处理")
    logger.info("-" * 60)
    
    test_file_1 = Path("data/temp_images/test_image_1.jpg").absolute()
    test_file_2 = Path("data/temp_images/test_image_2.jpg").absolute()
    test_file_3 = Path("data/temp_images/test_image_3.jpg").absolute()
    
    # 标记三个文件
    tracker.mark_as_processed(test_file_1, "output/excel_1.xlsx", "success")
    tracker.mark_as_processed(test_file_2, "output/excel_2.xlsx", "success")
    tracker.mark_as_processed(test_file_3, status="failed")
    
    new_stats = tracker.get_stats()
    logger.info(f"✓ 文件标记完成")
    logger.info(f"  总文件数: {new_stats['total']} (增加 3 个)")
    logger.info(f"  成功: {new_stats['success']}")
    logger.info(f"  失败: {new_stats['failed']}")
    
    # 测试 3：检查文件是否已处理
    logger.info("\n[测试 3] 检查文件是否已处理")
    logger.info("-" * 60)
    
    is_processed_1 = tracker.is_processed(test_file_1)
    is_processed_2 = tracker.is_processed(test_file_2)
    is_processed_unknown = tracker.is_processed(Path("data/temp_images/test_unknown.jpg"))
    
    logger.info(f"✓ test_image_1.jpg 已处理: {is_processed_1}")
    logger.info(f"✓ test_image_2.jpg 已处理: {is_processed_2}")
    logger.info(f"✓ test_unknown.jpg 已处理: {is_processed_unknown}")
    
    assert is_processed_1, "test_image_1.jpg 应该被标记为已处理"
    assert is_processed_2, "test_image_2.jpg 应该被标记为已处理"
    assert not is_processed_unknown, "test_unknown.jpg 应该未被处理"
    
    logger.info("✓ 所有检查通过")
    
    # 测试 4：从跟踪中移除文件
    logger.info("\n[测试 4] 从跟踪中移除文件")
    logger.info("-" * 60)
    
    tracker.remove_file(test_file_1)
    is_processed_1_after = tracker.is_processed(test_file_1)
    
    logger.info(f"✓ test_image_1.jpg 已从跟踪中移除")
    logger.info(f"✓ 移除后，test_image_1.jpg 已处理: {is_processed_1_after}")
    
    assert not is_processed_1_after, "test_image_1.jpg 应该被移除后未被处理"
    logger.info("✓ 移除验证通过")
    
    # 测试 5：检查跟踪记录文件
    logger.info("\n[测试 5] 检查跟踪记录文件")
    logger.info("-" * 60)
    
    tracker_file = Path("data/.processed_files.json")
    if tracker_file.exists():
        with open(tracker_file, 'r', encoding='utf-8') as f:
            tracker_data = json.load(f)
        
        logger.info(f"✓ 跟踪记录文件存在: {tracker_file}")
        logger.info(f"✓ 记录文件数: {len(tracker_data)}")
        
        # 显示部分记录
        for i, (file_path, info) in enumerate(list(tracker_data.items())[:3], 1):
            file_name = Path(file_path).name
            status = info.get('status', 'unknown')
            logger.info(f"   [{i}] {file_name}: {status}")
    
    # 测试 6：LocalFileListener 集成测试
    logger.info("\n[测试 6] LocalFileListener 集成测试")
    logger.info("-" * 60)
    
    # 创建监听器
    listener = LocalFileListener(watch_dir="data/temp_images")
    
    logger.info(f"✓ LocalFileListener 初始化成功")
    logger.info(f"✓ 已处理文件数: {listener.file_tracker.get_processed_count()}")
    
    # 获取消息（应该为空，因为没有新图片）
    messages = listener.get_new_messages()
    logger.info(f"✓ 扫描结果: {len(messages)} 个新消息")
    
    if messages:
        logger.warning("⚠ 检测到意外的新消息（可能有新图片在目录中）")
        for msg in messages:
            logger.info(f"   - {Path(msg['data']).name}")
    
    logger.info("✓ 集成测试完成")
    
    # 最终统计
    logger.info("\n" + "=" * 60)
    logger.info("✅ 所有测试通过！")
    logger.info("=" * 60)
    
    final_stats = tracker.get_stats()
    logger.info(f"\n最终统计:")
    logger.info(f"  总文件数: {final_stats['total']}")
    logger.info(f"  成功处理: {final_stats['success']}")
    logger.info(f"  处理失败: {final_stats['failed']}")
    logger.info(f"  跳过: {final_stats['skipped']}")
    logger.info(f"\n跟踪记录文件: {tracker.tracker_file.absolute()}")


if __name__ == "__main__":
    test_file_tracker()
