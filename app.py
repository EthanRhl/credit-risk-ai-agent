import streamlit as st
import os
import sys

# 添加 modules 到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.ocr_engine import extract_id_info
from modules.asr_engine import transcribe_voice
from modules.llm_agent import analyze_risk
from modules.report_gen import create_risk_chart

st.set_page_config(page_title="多模态信贷审核智能体", layout="wide")

st.title("多模态信贷审核智能体 (AI Training Project)")
st.markdown("""
**项目亮点**：覆盖 OCR 视觉识别、ASR 语音转写、Agent 决策工作流、AIGC 可视化报告。
**操作指南**：左侧上传您的身份证照片和录音，点击开始审核。
""")

# 侧边栏
st.sidebar.header("1. 上传审核材料")
uploaded_file_img = st.sidebar.file_uploader("上传身份证正面 (.jpg)", type=["jpg", "jpeg"])
uploaded_file_audio = st.sidebar.file_uploader("上传客户录音 (.wav)", type=["wav"])

start_btn = st.sidebar.button("开始智能审核", type="primary")

if start_btn:
    if uploaded_file_img and uploaded_file_audio:
        # 保存临时文件
        img_path = "assets/temp_id.jpg"
        audio_path = "assets/temp_voice.wav"

        with open(img_path, "wb") as f:
            f.write(uploaded_file_img.getbuffer())
        with open(audio_path, "wb") as f:
            f.write(uploaded_file_audio.getbuffer())

        st.success("文件上传成功，开始处理...")

        # 分列展示
        col1, col2, col3 = st.columns([1, 1, 1.5])

        # --- 模块 1: 视觉识别 ---
        with col1:
            st.subheader("视觉识别 (OCR)")
            with st.spinner("正在读取身份证信息..."):
                ocr_res = extract_id_info(img_path)
                if ocr_res['status'] == 'success':
                    st.success(f"识别成功 (置信度:{ocr_res.get('confidence', 0)}%)")

                    # 展示提取的字段
                    fields = ocr_res.get('fields', {})
                    st.markdown("**提取字段：**")
                    for k, v in fields.items():
                        if v:
                            st.text(f"{k}: {v}")

                    # 原始文本折叠展示
                    with st.expander("查看原始识别文本"):
                        st.text_area("提取内容预览", ocr_res['data'], height=150)

                    st.image(img_path, caption="原始图片", use_container_width=True)
                else:
                    st.error(f"识别失败：{ocr_res['message']}")

        # --- 模块 2: 语音识别 ---
        with col2:
            st.subheader("🎙️ 语音识别 (ASR)")
            with st.spinner("正在转写录音..."):
                asr_res = transcribe_voice(audio_path)
                if asr_res['status'] in ['success', 'mock']:
                    st.success("转写完成")
                    if asr_res['status'] == 'mock':
                        st.warning("注：使用离线模拟数据 (网络受限)")
                    st.info(f"用户原话：{asr_res['text']}")
                    st.audio(audio_path)
                else:
                    st.error(f"转写失败：{asr_res.get('reason', '未知错误')}")

        # --- 模块 3: 决策与报告 ---
        with col3:
            st.subheader("AI 决策报告")
            with st.spinner("Agent 正在综合研判..."):
                # 即使某一步失败，也尝试传递部分结果
                safe_ocr_fields = ocr_res.get('fields', {}) if ocr_res.get('status') == 'success' else {}
                safe_asr_text = asr_res.get('text', '') if asr_res.get('status') in ['success', 'mock'] else ""

                decision = analyze_risk(safe_ocr_fields, safe_asr_text)

                # 获取风险数据
                risk_data = decision.get('data', {}) if decision.get('status') == 'success' else decision

                risk_level = risk_data.get('risk_level', 'UNKNOWN')
                if risk_level == 'HIGH':
                    st.error(f"风险等级：{risk_level}")
                elif risk_level == 'MEDIUM':
                    st.warning(f"⚡ 风险等级：{risk_level}")
                else:
                    st.success(f"风险等级：{risk_level}")

                # 风险评分
                st.metric("风险评分", f"{risk_data.get('risk_score', 0)}/100")

                # 决策建议
                st.write("**审核建议：**")
                st.write(risk_data.get('recommendation', '暂无建议'))

                # 风险因素
                st.write("**判断依据：**")
                for factor in risk_data.get('risk_factors', ['无']):
                    st.write(f"- {factor}")

                # 分析理由（折叠展示）
                with st.expander("查看详细分析理由"):
                    st.write(risk_data.get('reasoning', '无详细分析'))

                # API 消耗信息（如果有的话）
                if decision.get('status') == 'success':
                    st.info(
                        f"API 消耗：{decision.get('estimated_cost', '¥0.00')} (Tokens: {decision.get('tokens_used', 0)})")

                # 生成图表
                chart = create_risk_chart(risk_level)
                st.plotly_chart(chart, use_container_width=True)

        st.balloons()

    else:
        st.warning("请同时上传身份证图片和录音文件！")
else:
    st.info("请在左侧上传文件并点击开始按钮")