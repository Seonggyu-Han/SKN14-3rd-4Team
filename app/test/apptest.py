import streamlit as st
import openai
import os
import base64
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- 초기 설정 및 함수 정의 ---

# OpenAI API 키 설정
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


def analyze_image_with_prompt(user_prompt, image_bytes=None):
    """OpenAI Vision API를 사용해 이미지와 사용자 질문을 함께 분석"""
    if image_bytes is not None:
        try:
            response = openai.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_bytes.decode('utf-8')}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"이미지 분석 중 오류 발생: {e}", icon="🔥")
            return "죄송합니다, 요청을 처리하는 중 오류가 발생했습니다."
    else:
        response = openai.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                    ],
                }
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content


# --- Streamlit UI 구성 ---

st.set_page_config(page_title="AI 영양 분석 챗봇", page_icon="🥗", layout="centered")

# 사이드바 내용
with st.sidebar:
    st.title("🥗 AI 영양 분석 챗봇")
    st.markdown("""
    음식 사진을 올리고 궁금한 점을 질문해보세요! AI가 사진과 질문을 함께 분석하여 답변해 드립니다.

    **사용 방법:**
    1. 하단 📎 버튼으로 이미지 업로드
    2. 채팅창에 질문 입력
    (예: 이 음식 칼로리 알려줘)
    """)

# 메인 화면 제목
st.title("📸 음식 사진으로 영양성분 알아보기")
st.divider()

# CSS 스타일 추가
st.markdown("""
    <style>
        /* 하단 고정 입력창 스타일 */
        .fixed-bottom-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: var(--background-color);
            padding: 1rem;
            border-top: 1px solid var(--border-color);
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* 이미지 업로드 버튼 스타일 */
        .upload-button {
            background-color: #f0f2f6;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 18px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 44px;
            height: 44px;
        }

        .upload-button:hover {
            background-color: #e5e7eb;
            border-color: #9ca3af;
        }

        /* 첨부된 이미지 표시 스타일 */
        .attached-image {
            max-height: 60px;
            border-radius: 4px;
            margin-right: 10px;
        }

        /* 메인 컨테이너 하단 여백 */
        .main-container {
            margin-bottom: 120px;
        }

        /* 파일 업로더 숨기기 */
        .hidden-uploader {
            display: none !important;
        }

        /* 첨부 이미지 미리보기 컨테이너 */
        .attachment-preview {
            position: fixed;
            bottom: 80px;
            left: 1rem;
            right: 1rem;
            background-color: var(--background-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .remove-attachment {
            background-color: #ef4444;
            color: white;
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)

# 채팅 기록 및 업로드된 이미지 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 분석할 음식 사진을 올려주세요."}
    ]

if "uploaded_image_bytes" not in st.session_state:
    st.session_state.uploaded_image_bytes = None

if "file_uploader_key_counter" not in st.session_state:
    st.session_state.file_uploader_key_counter = 0

# 메인 컨테이너 div 시작
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 기존 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image_bytes" in message:
            st.image(message["image_bytes"], width=250)
        st.markdown(message["content"])

# 메인 컨테이너 div 끝
st.markdown('</div>', unsafe_allow_html=True)

# 방법 1: 숨겨진 파일 업로더 + 커스텀 버튼
# 숨겨진 파일 업로더
uploaded_file = st.file_uploader(
    "",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed",
    key=f"file_uploader_{st.session_state.file_uploader_key_counter}",
    help="이미지 파일을 선택하세요"
)

# 파일이 업로드되면 세션에 저장
if uploaded_file:
    st.session_state.uploaded_image_bytes = uploaded_file.getvalue()
    st.session_state.file_uploader_key_counter += 1
    st.rerun()

# 첨부된 이미지 미리보기 (있는 경우)
if st.session_state.uploaded_image_bytes is not None:
    st.markdown("""
        <div class="attachment-preview">
            <span>📎 이미지 첨부됨</span>
            <button class="remove-attachment" onclick="window.parent.document.querySelector('[data-testid=\"stButton\"]').click()">×</button>
        </div>
    """, unsafe_allow_html=True)

    # 첨부 이미지 미리보기
    st.image(st.session_state.uploaded_image_bytes, width=60)

    # 첨부 제거 버튼
    if st.button("첨부 제거", key="remove_attachment"):
        st.session_state.uploaded_image_bytes = None
        st.rerun()

# 방법 2: JavaScript와 커스텀 HTML을 사용한 더 세련된 접근
# st.markdown("""
#     <div class="fixed-bottom-container">
#         <label for="file-input" class="upload-button" title="이미지 첨부">
#             📎
#         </label>
#         <div style="flex: 1;">
#             <!-- 여기에 채팅 입력창이 오게 될 예정 -->
#         </div>
#     </div>
#
#     <script>
#         // 파일 업로더 버튼 클릭 시 실제 파일 업로더 트리거
#         document.addEventListener('DOMContentLoaded', function() {
#             const uploadButton = document.querySelector('.upload-button');
#             const fileUploader = document.querySelector('[data-testid="stFileUploader"] input[type="file"]');
#
#             if (uploadButton && fileUploader) {
#                 uploadButton.addEventListener('click', function() {
#                     fileUploader.click();
#                 });
#             }
#         });
#     </script>
# """, unsafe_allow_html=True)

# 사용자 입력(채팅창) 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    user_message = {"role": "user", "content": prompt}

    # 세션에 첨부된 이미지가 있으면 메시지에 추가
    if st.session_state.uploaded_image_bytes is not None:
        user_message["image_bytes"] = st.session_state.uploaded_image_bytes

    # 사용자 메시지를 채팅 기록에 추가
    st.session_state.messages.append(user_message)

    # 화면에 사용자 메시지 표시 (이미지 + 텍스트)
    with st.chat_message("user"):
        if "image_bytes" in user_message:
            st.image(user_message["image_bytes"], width=250)
        st.markdown(user_message["content"])

    # AI 응답 처리
    with st.chat_message("assistant"):
        with st.spinner("AI가 분석하고 있어요... 🤖"):
            # 이미지가 첨부된 경우
            if "image_bytes" in user_message:
                image_b64 = base64.b64encode(user_message["image_bytes"])
                ai_response = analyze_image_with_prompt(prompt, image_bytes=image_b64)
                st.session_state.uploaded_image_bytes = None  # 분석 후 첨부된 이미지 초기화
            # 텍스트만 있는 경우
            else:
                ai_response = analyze_image_with_prompt(prompt)

            st.markdown(ai_response)
            # AI 응답을 채팅 기록에 추가
            st.session_state.messages.append({"role": "assistant", "content": ai_response})