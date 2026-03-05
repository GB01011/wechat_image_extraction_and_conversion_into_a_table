import cv2
import numpy as np
import os
from src.logger import logger

class ImageProcessor:
    """图片预处理模块"""
    
    @staticmethod
    def preprocess_image(image_path, output_dir=None):
        """
        预处理图片，提升识别效果
        
        Args:
            image_path: 输入图片路径
            output_dir: 输出目录（可选）
        
        Returns:
            处理后的图片路径
        """
        try:
            # 读取图片
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"无法读取图片: {image_path}")
                return image_path
            
            # 1. 降噪
            img = cv2.fastNlMeansDenoisingColored(img, None, h=10, hForColorComponents=10, templateWindowSize=7, searchWindowSize=21)
            
            # 2. 增强对比度
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            img = cv2.merge([l, a, b])
            img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)
            
            # 3. 自动旋转校正（检测文本方向）
            img = ImageProcessor._auto_rotate(img)
            
            # 保存或返回
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"processed_{os.path.basename(image_path)}")
                cv2.imwrite(output_path, img)
                logger.info(f"预处理完成: {output_path}")
                return output_path
            
            return image_path
        
        except Exception as e:
            logger.error(f"图片预处理失败: {e}")
            return image_path
    
    @staticmethod
    def _auto_rotate(img):
        """自动旋转图片"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
        
        if lines is None or len(lines) == 0:
            return img
        
        # 计算主要直线的角度
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            angles.append(angle)
        
        # 选择最常见的角度
        from statistics import mode
        try:
            dominant_angle = mode(angles)
        except:
            dominant_angle = np.mean(angles)
        
        # 旋转图片
        if abs(dominant_angle) > 5:
            h, w = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, dominant_angle, 1.0)
            img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        
        return img