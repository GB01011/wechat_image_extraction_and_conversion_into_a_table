# -*- coding: utf-8 -*-
"""
文件处理跟踪模块

功能：
- 记录已处理的文件
- 避免重复处理同一个文件
- 支持增量处理（只处理新文件）
- 提供文件状态查询和管理功能
"""

import json
from pathlib import Path
from datetime import datetime
from src.logger import logger


class FileTracker:
    """文件处理跟踪器（用于避免重复处理）"""
    
    def __init__(self, tracker_file="data/.processed_files.json"):
        """
        初始化文件跟踪器
        
        Args:
            tracker_file: 跟踪记录文件路径
        """
        self.tracker_file = Path(tracker_file)
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_files = self._load_tracker()
        
        logger.info(f"✓ 文件跟踪器已初始化")
        logger.info(f"  记录文件: {self.tracker_file.absolute()}")
        logger.info(f"  已记录文件数: {len(self.processed_files)}")
    
    def _load_tracker(self):
        """
        加载跟踪记录
        
        Returns:
            dict: 已处理文件字典 {文件路径: {处理信息}}
        """
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    tracker_data = json.load(f)
                    logger.info(f"✓ 成功加载跟踪记录，包含 {len(tracker_data)} 个文件")
                    return tracker_data
            except Exception as e:
                logger.warning(f"⚠ 加载跟踪记录失败: {e}，初始化为空")
                return {}
        
        logger.debug(f"跟踪记录文件不存在，初始化为空: {self.tracker_file}")
        return {}
    
    def _save_tracker(self):
        """保存跟踪记录到文件"""
        try:
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_files, f, ensure_ascii=False, indent=2)
            logger.debug(f"✓ 跟踪记录已保存，总计 {len(self.processed_files)} 个文件")
        except Exception as e:
            logger.error(f"❌ 保存跟踪记录失败: {e}")
    
    def is_processed(self, file_path):
        """
        检查文件是否已处理过
        
        Args:
            file_path: 文件路径（支持相对路径或绝对路径）
        
        Returns:
            bool: True 表示已处理，False 表示未处理
        """
        file_path = str(Path(file_path).absolute())
        
        if file_path in self.processed_files:
            record = self.processed_files[file_path]
            status = record.get('status', 'unknown')
            logger.debug(f"✓ 文件已处理（状态: {status}），跳过: {Path(file_path).name}")
            return True
        
        return False
    
    def mark_as_processed(self, file_path, excel_path=None, status="success"):
        """
        标记文件为已处理
        
        Args:
            file_path: 图片文件路径
            excel_path: 生成的 Excel 文件路径（可选）
            status: 处理状态，可选值：
                - "success": 成功处理
                - "failed": 处理失败
                - "skipped": 跳过处理
        
        Returns:
            bool: 是否标记成功
        """
        try:
            file_path = str(Path(file_path).absolute())
            
            self.processed_files[file_path] = {
                'timestamp': datetime.now().isoformat(),
                'excel_path': excel_path,
                'status': status
            }
            
            self._save_tracker()
            
            if status == "success":
                logger.info(f"✓ 文件已标记为已处理: {Path(file_path).name}")
            elif status == "failed":
                logger.warning(f"⚠ 文件标记为失败: {Path(file_path).name}")
            else:
                logger.debug(f"✓ 文件已标记为 {status}: {Path(file_path).name}")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ 标记文件失败: {e}")
            return False
    
    def get_processed_count(self):
        """
        获取已处理文件总数
        
        Returns:
            int: 已处理文件数量
        """
        return len(self.processed_files)
    
    def get_unprocessed_files(self, file_list):
        """
        从文件列表中筛选出未处理的文件
        
        Args:
            file_list: 文件路径列表
        
        Returns:
            list: 未处理的文件路径列表
        """
        unprocessed = []
        
        for file_path in file_list:
            if not self.is_processed(file_path):
                unprocessed.append(file_path)
        
        return unprocessed
    
    def get_processed_files(self):
        """
        获取所有已处理文件列表
        
        Returns:
            list: 已处理文件路径列表
        """
        return list(self.processed_files.keys())
    
    def get_processed_by_status(self, status="success"):
        """
        按状态获取已处理文件
        
        Args:
            status: 状态过滤器（"success", "failed", "skipped"）
        
        Returns:
            list: 符合条件的文件路径列表
        """
        matched = []
        
        for file_path, info in self.processed_files.items():
            if info.get('status') == status:
                matched.append(file_path)
        
        return matched
    
    def remove_file(self, file_path):
        """
        从跟踪中移除某个文件（用于重新处理）
        
        Args:
            file_path: 文件路径
        
        Returns:
            bool: 是否移除成功
        """
        file_path = str(Path(file_path).absolute())
        
        if file_path in self.processed_files:
            del self.processed_files[file_path]
            self._save_tracker()
            logger.info(f"✓ 文件已从跟踪中移除，将重新处理: {Path(file_path).name}")
            return True
        else:
            logger.warning(f"⚠ 文件未在跟踪记录中: {Path(file_path).name}")
            return False
    
    def clear_tracker(self):
        """
        清空所有跟踪记录（谨慎使用！）
        
        清空后，所有文件都会被重新处理
        """
        file_count = len(self.processed_files)
        self.processed_files = {}
        self._save_tracker()
        logger.warning(f"⚠ 文件跟踪记录已清空，移除了 {file_count} 个文件记录")
        logger.warning("⚠ 下次运行时，所有文件都将被重新处理")
    
    def get_stats(self):
        """
        获取统计信息
        
        Returns:
            dict: 统计信息
        """
        success_count = len(self.get_processed_by_status("success"))
        failed_count = len(self.get_processed_by_status("failed"))
        skipped_count = len(self.get_processed_by_status("skipped"))
        
        return {
            'total': len(self.processed_files),
            'success': success_count,
            'failed': failed_count,
            'skipped': skipped_count
        }
