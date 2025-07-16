import streamlit as st

def main_page():
    # 메인 페이지 전용 CSS
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #2E7D32;
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .sub-header {
            text-align: center;
            color: #4CAF50;
            font-size: 1.3rem;
            margin-bottom: 2rem;
            font-weight: 500;
        }

        .description-box {
            background: linear-gradient(135deg, #E8F5E8 0%, #F1F8E9 100%);
            padding: 2rem;
            border-radius: 15px;
            border-left: 5px solid #4CAF50;
            margin: 2rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .description-text {
            color: #2E7D32;
            font-size: 1.1rem;
            line-height: 1.6;
            text-align: center;
        }

        .stButton > button {
            background: linear-gradient(45deg, #4CAF50, #66BB6A);
            color: white;
            border: none;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            font-weight: bold;
            border-radius: 25px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }

        .stButton > button:hover {
            background: linear-gradient(45deg, #388E3C, #4CAF50);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }

        .feature-box {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border: 2px solid #E8F5E8;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
        }

        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }

        .feature-title {
            color: #2E7D32;
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .feature-text {
            color: #555;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        /* 메인 페이지에서 사이드바 숨기기 (main_page 전용) */
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        /* 기타 Streamlit 기본 요소 간격 조절 (메인 페이지에만 적용) */
        .st-emotion-cache-z5fcl4,
        .main .block-container,
        .stVerticalBlock,
        .st-emotion-cache-mncm6h,
        .stElementContainer,
        .st-emotion-cache-kj6hex,
        .st-emotion-cache-8atqhb {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: 0rem !important;
            margin-bottom: 0rem !important;
            min-height: unset !important;
            height: auto !important;
            gap: 0 !important;
        }
        .st-emotion-cache-1r6y92h,
        .st-emotion-cache-1xw8pjm,
        .st-emotion-cache-1kyx218 {
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
            min-height: unset !important;
            height: auto !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 헤더
    st.markdown('<h1 class="main-header">💪 GYM-PT</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">식단과 운동을 관리해주는 당신만의 트레이너</p>', unsafe_allow_html=True)

    # 메인 설명
    st.markdown("""
    <div class="description-box">
        <div class="description-text">
            <strong>🍎 오늘 섭취한 음식의 사진들과 약간의 신체정보를 넣어주시면</strong><br><br>
            ✅ 이 음식은 몇 칼로리인지<br>
            ✅ 이 칼로리를 소모하려면 어떤 운동을 얼만큼 해야하는지<br>
            ✅ 남은 끼니는 어떤 음식을 섭취하면 좋을지<br><br>
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
            <div class="feature-text">음식 사진을 올리면 AI가 메뉴와 칼로리를 분석해드려요</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🏃‍♂️</div>
            <div class="feature-title">운동 추천</div>
            <div class="feature-text">섭취한 칼로리에 맞는 맞춤형 운동 계획을 제공해드려요</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🥗</div>
            <div class="feature-title">식단 관리</div>
            <div class="feature-text">남은 칼로리에 맞는 건강한 식단을 추천해드려요</div>
        </div>
        """, unsafe_allow_html=True)

    # 시작 버튼
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🍽️오늘 식사 입력하기!", use_container_width=True):
            st.session_state.page = 'chat'
            st.rerun()