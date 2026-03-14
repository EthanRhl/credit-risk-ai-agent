# modules/llm_agent.py
import json
import sys
import os

# 导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MOONSHOT_API_KEY, MOONSHOT_BASE_URL, MOONSHOT_MODEL

# 安装依赖：pip install openai
from openai import OpenAI


def init_client():
    """初始化Moonshot客户端"""
    return OpenAI(
        api_key=MOONSHOT_API_KEY,
        base_url=MOONSHOT_BASE_URL
    )


def analyze_risk(ocr_fields, asr_text):
    """
    使用Moonshot大模型进行信贷风险决策

    参数:
        ocr_fields: dict, OCR提取的身份证字段
        asr_text: str, 语音转文字内容

    返回:
        dict: 风险分析结果
    """
    try:
        client = init_client()

        # 构建Prompt
        prompt = build_risk_prompt(ocr_fields, asr_text)

        # 调用API
        response = client.chat.completions.create(
            model=MOONSHOT_MODEL,
            messages=[
                {"role": "system", "content": "你是一名专业的金融信贷风控审核员，拥有丰富的信贷审批经验。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # 降低随机性
            max_tokens=1000
        )

        # 解析结果
        result_text = response.choices[0].message.content

        # 尝试解析JSON
        risk_result = parse_risk_result(result_text)

        # 计算API调用成本（估算）
        tokens_used = response.usage.total_tokens
        cost = (tokens_used / 1000) * 0.012  # 8k模型价格

        return {
            "status": "success",
            "message": "风险分析完成",
            "data": risk_result,
            "tokens_used": tokens_used,
            "estimated_cost": f"¥{cost:.4f}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"大模型调用失败: {str(e)}",
            "data": get_rule_based_risk(ocr_fields, asr_text),  # 降级为规则判断
            "tokens_used": 0,
            "estimated_cost": "¥0.00"
        }


def build_risk_prompt(ocr_fields, asr_text):
    """构建风险分析Prompt"""

    prompt = f"""
请根据以下客户信息进行信贷风险评估：

【客户基本信息】
- 姓名：{ocr_fields.get('姓名', '未识别')}
- 身份证号：{ocr_fields.get('身份证号', '未识别')}
- 性别：{ocr_fields.get('性别', '未识别')}
- 民族：{ocr_fields.get('民族', '未识别')}
- 出生日期：{ocr_fields.get('出生日期', '未识别')}
- 住址：{ocr_fields.get('住址', '未识别')}

【客户语音陈述】
{asr_text if asr_text else '无语音信息'}

【评估要求】
请严格按照以下JSON格式输出（只输出JSON，不要其他文字）：
{{
    "risk_level": "HIGH/MEDIUM/LOW",
    "risk_score": 0-100之间的整数,
    "risk_factors": ["风险因素1", "风险因素2", ...],
    "recommendation": "通过/拒绝/人工复核",
    "reasoning": "200字以内的详细分析理由"
}}

【风险评估标准】
- 高风险(HIGH, 70-100分)：年龄<22岁或>60岁、无稳定收入、负债过高、语音中透露还款困难
- 中风险(MEDIUM, 40-69分)：年龄22-35岁、收入一般、有少量负债、语音中态度犹豫
- 低风险(LOW, 0-39分)：年龄35-50岁、收入稳定且较高、无负债、语音中表达清晰且还款意愿强

请基于以上标准进行专业评估。
"""
    return prompt


def parse_risk_result(result_text):
    """解析大模型返回的JSON结果"""
    try:
        # 尝试直接解析
        result = json.loads(result_text)
    except:
        # 尝试提取JSON部分
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            # 解析失败，返回默认结构
            result = {
                "risk_level": "MEDIUM",
                "risk_score": 50,
                "risk_factors": ["无法解析大模型返回结果"],
                "recommendation": "人工复核",
                "reasoning": result_text[:200]
            }

    return result


def get_rule_based_risk(ocr_fields, asr_text):
    """降级方案：基于规则的风险判断（当API失败时使用）"""
    # 简单规则示例
    risk_score = 50
    risk_factors = []

    # 年龄判断
    birth = ocr_fields.get('出生日期', '')
    if birth:
        try:
            year = int(birth[:4])
            age = 2025 - year
            if age < 22 or age > 60:
                risk_score += 30
                risk_factors.append(f"年龄{age}岁，超出优选范围")
            elif 35 <= age <= 50:
                risk_score -= 20
                risk_factors.append(f"年龄{age}岁，属于优质年龄段")
        except:
            pass

    # 确定风险等级
    if risk_score >= 70:
        risk_level = "HIGH"
        recommendation = "拒绝"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
        recommendation = "人工复核"
    else:
        risk_level = "LOW"
        recommendation = "通过"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_factors": risk_factors if risk_factors else ["基于规则评估"],
        "recommendation": recommendation,
        "reasoning": "基于预设规则的自动评估（大模型调用失败时的降级方案）"
    }


def analyze_risk_simple(ocr_text, asr_text):
    """
    兼容旧版本的函数（如果app.py调用的是这个）
    """
    # 简单提取字段
    fields = {
        '姓名': '',
        '身份证号': '',
        '性别': '',
        '民族': '',
        '出生日期': '',
        '住址': ''
    }
    result = analyze_risk(fields, asr_text)
    return result.get('data', {})


if __name__ == "__main__":
    # 本地测试
    test_ocr = {
        '姓名': '张三',
        '身份证号': '110101199001011234',
        '性别': '男',
        '民族': '汉',
        '出生日期': '1990年01月01日',
        '住址': '北京市朝阳区某某路某某号'
    }
    test_asr = "我想申请一笔5万元的贷款，用于装修房子，我有稳定的工作，月收入8000元。"

    result = analyze_risk(test_ocr, test_asr)
    print("=" * 50)
    print(f"状态：{result['status']}")
    print(f"Token消耗：{result.get('tokens_used', 0)}")
    print(f"估算成本：{result.get('estimated_cost', '¥0.00')}")
    print("=" * 50)
    if result['data']:
        for k, v in result['data'].items():
            print(f"{k}: {v}")
    print("=" * 50)