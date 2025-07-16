import streamlit as st
import os
from dotenv import load_dotenv

# Import page functions (chat_page는 이제 chatbot.py의 내용을 그대로 사용)
from main_page import main_page
from chat_page import chat_page # chat_page는 이제 원래 chatbot.py와 동일

load_dotenv() # 환경 변수 로드는 필요하다면 여기에 유지하거나 각 페이지로 옮길 수 있음.
              # 지금은 chat_page에서 다시 로드하므로 여기서는 삭제해도 무방.
              # 명확성을 위해 chat_page에서 load_dotenv()를 유지합니다.

# --- 세션 상태 초기화 (페이지 전환을 위한 최소한의 상태만 유지) ---
if 'page' not in st.session_state:
    st.session_state.page = 'main'
# --- 세션 상태 초기화 끝 ---

def main():
    # main.py에서는 더 이상 st.set_page_config를 호출하지 않습니다.
    # 각 페이지가 자신의 레이아웃을 설정하도록 합니다.
    # 단, 앱의 전역적인 아이콘/타이틀이 필요하다면 여기에 둘 수 있지만,
    # 복수 페이지에서는 각 페이지에서 설정하는 것이 더 유연합니다.

    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'chat':
        chat_page() # chatbot.py의 모든 내용이 이 함수에서 실행됩니다.

if __name__ == "__main__":
    main()