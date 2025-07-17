import streamlit as st
from util import *

# 메인 페이지
def main_page():
    session_initiate()

    # 헤더
    st.markdown('<h1 class="main-header">💪 GYM-PT</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">식단과 운동을 관리해주는 당신만의 트레이너</p>', unsafe_allow_html=True)

    # 메인 설명
    st.markdown("""
    <div class="description-box">
        <div class="description-text">
            <strong>🍎 오늘 섭취한 음식의 사진들과 약간의 신체정보를 넣어주시면</strong><br><br>
            <span class="list-item">✅ 이 음식은 몇 칼로리인지</span><br>
            <span class="list-item">✅ 이 칼로리를 소모하려면 어떤 운동을 얼만큼 해야하는지</span><br>
            <span class="list-item">✅ 남은 끼니는 어떤 음식을 섭취하면 좋을지</span><br><br>
            <strong>전문적으로 알려드릴게요!</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 기능 소개
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📸</div>
            <div class="feature-title">이미지 분석</div>
            <div class="feature-text">음식 사진을 올리면<br/>AI가 메뉴와 칼로리를 분석해드려요</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🏃‍♂️</div>
            <div class="feature-title">운동 추천</div>
            <div class="feature-text">섭취한 칼로리에 맞는<br/>맞춤형 운동 계획을 제공해드려요</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🥗</div>
            <div class="feature-title">식단 관리</div>
            <div class="feature-text">남은 칼로리에 맞는<br/>건강한 식단을 추천해드려요</div>
        </div>
        """, unsafe_allow_html=True)

    # 시작 버튼
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🍽️ 오늘의 식사 입력하기", use_container_width=True):
            st.session_state.page = 'chat'
            st.rerun()