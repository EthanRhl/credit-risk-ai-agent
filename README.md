# 多模态信贷审核智能体

## 项目简介

本项目是一个基于OCR、ASR和大模型的多模态信贷审核智能体，整合了身份证OCR识别、语音意图识别和大模型风险决策三大模块。针对大模型决策不稳定的问题，引入规则引擎辅助决策，提升风险评估的准确性和稳定性。

## 技术栈

| 类别 | 工具/技术 |
|------|-----------|
| 编程语言 | Python 3.12 |
| OCR处理 | OpenCV, Tesseract, PaddleOCR |
| 语音识别 | SpeechRecognition |
| 大模型 | Moonshot AI（月之暗面） |
| 规则引擎 | 自定义规则系统 |
| Web框架 | Streamlit |
| 可视化 | Plotly |

## 项目结构

```
credit-risk-ai-agent/
├── README.md                    # 项目文档
├── requirements.txt             # Python依赖
├── config.py                    # 配置文件
├── app.py                       # Streamlit主应用
├── modules/
│   ├── __init__.py
│   ├── ocr_engine.py            # OCR识别模块
│   ├── asr_engine.py            # 语音识别模块
│   ├── llm_agent.py             # 大模型决策模块
│   ├── rule_engine.py           # 规则引擎模块
│   └── report_gen.py            # 报告生成模块
├── assets/                      # 测试素材
│   ├── sample_id.jpg            # 示例身份证图片
│   └── sample_voice.wav         # 示例语音文件
├── scripts/
│   └── evaluate_model.py        # 模型评估脚本
└── docs/
    └── prompt_template.md       # Prompt模板文档
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
conda create -n credit_agent python=3.12
conda activate credit_agent

# 安装依赖
pip install -r requirements.txt

# 安装Tesseract OCR
# Windows: 下载安装 https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

### 2. 配置API Key

编辑 `config.py`，配置大模型API：
```python
# Moonshot AI (推荐)
MOONSHOT_API_KEY = "your_moonshot_api_key"

# 或使用OpenAI
OPENAI_API_KEY = "your_openai_api_key"
```

### 3. 运行应用

```bash
streamlit run app.py
```

## 核心功能

### 1. OCR身份证识别

- 图像预处理：灰度化、CLAHE增强、去噪
- Tesseract文字识别
- 字段提取：姓名、性别、民族、出生日期、住址、身份证号
- 形近字校正字典

### 2. 语音意图识别

- 支持WAV格式语音输入
- 使用SpeechRecognition进行语音转文字
- 提取关键信息：贷款金额、贷款用途、还款意愿

### 3. 规则引擎决策

基于业务规则的风险评估：

| 规则 | 条件 | 风险加分 |
|------|------|----------|
| 年龄规则 | 年龄<22 或 >55 | +20分 |
| 收入规则 | 月收入<3000 | +15分 |
| 负债规则 | 负债比>50% | +25分 |
| 信用规则 | 有逾期记录 | +30分 |
| 工作规则 | 工作年限<1年 | +10分 |

### 4. 大模型风险决策

使用优化后的Prompt进行风险评估：
- 结构化输出格式
- Few-shot示例引导
- Chain-of-Thought推理

## 评估指标

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 风险等级准确率 | 18% | 55%+ | +37% |
| 决策建议准确率 | 16% | 50%+ | +34% |
| 评分可接受率 | 26% | 60%+ | +34% |

## Prompt优化要点

### 优化前（简单Prompt）
```
请根据以下信息评估贷款风险：
姓名：{name}
年龄：{age}
收入：{income}
```

### 优化后（结构化Prompt）
```
你是一位专业的信贷风险评估专家，请根据以下客户信息进行风险评估。

## 客户信息
- 姓名：{name}
- 年龄：{age}岁
- 月收入：{income}元
- 负债比：{debt_ratio}%
- 工作年限：{work_years}年

## 评估要求
1. 综合评估客户风险等级（低/中/高）
2. 给出风险评分（0-100分，分数越高风险越大）
3. 列出主要风险因素
4. 提供审核建议

## 输出格式（JSON）
{
  "risk_level": "低/中/高",
  "risk_score": 数字,
  "risk_factors": ["因素1", "因素2"],
  "recommendation": "审核建议",
  "reasoning": "详细分析"
}

## 参考案例
案例1：年龄25岁，月收入8000元，负债比20%，工作3年
→ 风险等级：低，评分：25分，建议：正常审批

案例2：年龄58岁，月收入3000元，负债比60%，工作1年
→ 风险等级：高，评分：75分，建议：谨慎审批或拒绝
```

## 规则引擎设计

```python
class RuleEngine:
    """规则引擎"""
    
    def calculate_risk_score(self, customer_info):
        score = 0
        
        # 年龄规则
        age = customer_info.get('age', 0)
        if age < 22 or age > 55:
            score += 20
        
        # 收入规则
        income = customer_info.get('income', 0)
        if income < 3000:
            score += 15
        elif income < 5000:
            score += 5
        
        # 负债规则
        debt_ratio = customer_info.get('debt_ratio', 0)
        if debt_ratio > 50:
            score += 25
        elif debt_ratio > 30:
            score += 10
        
        return score
    
    def get_risk_level(self, score):
        if score < 30:
            return '低'
        elif score < 60:
            return '中'
        else:
            return '高'
```

## 项目亮点

1. **多模态融合**：OCR + ASR + LLM三种技术整合
2. **规则引擎**：业务规则辅助决策，提升稳定性
3. **Prompt优化**：结构化输出、Few-shot示例
4. **模块化设计**：各模块独立，易于维护扩展
5. **Web应用**：Streamlit快速构建交互界面

## 学习要点

- OCR图像处理流程
- 语音识别技术应用
- 大模型Prompt工程
- 规则引擎设计
- 多模态系统架构

## 注意事项

- 本项目仅用于学习交流
- 不得用于真实商业信贷审核
- 测试数据为模拟数据
- 实际效果需使用真实业务数据验证

## 作者

EthanRhl

## 许可证

MIT License
