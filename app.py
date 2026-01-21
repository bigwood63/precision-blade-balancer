import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. 페이지 설정 및 비즈니스 브랜딩 ---
st.set_page_config(page_title="B-Balance.tech | Blade Vector Analysis", layout="wide")

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

# --- 2. 벡터 계산 함수 ---
def calculate_analysis(df):
    if df.empty: return 0, 0
    mags = pd.to_numeric(df['Magnitude'], errors='coerce').fillna(0)
    phases = pd.to_numeric(df['Phase'], errors='coerce').fillna(0)
    rads = np.radians(phases)
    sx = np.sum(mags * np.cos(rads))
    sy = np.sum(mags * np.sin(rads))
    mag = np.hypot(sx, sy)
    ang = (np.degrees(np.atan2(sy, sx)) + 360) % 360
    return mag, ang

# --- 3. PDF 보고서 생성 함수 (바이트 변환 수정 및 양식 보강) ---
def generate_pdf(df, mag, ang):
    pdf = FPDF()
    pdf.add_page()
    
    # 헤더 섹션 (전문 엔지니어링 양식)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "BLADE MOMENT WEIGHT REPORT", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 5, "B-Balance.tech Precision Engineering Portal", ln=True, align="C")
    pdf.ln(10)

    # 1. 요약 정보 (Resultant)
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, " 1. VECTOR SYNTHESIS SUMMARY", ln=True, fill=True, border='B')
    pdf.set_font("Arial", "", 11)
    pdf.ln(3)
    pdf.cell(50, 8, f" Calculated Unbalance:", border=0)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, f"{mag:.6f} gin", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(50, 8, f" Calculated Angle:", border=0)
    pdf.cell(0, 8, f"{ang:.2f} deg", ln=True)
    
    # 상태 판정 (State)
    state_text = "IN TOLERANCE" if mag <= 10.0 else "OUT OF TOLERANCE"
    pdf.set_font("Arial", "B", 11)
    pdf.cell(50, 10, " Current State:", border=0)
    if mag > 10.0: pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, state_text, ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # 2. 상세 데이터 테이블
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 2. BLADE DISTRIBUTION DATA", ln=True, fill=True, border='B')
    pdf.ln(3)
    pdf.set_font("Arial", "B", 10)
    
    # 테이블 헤더
    pdf.cell(20, 8, "Pos.", border=1, align='C')
    pdf.cell(60, 8, "Serial / Blade No.", border=1, align='C')
    pdf.cell(55, 8, "Magnitude (Moment)", border=1, align='C')
    pdf.cell(55, 8, "Phase Angle (deg)", border=1, align='C', ln=True)
    
    # 테이블 내용
    pdf.set_font("Arial", "", 10)
    for i, row in df.iterrows():
        serial = str(row['Serial']) if row['Serial'] else f"Bld-{int(i+1):02d}"
        pdf.cell(20, 8, str(int(i+1)), border=1, align='C')
        pdf.cell(60, 8, serial, border=1, align='C')
        pdf.cell(55, 8, f"{float(row['Magnitude']):.3f}", border=1, align='R')
        pdf.cell(55, 8, f"{float(row['Phase']):.3f}", border=1, align='R', ln=True)
    
    pdf.ln(20)
    # 전문가 서명란 (신뢰도 장치)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Verified by B-Balance Analysis Engine", ln=True, align="R")
    pdf.cell(0, 10, "Authorized Signature: ________________________", ln=True, align="R")

    # [핵심 수정] PDF를 바이트 객체로 변환하여 반환
    return bytes(pdf.output())

# --- 4. 메인 화면 구성 ---
st.markdown("""<div class="hero-container"><h1>B-Balance.tech</h1><p>Professional Blade Vector Analysis Portal</p></div>""", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 3], gap="large")

with col_input:
    st.subheader("📥 Data Input")
    st.caption("Excel에서 [일련번호 크기 위상] 순으로 붙여넣으세요.")
    raw_input = st.text_area("Input Area", height=450, placeholder="C1ZP01 211522.8 0.0\nC1ZP02 211621.1 3.9...")
    
    parsed = []
    if raw_input.strip():
        for line in raw_input.strip().split('\n'):
            parts = line.replace('\t', ' ').split()
            if len(parts) >= 3:
                parsed.append([parts[0], float(parts[1]), float(parts[2])])
            elif len(parts) == 2:
                parsed.append([None, float(parts[0]), float(parts[1])])
    
    df = pd.DataFrame(parsed, columns=['Serial', 'Magnitude', 'Phase'])

with col_output:
    if not df.empty:
        mag, ang = calculate_analysis(df)
        
        st.markdown(f"""<div class="result-display"><p style='color:#64748b;margin:0;'>Total Resultant Unbalance</p><h1 style='color:#1e40af;font-size:4.5em;margin:0;'>{mag:.6f}</h1><p style='font-size:1.3em;'>at Vector Angle: <b>{ang:.2f}°</b></p></div>""", unsafe_allow_html=True)

        c_chart, c_report = st.columns([2, 1])
        
        with c_chart:
            fig = go.Figure()
            for _, row in df.iterrows():
                fig.add_trace(go.Scatterpolar(r=[0, row['Magnitude']], theta=[0, row['Phase']], mode='lines', line=dict(color='rgba(148, 163, 184, 0.2)', width=1), showlegend=False))
            fig.add_trace(go.Scatterpolar(r=[0, mag], theta=[0, ang], mode='lines+markers', line=dict(color='#ef4444', width=5), name='Resultant'))
            fig.update_layout(polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")), height=500)
            st.plotly_chart(fig, use_container_width=True)
            
        with c_report:
            st.subheader("📊 Report & Action")
            st.write(f"**Detected Blades:** {len(df)}")
            
            # PDF 생성 로직 (오류 수정 포인트)
            try:
                pdf_bytes = generate_pdf(df, mag, ang)
                st.download_button(
                    label="📥 Download Engineering PDF",
                    data=pdf_bytes,
                    file_name=f"B-Balance_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF 생성 중 오류 발생: {e}")
            
            st.markdown("""<div class="expert-call"><h4>🚀 Professional Optimization</h4><p>정밀 알고리즘을 통해 언밸런스를 90% 이상 제거할 수 있는 최적 배열표를 제공합니다.</p></div>""", unsafe_allow_html=True)
            mail_link = f"mailto:whynot0926@gmail.com?subject=[Request] Optimization&body=Resultant: {mag:.6f}"
            st.markdown(f'<a href="{mail_link}"><button style="width:100%; height:50px; background-color:#1e40af; color:white; border:none; border-radius:10px; cursor:pointer;">Order Expert Service</button></a>', unsafe_allow_html=True)
    else:
        st.info("좌측에 데이터를 입력하면 분석 결과와 보고서가 생성됩니다.")

st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.8em; margin-top: 50px;'>© 2026 B-Balance.tech | All Calculations Verified by Physics-based Algorithms</p>", unsafe_allow_html=True)