import streamlit as st
from main_page import *
from chat_page import *
from config import *

session_initiate()

# 페이지 설정
st.set_page_config(
    page_title="GYM-PT - 당신만의 트레이너",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일링
st.markdown("""
<style>
    .stMainBlockContainer {
        min-width:1000px;
    }
    
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
    
    .description-text > .list-item {
        display: inline-block;
        min-width: 480px;
        text-align: left;
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
    
    /* 채팅 전체 배경 */
    .chat-container {
        background: #F8F9FA;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #E8F5E8;
    }
    
    /* 채팅 메시지 스타일 */
    .chat-message {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
        color: #000000 !important;  /* 검정 텍스트 */
    }
    
    .user-message {
        background: #E8F5E8;
        border-left: 4px solid #2E7D32;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: white;
        border-left: 4px solid #4CAF50;
        margin-right: 2rem;
    }
    
    .upload-area {
        background: #F8F9FA;
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #E8F5E8 0%, #F1F8E9 100%);
    }
</style>
""", unsafe_allow_html=True)

# 메인 앱 실행
if st.session_state.page == 'main':
    main_page()
elif st.session_state.page == 'chat':
    chat_page()

