import cv2
import numpy as np
import re
from PIL import Image


class OCREngine:
    """OCR识别引擎"""
    
    def __init__(self, tesseract_path=None, language='chi_sim+eng'):
        """
        初始化OCR引擎
        
        参数:
            tesseract_path: Tesseract可执行文件路径
            language: 识别语言
        """
        self.language = language
        
        # 配置Tesseract路径
        if tesseract_path:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # 形近字校正字典
        self.correction_dict = {
            '男': ['勇', '勇'],
            '女': ['文', '文'],
            '汉': ['汉', '漠'],
            '族': ['族', '挨'],
            '出生': ['出主', '山生'],
            '年': ['午', '年'],
            '月': ['日', '月'],
            '日': ['日', '曰'],
            '住': ['佳', '住'],
            '址': ['扯', '址'],
            '身': ['身', '射'],
            '份': ['份', '份'],
            '证': ['证', '让']
        }
    
    def preprocess_image(self, image_path):
        """
        图像预处理
        
        参数:
            image_path: 图片路径
        """
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # CLAHE增强
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # 自适应阈值二值化
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary, img
    
    def extract_text(self, image_path):
        """
        提取图片中的文字
        
        参数:
            image_path: 图片路径
        """
        try:
            import pytesseract
            
            # 预处理
            processed, original = self.preprocess_image(image_path)
            
            # OCR识别
            text = pytesseract.image_to_string(
                processed,
                lang=self.language,
                config='--psm 6'
            )
            
            # 校正文字
            corrected = self.correct_text(text)
            
            return {
                'status': 'success',
                'text': corrected,
                'confidence': self._estimate_confidence(corrected)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'text': '',
                'confidence': 0
            }
    
    def correct_text(self, text):
        """校正识别错误的文字"""
        corrected = text
        for correct, wrong_list in self.correction_dict.items():
            for wrong in wrong_list:
                corrected = corrected.replace(wrong, correct)
        return corrected
    
    def _estimate_confidence(self, text):
        """估算识别置信度"""
        # 简单的置信度估算：检查是否包含关键字
        keywords = ['姓名', '性别', '民族', '出生', '住址', '公民身份号码']
        found = sum(1 for kw in keywords if kw in text)
        return int(found / len(keywords) * 100)
    
    def extract_id_info(self, image_path):
        """
        提取身份证信息
        
        参数:
            image_path: 身份证图片路径
        """
        result = self.extract_text(image_path)
        
        if result['status'] != 'success':
            return result
        
        text = result['text']
        
        # 提取字段
        fields = {}
        
        # 姓名
        name_match = re.search(r'姓\s*名\s*[：:]?\s*([^\n\r]+)', text)
        if name_match:
            fields['name'] = name_match.group(1).strip()
        
        # 性别
        gender_match = re.search(r'性\s*别\s*[：:]?\s*([男女])', text)
        if gender_match:
            fields['gender'] = gender_match.group(1)
        
        # 民族
        nation_match = re.search(r'民\s*族\s*[：:]?\s*([^\n\r]+)', text)
        if nation_match:
            fields['nation'] = nation_match.group(1).strip()
        
        # 出生日期
        birth_match = re.search(r'出\s*生\s*[：:]?\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', text)
        if birth_match:
            fields['birth_date'] = f"{birth_match.group(1)}-{birth_match.group(2).zfill(2)}-{birth_match.group(3).zfill(2)}"
        
        # 住址
        address_match = re.search(r'住\s*址\s*[：:]?\s*([^\n\r]+)', text)
        if address_match:
            fields['address'] = address_match.group(1).strip()
        
        # 身份证号
        id_match = re.search(r'(\d{17}[\dXx])', text)
        if id_match:
            fields['id_number'] = id_match.group(1).upper()
        
        # 计算年龄
        if 'birth_date' in fields:
            from datetime import datetime
            birth = datetime.strptime(fields['birth_date'], '%Y-%m-%d')
            age = (datetime.now() - birth).days // 365
            fields['age'] = age
        
        return {
            'status': 'success',
            'text': text,
            'fields': fields,
            'confidence': result['confidence']
        }


def extract_id_info(image_path):
    """提取身份证信息的便捷函数"""
    engine = OCREngine()
    return engine.extract_id_info(image_path)


if __name__ == '__main__':
    # 测试代码
    print("OCR引擎初始化成功")
    
    # 如果有测试图片，可以运行以下代码
    # result = extract_id_info('assets/sample_id.jpg')
    # print(result)
