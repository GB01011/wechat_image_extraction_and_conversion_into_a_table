"""
图片预处理模块

功能：
- 图片降噪
- 对比度增强
- 自动旋转校正
- 图片压缩（如果超过尺寸限制）
"""

import cv2
import numpy as np
import os
from src.logger import logger


class ImageProcessor:
    """图片预处理模块，提升OCR识别效果"""
    
    def __init__(self, enable_preprocessing=True, save_processed=False, 
                 max_width=4096, max_height=4096):
        """
        初始化图片处理器
        
        Args:
            enable_preprocessing: 是否启用预处理
            save_processed: 是否保存处理后的图片
            max_width: 最大宽度
            max_height: 最大高度
        """
        self.enable_preprocessing = enable_preprocessing
        self.save_processed = save_processed
        self.max_width = max_width
        self.max_height = max_height
    
    def preprocess_image(self, image_path, output_dir=None):
        """
        预处理图片，提升识别效果
        
        处理步骤：
        1. 检查图片有效性
        2. 图片压缩（如果超过尺寸限制）
        3. 降噪处理
        4. 对比度增强
        5. 自动旋转校正
        
        Args:
            image_path: 输入图片路径
            output_dir: 输出目录（可选）
        
        Returns:
            处理后的图片路径
        """
        try:
            # 1. 验证图片文件
            if not os.path.exists(image_path):
                logger.error(f"图片文件不存在: {image_path}")
                return image_path
            
            # 2. 读取图片
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"无法读取图片: {image_path}")
                return image_path
            
            h, w = img.shape[:2]
            logger.info(f"原始图片尺寸: {w}x{h}")
            
            # 3. 如果不启用预处理，直接返回
            if not self.enable_preprocessing:
                return image_path
            
            # 4. 压缩过大的图片
            if w > self.max_width or h > self.max_height:
                logger.info(f"图片尺寸超限，进行压缩")
                img = self._resize_image(img)
            
            # 5. 降噪处理
            logger.info("执行降噪processing...")
            img = self._denoise_image(img)
            
            # 6. 增强对比度
            logger.info("执行对比度增强...")
            img = self._enhance_contrast(img)
            
            # 7. 自动旋转校正
            logger.info("执行自动旋转校正...")
            img = self._auto_rotate(img)
            
            # 8. 保存或返回
            if output_dir and self.save_processed:
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"processed_{os.path.basename(image_path)}")
                cv2.imwrite(output_path, img)
                logger.info(f"✓ 预处理完成，保存至: {output_path}")
                return output_path
            else:
                # 覆写原文件或临时保存
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, f"temp_{os.path.basename(image_path)}")
                    cv2.imwrite(output_path, img)
                    logger.info(f"✓ 预处理完成，临时保存至: {output_path}")
                    return output_path
                else:
                    logger.info("✓ 预处理完成")
                    return image_path
        
        except Exception as e:
            logger.error(f"图片预处理失败: {e}")
            return image_path
    
    @staticmethod
    def _resize_image(img, max_width=4096, max_height=4096):
        """
        压缩超大图片
        
        Args:
            img: 原始图片
            max_width: 最大宽度
            max_height: 最大高度
        
        Returns:
            压缩后的图片
        """
        h, w = img.shape[:2]
        scale = min(max_width / w, max_height / h, 1.0)
        
        if scale < 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            logger.info(f"图片已压缩至: {new_w}x{new_h}")
        
        return img
    
    @staticmethod
    def _denoise_image(img):
        """
        使用高斯模糊和形态学操作降噪
        
        Args:
            img: 原始图片
        
        Returns:
            降噪后的图片
        """
        try:
            # 使用双边滤波保留边缘的同时降噪
            img = cv2.bilateralFilter(img, 9, 75, 75)
            # 再用高斯模糊进一步平滑
            img = cv2.GaussianBlur(img, (5, 5), 0)
            return img
        except Exception as e:
            logger.warning(f"降噪处理失败: {e}")
            return img
    
    @staticmethod
    def _enhance_contrast(img):
        """
        使用CLAHE（对比度自适应直方图均衡化）增强对比度
        
        Args:
            img: 原始图片
        
        Returns:
            对比度增强后的图片
        """
        try:
            # 转换为LAB颜色空间
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # 对L通道应用CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # 合并回原多通道
            img = cv2.merge([l, a, b])
            img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)
            
            return img
        except Exception as e:
            logger.warning(f"对比度增强失败: {e}")
            return img
    
    @staticmethod
    def _auto_rotate(img):
        """
        自动检测和校正文本方向（倾斜角度）
        
        通过检测直线来推断主要方向，然后旋转
        
        Args:
            img: 原始图片
        
        Returns:
            旋转校正后的图片
        """
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 霍夫直线检测
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
            
            if lines is None or len(lines) == 0:
                logger.debug("未检测到直线，跳过旋转校正")
                return img
            
            # 计算主要直线的角度
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 != x1:  # 避免垂直线导致的除0
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    # 将角度限制在 -45 到 45 度（以水平线为参考）
                    if angle > 45:
                        angle -= 90
                    elif angle < -45:
                        angle += 90
                    angles.append(angle)
            
            if not angles:
                return img
            
            # 找出最常见的角度（众数）
            try:
                from statistics import mode
                dominant_angle = mode(angles)
            except:
                # 如果无法计算众数，使用平均值
                dominant_angle = np.median(angles)
            
            # 仅当角度偏离较大时才旋转
            if abs(dominant_angle) > 2:
                logger.info(f"检测到文本倾斜角度: {dominant_angle:.2f}°，进行校正")
                h, w = img.shape[:2]
                center = (w // 2, h // 2)
                
                # 生成旋转矩阵
                M = cv2.getRotationMatrix2D(center, dominant_angle, 1.0)
                
                # 计算旋转后的图片尺寸
                cos = np.abs(M[0, 0])
                sin = np.abs(M[0, 1])
                new_w = int((h * sin) + (w * cos))
                new_h = int((h * cos) + (w * sin))
                M[0, 2] += (new_w / 2) - center[0]
                M[1, 2] += (new_h / 2) - center[1]
                
                # 执行旋转
                img = cv2.warpAffine(img, M, (new_w, new_h), borderMode=cv2.BORDER_REPLICATE)
                logger.info(f"✓ 旋转完成，新尺寸: {new_w}x{new_h}")
            else:
                logger.debug("文本方向正常，无需旋转")
            
            return img
        
        except Exception as e:
            logger.warning(f"自动旋转校正失败: {e}")
            return img
