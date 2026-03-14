# 多模态信贷审核智能体

基于 OCR + ASR + 大模型的金融信贷风险审核系统

## 项目简介
整合身份证 OCR 识别、语音意图识别、大模型风险决策三大模块，实现信贷审核全流程自动化。

## 功能特点
- **OCR 识别**: Tesseract + 图像预处理 + 字典校正
- **语音识别**: SpeechRecognition + 离线降级
- **风险决策**: Moonshot 大模型 + Prompt 工程
- **可视化报告**: Plotly + Streamlit

## 技术栈
Python 3.12+ | OpenCV | Tesseract | Moonshot AI | Streamlit | Plotly

## 快速开始

# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key（编辑 config.py）
# 获取地址：https://platform.moonshot.cn/

# 3. 运行应用
streamlit run app.py

## 项目结构
├── app.py              # 主应用
├── config.py           # 配置文件
├── modules/            # 功能模块
│   ├── ocr_engine.py   # OCR 识别
│   ├── asr_engine.py   # 语音识别
│   ├── llm_agent.py    # 大模型决策
│   └── report_gen.py   # 报告生成
└── assets/             # 测试素材

核心功能
OCR 优化: 灰度化 + CLAHE 增强 + 形近字校正，识别准确率 85%+
风险决策: 大模型评估 + 规则降级，单次成本约 ¥0.005
语音识别: 支持 WAV 格式，网络受限可离线模拟

项目亮点
完整可运行的多模态 AI 应用
API 失败自动降级，保证可用性
模块化设计，便于扩展

使用说明
项目仅用于学习
不得用于真实商业信贷审核
