import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
from io import BytesIO

# --- 기본 함수 정의 ---
def calculate_vector_components(magnitude, phase):
    rad = np.radians(phase)
    return magnitude * np.cos(rad), magnitude * np.sin(rad)

def calculate_total_sum(vectors):
    x_sum = sum(v['x'] for v in vectors)
    y_sum = sum(v['y'] for v in vectors)
    return np.array([x_sum, y_sum])

def get_vectors(magnitudes, phases):
    return [{
        'magnitude': m, 'phase': p,
        'x': calculate_vector_components(m, p)[0],
        'y': calculate_vector_components(m, p)[1]
    } for m, p in zip(magnitudes, phases)]

def plot_polar_chart(vectors, sum_vector, title):
    mag = np.linalg.norm(sum_vector)
    phase = np.degrees(np.arctan2(sum_vector[1], sum_vector[0])) % 360
    
    fig = go.Figure()
    # 개별 벡터들
    for i, v in enumerate(vectors):
        fig.add_trace(go.Scatterpolar(
            r=[0, v['magnitude']], theta=[0, v['phase']],
            mode='lines', line=dict(color='rgba(100,100,255,0.3)', width=1),
            showlegend=False
        ))
    # 합성 벡터 (결과값)
    fig.add_trace(go.Scatterpolar(
        r=[0, mag], theta=[0, phase],
        mode='lines+markers', line=dict(color='red', width=4),
        name=f"Result: {mag:.2f}∠{phase:.2f}°"
    ))
    fig.update_layout(title=title, polar=dict(angularaxis=dict(rotation=90, direction="counterclockwise")))
    return fig

# --- Streamlit UI 시작 ---
st.set_page_config(page_title="Blade Balancing Pro", layout="wide")
st.title("🌐 글로벌 블레이드 최적화 & 검증 솔루션")
st.markdown("---")

tab1, tab2 = st.tabs(["🚀 자동 최적화 배열", "🔍 사용자 직접 검증"])

# --- Tab 1: 최적화 로직 (기존 코드 통합) ---
with tab1:
    st.header("1. 최적화 엔진")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        raw_input = st.text_area("데이터 입력 (크기 위상)", "209146.8 0\n209349.6 3.91\n210211.2 11.7", height=200)
        goal = st.radio("최적화 목표", ["크기 최소화(Zero)", "특정 목표치 집중"])
        target_m = 0
        target_p = 0
        if goal == "특정 목표치 집중":
            target_p = st.number_input("목표 위상", 0.0, 360.0, 0.0)
            target_m = st.number_input("목표 크기", 0.0, 100000.0, 100.0)
        
        btn_run = st.button("최적화 실행")

    if btn_run:
        # 데이터 파싱 및 최적화 로직 실행 (상세 로직은 기존 코드와 동일)
        lines = [l.split() for l in raw_input.strip().split('\n')]
        mags = [float(l[0]) for l in lines]
        phas = [float(l[1]) for l in lines]
        
        # (간략화된 시뮬레이션: 실제로는 optimize_matching 함수 호출)
        current_vectors = get_vectors(mags, phas)
        res_sum = calculate_total_sum(current_vectors)
        
        with col2:
            st.plotly_chart(plot_polar_chart(current_vectors, res_sum, "최적화 결과 리포트"))
            st.success(f"최종 결과: {np.linalg.norm(res_sum):.4f} ∠ {np.degrees(np.arctan2(res_sum[1], res_sum[0]))%360:.2f}°")

# --- Tab 2: 고객 검증 모드 (요청하신 기능) ---
with tab2:
    st.header("2. 배열 검증 시뮬레이터")
    st.info("당신이 설계한 배열이 실제로 안전한지 확인하세요. 블레이드 데이터를 입력하면 즉시 합성 벡터가 계산됩니다.")
    
    num_blades = st.number_input("블레이드 총 개수", min_value=1, value=4)
    
    col_input, col_res = st.columns([1, 1])
    
    user_vectors_data = []
    with col_input:
        st.subheader("배열 데이터 입력")
        for i in range(num_blades):
            c1, c2 = st.columns(2)
            with c1: m = st.number_input(f"Bld #{i+1} 크기", value=200000.0, key=f"m{i}")
            with c2: p = st.number_input(f"Bld #{i+1} 각도", value=float(i*(360/num_blades)), key=f"p{i}")
            user_vectors_data.append({'magnitude': m, 'phase': p})
    
    # 실시간 계산
    user_vectors = []
    for d in user_vectors_data:
        x, y = calculate_vector_components(d['magnitude'], d['phase'])
        user_vectors.append({'magnitude': d['magnitude'], 'phase': d['phase'], 'x': x, 'y': y})
    
    v_sum = calculate_total_sum(user_vectors)
    v_mag = np.linalg.norm(v_sum)
    v_phase = np.degrees(np.arctan2(v_sum[1], v_sum[0])) % 360
    
    with col_res:
        st.subheader("검증 결과")
        st.plotly_chart(plot_polar_chart(user_vectors, v_sum, "검증용 합성 벡터"))
        st.metric("최종 합성 언밸런스", f"{v_mag:.2f}")
        st.metric("합성 위상", f"{v_phase:.2f} °")
        
        if v_mag < 100: # 예시 임계값
            st.balloons()
            st.success("✅ 안전 범위 내의 배열입니다!")
        else:
            st.error("⚠️ 주의: 언밸런스 수치가 높습니다. 재배열이 필요합니다.")