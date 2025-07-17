import streamlit as st
from inferer import *
from util import *
from config import *

# 멀티턴 챗봇: chat_history를 LLM context로 넣어줌!
def chat_page():
    session_initiate()
    print_session_state()

    st.markdown('<h2 style="text-align: center; color: #2E7D32; margin-bottom: 2rem;">💬 GYM-PT와 대화하기</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("← 메인으로"):
            st.session_state.page = 'main'
            st.rerun()
    chat_container = st.container()
    with chat_container:
        # st.markdown('<div class="chat-container">', unsafe_allow_html=True)   # 이 줄 삭제
        if st.session_state.chat_history:
            for i, (role, content, images) in enumerate(st.session_state.chat_history):
                if role == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 사용자:</strong><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 GYM-PT:</strong><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
        # st.markdown('</div>', unsafe_allow_html=True)  # 이 줄 삭제

    st.markdown("---")
    st.markdown("### 📝 새로운 메시지")
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
                        user_images = []
                        if uploaded_files:
                            for uploaded_file in uploaded_files:
                                img = Image.open(uploaded_file)
                                user_images.append(img)
                        st.session_state.chat_history.append(("user", user_text, user_images))
                        if uploaded_files:
                            os.environ.setdefault("OPENAI_API_KEY", "your-api-key-here")
                            inferer = OpenAIInferer("gpt-4o-mini", 0.0)
                            images = [Inferer.to_pil_image(f) for f in uploaded_files]
                            filenames = [f.name for f in uploaded_files]
                            try:
                                results = inferer(images, filenames)
                                response_parts = []
                                for filename, pred_str in results.items():
                                    menu_name, ingredients = parse_prediction(pred_str)
                                    rag_context, calorie = get_menu_context_with_threshold(menu_name)
                                    analysis = analyze_meal_with_llm(
                                        menu_name, calorie, user_text,
                                        chat_history=st.session_state.chat_history
                                    )
                                    response_parts.append(f"📸 **{filename}**\n{rag_context}\n\n{analysis}")

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
                            # 이미지가 없는 경우에도 멀티턴 context 활용!
                            final_response = analyze_meal_with_llm(
                                menu_name="", calorie="", user_info=user_text,
                                chat_history=st.session_state.chat_history
                            )
                        st.session_state.chat_history.append(("assistant", final_response, None))
                        st.rerun()
                    except Exception as e:
                        st.error(f"분석 중 오류가 발생했습니다: {str(e)}")