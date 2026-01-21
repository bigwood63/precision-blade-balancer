import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- 배경 로직 ---
def calculate_vector_components(magnitude, phase):
    rad = np.radians(phase)
    return magnitude * np.cos(rad), magnitude * np.sin(rad)

def get_vectors(magnitudes, phases):
    return [{'magnitude': m, 'phase': p, 
             'x': calculate_vector_components(m, p)[0], 
             'y': calculate_vector_components(m, p)[1]} 
            for m, p in zip(magnitudes, phases)]

def draw_chart(vectors, title):
    x_sum = sum(v['x'] for v in vectors)
    y_sum = sum(v['y'] for v in vectors)
    mag = np.linalg.norm([x_sum, y_sum])
    phase = np.degrees(np.arctan2(y_sum, x_sum)) % 360
    
    fig = go.Figure()
    for v in vectors:
        fig.add_trace(go.Scatterpolar(r=[0, v['magnitude']], theta=[0, v['phase']], mode='lines', line=dict(color='gray', width=1), showlegend=False))
    
    fig.add_trace(go.Scatterpolar(r=[0, mag], theta=[0, phase], mode='lines+markers', line=dict(color='red', width=4), name='Result (Unbalance)'))
    fig.update_layout(title=title, polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")))
    return fig, mag, phase

# --- 웹 화면 구성 ---
st.set_page_config(page_title="Blade Balancing Pro", layout="wide")
st.title("⚖️ Global Blade Balancing Solution")
st.write("블레이드 배열 최적화 및 검증 시스템입니다.")

menu = st.sidebar.selectbox("메뉴 선택", ["1. 자가 검증 (Verification)", "2. 자동 최적화 (Optimization)"])

if menu == "1. 자가 검증 (Verification)":
    st.header("🔍 고객용 자가 검증 시뮬레이터")
    st.write("현재 사용 중인 블레이드 배열을 입력하여 언밸런스 수치를 확인하세요.")
    
    num = st.number_input("블레이드 개수", 1, 100, 4)
    data = []
    cols = st.columns(2)
    for i in range(num):
        with cols[0]: m = st.number_input(f"Bld {i+1} 무게(g)", key=f"m{i}")
        with cols[1]: p = st.number_input(f"Bld {i+1} 각도(°)", value=float(i*(360/num)), key=f"p{i}")
        data.append({'m': m, 'p': p})
    
    if st.button("배열 검증 실행"):
        vecs = get_vectors([d['m'] for d in data], [d['p'] for d in data])
        fig, m, p = draw_chart(vecs, "검증 결과 리포트")
        st.plotly_chart(fig)
        st.metric("최종 합성 벡터 (Unbalance)", f"{m:.2f}")
        if m > 100: st.warning("⚠️ 주의: 언밸런스가 높습니다! 최적화 서비스가 필요합니다.")
        else: st.success("✅ 안전한 배열입니다.")

elif menu == "2. 자동 최적화 (Optimization)":
    st.header("🚀 전문가용 최적화 배열 생성")
    st.write("보유하신 블레이드 데이터를 넣으면 가장 진동이 적은 순서를 찾아드립니다.")
    # (여기에 기존의 optimize_matching 로직을 그대로 넣으시면 됩니다.)
    st.info("이 기능은 프리미엄 서비스입니다. 문의: your@email.com")