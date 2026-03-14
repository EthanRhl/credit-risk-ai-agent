 🤖 多模态信贷审核智能体

> 基于 OCR + ASR + 大模型的金融信贷风险审核系统 | AI 训练师实战项目

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)

---

## 📌 项目简介

本项目是一个面向金融信贷场景的**多模态 AI 审核系统**，整合了**身份证 OCR 识别**、**语音意图识别**、**大模型风险决策**三大核心模块，可实现从客户材料上传到风险报告生成的全流程自动化审核。

---

## ✨ 功能特点

| 模块 | 功能 | 技术实现 |
|------|------|---------|
| 👁️ 视觉识别 | 身份证信息自动提取 | Tesseract OCR + 图像预处理 + 字典校正 |
| 🎙️ 语音识别 | 客户语音转文字 | SpeechRecognition + 离线模拟降级 |
| 🧠 风险决策 | 智能风险评估与建议 | Moonshot 大模型 + Prompt 工程 |
| 📊 可视化报告 | 风险等级图表展示 | Plotly + Streamlit |

---

## 🛠️ 技术栈

- **编程语言**: Python 3.8+
- **图像处理**: OpenCV, PIL, Tesseract OCR
- **语音处理**: SpeechRecognition, PyAudio
- **大模型**: Moonshot AI (Kimi), OpenAI API 兼容
- **前端交互**: Streamlit
- **数据可视化**: Plotly
- **工具链**: Git, GitHub, PyCharm

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/你的用户名/credit-risk-ai-agent.git
cd credit-risk-ai-agent

# 安装依赖
pip install -r requirements.txt
2. 配置 API Key
bash

编辑



# 复制配置模板
cp config.example.py config.py

# 编辑 config.py，填写你的 Moonshot API Key
# 获取地址：https://platform.moonshot.cn/
3. 运行应用
streamlit run app.py
浏览器访问 http://localhost:8501 即可使用。
项目结构
credit-risk-ai-agent/
├── app.py                 # 主应用入口 (Streamlit)
├── config.py              # 配置文件 (不上传)
├── config.example.py      # 配置模板
├── requirements.txt       # 依赖列表
├── README.md              # 项目说明
├── .gitignore             # Git 忽略文件
├── modules/               # 功能模块
│   ├── ocr_engine.py      # OCR 识别模块
│   ├── asr_engine.py      # 语音识别模块
│   ├── llm_agent.py       # 大模型决策模块
│   └── report_gen.py      # 报告生成模块
└── assets/                # 测试素材
    ├── id_card.jpg        # 测试身份证图片
    └── voice.wav          # 测试录音文件
核心功能说明
1. OCR 识别优化
图像预处理：灰度化 + CLAHE 对比度增强 + 高斯降噪
字典校正：形近字自动校正（如 1/l/I, 0/O/D）
字段提取：正则匹配姓名、身份证号、地址等关键字段
置信度评估：根据字段完整度计算识别可信度
2. 大模型风险决策
基于 Moonshot API 进行智能风险评估
Prompt 工程：角色设定 + 任务描述 + 输出格式规范
降级方案：API 失败时自动切换规则引擎
成本控制：单次调用约 ¥0.005-0.01
3. 语音识别
支持 WAV 格式录音上传
离线模拟降级（网络受限时可用）
语音内容用于辅助风险判断
项目亮点
业务理解: 基于消费金融业务经验设计风控规则
工程落地: 完整可运行的多模态 AI 应用
成本优化: API 调用缓存机制，降低重复调用成本
降级方案: 大模型失败时自动切换规则引擎，保证可用性
可扩展性: 模块化设计，便于接入 RAG、微调等功能
待优化方向
接入 RAG 知识库，检索历史风险案例
支持更多证件类型（驾驶证、银行卡）
增加模型微调模块（LoRA）
部署到云服务器（阿里云/腾讯云）
使用说明
本项目仅用于学习
不得用于真实商业信贷审核场景
生产环境需增加数据加密、权限控制等安全措施
联系方式
平台	信息
GitHub	https://github.com/你的用户名
邮箱	mailto:your.email@example.com
如果觉得有帮助，欢迎 Star 
使用前请修改
位置	原内容	修改为
第 1 处	你的用户名	你的 GitHub 用户名
第 2 处	your.email@example.com	你的真实邮箱
保存步骤
PyCharm 中右键项目根目录 → New → File
输入文件名：README.md
粘贴上述全部内容
按 Ctrl+S 保存
提交到 GitHub：



git add README.md
git commit -m "Add README documentation"
git push
