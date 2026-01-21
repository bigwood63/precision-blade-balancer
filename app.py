import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- 기본 설정 ---
st.set_page_config(page_title="B-Balance.tech", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #1d4ed8; color: white; }
    .result-card {
        background-color: #ffffff; padding: 20px; border-radius: 10px;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 벡터 계산 함수 ---
def calculate_vector_sum(df):
    if df.empty:
        return 0, 0
    # 데이터 타입 변환 및 오류 처리
    mags = pd.to_numeric(df['Magnitude'], errors='coerce').fillna(0)
    phases = pd.to_numeric(df['Phase'], errors='coerce').fillna(0)
    
    rads = np.radians(phases)
    sx = np.sum(mags * np.cos(rads))
    sy = np.sum(mags * np.sin(rads))
    
    mag = np.hypot(sx, sy)
    ang = (np.degrees(np.atan2(sy, sx)) + 360) % 360
    return mag, ang

# --- 세션 상태 관리 (언어) ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'ko'

# --- 헤더 및 언어 전환 ---
col_title, col_lang = st.columns([4, 1])
with col_title:
    st.title("🌐 B-Balance.tech")
with col_lang:
    if st.button("🌐 English / 한국어"):
        st.session_state.lang = 'en' if st.session_state.lang == 'ko' else 'ko'

L = {
    'ko': {
        'hero': "Global Blade Balancing — 정밀 검증 포털",
        'tab1': "🔍 데이터 붙여넣기 검증",
        'tab2': "📧 이메일 의뢰",
        'input_label': "엑셀 데이터를 아래에 붙여넣으세요 (크기 위상)",
        'input_help': "엑셀에서 '크기'와 '위상' 두 칼럼을 복사해서 붙여넣으세요.",
        'res_title': "합성 결과 (Resultant)",
        'count_info': "인식된 블레이드 개수",
    },
    'en': {
        'hero': "Global Blade Balancing — Precision Verification",
        'tab1': "🔍 Paste Data & Verify",
        'tab2': "📧 Order via Email",
        'input_label': "Paste Excel data here (Magnitude Phase)",
        'input_help': "Copy 'Magnitude' and 'Phase' columns from Excel and paste.",
        'res_title': "Resultant",
        'count_info': "Detected Blades",
    }
}[st.session_state.lang]

st.markdown(f"<h2 style='text-align: center;'>{L['hero']}</h2>", unsafe_allow_html=True)
st.write("---")

tab1, tab2 = st.tabs([L['tab1'], L['tab2']])

with tab1:
    col_input, col_result = st.columns([1, 1])
    
    with col_input:
        # 텍스트 에어리어로 엑셀 데이터 통째로 입력 받기
        raw_data = st.text_area(L['input_label'], 
                               placeholder="예:\n10.5 0\n10.2 30\n9.8 60", 
                               height=300, 
                               help=L['input_help'])
        
        parsed_data = []
        if raw_data.strip():
            lines = raw_data.strip().split('\n')
            for line in lines:
                parts = line.replace('\t', ' ').split() # 탭이나 공백 구분
                if len(parts) >= 2:
                    try:
                        parsed_data.append([float(parts[0]), float(parts[1])])
                    except ValueError:
                        continue
        
        df = pd.DataFrame(parsed_data, columns=['Magnitude', 'Phase'])
        
        if not df.empty:
            st.info(f"✅ {L['count_info']}: {len(df)}")
            st.dataframe(df, use_container_width=True, height=200)
        else:
            st.warning("데이터를 입력하면 자동으로 분석됩니다.")

    with col_result:
        mag, ang = calculate_vector_sum(df)
        
        # 결과 표시 카드
        st.markdown(f"""
            <div class="result-card">
                <p style='color: #64748b; margin-bottom: 0;'>{L['res_title']}</p>
                <h1 style='color: #1d4ed8; margin-top: 0;'>{mag:.6f}</h1>
                <p style='font-size: 1.2em;'>at <b>{ang:.2f}°</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        # 그래프 그리기
        fig = go.Figure()
        if not df.empty:
            for _, row in df.iterrows():
                fig.add_trace(go.Scatterpolar(r=[0, row['Magnitude']], theta=[0, row['Phase']], 
                                             mode='lines', line=dict(color='rgba(100,100,255,0.3)', width=1), showlegend=False))
            
            fig.add_trace(go.Scatterpolar(r=[0, mag], theta=[0, ang], 
                                         mode='lines+markers', line=dict(color='red', width=4), name=L['res_title']))
        
        fig.update_layout(polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")), 
                          margin=dict(l=40, r=40, t=40, b=40), height=350)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.info("whynot0926@gmail.com")
    mail_body = "Hello, I would like to request blade balancing optimization service."
    mail_link = f"mailto:whynot0926@gmail.com?subject=[B-Balance.tech] Inquiry&body={mail_body}"
    st.markdown(f'<a href="{mail_link}"><button style="width:100%; height:50px; background-color:#1d4ed8; color:white; border:none; border-radius:5px; cursor:pointer;">이메일 작성하기 (Send Email)</button></a>', unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 11px; margin-top: 50px;'>© 2026 B-Balance.tech | All Calculations Verified by Physics</div>", unsafe_allow_html=True)