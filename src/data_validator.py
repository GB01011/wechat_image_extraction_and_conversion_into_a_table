"""
数据验证和清洗模块

功能：
- 数据格式验证
- 必填字段检查
- 数据清洗和标准化
- 重复记录检测和去重
- 数据质量评估
"""

from src.logger import logger


class DataValidator:
    """数据验证和清洗模块"""
    
    # 标准字段定义（后向兼容）
    REQUIRED_FIELDS = ["品名"]  # 必填字段
    ALL_FIELDS = ["品名", "规格", "材质", "产地", "仓库", "价格"]
    
    @staticmethod
    def validate_and_clean(data_list, enable_dedup=True, columns=None):
        """
        验证并清洗数据（支持动态列名）
        
        处理步骤：
        1. 检查数据格式
        2. 确定列名（动态或使用标准列名）
        3. 补齐缺失字段
        4. 检查必填字段（第一个字段）
        5. 字符串清洗（去空格、统一编码）
        6. 去除重复记录（可选）
        7. 数据质量评估
        
        Args:
            data_list: 原始数据列表
            enable_dedup: 是否启用去重
            columns: 指定的列名列表（如果为 None，则使用标准列名）
        
        Returns:
            清洗后的数据列表
        """
        if not isinstance(data_list, list):
            logger.error(f"❌ 数据格式错误，期望列表但收到 {type(data_list)}")
            return []
        
        if len(data_list) == 0:
            logger.warning("⚠ 数据列表为空")
            return []
        
        # 确定列名：使用提供的列名或默认标准列名
        if columns is None:
            columns = DataValidator.ALL_FIELDS
        
        logger.info(f"📋 开始数据清洗，列名: {columns}")
        
        cleaned_data = []
        skipped_count = 0
        
        # 确定必填字段（第一个列名作为必填字段）
        required_field = columns[0] if columns else None
        
        for idx, record in enumerate(data_list, 1):
            try:
                # 1. 检查是否为字典
                if not isinstance(record, dict):
                    logger.debug(f"⚠ 第 {idx} 条记录格式错误，不是字典")
                    skipped_count += 1
                    continue
                
                # 2. 补齐缺失字段
                for field in columns:
                    if field not in record:
                        record[field] = ""
                
                # 3. 检查必填字段（第一个列名）
                if required_field:
                    required_value = str(record.get(required_field, "")).strip()
                    if not required_value:
                        logger.debug(f"⚠ 第 {idx} 条记录缺少必填字段'{required_field}'，跳过")
                        skipped_count += 1
                        continue
                
                # 4. 数据清洗：去除前后空格，统一编码
                cleaned_record = {}
                for field in columns:
                    value = str(record.get(field, "")).strip()
                    # 替换全角空格为半角空格
                    value = value.replace("　", " ")
                    # 移除多余空格
                    value = " ".join(value.split())
                    cleaned_record[field] = value
                
                # 5. 检查数据质量（空字段数量）
                empty_field_count = sum(1 for v in cleaned_record.values() if not v)
                max_allowed_empty = max(len(columns) - 2, 1)  # 最多允许空的字段数
                if empty_field_count > max_allowed_empty:
                    logger.debug(f"⚠ 第 {idx} 条记录数据不完整，{empty_field_count} 个空字段，跳过")
                    skipped_count += 1
                    continue
                
                # 6. 去重检查（基于前两个字段）
                if enable_dedup and len(columns) >= 2:
                    is_duplicate = False
                    dedup_key_1 = cleaned_record.get(columns[0], "")
                    dedup_key_2 = cleaned_record.get(columns[1], "")
                    
                    for existing in cleaned_data:
                        if (dedup_key_1 == existing.get(columns[0], "") and 
                            dedup_key_2 == existing.get(columns[1], "")):
                            logger.debug(f"⚠ 检测到重复记录: {dedup_key_1} {dedup_key_2}, 跳过")
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        skipped_count += 1
                        continue
                
                # 7. 记录添加到清洗列表
                cleaned_data.append(cleaned_record)
                logger.debug(f"✓ 第 {idx} 条记录清洗成功")
            
            except Exception as e:
                logger.warning(f"⚠ 第 {idx} 条记录处理失败: {e}")
                skipped_count += 1
                continue
        
        # 输出统计信息
        logger.info(f"========== 数据清洗统计 ==========")
        logger.info(f"  总记录数: {len(data_list)}")
        logger.info(f"  有效记录数: {len(cleaned_data)}")
        logger.info(f"  跳过记录数: {skipped_count}")
        if len(data_list) > 0:
            logger.info(f"  清洗完成率: {len(cleaned_data)}/{len(data_list)} ({100*len(cleaned_data)//len(data_list)}%)")
        logger.info(f"================================")
        
        return cleaned_data
    
    @staticmethod
    def validate_field(field_name, field_value):
        """
        验证单个字段
        
        Args:
            field_name: 字段名
            field_value: 字段值
        
        Returns:
            是否有效
        """
        if field_name == "品名":
            return bool(str(field_value).strip())
        
        elif field_name == "价格":
            # 简单验证价格格式
            value = str(field_value).strip()
            if not value:
                return True  # 价格可为空
            # 检查是否包含数字
            return any(c.isdigit() for c in value)
        
        else:
            # 其他字段只需非空即可
            return True
    
    @staticmethod
    def assess_data_quality(cleaned_data, columns=None):
        """
        评估数据质量，返回质量分数
        
        Args:
            cleaned_data: 清洗后的数据
            columns: 列名列表（如果为 None，使用标准列名）
        
        Returns:
            质量分数（0-100）
        """
        if not cleaned_data:
            return 0.0
        
        # 确定列名
        if columns is None:
            columns = DataValidator.ALL_FIELDS
        
        total_fields = len(cleaned_data) * len(columns)
        filled_fields = 0
        
        for record in cleaned_data:
            for field in columns:
                if record.get(field, "").strip():
                    filled_fields += 1
        
        quality_score = (filled_fields / total_fields) * 100 if total_fields > 0 else 0
        
        logger.info(f"数据质量评分: {quality_score:.1f}%")
        return quality_score
