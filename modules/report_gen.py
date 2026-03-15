import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_risk_chart(risk_level, risk_score=50):
    """
    创建风险评分图表
    
    参数:
        risk_level: 风险等级
        risk_score: 风险评分
    """
    # 创建仪表盘图
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"风险等级: {risk_level}"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 60], 'color': "lightyellow"},
                {'range': [60, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': risk_score
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_risk_factors_chart(factors):
    """
    创建风险因素图表
    
    参数:
        factors: 风险因素列表
    """
    if not factors:
        factors = ['无风险因素']
    
    fig = go.Figure(go.Bar(
        x=list(range(1, len(factors) + 1)),
        y=[1] * len(factors),
        text=factors,
        textposition='inside',
        marker_color=['#ff6b6b' if '高' in f else '#ffd93d' if '中' in f else '#6bcb77' for f in factors]
    ))
    
    fig.update_layout(
        title="风险因素",
        xaxis_title="序号",
        yaxis_visible=False,
        height=200,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


if __name__ == '__main__':
    # 测试代码
    fig = create_risk_chart('中', 45)
    fig.show()
