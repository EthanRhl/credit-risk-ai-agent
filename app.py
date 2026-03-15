import streamlit as st
import os
import sys

# 添加modules到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ocr_engine import extract_id_info
from modules.asr_engine import transcribe_voice
from modules.llm_agent import analyze_risk
from modules.rule_engine import RuleEngine

# 页面配置
st.set_page_config(
    page_title="多模态信贷审核智能体",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题
st.title("多模态信贷审核智能体")
st.markdown("""
**项目亮点**：OCR身份证识别 + 语音意图识别 + 规则引擎 + 大模型决策

**使用说明**：左侧上传身份证图片和语音文件，点击开始审核
""")

# 侧边栏
st.sidebar.header("上传审核材料")
uploaded_file_img = st.sidebar.file_uploader(
    "上传身份证正面 (.jpg/.png)", 
    type=["jpg", "jpeg", "png"]
)
uploaded_file_audio = st.sidebar.file_uploader(
    "上传客户录音 (.wav)", 
    type=["wav"]
)

# API Key输入
st.sidebar.header("API配置（可选）")
api_key = st.sidebar.text_input(
    "Moonshot API Key", 
    type="password",
    help="不填写则使用规则引擎模拟决策"
)

start_btn = st.sidebar.button("开始智能审核", type="primary")

# 初始化规则引擎
rule_engine = RuleEngine()

if start_btn:
    if uploaded_file_img:
        # 保存临时文件
        img_path = "assets/temp_id.jpg"
        with open(img_path, "wb") as f:
            f.write(uploaded_file_img.getbuffer())
        
        st.success("文件上传成功，开始处理...")
        
        # 分列展示
        col1, col2, col3 = st.columns([1, 1, 1.5])
        
        # --- 模块1: OCR识别 ---
        with col1:
            st.subheader("视觉识别 (OCR)")
            with st.spinner("正在读取身份证信息..."):
                ocr_res = extract_id_info(img_path)
                
                if ocr_res['status'] == 'success':
                    st.success(f"识别成功 (置信度: {ocr_res.get('confidence', 0)}%)")
                    
                    # 展示提取的字段
                    fields = ocr_res.get('fields', {})
                    st.markdown("**提取字段：**")
                    for k, v in fields.items():
                        if v:
                            st.text(f"{k}: {v}")
                    
                    # 原始文本折叠展示
                    with st.expander("查看原始识别文本"):
                        st.text_area("提取内容预览", ocr_res['text'], height=150)
                    
                    st.image(img_path, caption="原始图片", use_container_width=True)
                else:
                    st.error(f"识别失败：{ocr_res.get('message', '未知错误')}")
        
        # --- 模块2: 语音识别 ---
        with col2:
            st.subheader("语音识别 (ASR)")
            
            if uploaded_file_audio:
                audio_path = "assets/temp_voice.wav"
                with open(audio_path, "wb") as f:
                    f.write(uploaded_file_audio.getbuffer())
                
                with st.spinner("正在转写录音..."):
                    asr_res = transcribe_voice(audio_path)
                    
                    if asr_res['status'] in ['success', 'mock']:
                        st.success("转写完成")
                        if asr_res['status'] == 'mock':
                            st.warning("注：使用模拟数据")
                        st.info(f"用户原话：{asr_res['text']}")
                        st.audio(audio_path)
                    else:
                        st.error(f"转写失败：{asr_res.get('reason', '未知错误')}")
            else:
                st.info("未上传语音文件")
                asr_res = {'status': 'mock', 'text': '我想申请贷款，月收入8000元'}
        
        # --- 模块3: 决策与报告 ---
        with col3:
            st.subheader("AI决策报告")
            
            with st.spinner("正在综合研判..."):
                # 获取OCR字段
                safe_ocr_fields = ocr_res.get('fields', {}) if ocr_res.get('status') == 'success' else {}
                safe_asr_text = asr_res.get('text', '') if asr_res.get('status') in ['success', 'mock'] else ""
                
                # 1. 规则引擎评估
                rule_result = rule_engine.evaluate({
                    'age': safe_ocr_fields.get('age'),
                    'income': 8000,  # 默认值
                    'debt_ratio': 30,
                    'work_years': 2
                })
                
                # 2. 大模型评估
                llm_result = analyze_risk(safe_ocr_fields, safe_asr_text, api_key=api_key if api_key else None)
                
                # 合并结果
                if llm_result.get('status') == 'success':
                    llm_data = llm_result.get('data', {})
                    risk_level = llm_data.get('risk_level', rule_result['risk_level'])
                    risk_score = llm_data.get('risk_score', rule_result['risk_score'])
                    risk_factors = llm_data.get('risk_factors', rule_result['risk_factors'])
                    recommendation = llm_data.get('recommendation', rule_result['recommendation'])
                else:
                    risk_level = rule_result['risk_level']
                    risk_score = rule_result['risk_score']
                    risk_factors = rule_result['risk_factors']
                    recommendation = rule_result['recommendation']
                
                # 显示风险等级
                if risk_level == '高':
                    st.error(f"风险等级：{risk_level}")
                elif risk_level == '中':
                    st.warning(f"风险等级：{risk_level}")
                else:
                    st.success(f"风险等级：{risk_level}")
                
                # 风险评分
                st.metric("风险评分", f"{risk_score}/100")
                
                # 决策建议
                st.write("**审核建议：**")
                st.write(recommendation)
                
                # 风险因素
                st.write("**判断依据：**")
                for factor in risk_factors:
                    st.write(f"- {factor}")
                
                # 规则引擎结果（折叠展示）
                with st.expander("查看规则引擎评估详情"):
                    st.json({
                        'rule_engine_score': rule_result['risk_score'],
                        'rule_engine_level': rule_result['risk_level'],
                        'rule_engine_factors': rule_result['risk_factors']
                    })
        
        st.balloons()
    
    else:
        st.warning("请上传身份证图片！")

else:
    st.info("请在左侧上传文件并点击开始按钮")
    
    # 展示项目说明
    with st.expander("项目说明"):
        st.markdown("""
        ### 项目特点
        
        1. **OCR身份证识别**
           - 图像预处理：灰度化、CLAHE增强
           - Tesseract文字识别
           - 字段提取：姓名、年龄、性别等
        
        2. **语音意图识别**
           - 支持WAV格式语音
           - 提取贷款金额、用途等关键信息
        
        3. **规则引擎决策**
           - 年龄、收入、负债比等规则评估
           - 稳定的风险评分系统
        
        4. **大模型辅助决策**
           - 优化后的Prompt工程
           - 结构化JSON输出
           - Few-shot示例引导
        
        ### 注意事项
        - 本项目仅用于学习交流
        - 不得用于真实商业信贷审核
        """)
