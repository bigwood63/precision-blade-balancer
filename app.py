import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import io
import math

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="B-Balance.tech | Blade Engineering", layout="wide")

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

# --- 3. 인터랙티브 HTML 배열도 생성 함수 ---
def generate_interactive_chart(df, mag, ang):
    fig = go.Figure()
    # 개별 블레이드 (바 형태)
    for i, row in df.iterrows():
        serial = str(row['Serial']) if row['Serial'] else f"Pos {i+1}"
        fig.add_trace(go.Scatterpolar(
            r=[0, row['Magnitude']],
            theta=[0, row['Phase']],
            mode='lines+markers',
            line=dict(color='#94a3b8', width=2),
            marker=dict(size=4),
            name=f"#{i+1}: {serial}",
            hovertemplate=f"Pos: {i+1}<br>Serial: {serial}<br>Moment: %{{r}}<br>Angle: %{{theta}}°<extra></extra>"
        ))
    # 합성 벡터
    fig.add_trace(go.Scatterpolar(
        r=[0, mag], theta=[0, ang],
        mode='lines+markers',
        line=dict(color='#ef4444', width=6),
        marker=dict(size=10),
        name='Resultant Unbalance'
    ))
    fig.update_layout(
        title="Blade Arrangement Diagram (Interactive)",
        polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")),
        showlegend=False,
        height=700
    )
    # HTML을 바이트로 변환
    buffer = io.StringIO()
    fig.write_html(buffer, include_plotlyjs='cdn')
    return buffer.getvalue().encode('utf-8')

# --- 4. PDF 보고서 생성 함수 (배열도 페이지 추가) ---
def generate_pdf(df, mag, ang):
    pdf = FPDF()
    pdf.add_page()
    
    # [Page 1] 데이터 및 요약
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "BLADE MOMENT WEIGHT REPORT", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 5, "B-Balance.tech Precision Engineering Portal", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, " 1. VECTOR SYNTHESIS SUMMARY", ln=True, fill=True, border='B')
    pdf.set_font("Arial", "", 11)
    pdf.ln(3)
    pdf.cell(50, 8, " Calculated Unbalance:", border=0)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, f"{mag:.6f} gin", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(50, 8, " Calculated Angle:", border=0)
    pdf.cell(0, 8, f"{ang:.2f} deg", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 2. BLADE DISTRIBUTION DATA", ln=True, fill=True, border='B')
    pdf.ln(3)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(15, 7, "Pos.", border=1, align='C')
    pdf.cell(60, 7, "Serial / Blade No.", border=1, align='C')
    pdf.cell(55, 7, "Magnitude (Moment)", border=1, align='C')
    pdf.cell(55, 7, "Phase Angle (deg)", border=1, align='C', ln=True)
    
    pdf.set_font("Arial", "", 9)
    for i, row in df.iterrows():
        if i > 20 and i < len(df)-5: # 중간 생략 로직 (페이지 초과 방지, 필요시 루프 조정)
            if i == 21: pdf.cell(185, 7, "... (Omitted for brevity) ...", border=1, align='C', ln=True)
            continue
        serial = str(row['Serial']) if row['Serial'] else f"Bld-{int(i+1):02d}"
        pdf.cell(15, 7, str(int(i+1)), border=1, align='C')
        pdf.cell(60, 7, serial, border=1, align='C')
        pdf.cell(55, 7, f"{float(row['Magnitude']):.3f}", border=1, align='R')
        pdf.cell(55, 7, f"{float(row['Phase']):.3f}", border=1, align='R', ln=True)

    # [Page 2] Blade Arrangement Diagram (도면 페이지)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "3. BLADE ARRANGEMENT DIAGRAM", ln=True, align="L")
    pdf.ln(10)
    
    # 도면 그리기 매개변수
    cx, cy = 105, 140 # 중심 좌표 (mm)
    base_r = 45 # 기본 원 반지름
    max_moment = df['Magnitude'].max()
    
    # 중앙 원
    pdf.set_draw_color(100, 100, 100)
    pdf.circle(cx-5, cy-5, 10) 
    
    # 블레이드 및 일련번호 배치
    pdf.set_font("Arial", "", 6)
    for i, row in df.iterrows():
        angle_rad = math.radians(90 - row['Phase']) # 90도(상단) 기준 반시계방향
        
        # 블레이드 막대 (바 형태)
        length = (row['Magnitude'] / max_moment) * 40 # 최대 40mm 길이로 스케일링
        x1 = cx + (base_r * math.cos(angle_rad))
        y1 = cy - (base_r * math.sin(angle_rad))
        x2 = cx + ((base_r + length) * math.cos(angle_rad))
        y2 = cy - ((base_r + length) * math.sin(angle_rad))
        
        pdf.set_draw_color(180, 180, 180)
        pdf.line(x1, y1, x2, y2)
        
        # 원주면 일련번호 라벨
        lx = cx + ((base_r + length + 5) * math.cos(angle_rad))
        ly = cy - ((base_r + length + 5) * math.sin(angle_rad))
        label = str(row['Serial']) if row['Serial'] else str(i+1)
        pdf.text(lx - 2, ly, label)

    # 합성 벡터 (붉은 화살표)
    pdf.set_draw_color(255, 0, 0)
    pdf.set_line_width(1)
    res_angle_rad = math.radians(90 - ang)
    rx2 = cx + ((base_r + 45) * math.cos(res_angle_rad))
    ry2 = cy - ((base_r + 45) * math.sin(res_angle_rad))
    pdf.line(cx, cy, rx2, ry2)
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(255, 0, 0)
    pdf.text(rx2 + 2, ry2, f"RESULTANT: {mag:.4f} @ {ang:.2f} deg")

    return bytes(pdf.output())

# --- 5. UI 메인 화면 ---
st.markdown("""<div class="hero-container"><h1>B-Balance.tech Portal</h1><p>Professional Vector Analysis & Report System</p></div>""", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 3], gap="large")

with col_input:
    st.subheader("📥 Data Input")
    st.caption("Excel: [Serial No  Magnitude  Phase]")
    raw_input = st.text_area("Input Area", height=450, placeholder="B-001 211522.8 0.0\nB-002 211621.1 3.9...")
    
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
        
        # 대형 결과 카드
        st.markdown(f"""<div class="result-display"><p style='color:#64748b;margin:0;'>Resultant Unbalance</p><h1 style='color:#1e40af;font-size:4em;margin:0;'>{mag:.6f}</h1><p style='font-size:1.3em;'>at <b>{ang:.2f}°</b></p></div>""", unsafe_allow_html=True)

        c_chart, c_report = st.columns([2, 1])
        
        with c_chart:
            # 웹용 실시간 차트
            fig = go.Figure()
            for _, r in df.iterrows():
                fig.add_trace(go.Scatterpolar(r=[0, r['Magnitude']], theta=[0, r['Phase']], mode='lines', line=dict(color='rgba(148,163,184,0.3)', width=1), showlegend=False))
            fig.add_trace(go.Scatterpolar(r=[0, mag], theta=[0, ang], mode='lines+markers', line=dict(color='red', width=5), name='Resultant'))
            fig.update_layout(polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")), height=450)
            st.plotly_chart(fig, use_container_width=True)
            
        with c_report:
            st.subheader("📥 Downloads")
            
            # 1. PDF 보고서 다운로드
            pdf_bytes = generate_pdf(df, mag, ang)
            st.download_button("📜 Engineering PDF Report", data=pdf_bytes, file_name=f"B-Balance_Report.pdf", mime="application/pdf", use_container_width=True)
            
            # 2. 인터랙티브 배열도 다운로드
            html_bytes = generate_interactive_chart(df, mag, ang)
            st.download_button("📊 Interactive Diagram (HTML)", data=html_bytes, file_name=f"Blade_Arrangement_Diagram.html", mime="text/html", use_container_width=True)
            
            st.markdown("---")
            st.info("전문 정밀 최적화 서비스가 필요하시면 아래 버튼을 누르세요.")
            mail_link = f"mailto:whynot0926@gmail.com?subject=[Request] Optimization&body=Current Unbalance: {mag:.6f}"
            st.markdown(f'<a href="{mail_link}"><button style="width:100%; height:50px; background-color:#1e40af; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">Order Optimization</button></a>', unsafe_allow_html=True)
    else:
        st.info("좌측에 데이터를 입력하면 정밀 보고서와 도면이 자동 생성됩니다.")

st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.8em; margin-top: 50px;'>© 2026 B-Balance.tech | Global Turbine Engineering Specialist</p>", unsafe_allow_html=True)