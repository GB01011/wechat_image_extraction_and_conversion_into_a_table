# -*- coding: utf-8 -*-
"""
大模型视觉解析模块

功能：
- 调用大模型进行图像识别
- 提取表格结构和数据
- 支持重试机制和容错
"""

import base64
import json
import time
from openai import OpenAI
from src.logger import logger


# 改进后的提示词
VISION_PARSER_PROMPT = """
你是一个专业的表格识别专家。请分析以下图片中的表格内容。

【重要要求】：
1. 识别表格的所有列名（表头）
2. 提取表格的所有数据行
3. 必须返回完整的JSON格式（不要截断）
4. 如果表格很大，继续完整返回所有数据
5. 直接输出JSON，不要输出任何其他文字

【输出格式】（必须是完整的JSON，不能有任何遗漏）：
{
  "has_table": true,
  "table_type": "structured",
  "columns": ["列名1", "列名2", "列名3"],
  "rows": [
    {"列名1": "值1", "列名2": "值2", "列名3": "值3"},
    {"列名1": "值1", "列名2": "值2", "列名3": "值3"}
  ],
  "notes": "说明"
}

【处理说明】：
- 如果第一列是空字符串，保留为空 ""
- 如果单元格包含换行符，可以保留换行
- 如果无列名，设置 columns 为空数组 []
- 如果没有表格，返回 {"has_table": false}
- 必须返回完整的JSON，即使需要多行

【特别提醒】：
- 不要截断响应，返回完整的JSON
- 不要删除任何数据
- 不要在JSON前后添加任何其他文字
"""


class LLMParser:
    """大模型视觉解析器"""
    
    def __init__(self, api_key, base_url, model_name, request_timeout=30, max_retries=3):
        """
        初始化 LLM 解析器
        
        Args:
            api_key: API 密钥
            base_url: API 基地址
            model_name: 模型名称
            request_timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        try:
            self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=request_timeout)
            self.model_name = model_name
            self.request_timeout = request_timeout
            self.max_retries = max_retries
            logger.info(f"✓ LLM 解析器已初始化: {model_name}")
        except Exception as e:
            logger.error(f"❌ LLM 解析器初始化失败: {e}")
            raise
    
    def parse_content(self, image_path=None, text_content=None):
        """
        解析图片或文本内容
        
        Args:
            image_path: 图片路径
            text_content: 文本内容
        
        Returns:
            解析结果（字典格式）
        """
        if image_path:
            return self._parse_image(image_path)
        elif text_content:
            return self._parse_text(text_content)
        else:
            logger.error("❌ 必须提供 image_path 或 text_content")
            return None
    
    def _parse_image(self, image_path):
        """
        解析图片
        
        Args:
            image_path: 图片路径
        
        Returns:
            解析结果
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"已加载图片: {image_path}")
                logger.info(f"正在调用大模型进行表格识别（第{attempt}/{self.max_retries}次）...")
                
                # 读取并编码图片
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                
                # 调用 API
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": VISION_PARSER_PROMPT
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    timeout=self.request_timeout
                )
                
                # 提取响应内容
                raw_response = response.choices[0].message.content
                logger.debug(f"原始响应长度: {len(raw_response)} 字符")
                
                # 尝试提取并解析 JSON
                parsed_data = self._extract_and_parse_json(raw_response)
                
                if parsed_data:
                    logger.info("✓ 大模型识别成功")
                    return parsed_data
                else:
                    logger.warning(f"⚠ 第 {attempt} 次尝试失败，JSON 解析失败")
                    if attempt < self.max_retries:
                        logger.info(f"等待 2 秒后重试...")
                        time.sleep(2)
                        continue
                    else:
                        logger.error("❌ 已达最大重试次数，无法获取有效响应")
                        return None
            
            except Exception as e:
                logger.error(f"❌ LLM 调用失败（第 {attempt} 次）: {type(e).__name__}: {e}")
                if attempt < self.max_retries:
                    logger.info(f"等待 2 秒后重试...")
                    time.sleep(2)
                    continue
                else:
                    logger.error("❌ 已达最大重试次数")
                    return None
        
        return None
    
    def _parse_text(self, text_content):
        """
        解析文本内容
        
        Args:
            text_content: 文本内容
        
        Returns:
            解析结果
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"正在调用大模型进行文本解析（第{attempt}/{self.max_retries}次）...")
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": f"{VISION_PARSER_PROMPT}\n\n【要分析的文本内容】：\n{text_content}"
                        }
                    ],
                    timeout=self.request_timeout
                )
                
                raw_response = response.choices[0].message.content
                logger.debug(f"原始响应长度: {len(raw_response)} 字符")
                
                # 尝试提取并解析 JSON
                parsed_data = self._extract_and_parse_json(raw_response)
                
                if parsed_data:
                    logger.info("✓ 大模型识别成功")
                    return parsed_data
                else:
                    logger.warning(f"⚠ 第 {attempt} 次尝试失败，JSON 解析失败")
                    if attempt < self.max_retries:
                        logger.info(f"等待 2 秒后重试...")
                        time.sleep(2)
                        continue
            
            except Exception as e:
                logger.error(f"❌ LLM 调用失败（第 {attempt} 次）: {type(e).__name__}: {e}")
                if attempt < self.max_retries:
                    logger.info(f"等待 2 秒后重试...")
                    time.sleep(2)
                    continue
        
        return None
    
    @staticmethod
    def _extract_and_parse_json(response_text):
        """
        从 LLM 响应中提取并解析 JSON
        
        重要改进：
        1. 支持多行 JSON 响应
        2. 自动移除代码块标记
        3. 增加容错机制
        
        Args:
            response_text: LLM 响应文本
        
        Returns:
            解析后的字典，失败返回 None
        """
        try:
            if not response_text:
                logger.error("❌ 响应文本为空")
                return None
            
            # 1. 移除 markdown 代码块标记
            cleaned_text = response_text.strip()
            
            # 移除开始的代码块标记
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.lstrip("`").lstrip("json").lstrip("`").strip()
            
            # 移除结尾的代码块标记
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text.rstrip("`").strip()
            
            logger.debug(f"清理后的响应长度: {len(cleaned_text)} 字符")
            
            # 2. 尝试直接解析 JSON
            try:
                parsed = json.loads(cleaned_text)
                logger.info("✓ JSON 解析成功（直接解析）")
                return parsed
            except json.JSONDecodeError as e:
                logger.debug(f"直接解析失败: {e}")
            
            # 3. 如果直接解析失败，尝试找到 JSON 对象的开始和结束位置
            json_start = cleaned_text.find('{')
            json_end = cleaned_text.rfind('}')
            
            if json_start != -1 and json_end != -1 and json_end > json_start:
                # 提取可能的 JSON 字符串
                potential_json = cleaned_text[json_start:json_end+1]
                logger.debug(f"提取的 JSON 片段（长度: {len(potential_json)} 字符）")
                
                try:
                    parsed = json.loads(potential_json)
                    logger.info("✓ JSON 解析成功（精确提取）")
                    return parsed
                except json.JSONDecodeError as e:
                    logger.debug(f"精确提取后仍解析失败: {e}")
            
            # 4. 如果还是失败，尝试修复常见的 JSON 问题
            fixed_json = LLMParser._fix_json_format(cleaned_text)
            if fixed_json:
                try:
                    parsed = json.loads(fixed_json)
                    logger.info("✓ JSON 解析成功（修复格式后）")
                    return parsed
                except json.JSONDecodeError as e:
                    logger.debug(f"修复后仍解析失败: {e}")
            
            logger.error(f"❌ JSON 解析失败: 无法从响应中提取有效的 JSON")
            logger.debug(f"原始响应（前 300 字符）: {response_text[:300]}...")
            return None
        
        except Exception as e:
            logger.error(f"❌ JSON 处理异常: {type(e).__name__}: {e}")
            return None
    
    @staticmethod
    def _fix_json_format(text):
        """
        修复常见的 JSON 格式问题
        
        Args:
            text: 原始文本
        
        Returns:
            修复后的 JSON 字符串，如果无法修复返回 None
        """
        try:
            # 移除控制字符（保留 \n \t）
            text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\t')
            
            # 尝试添加缺失的闭合大括号
            open_braces = text.count('{')
            close_braces = text.count('}')
            
            if open_braces > close_braces:
                text += '}' * (open_braces - close_braces)
            
            # 尝试添加缺失的闭合方括号
            open_brackets = text.count('[')
            close_brackets = text.count(']')
            
            if open_brackets > close_brackets:
                text += ']' * (open_brackets - close_brackets)
            
            return text
        
        except Exception as e:
            logger.debug(f"JSON 修复失败: {e}")
            return None