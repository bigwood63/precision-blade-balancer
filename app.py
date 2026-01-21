import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- 1. 페이지 설정 및 비즈니스 브랜딩 ---
st.set_page_config(page_title="B-Balance.tech | Blade Vector Analysis", layout="wide")

# UI 디자인 고도화를 위한 CSS
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .hero-container {
        background: linear-gradient(100deg, #0f172a 0%, #1e3a8a 100%);
        padding: 40px; border-radius: 15px; color: white;
        margin-bottom: 30px; text-align: center;
    }
    .result-display {
        background-color: white; padding: 40px; border-radius: 20px;
        border: 2px solid #e2e8f0; text-align: center;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .expert-call {
        background-color: #eff6ff; padding: 25px; border-radius: 12px;
        border-left: 6px solid #2563eb; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 벡터 계산 및 진단 로직 ---
def calculate_analysis(df):
    if df.empty: return 0, 0
    mags = pd.to_numeric(df['Magnitude'], errors='coerce').fillna(0)
    phases = pd.to_numeric(df['Phase'], errors='coerce').fillna(0)
    rads = np.radians(phases)
    sx = np.sum(mags * np.cos(rads))
    sy = np.sum(mags * np.sin(rads))
    return np.hypot(sx, sy), (np.degrees(np.atan2(sy, sx)) + 360) % 360

# --- 3. 헤더 섹션 ---
st.markdown("""
    <div class="hero-container">
        <h1 style='margin-bottom:0;'>B-Balance.tech</h1>
        <p style='opacity:0.8; font-size:1.1em;'>Precision Blade Vector Synthesis & Performance Optimization Consulting</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. 메인 콘텐츠 (비율 1:3 적용) ---
col_input, col_output = st.columns([1, 3], gap="large")

with col_input:
    st.subheader("📥 Data Input")
    st.write("엑셀 데이터를 붙여넣으세요.")
    
    raw_input = st.text_area(
        "Magnitude Phase", 
        placeholder="211522.8 0.0\n211621.1 3.9...",
        height=450,
        help="엑셀의 '크기'와 '위상' 칼럼을 드래그하여 이곳에 붙여넣으세요."
    )
    
    parsed = []
    if raw_input.strip():
        for line in raw_input.strip().split('\n'):
            parts = line.replace('\t', ' ').split()
            if len(parts) >= 2:
                try: parsed.append([float(parts[0]), float(parts[1])])
                except: continue
    
    df = pd.DataFrame(parsed, columns=['Magnitude', 'Phase'])
    
    if not df.empty:
        st.info(f"✅ 인식된 블레이드: {len(df)}개")
        with st.expander("입력 데이터 확인"):
            st.dataframe(df, use_container_width=True, height=200)

with col_output:
    if not df.empty:
        mag, ang = calculate_analysis(df)
        
        # 상단 결과 수치 카드
        st.markdown(f"""
            <div class="result-display">
                <p style='font-size:1.1em; color:#64748b; margin-bottom:10px;'>Total Resultant Unbalance (Static Moment Sum)</p>
                <h1 style='font-size:5em; color:#1e40af; margin:0;'>{mag:.6f}</h1>
                <p style='font-size:1.5em; color:#1e40af;'>at Vector Angle: <b>{ang:.2f}°</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        # 차트와 진단 섹션
        c_chart, c_consult = st.columns([2, 1])
        
        with c_chart:
            fig = go.Figure()
            # 개별 블레이드 벡터
            for _, row in df.iterrows():
                fig.add_trace(go.Scatterpolar(
                    r=[0, row['Magnitude']], theta=[0, row['Phase']],
                    mode='lines', line=dict(color='rgba(148, 163, 184, 0.2)', width=1),
                    showlegend=False
                ))
            # 최종 합성 벡터
            fig.add_trace(go.Scatterpolar(
                r=[0, mag], theta=[0, ang],
                mode='lines+markers', line=dict(color='#ef4444', width=5),
                name='Resultant'
            ))
            fig.update_layout(
                polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")),
                margin=dict(t=40, b=40), height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with c_consult:
            st.markdown("### 📊 Diagnosis")
            
            # 현실적인 판정 로직 (비즈니스 문구 반영)
            if mag > 10.0:
                st.error(f"❌ **Critical Unbalance**\n\n허용 범위를 초과했습니다. 진동으로 인한 베어링 손상이 우려되오니 즉시 정밀 최적화 배열이 필요합니다..")
            elif 1.0 <= mag <= 10.0:
                st.warning(f"⚠️ **Attention Required**\n\n현재 수치는 가동 가능 범위이나, 정밀 최적화를 통해 잔류 언밸런스를 1.0 이하로 개선하여 설비 안정성을 높일 수 있습니다.")
            else:
                st.success(f"✅ **Stable Condition**\n\n현재 상태가 매우 양호합니다. 최상의 성능 유지를 위해 정기적인 벡터 모니터링을 권장합니다.")
            
            st.markdown("""
                <div class="expert-call">
                    <h4>🚀 Performance Plus</h4>
                    <p>현재 결과에 만족하시나요? 당사의 <b>Genetic Matching</b> 알고리즘을 적용하면 현재 수치를 <b>최대 95% 이상 추가 감소</b>시킬 수 있습니다.</p>
                </div>
            """, unsafe_allow_html=True)
            
            mail_link = f"mailto:whynot0926@gmail.com?subject=[B-Balance.tech] Optimization Inquiry&body=Blades: {len(df)}, Current Resultant: {mag:.6f}"
            st.markdown(f'''
                <a href="{mail_link}" target="_blank">
                    <button style="width:100%; height:60px; background-color:#1e40af; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer; margin-top:10px;">
                        의뢰하기 (Get Expert Report)
                    </button>
                </a>
            ''', unsafe_allow_html=True)
    else:
        st.info("👈 왼쪽 입력창에 데이터를 붙여넣으시면 분석 리포트가 즉시 생성됩니다.")
        st.markdown("""
        ### Why B-Balance.tech?
        - **Precision Analysis**: 수천 번의 반복 시뮬레이션을 통한 물리적 정밀 검증
        - **Expert Insight**: 수십 년간 터빈 현장을 누빈 엔지니어링 전문가의 실전 솔루션 제공
        - **Cost Efficiency**: 정밀 밸런싱을 통한 설비 사고 예방 및 유지보수 비용 절감
        """)

# --- 5. 푸터 (SEO 및 키워드 포함) ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #94a3b8; font-size: 0.9em;'>
        <p>Turbine Blade Balancing | Static Moment Vector Synthesis | Gas Turbine Vibration Optimization Expert</p>
        <p>© 2026 B-Balance.tech | Retired Engineering Expert Services | whynot0926@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)