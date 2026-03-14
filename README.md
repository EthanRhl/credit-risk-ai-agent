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
Python 3.8+ | OpenCV | Tesseract | Moonshot AI | Streamlit | Plotly

## 快速开始
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key（编辑 config.py）
# 获取地址：https://platform.moonshot.cn/

# 3. 运行应用
streamlit run app.py
