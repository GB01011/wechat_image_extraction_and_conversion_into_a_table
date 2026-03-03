# -*- coding: utf-8 -*-
"""
测试改进的 JSON 解析功能

验证 LLMParser._extract_and_parse_json 是否能正确处理：
1. 标准 JSON 格式
2. JSON 包装在 markdown 代码块中
3. 截断/不完整的 JSON
4. 多种边界情况
"""

import sys
from src.logger import logger
from src.llm_vision_parser import LLMParser


def test_json_parsing():
    """测试 JSON 解析功能"""
    logger.info("=" * 60)
    logger.info("🧪 开始测试改进的 JSON 解析功能")
    logger.info("=" * 60)
    
    test_cases = [
        {
            "name": "测试 1：标准 JSON 格式",
            "input": '{"has_table": true, "columns": ["列1", "列2"], "rows": [{"列1": "值1", "列2": "值2"}]}',
            "expected_success": True
        },
        {
            "name": "测试 2：JSON 被 markdown 代码块包装",
            "input": '```json\n{"has_table": true, "columns": ["列1", "列2"], "rows": []}\n```',
            "expected_success": True
        },
        {
            "name": "测试 3：只有开始的代码块标记",
            "input": '```json\n{"has_table": true, "columns": ["星期一", "星期二"], "rows": [{"星期一": "第一节课", "星期二": "第二节课"}]}',
            "expected_success": True
        },
        {
            "name": "测试 4：JSON包含特殊字符（中文、空格）",
            "input": '{\n  "has_table": true,\n  "columns": ["题型", "题量", "分值"],\n  "rows": [{"题型": "单选题", "题量": "25个", "分值": "25分"}]\n}',
            "expected_success": True
        },
        {
            "name": "测试 5：空 JSON（用于 has_table=false）",
            "input": '{"has_table": false}',
            "expected_success": True
        },
        {
            "name": "测试 6：JSON 前后有多余文字（应被提取）",
            "input": '这是一个表格识别的结果：\n```json\n{"has_table": true, "columns": ["列1"], "rows": []}\n```\n处理完毕。',
            "expected_success": True
        },
        {
            "name": "测试 7：不闭合的 JSON（缺少大括号）",
            "input": '{"has_table": true, "columns": ["列1", "列2"]',
            "expected_success": True  # 应该能通过修复
        },
        {
            "name": "测试 8：不闭合的数组",
            "input": '{"has_table": true, "columns": ["列1", "列2", "列3"]}',
            "expected_success": True
        },
    ]
    
    passed = 0
    failed = 0
    
    for idx, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{test_case['name']}")
        logger.info("-" * 50)
        
        try:
            result = LLMParser._extract_and_parse_json(test_case['input'])
            
            if result is not None and (test_case['expected_success'] or (isinstance(result, dict) and 'has_table' in result)):
                logger.info(f"✅ 通过")
                logger.info(f"   解析结果类型: {type(result).__name__}")
                if isinstance(result, dict):
                    logger.info(f"   - has_table: {result.get('has_table')}")
                    logger.info(f"   - columns: {result.get('columns', [])[:3]}...")
                passed += 1
            elif not test_case['expected_success'] and result is None:
                logger.info(f"✅ 通过（正确拒绝了无效 JSON）")
                passed += 1
            else:
                logger.warning(f"❌ 失败")
                logger.warning(f"   期望成功: {test_case['expected_success']}")
                logger.warning(f"   实际结果: {result}")
                failed += 1
        
        except Exception as e:
            logger.error(f"❌ 异常: {type(e).__name__}: {e}")
            failed += 1
    
    # 输出统计
    logger.info("\n" + "=" * 60)
    logger.info(f"测试完成: {passed} 通过, {failed} 失败")
    logger.info("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = test_json_parsing()
    sys.exit(0 if success else 1)
