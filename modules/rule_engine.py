class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        """初始化规则引擎"""
        # 风险规则权重
        self.rules = {
            'age': {
                'weight': 20,
                'low_risk': (22, 45),
                'medium_risk': [(18, 22), (45, 55)],
                'high_risk': [(0, 18), (55, 100)]
            },
            'income': {
                'weight': 25,
                'low_risk': (10000, float('inf')),
                'medium_risk': (5000, 10000),
                'high_risk': (0, 5000)
            },
            'debt_ratio': {
                'weight': 30,
                'low_risk': (0, 30),
                'medium_risk': (30, 50),
                'high_risk': (50, 100)
            },
            'work_years': {
                'weight': 15,
                'low_risk': (3, float('inf')),
                'medium_risk': (1, 3),
                'high_risk': (0, 1)
            },
            'credit_history': {
                'weight': 10,
                'good': 0,
                'normal': 10,
                'bad': 30
            }
        }
    
    def evaluate_age(self, age):
        """评估年龄风险"""
        if age is None:
            return 10
        
        rule = self.rules['age']
        
        # 低风险年龄
        if rule['low_risk'][0] <= age <= rule['low_risk'][1]:
            return 0
        # 高风险年龄
        for low, high in rule['high_risk']:
            if low <= age < high:
                return rule['weight']
        # 中风险年龄
        return rule['weight'] // 2
    
    def evaluate_income(self, income):
        """评估收入风险"""
        if income is None:
            return 15
        
        rule = self.rules['income']
        
        if income >= rule['low_risk'][0]:
            return 0
        elif income >= rule['medium_risk'][0]:
            return rule['weight'] // 2
        else:
            return rule['weight']
    
    def evaluate_debt_ratio(self, debt_ratio):
        """评估负债比风险"""
        if debt_ratio is None:
            return 15
        
        rule = self.rules['debt_ratio']
        
        if debt_ratio <= rule['low_risk'][1]:
            return 0
        elif debt_ratio <= rule['medium_risk'][1]:
            return rule['weight'] // 2
        else:
            return rule['weight']
    
    def evaluate_work_years(self, work_years):
        """评估工作年限风险"""
        if work_years is None:
            return 10
        
        rule = self.rules['work_years']
        
        if work_years >= rule['low_risk'][0]:
            return 0
        elif work_years >= rule['medium_risk'][0]:
            return rule['weight'] // 2
        else:
            return rule['weight']
    
    def calculate_risk_score(self, customer_info):
        """
        计算综合风险评分
        
        参数:
            customer_info: 客户信息字典
        """
        score = 0
        factors = []
        
        # 年龄评估
        age = customer_info.get('age')
        age_score = self.evaluate_age(age)
        score += age_score
        if age_score > 0:
            if age and (age < 22 or age > 55):
                factors.append(f"年龄{age}岁，属于风险年龄段")
        
        # 收入评估
        income = customer_info.get('income')
        income_score = self.evaluate_income(income)
        score += income_score
        if income_score > 0:
            if income and income < 5000:
                factors.append(f"月收入{income}元，收入偏低")
        
        # 负债比评估
        debt_ratio = customer_info.get('debt_ratio')
        debt_score = self.evaluate_debt_ratio(debt_ratio)
        score += debt_score
        if debt_score > 0:
            if debt_ratio and debt_ratio > 50:
                factors.append(f"负债比{debt_ratio}%，负债较高")
        
        # 工作年限评估
        work_years = customer_info.get('work_years')
        work_score = self.evaluate_work_years(work_years)
        score += work_score
        if work_score > 0:
            if work_years is not None and work_years < 1:
                factors.append("工作年限不足1年")
        
        # 确保分数在0-100范围内
        score = min(100, max(0, score))
        
        return score, factors
    
    def get_risk_level(self, score):
        """
        根据评分获取风险等级
        
        参数:
            score: 风险评分
        """
        if score < 30:
            return '低'
        elif score < 60:
            return '中'
        else:
            return '高'
    
    def get_recommendation(self, score, risk_level):
        """
        获取审核建议
        
        参数:
            score: 风险评分
            risk_level: 风险等级
        """
        if risk_level == '低':
            return "建议：正常审批，可给予标准额度"
        elif risk_level == '中':
            return "建议：谨慎审批，建议适当降低额度或增加担保"
        else:
            return "建议：高风险客户，建议拒绝或需额外审核"
    
    def evaluate(self, customer_info):
        """
        完整风险评估
        
        参数:
            customer_info: 客户信息字典
        """
        score, factors = self.calculate_risk_score(customer_info)
        level = self.get_risk_level(score)
        recommendation = self.get_recommendation(score, level)
        
        return {
            'risk_score': score,
            'risk_level': level,
            'risk_factors': factors if factors else ['未发现明显风险因素'],
            'recommendation': recommendation
        }


if __name__ == '__main__':
    # 测试代码
    engine = RuleEngine()
    
    # 测试用例
    test_cases = [
        {'age': 25, 'income': 8000, 'debt_ratio': 20, 'work_years': 3},
        {'age': 58, 'income': 3000, 'debt_ratio': 60, 'work_years': 0.5},
        {'age': 35, 'income': 15000, 'debt_ratio': 25, 'work_years': 5}
    ]
    
    for i, info in enumerate(test_cases, 1):
        result = engine.evaluate(info)
        print(f"\n测试用例 {i}:")
        print(f"  输入: {info}")
        print(f"  风险评分: {result['risk_score']}")
        print(f"  风险等级: {result['risk_level']}")
        print(f"  风险因素: {result['risk_factors']}")
        print(f"  审核建议: {result['recommendation']}")
