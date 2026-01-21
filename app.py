import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- 1. 페이지 설정 및 비즈니스 브랜딩 ---
st.set_page_config(page_title="B-Balance.tech | Blade Vector Analysis", layout="wide")

# CSS를 통한 세밀한 디자인 제어
st.markdown("""
    <style>
    /* 배경 및 기본 폰트 */
    .main { background-color: #f8fafc; }
    
    /* 비즈니스 히어로 섹션 */
    .hero-container {
        background: linear-gradient(100deg, #0f172a 0%, #1e3a8a 100%);
        padding: 40px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        text-align: center;
    }
    
    /* 결과 카드 (대형화) */
    .result-display {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    /* 전문가 섹션 강조 */
    .expert-call {
        background-color: #eff6ff;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #2563eb;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 벡터 계산 함수 ---
def calculate_analysis(df):
    if df.empty: return 0, 0
    mags = pd.to_numeric(df['Magnitude'], errors='coerce').fillna(0)
    phases = pd.to_numeric(df['Phase'], errors='coerce').fillna(0)
    rads = np.radians(phases)
    sx = np.sum(mags * np.cos(rads))
    sy = np.sum(mags * np.sin(rads))
    return np.hypot(sx, sy), (np.degrees(np.atan2(sy, sx)) + 360) % 360

# --- 3. 헤더 (비즈니스 타이틀) ---
st.markdown("""
    <div class="hero-container">
        <h1 style='margin-bottom:0;'>B-Balance.tech</h1>
        <p style='opacity:0.8; font-size:1.1em;'>Professional Blade Vector Synthesis & Optimization Consulting</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. 메인 콘텐츠 (비율 1:3 적용) ---
# col1(입력) : col2(출력) 비율을 1:3으로 설정
col_input, col_output = st.columns([1, 3], gap="large")

with col_input:
    st.subheader("📥 Data Input")
    st.write("엑셀 데이터를 붙여넣으세요.")
    
    raw_input = st.text_area(
        "Magnitude Phase", 
        placeholder="211522.842 0.000\n211621.13 3.913...",
        height=450,
        help="엑셀의 '크기'와 '위상' 칼럼을 복사하여 이곳에 붙여넣으세요."
    )
    
    # 데이터 파싱
    parsed = []
    if raw_input.strip():
        for line in raw_input.strip().split('\n'):
            parts = line.replace('\t', ' ').split()
            if len(parts) >= 2:
                try: parsed.append([float(parts[0]), float(parts[1])])
                except: continue
    
    df = pd.DataFrame(parsed, columns=['Magnitude', 'Phase'])
    
    if not df.empty:
        st.success(f"Detected: {len(df)} Blades")
        with st.expander("입력 데이터 확인"):
            st.dataframe(df, use_container_width=True, height=200)

with col_output:
    if not df.empty:
        mag, ang = calculate_analysis(df)
        
        # 상단 결과 수치 카드 (크고 명확하게)
        st.markdown(f"""
            <div class="result-display">
                <p style='font-size:1.1em; color:#64748b; margin-bottom:10px;'>Total Resultant Unbalance (Static Moment Sum)</p>
                <h1 style='font-size:5em; color:#1e40af; margin:0;'>{mag:.6f}</h1>
                <p style='font-size:1.5em; color:#1e40af;'>at Vector Angle: <b>{ang:.2f}°</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        # 차트와 분석 섹션
        c_chart, c_consult = st.columns([2, 1])
        
        with c_chart:
            fig = go.Figure()
            # 개별 블레이드 벡터 (연하게)
            for _, row in df.iterrows():
                fig.add_trace(go.Scatterpolar(
                    r=[0, row['Magnitude']], theta=[0, row['Phase']],
                    mode='lines', line=dict(color='rgba(148, 163, 184, 0.2)', width=1),
                    showlegend=False
                ))
            # 최종 합성 벡터 (강렬하게)
            fig.add_trace(go.Scatterpolar(
                r=[0, mag], theta=[0, ang],
                mode='lines+markers', line=dict(color='#ef4444', width=5),
                name='Resultant'
            ))
            fig.update_layout(
                polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")),
                margin=dict(t=40, b=40),
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with c_consult:
            st.markdown("### 📊 Diagnosis")
            if mag > 0.05: # 예시 기준치
                st.error("⚠️ **Critical Unbalance**\n\n현재 합성 언밸런스 수치가 허용 범위를 초과했습니다. 진동으로 인한 베어링 손상 및 설비 수명 단축이 우려됩니다.")
            else:
                st.success("✅ **Stable Condition**\n\n현재 배열 상태가 비교적 양호합니다.")
            
            st.markdown("""
                <div class="expert-call">
                    <h4>🚀 Professional Optimization</h4>
                    <p>당사의 <b>Genetic Algorithm</b>을 통해 언밸런스를 90% 이상 제거할 수 있는 '최적 배열표'를 받아보세요.</p>
                </div>
            """, unsafe_allow_html=True)
            
            mail_link = f"mailto:whynot0926@gmail.com?subject=[B-Balance.tech] Optimization Request&body=Blade Count: {len(df)}, Resultant: {mag:.6f}"
            st.markdown(f'''
                <a href="{mail_link}" target="_blank">
                    <button style="width:100%; height:60px; background-color:#1e40af; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer; margin-top:10px;">
                        의뢰하기 (Order via Email)
                    </button>
                </a>
            ''', unsafe_allow_html=True)
    else:
        # 데이터가 없을 때의 초기 화면
        st.info("👈 왼쪽 입력창에 데이터를 붙여넣으면 분석 리포트가 이곳에 생성됩니다.")
        # 비즈니스 가치 제안
        st.markdown("""
        ### Why B-Balance.tech?
        - **Precision Analysis**: 수천 번의 시뮬레이션을 통한 물리적 정밀 검증
        - **Cost Efficiency**: 진동으로 인한 돌발 정지 사고 예방
        - **Expert Insight**: 수십 년 경력의 엔지니어링 전문가가 제공하는 최적 배열 가이드
        """)

# --- 5. 푸터 ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #94a3b8;'>© 2026 B-Balance.tech | Global Engineering Service | whynot0926@gmail.com</p>", unsafe_allow_html=True)