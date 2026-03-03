# -*- coding: utf-8 -*-
"""
表格结构检测模块

功能：
- 检测表格是否有列名
- 提取动态列名
- 建立列名与数据的映射关系
- 规范化数据格式
"""

import json
from src.logger import logger


class TableStructureDetector:
    """表格结构检测器"""
    
    @staticmethod
    def detect_structure(llm_response):
        """
        检测表格结构（是否有列名、数据映射等）
        
        Args:
            llm_response: LLM 返回的识别结果（JSON 格式或字符串）
        
        Returns:
            {
                'has_table': 是否有表格,
                'has_columns': 是否有列名,
                'columns': 列名列表,
                'rows': 数据行,
                'column_mapping': 列名映射,
                'data_format': 'object' 或 'array'
            }
        """
        try:
            # 检查 llm_response 是否为 None
            if llm_response is None:
                logger.error("❌ LLM 响应为 None，无法检测表格结构")
                return None
            
            # 解析 LLM 返回的 JSON
            if isinstance(llm_response, str):
                response_data = json.loads(llm_response)
            else:
                response_data = llm_response
            
            # 检查响应数据是否有效
            if not isinstance(response_data, dict):
                logger.error(f"❌ 响应数据类型错误，期望 dict 但得到 {type(response_data)}")
                return None
            
            # 提取信息
            has_table = response_data.get('has_table', False)
            columns = response_data.get('columns', [])
            rows = response_data.get('rows', [])
            
            # 判断是否有列名
            has_columns = bool(columns) and len(columns) > 0
            
            # 确定数据格式
            if rows:
                first_row = rows[0]
                data_format = 'object' if isinstance(first_row, dict) else 'array'
            else:
                data_format = 'object' if has_columns else 'array'
            
            logger.info(f"✓ 表格结构检测完成")
            logger.info(f"  - 有表格: {has_table}")
            logger.info(f"  - 有列名: {has_columns}")
            if columns:
                logger.info(f"  - 列名: {columns}")
            logger.info(f"  - 数据行数: {len(rows)}")
            logger.info(f"  - 数据格式: {data_format}")
            
            return {
                'has_table': has_table,
                'has_columns': has_columns,
                'columns': columns,
                'rows': rows,
                'data_format': data_format,
                'column_mapping': TableStructureDetector._build_column_mapping(columns, rows)
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 解析失败: {e}")
            logger.debug(f"   原始响应: {llm_response}")
            return None
        except Exception as e:
            logger.error(f"❌ 表格结构检测失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _build_column_mapping(columns, rows):
        """
        构建列名映射（用于数据校验）
        
        Args:
            columns: 列名列表
            rows: 数据行
        
        Returns:
            列名映射字典 {列名: 索引}
        """
        mapping = {}
        
        if not columns:
            # 如果无列名，为每列生成默认名称
            if rows:
                first_row = rows[0]
                if isinstance(first_row, (list, tuple)):
                    num_cols = len(first_row)
                    columns = [f"列{i+1}" for i in range(num_cols)]
                elif isinstance(first_row, dict):
                    columns = list(first_row.keys())
        
        for idx, col in enumerate(columns):
            mapping[col] = idx
        
        return mapping
    
    @staticmethod
    def normalize_data(structure_result):
        """
        规范化数据格式（转换为统一的字典列表格式）
        
        Args:
            structure_result: 表格结构检测结果
        
        Returns:
            规范化后的数据：[{列名: 值, ...}, ...]
        """
        columns = structure_result['columns']
        rows = structure_result['rows']
        data_format = structure_result['data_format']
        
        normalized_rows = []
        
        if data_format == 'object':
            # 如果已经是对象格式，直接使用
            normalized_rows = rows
        else:
            # 如果是数组格式，需要建立映射
            if columns:
                # 有列名：将数组值映射到列名
                for row in rows:
                    if isinstance(row, (list, tuple)):
                        row_dict = {}
                        for idx, col in enumerate(columns):
                            if idx < len(row):
                                row_dict[col] = str(row[idx]).strip() if row[idx] else ""
                            else:
                                row_dict[col] = ""  # 缺失值用空字符串填充
                        normalized_rows.append(row_dict)
            else:
                # 无列名：保持数组格式但转为字典（用索引作为键）
                for row in rows:
                    if isinstance(row, (list, tuple)):
                        row_dict = {f"列{i+1}": str(val).strip() if val else "" for i, val in enumerate(row)}
                        normalized_rows.append(row_dict)
        
        return normalized_rows
    
    @staticmethod
    def validate_data_mapping(normalized_data, columns):
        """
        验证数据与列名的映射是否正确
        
        Args:
            normalized_data: 规范化后的数据
            columns: 列名列表
        
        Returns:
            验证报告 {'valid': bool, 'issues': [问题列表]}
        """
        issues = []
        
        if not normalized_data:
            issues.append("数据为空")
            return {'valid': False, 'issues': issues}
        
        # 检查每行是否都有所有列
        for idx, row in enumerate(normalized_data, 1):
            for col in columns:
                if col not in row:
                    issues.append(f"第 {idx} 行缺少列 '{col}'")
        
        # 检查是否有空值过多的行
        max_empty_allowed = 3  # 最多允许 3 个空值
        for idx, row in enumerate(normalized_data, 1):
            empty_count = sum(1 for col in columns if not row.get(col, ""))
            if empty_count > max_empty_allowed:
                issues.append(f"第 {idx} 行有 {empty_count} 个空值（超过限制 {max_empty_allowed}）")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
