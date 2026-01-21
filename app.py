import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- 배경 설정 및 CSS (React의 UI 감각 재현) ---
st.set_page_config(page_title="B-Balance.tech", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1d4ed8;
        color: white;
    }
    .result-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 핵심 로직 (summarize 함수 이식) ---
def calculate_vector_sum(data):
    sx, sy = 0, 0
    for _, row in data.iterrows():
        m = float(row['Moment']) if row['Moment'] else 0
        p = float(row['Phase'])
        rad = np.radians(p)
        sx += m * np.cos(rad)
        sy += m * np.sin(rad)
    
    mag = np.hypot(sx, sy)
    ang = (np.degrees(np.atan2(sy, sx)) + 360) % 360
    return mag, ang

# --- 언어 선택 ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'ko'

col_title, col_lang = st.columns([4, 1])
with col_title:
    st.title("🌐 B-Balance.tech")
with col_lang:
    if st.button("🌐 English / 한국어"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ko' else 'ko'

L = {
    'ko': {
        'hero': "Global Blade Balancing — Physics 기반 정밀 검증",
        'sub': "데이터와 물리 법칙에 기반한 정밀 검증. 전 세계 어디서나 이메일로 의뢰하고 즉시 검증하세요.",
        'tab1': "🔍 검증(벡터 합성) 툴",
        'tab2': "📧 이메일로 의뢰",
        'count': "블레이드 개수 (N)",
        'start': "시작 각도 (Start °)",
        'res': "합성 결과 (Resultant)",
        'mail_body': "안녕하세요, 블레이드 밸런싱 최적화 의뢰를 문의합니다."
    },
    'en': {
        'hero': "Global Blade Balancing — Verified by Physics",
        'sub': "Data- and physics-based verification. Request via email and verify instantly on this portal.",
        'tab1': "🔍 Verification Tool",
        'tab2': "📧 Order via Email",
        'count': "Number of Blades (N)",
        'start': "Start Angle (Start °)",
        'res': "Resultant",
        'mail_body': "Hello, I would like to request blade balancing optimization service."
    }
}[st.session_state.lang]

# --- Hero Section ---
st.markdown(f"<h2 style='text-align: center; font-size: 40px;'>{L['hero']}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #64748b;'>{L['sub']}</p>", unsafe_allow_html=True)
st.write("---")

tab1, tab2 = st.tabs([L['tab1'], L['tab2']])

# --- 검증 툴 탭 ---
with tab1:
    col_in, col_chart = st.columns([1, 1])
    
    with col_in:
        c1, c2 = st.columns(2)
        with c1:
            n_count = st.number_input(L['count'], min_value=1, value=12)
        with c2:
            s_angle = st.number_input(L['start'], value=0.0)
        
        # 데이터프레임 생성 (React의 autoPhases 로직)
        phases = [round((s_angle + i * (360/n_count)), 5) for i in range(n_count)]
        df = pd.DataFrame({
            '#': range(1, n_count + 1),
            'Moment': [0.0] * n_count,
            'Phase': phases
        })
        
        edited_df = st.data_editor(df, hide_index=True, use_container_width=True)
        mag, ang = calculate_vector_sum(edited_df)
    
    with col_chart:
        # 결과 표시
        st.markdown(f"""
            <div class="result-card">
                <h3>{L['res']}</h3>
                <h2 style='color: #1d4ed8;'>{mag:.6f}</h2>
                <p>at {ang:.2f}°</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 차트 시각화
        fig = go.Figure()
        for _, row in edited_df.iterrows():
            fig.add_trace(go.Scatterpolar(r=[0, row['Moment']], theta=[0, row['Phase']], mode='lines', line=dict(color='gray', width=1), showlegend=False))
        fig.add_trace(go.Scatterpolar(r=[0, mag], theta=[0, ang], mode='lines+markers', line=dict(color='red', width=4), name=L['res']))
        fig.update_layout(polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")), height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- 이메일 의뢰 탭 ---
with tab2:
    st.info("whynot0926@gmail.com")
    st.write("카드 결제 없이 해외·국내 계좌 이체만 지원합니다. (Bank Transfer Only)")
    
    mail_link = f"mailto:whynot0926@gmail.com?subject=[B-Balance.tech] Inquiry&body={L['mail_body']}"
    st.markdown(f'<a href="{mail_link}"><button style="width:100%; height:50px; background-color:#1d4ed8; color:white; border:none; border-radius:5px; cursor:pointer;">이메일 작성하기 (Send Email)</button></a>', unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 12px; margin-top: 50px;'>© 2026 B-Balance.tech | Tests: All pass</div>", unsafe_allow_html=True)