import plotly.graph_objects as go


def create_risk_chart(risk_level):
    """
    根据风险等级生成雷达图
    """
    # 定义不同等级的分数
    scores_map = {
        "LOW": [90, 95, 85, 90, 88],
        "MEDIUM": [60, 70, 65, 60, 65],
        "HIGH": [20, 30, 25, 20, 30]
    }

    values = scores_map.get(risk_level, [50, 50, 50, 50, 50])

    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=['身份真实性', '还款意愿', '金额匹配度', '历史信用', '行为一致性'],
        fill='toself',
        name='综合评分'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title=f"AI 智能体风险评估雷达图：{risk_level}",
        height=400
    )

    return fig