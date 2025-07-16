# main.py

import streamlit as st
import openai
import os
import base64
import ast
import threading
from io import BytesIO
from typing import List, Tuple, Dict, Any
from PIL import Image

from dotenv import load_dotenv

# chatbot.py에서 필요한 함수들을 임포트합니다.
from apptest import get_ai_response, Inferer, OpenAIInferer, parse_prediction, ask_llm_calorie, analyze_meal_with_llm

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- 전역 변수 및 상수 ---
GPT_MODEL = "gpt-4o-mini"

# --- 세션 상태 초기화 ---
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if "uploaded_image_bytes" not in st.session_state:
    st.session_state.uploaded_image_bytes = None
if "file_uploader_key_sidebar_counter" not in st.session_state:
    st.session_state.file_uploader_key_sidebar_counter = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "height": None,
        "weight": None,
        "age": None,
        "gender": "미선택"
    }
# --- 세션 상태 초기화 끝 ---


# --- OpenAI API 키 설정 ---
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except (KeyError, FileNotFoundError):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError
    except (ValueError, TypeError):
        st.error("OpenAI API 키가 설정되지 않았습니다. .env 파일이나 Streamlit secrets에 추가해주세요.", icon="🚨")
        st.stop()


# --- 메인 페이지 함수 ---
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
        /* 메인 페이지에서 사이드바 숨기기 (원한다면) */
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
        if st.button("🍽️ 오늘의 식사 입력하기", use_container_width=True):
            st.session_state.page = 'chat'
            st.rerun()


# --- 챗봇 페이지 함수 ---
def chat_page():
    # 챗봇 페이지 전용 CSS
    st.markdown("""
    <style>
        /* 메인 컨텐츠 영역에 하단 여백 추가 (채팅 바 높이만큼) */
        .main .block-container {
            padding-bottom: 120px !important; /* 채팅 바 높이 + 여유공간 */
        }

        /* Streamlit 메인 콘텐츠 컨테이너 및 섹션의 패딩 제거 */
        .st-emotion-cache-z5fcl4,
        .main .block-container,
        section[data-testid="stSidebar"],
        section[data-testid="stSidebarContent"],
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

        /* st.columns 컨테이너 자체의 간격 제거 */
        .st-emotion-cache-1r6y92h,
        .st-emotion-cache-1xw8pjm,
        .st-emotion-cache-1kyx218 {
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
            min-height: unset !important;
            height: auto !important;
        }

        /* 파일 업로더 전체 컨테이너 (stFileUploaderDropzone) */
        [data-testid="stFileUploaderDropzone"] {
            height: 100% !important;
            width: 100% !important;
            min-height: 50px !important;
            padding: 0 !important;
            margin: 1 !important;
            background-color: white !important;
            border: solid !important;
            cursor: pointer;
        }

        /* "Browse files" 버튼 - 파일 업로더 내부에만 적용되도록 수정 */
        [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
            height: 40px !important;
            line-height: 40px !important;
            padding: 0 1px !important;
            font-size: 0 !important;
            width: 100% !important;
            min-width: unset !important;
            margin: 0 !important;
            background-color: transparent !important;
            border: 0 !important;
            position: absolute;
            top: 0;
            left: 0;
            opacity: 0;
            cursor: pointer;
        }

        /* "Browse files" 버튼 내부의 텍스트 숨기기 */
        [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] span {
            display: none !important;
        }

        /* 드래그 앤 드롭 영역의 지침 (아이콘과 텍스트를 포함하는 부모 div) */
        [data-testid="stFileUploaderDropzoneInstructions"] {
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            padding: 0 !important;
            overflow: hidden;
            position: absolute;
            top: 0;
            left: 0;
            /* background-image는 chat_page 내부에서 조건부로 설정됨 */
            background-size: 35px 35px !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
        }

        /* "Drag and drop file here" 텍스트 숨기기 */
        .st-emotion-cache-9ycgxx.e17y52ym3 {
            display: none !important;
        }

        /* "Limit 200MB per file" 소제목 텍스트 숨기기 */
        .st-emotion-cache-1rpn56r.ejh2rmr0 {
            display: none !important;
        }

        /* 파일이 선택되었을 때 표시되는 파일 이름 텍스트 숨기기 */
        .stFileUploader p {
            display: none !important;
        }

        /* 채팅 메시지 컨테이너가 하단 고정 바에 가려지지 않도록 설정 */
        .stChatMessage {
            margin-bottom: 10px !important;
        }

        /* 스크롤 시 하단 여백 유지 */
        .element-container:last-child {
            margin-bottom: 120px !important;
        }
        /* 챗봇 페이지에서 사이드바 보이게 하기 (기본값) */
        section[data-testid="stSidebar"] {
            display: block !important; /* 사이드바를 보이게 합니다 */
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h2 style="text-align: center; color: #2E7D32; margin-bottom: 2rem;">💬 GYM-PT와 대화하기</h2>',
                unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("← 메인으로"):
            st.session_state.page = 'main'
            st.rerun()

    if not st.session_state.messages:
        st.session_state.messages.append(
            {"role": "assistant", "content": "안녕하세요! GYM-PT입니다. 오늘의 식사 사진과 신체 정보를 알려주시면 맞춤형 조언을 해드릴게요."})

    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 사용자:</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 GYM-PT:</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📝 새로운 메시지")

    # 사이드바 내용
    with st.sidebar:
        st.title("🥗 다이어트 챗봇 프로젝트명")
        st.markdown("""
        다이어트 관련해서 추천을 받거나, 음식 사진을 올리고 궁금한 점을 질문해보세요! AI가 사진과 질문을 함께 분석하여 답변해 드립니다.
        """)
        st.text('')

        # --- 개인 정보 입력 섹션 ---
        st.subheader("👤 내 정보 입력")

        col_height, col_weight = st.columns(2)
        with col_height:
            height_input = st.text_input(
                "키 (cm)",
                value=st.session_state.user_info.get("height", ""),
                key="height_input_key"
            )
        with col_weight:
            weight_input = st.text_input(
                "몸무게 (kg)",
                value=st.session_state.user_info.get("weight", ""),
                key="weight_input_key"
            )
        col_age, col_gender = st.columns([35, 18], vertical_alignment="center")
        with col_age:
            age_input = st.slider(
                "나이",
                min_value=1,
                max_value=99,
                value=st.session_state.user_info.get("age", 25),
                key="age_input_key"
            )
        with col_gender:
            gender_options = ["미선택", "남성", "여성"]
            gender_current_index = gender_options.index(st.session_state.user_info.get("gender", "미선택"))
            gender_input = st.radio(
                "성별",
                gender_options,
                index=gender_current_index,
                key="gender_input_key"
            )

        if st.button("개인 정보 저장", key="save_user_info_button"):
            try:
                st.session_state.user_info["height"] = float(height_input) if height_input else None
                st.session_state.user_info["weight"] = float(weight_input) if weight_input else None
                st.session_state.user_info["age"] = int(age_input)
                st.session_state.user_info["gender"] = gender_input
                st.success("개인 정보가 저장되었습니다! (새로고침해도 유지됩니다.)")
            except ValueError:
                st.error("키와 몸무게는 숫자로 입력해주세요.", icon="⚠️")

        st.markdown("---\n")

        st.markdown('### 보여주실 음식 사진이 있으신가요? 영양 성분을 분석해 드립니다!')

        current_uploader_key = f"file_uploader_key_sidebar_{st.session_state.file_uploader_key_sidebar_counter}"
        uploaded_file_sidebar = st.file_uploader(
            "",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key=current_uploader_key
        )

        if uploaded_file_sidebar:
            st.session_state.uploaded_image_bytes = uploaded_file_sidebar.getvalue()
            st.success("이미지가 업로드되었습니다! 이제 사진에 대해 질문해보세요.")

    # 이미지 업로더 CSS를 위한 변수 (메인 화면용 CSS와 분리)
    is_image_uploaded_css = 'url("https://toppng.com/uploads/preview/file-upload-image-icon-115632290507ftgixivqp.png")'
    if st.session_state.uploaded_image_bytes is not None:
        is_image_uploaded_css = 'none'

    st.markdown(f"""
    <style>
        [data-testid="stFileUploaderDropzoneInstructions"] {{
            background-image: {is_image_uploaded_css} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "음식 사진을 업로드해주세요 (최대 5개)",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="섭취한 음식의 사진을 올려주세요. 최대 5개까지 업로드 가능합니다."
    )
    if uploaded_files and len(uploaded_files) > 5:
        st.error("최대 5개의 이미지만 업로드 가능합니다.")
        uploaded_files = uploaded_files[:5]

    user_text = st.text_area(
        "신체 정보와 음식에 대한 추가 정보를 입력해주세요",
        placeholder="예: 나이 25세, 남성, 키 175cm, 몸무게 70kg, 평소 운동량 중간, 아침에 삶은 계란 2개 먹음....",
        height=100
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📤 분석 요청하기", use_container_width=True):
            if not uploaded_files and not user_text:
                st.error("이미지나 텍스트 중 하나는 입력해주세요.")
            else:
                with st.spinner("분석 중입니다..."):
                    try:
                        current_user_images = []
                        if uploaded_files:
                            for uploaded_file in uploaded_files:
                                img_pil = Image.open(uploaded_file)
                                current_user_images.append(img_pil)
                        st.session_state.chat_history.append(("user", user_text, current_user_images))
                        st.session_state.messages.append({"role": "user", "content": user_text})

                        final_response = ""
                        if uploaded_files:
                            inferer = OpenAIInferer(model_id=GPT_MODEL, temperature=0.0)

                            images_for_inferer = [Inferer.to_pil_image(f) for f in uploaded_files]
                            filenames_for_inferer = [f.name for f in uploaded_files]

                            try:
                                results = inferer(images_for_inferer, filenames_for_inferer)
                                response_parts = []
                                for filename, pred_str in results.items():
                                    menu_name, ingredients = parse_prediction(pred_str)
                                    calorie = ask_llm_calorie(menu_name)

                                    analysis = analyze_meal_with_llm(
                                        menu_name, calorie, user_text,
                                        chat_history=st.session_state.chat_history
                                    )
                                    response_parts.append(f"📸 **{filename}**\n{analysis}")
                                final_response = "\n\n---\n\n".join(response_parts)
                            except Exception as e:
                                final_response = f"""
🍎 **분석 결과 (Demo)**

드신 메뉴는 대략 **600kcal** 정도로 추정됩니다.

📊 **권장 섭취량 분석:**
- 입력하신 정보를 바탕으로 일일 권장 섭취량은 약 2,200kcal입니다.
- 현재 섭취량을 제외하면 약 1,600kcal가 남았습니다.

🏃‍♂️ **칼로리 소모 운동:**
- 빠른 걷기: 90분 (600kcal 소모)
- 자전거 타기: 60분 (600kcal 소모)
- 조깅: 45분 (600kcal 소모)

🥗 **추천 식단:**
- 닭가슴살 샐러드 (300kcal)
- 현미밥 1공기 (280kcal)
- 고구마 (200kcal)
- 두부요리 (150kcal)

건강한 식단 관리를 위해 균형잡힌 영양소 섭취를 권장합니다! 💪

*실제 사용시에는 OpenAI API 키를 설정해주세요.*
"""
                        else:
                            final_response = analyze_meal_with_llm(
                                menu_name="",
                                calorie="",
                                user_text=user_text,
                                chat_history=st.session_state.chat_history
                            )

                        st.session_state.messages.append({"role": "assistant", "content": final_response})
                        st.session_state.chat_history.append(("assistant", final_response, None))

                        if uploaded_files:
                            st.session_state.uploaded_image_bytes = None
                            st.session_state.file_uploader_key_sidebar_counter += 1
                        st.rerun()

                    except Exception as e:
                        st.error(f"분석 중 치명적인 오류가 발생했습니다: {str(e)}", icon="🚨")


# --- 메인 앱 실행 로직 ---
def main():
    # 이 부분의 st.set_page_config는 앱 전체에 적용되는 설정
    st.set_page_config(
        page_title="GYM-PT - 당신만의 트레이너",
        page_icon="💪",
        layout="wide",
        initial_sidebar_state="collapsed"  # 초기에는 사이드바를 숨김 (main_page에 맞춰)
    )

    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'chat':
        # 챗봇 페이지일 때만 사이드바를 확장
        # st.set_page_config는 한번만 호출되어야 하지만, initial_sidebar_state는 런타임에 영향을 줍니다.
        # 이 부분을 통해 챗봇 페이지로 전환될 때 사이드바가 펼쳐지게 할 수 있습니다.
        # 단, st.set_page_config는 스크립트 실행 초기에 호출되는 것이 권장됩니다.
        # 여기서는 사이드바의 display 속성을 CSS로 제어하는 방식이 더 안정적입니다.
        chat_page()


if __name__ == "__main__":
    main()