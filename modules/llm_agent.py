import json
import re


class LLMAgent:
    """大模型决策代理"""
    
    def __init__(self, api_key=None, model='moonshot-v1-8k', base_url=None):
        """
        初始化大模型代理
        
        参数:
            api_key: API密钥
            model: 模型名称
            base_url: API基础URL
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or 'https://api.moonshot.cn/v1'
        self.client = None
    
    def _init_client(self):
        """初始化API客户端"""
        if self.client is None:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise ImportError("请安装openai库: pip install openai")
    
    def build_prompt(self, ocr_fields, voice_text):
        """
        构建优化的Prompt
        
        参数:
            ocr_fields: OCR提取的字段
            voice_text: 语音转写文本
        """
        # 提取客户信息
        name = ocr_fields.get('name', '未知')
        age = ocr_fields.get('age', '未知')
        gender = ocr_fields.get('gender', '未知')
        
        # 从语音文本提取信息（简化处理）
        income = self._extract_income(voice_text)
        purpose = self._extract_purpose(voice_text)
        
        prompt = f"""你是一位专业的信贷风险评估专家，请根据以下客户信息进行风险评估。

## 客户信息
- 姓名：{name}
- 年龄：{age}岁
- 性别：{gender}
- 月收入：{income}元
- 贷款用途：{purpose}

## 评估要求
1. 综合评估客户风险等级（低/中/高）
2. 给出风险评分（0-100分，分数越高风险越大）
3. 列出主要风险因素（至少2个）
4. 提供审核建议

## 输出格式（严格按JSON格式输出）
{{
  "risk_level": "低",
  "risk_score": 25,
  "risk_factors": ["因素1", "因素2"],
  "recommendation": "审核建议",
  "reasoning": "详细分析原因"
}}

## 参考案例
案例1：年龄25岁，月收入8000元，负债比20%，工作3年
→ 风险等级：低，评分：25分，建议：正常审批

案例2：年龄58岁，月收入3000元，负债比60%，工作1年
→ 风险等级：高，评分：75分，建议：谨慎审批或拒绝

请根据以上信息进行风险评估，直接输出JSON结果："""
        
        return prompt, {
            'name': name,
            'age': age,
            'gender': gender,
            'income': income,
            'purpose': purpose
        }
    
    def _extract_income(self, text):
        """从文本中提取收入信息"""
        if not text:
            return '未知'
        
        # 尝试匹配收入数字
        patterns = [
            r'月收入[约]?(\d+)',
            r'收入[约]?(\d+)',
            r'月薪[约]?(\d+)',
            r'每个月[约]?(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return '未知'
    
    def _extract_purpose(self, text):
        """从文本中提取贷款用途"""
        if not text:
            return '未知'
        
        purposes = ['装修', '购车', '教育', '医疗', '旅游', '创业', '消费', '周转']
        for purpose in purposes:
            if purpose in text:
                return purpose
        
        return '个人消费'
    
    def analyze(self, ocr_fields, voice_text):
        """
        进行风险分析
        
        参数:
            ocr_fields: OCR提取的字段
            voice_text: 语音转写文本
        """
        # 如果没有API Key，返回模拟结果
        if not self.api_key or self.api_key == 'your_api_key_here':
            return self._mock_analyze(ocr_fields, voice_text)
        
        try:
            self._init_client()
            
            prompt, customer_info = self.build_prompt(ocr_fields, voice_text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': '你是一位专业的信贷风险评估专家，请严格按照JSON格式输出结果。'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            
            # 解析JSON结果
            result = self._parse_result(result_text)
            result['customer_info'] = customer_info
            result['tokens_used'] = response.usage.total_tokens if hasattr(response, 'usage') else 0
            result['estimated_cost'] = f"¥{result['tokens_used'] * 0.00001:.4f}"
            
            return {
                'status': 'success',
                'data': result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'data': self._mock_analyze(ocr_fields, voice_text)
            }
    
    def _parse_result(self, text):
        """解析模型输出的JSON结果"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # 解析失败，返回默认值
        return {
            'risk_level': '中',
            'risk_score': 50,
            'risk_factors': ['无法解析模型输出'],
            'recommendation': '建议人工审核',
            'reasoning': text[:200]
        }
    
    def _mock_analyze(self, ocr_fields, voice_text):
        """模拟分析（无API Key时使用）"""
        age = ocr_fields.get('age', 30)
        
        # 简单的规则模拟
        if age < 25:
            return {
                'risk_level': '中',
                'risk_score': 45,
                'risk_factors': ['年龄较小', '工作经验可能不足'],
                'recommendation': '建议谨慎审批，可适当降低额度',
                'reasoning': f'客户年龄{age}岁，属于年轻群体，建议关注还款能力'
            }
        elif age > 55:
            return {
                'risk_level': '高',
                'risk_score': 65,
                'risk_factors': ['年龄偏大', '收入稳定性需关注'],
                'recommendation': '建议谨慎审批或增加担保',
                'reasoning': f'客户年龄{age}岁，属于高风险年龄段'
            }
        else:
            return {
                'risk_level': '低',
                'risk_score': 25,
                'risk_factors': ['年龄适中', '无明显风险因素'],
                'recommendation': '建议正常审批',
                'reasoning': f'客户年龄{age}岁，属于正常工作年龄段'
            }


def analyze_risk(ocr_fields, voice_text, api_key=None):
    """风险分析的便捷函数"""
    agent = LLMAgent(api_key=api_key)
    return agent.analyze(ocr_fields, voice_text)


if __name__ == '__main__':
    # 测试代码
    agent = LLMAgent()
    
    test_ocr = {'name': '张三', 'age': 28, 'gender': '男'}
    test_voice = '我想申请贷款装修房子，月收入8000元'
    
    result = agent.analyze(test_ocr, test_voice)
    print("分析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
