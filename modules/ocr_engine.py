# modules/ocr_engine.py
import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
import re
import sys

# 导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TESSERACT_PATH

# 设置Tesseract路径
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# ============ 字典校正 ============
# 形近字校正字典
CHAR_CORRECTION = {
    '1': ['l', 'I', '|', '！'],
    '0': ['O', 'o', 'D'],
    '2': ['Z', 'z'],
    '5': ['S', 's'],
    '8': ['B', 'B'],
    '7': ['T', 't'],
    '民': ['氏', '氐'],
    '族': ['旋', '旅'],
    '住': ['往', '佳'],
    '址': ['扯', '趾'],
}

# 常见姓氏（用于校正）
COMMON_SURNAMES = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
                   '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗',
                   '郑', '梁', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹']


def preprocess_image(image_path, debug_save_path=None):
    """
    图像预处理：灰度化 + 对比度增强（温和版）
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    # 转为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE对比度增强（比直接二值化更温和）
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 轻微降噪
    denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # 保存调试图片
    if debug_save_path:
        cv2.imwrite(debug_save_path, denoised)

    # 转PIL格式
    pil_img = Image.fromarray(denoised)
    return pil_img


def correct_with_dict(text):
    """基于字典的后处理校正"""
    corrected = text

    # 形近字校正
    for correct_char, wrong_chars in CHAR_CORRECTION.items():
        for wrong in wrong_chars:
            corrected = corrected.replace(wrong, correct_char)

    return corrected


def extract_id_info(image_path):
    """
    主函数：OCR识别身份证信息
    """
    if not os.path.exists(image_path):
        return {"status": "error", "message": "文件未找到", "data": "", "fields": {}}

    try:
        # 1. 预处理
        debug_path = os.path.join(os.path.dirname(image_path), "processed_debug.jpg")
        processed_img = preprocess_image(image_path, debug_save_path=debug_path)

        if processed_img is None:
            return {"status": "error", "message": "无法读取图片", "data": "", "fields": {}}

        # 2. OCR识别
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed_img, lang='chi_sim+eng', config=custom_config)

        # 3. 字典校正
        clean_text = correct_with_dict(text)

        # 4. 提取关键字段（正则匹配）
        fields = extract_fields(clean_text)

        # 5. 计算置信度（根据字段完整度）
        confidence = calculate_confidence(fields)

        return {
            "status": "success",
            "message": "识别成功",
            "data": clean_text,
            "fields": fields,
            "confidence": confidence,
            "preview": clean_text[:300]
        }

    except Exception as e:
        return {"status": "error", "message": f"处理异常: {str(e)}", "data": "", "fields": {}}


def extract_fields(text):
    """从OCR文本中提取关键字段"""
    fields = {}

    # 身份证号匹配（18位）
    id_pattern = r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]'
    id_match = re.search(id_pattern, text)
    fields['身份证号'] = id_match.group(0) if id_match else ""

    # 姓名匹配（2-4个汉字，通常在"姓名"后面）
    name_pattern = r'姓名[：:\s]*([王李张刘陈杨赵黄周吴徐孙马朱胡郭何高林郑梁谢宋唐许韩冯邓曹][\u4e00-\u9fa5]{1,3})'
    name_match = re.search(name_pattern, text)
    fields['姓名'] = name_match.group(1) if name_match else ""

    # 性别匹配
    gender_pattern = r'性别[：:\s]*([男女])'
    gender_match = re.search(gender_pattern, text)
    fields['性别'] = gender_match.group(1) if gender_match else ""

    # 民族匹配
    ethnicity_pattern = r'民族[：:\s]*([汉回满蒙藏维壮])'
    ethnicity_match = re.search(ethnicity_pattern, text)
    fields['民族'] = ethnicity_match.group(1) if ethnicity_match else ""

    # 出生日期匹配
    birth_pattern = r'(18|19|20)\d{2}年(0?[1-9]|1[0-2])月(0?[1-9]|[12]\d|3[01])日'
    birth_match = re.search(birth_pattern, text)
    fields['出生日期'] = birth_match.group(0) if birth_match else ""

    # 地址匹配
    address_pattern = r'住址[：:\s]*([\u4e00-\u9fa5]{10,})'
    address_match = re.search(address_pattern, text)
    fields['住址'] = address_match.group(1) if address_match else ""

    return fields


def calculate_confidence(fields):
    """根据字段完整度计算置信度"""
    required_fields = ['姓名', '身份证号', '性别', '民族', '出生日期', '住址']
    filled = sum(1 for f in required_fields if fields.get(f))
    confidence = (filled / len(required_fields)) * 100
    return round(confidence, 1)


if __name__ == "__main__":
    # 本地测试
    test_path = "../assets/id_card.jpg"
    if not os.path.exists(test_path):
        test_path = "assets/id_card.jpg"

    result = extract_id_info(test_path)
    print("=" * 50)
    print(f"状态：{result['status']}")
    print(f"置信度：{result.get('confidence', 0)}%")
    print("=" * 50)
    for k, v in result.get('fields', {}).items():
        print(f"{k}: {v}")
    print("=" * 50)