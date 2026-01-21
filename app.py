import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import io
import math

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="B-Balance.tech | Engineering Portal", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. 로직 함수 ---
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

def generate_interactive_chart(df, mag, ang):
    fig = go.Figure()
    for i, row in df.iterrows():
        serial = str(row['Serial']) if row['Serial'] else f"Pos {i+1}"
        fig.add_trace(go.Scatterpolar(
            r=[0, row['Magnitude']], theta=[0, row['Phase']],
            mode='lines+markers', line=dict(color='#94a3b8', width=1.5),
            name=f"#{i+1}: {serial}"
        ))
    fig.add_trace(go.Scatterpolar(
        r=[0, mag], theta=[0, ang],
        mode='lines+markers', line=dict(color='red', width=5),
        marker=dict(size=10), name='Resultant'
    ))
    fig.update_layout(polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")), showlegend=False)
    buffer = io.StringIO()
    fig.write_html(buffer, include_plotlyjs='cdn')
    return buffer.getvalue().encode('utf-8')

# --- 3. PDF 생성 함수 (데이터 전량 표시 및 도면 캡션 강화) ---
def generate_pdf(df, mag, ang):
    pdf = FPDF()
    
    # [Page 1 & 이어지는 페이지들] 데이터 전량 표시
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "BLADE MOMENT WEIGHT ANALYSIS REPORT", ln=True, align="C")
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="R")
    pdf.ln(5)

    # 요약 정보
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, " 1. ANALYSIS SUMMARY", ln=True, fill=True, border='B')
    pdf.set_font("Arial", "", 10)
    pdf.ln(2)
    pdf.cell(50, 7, f" Total Blade Count: {len(df)}", ln=True)
    pdf.cell(50, 7, f" Calculated Unbalance: {mag:.6f} gin", ln=True)
    pdf.cell(50, 7, f" Calculated Angle: {ang:.2f} deg", ln=True)
    pdf.ln(5)

    # 데이터 테이블 (생략 없이 전부 표시)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 2. FULL BLADE DISTRIBUTION DATA", ln=True, fill=True, border='B')
    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(15, 7, "Pos.", border=1, align='C')
    pdf.cell(60, 7, "Serial No.", border=1, align='C')
    pdf.cell(55, 7, "Magnitude (Moment)", border=1, align='C')
    pdf.cell(55, 7, "Phase Angle (deg)", border=1, align='C', ln=True)
    
    pdf.set_font("Arial", "", 8)
    for i, row in df.iterrows():
        # 페이지 하단 도달 시 자동 페이지 추가
        if pdf.get_y() > 260:
            pdf.add_page()
            pdf.set_font("Arial", "B", 9)
            pdf.cell(15, 7, "Pos.", border=1, align='C')
            pdf.cell(60, 7, "Serial No.", border=1, align='C')
            pdf.cell(55, 7, "Magnitude (Moment)", border=1, align='C')
            pdf.cell(55, 7, "Phase Angle (deg)", border=1, align='C', ln=True)
            pdf.set_font("Arial", "", 8)
            
        serial = str(row['Serial']) if row['Serial'] else f"Bld-{int(i+1):02d}"
        pdf.cell(15, 6, str(int(i+1)), border=1, align='C')
        pdf.cell(60, 6, serial, border=1, align='C')
        pdf.cell(55, 6, f"{float(row['Magnitude']):.3f}", border=1, align='R')
        pdf.cell(55, 6, f"{float(row['Phase']):.3f}", border=1, align='R', ln=True)

    # [마지막 페이지] Blade Arrangement Diagram
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "3. BLADE ARRANGEMENT DIAGRAM", ln=True, align="L")
    pdf.ln(10)
    
    cx, cy = 105, 120 # 중심 좌표
    base_r = 50 # 기본 원 반지름
    max_m = df['Magnitude'].max()
    
    # 도면 그리기
    pdf.set_draw_color(150, 150, 150)
    pdf.circle(cx-10, cy-10, 20) # 중앙 축
    
    for i, row in df.iterrows():
        angle_rad = math.radians(90 - row['Phase'])
        # 막대 길이 스케일링
        length = (row['Magnitude'] / max_m) * 35 
        x1 = cx + (base_r * math.cos(angle_rad))
        y1 = cy - (base_r * math.sin(angle_rad))
        x2 = cx + ((base_r + length) * math.cos(angle_rad))
        y2 = cy - ((base_r + length) * math.sin(angle_rad))
        
        pdf.set_draw_color(200, 200, 200)
        pdf.line(x1, y1, x2, y2)
        
        # 일련번호 원주면 배치
        pdf.set_font("Arial", "", 5)
        lx = cx + ((base_r + length + 4) * math.cos(angle_rad))
        ly = cy - ((base_r + length + 4) * math.sin(angle_rad))
        pdf.text(lx - 1, ly, str(row['Serial']) if row['Serial'] else str(i+1))

    # 합성 벡터 강조 (도면 내 빨간 화살표)
    pdf.set_draw_color(220, 0, 0)
    pdf.set_line_width(1.2)
    res_rad = math.radians(90 - ang)
    pdf.line(cx, cy, cx + (base_r+40)*math.cos(res_rad), cy - (base_r+40)*math.sin(res_rad))

    # [핵심 요청] 도면 바로 아래 캡션(Caption) 추가
    pdf.set_y(cy + base_r + 50)
    pdf.set_fill_color(255, 235, 235)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(200, 0, 0)
    caption_text = f"RESULTANT UNBALANCE: {mag:.6f} gin  @  VECTOR ANGLE: {ang:.2f} deg"
    pdf.cell(0, 12, caption_text, border=1, ln=True, align="C", fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "I", 9)
    pdf.ln(5)
    pdf.cell(0, 10, "* This diagram represents the calculated static moment distribution and vector synthesis.", ln=True, align="C")

    return bytes(pdf.output())

# --- 4. 메인 UI ---
st.markdown("""<div class="hero-container"><h1>B-Balance.tech</h1><p>Professional Blade Vector Analysis & Report System</p></div>""", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 3], gap="large")

with col_input:
    st.subheader("📥 Data Input")
    raw_input = st.text_area("Paste: [Serial  Magnitude  Phase]", height=450)
    
    parsed = []
    if raw_input.strip():
        for line in raw_input.strip().split('\n'):
            parts = line.replace('\t', ' ').split()
            if len(parts) >= 3: parsed.append([parts[0], float(parts[1]), float(parts[2])])
            elif len(parts) == 2: parsed.append([None, float(parts[0]), float(parts[1])])
    df = pd.DataFrame(parsed, columns=['Serial', 'Magnitude', 'Phase'])

with col_output:
    if not df.empty:
        mag, ang = calculate_analysis(df)
        st.markdown(f"""<div class="result-display"><p style='color:#64748b;margin:0;'>Total Resultant Unbalance</p><h1 style='color:#1e40af;font-size:4.5em;margin:0;'>{mag:.6f}</h1><p style='font-size:1.3em;'>at <b>{ang:.2f}°</b></p></div>""", unsafe_allow_html=True)

        c_chart, c_report = st.columns([2, 1])
        with c_chart:
            fig = go.Figure()
            for _, r in df.iterrows():
                fig.add_trace(go.Scatterpolar(r=[0, r['Magnitude']], theta=[0, r['Phase']], mode='lines', line=dict(color='rgba(148,163,184,0.3)', width=1), showlegend=False))
            fig.add_trace(go.Scatterpolar(r=[0, mag], theta=[0, ang], mode='lines+markers', line=dict(color='red', width=5), name='Resultant'))
            fig.update_layout(polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")), height=450)
            st.plotly_chart(fig, use_container_width=True)
            
        with c_report:
            st.subheader("📥 Downloads")
            pdf_bytes = generate_pdf(df, mag, ang)
            st.download_button("📜 Download Full PDF Report", data=pdf_bytes, file_name="B-Balance_Full_Report.pdf", mime="application/pdf", use_container_width=True)
            html_bytes = generate_interactive_chart(df, mag, ang)
            st.download_button("📊 Download Interactive HTML", data=html_bytes, file_name="Arrangement_Diagram.html", mime="text/html", use_container_width=True)
            
            st.markdown("---")
            mail_link = f"mailto:whynot0926@gmail.com?subject=[Request] Optimization&body=Resultant: {mag:.6f}"
            st.markdown(f'<a href="{mail_link}"><button style="width:100%; height:50px; background-color:#1e40af; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">Order Optimization</button></a>', unsafe_allow_html=True)
    else:
        st.info("좌측에 데이터를 입력하면 정밀 보고서가 자동 생성됩니다.")

st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.8em; margin-top: 50px;'>© 2026 B-Balance.tech | All Calculations Verified by Physics-based Algorithms</p>", unsafe_allow_html=True)