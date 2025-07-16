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
                model="gpt-4.1-nano",  # 요청하신 대로 모델명 유지
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
            model="gpt-4.1-nano",  # 요청하신 대로 모델명 유지
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
    st.title("🥗 다이어트 챗봇 프로젝트명")
    st.markdown("""
    다이어트 관련해서 추천을 받거나, 음식 사진을 올리고 궁금한 점을 질문해보세요! AI가 사진과 질문을 함께 분석하여 답변해 드립니다.
    """)
    st.text('')

    # --- 개인 정보 입력 섹션 ---
    st.subheader("👤 내 정보 입력")

    # 세션 상태 초기화 (처음 앱 실행 시)
    if "user_info" not in st.session_state:
        st.session_state.user_info = {
            "height": None,
            "weight": None,
            "age": None,
            "gender": "미선택"  # 초기값을 "미선택"으로 변경
        }

    # 키와 몸무게를 한 행에 배치
    col_height, col_weight = st.columns(2)  # 2개의 컬럼 생성

    with col_height:
        # 키 입력 (text_input)
        height_input = st.text_input(
            "키 (cm)",
            value=st.session_state.user_info.get("height", ""),
            key="height_input_key"
        )
    with col_weight:
        # 몸무게 입력 (text_input)
        weight_input = st.text_input(
            "몸무게 (kg)",
            value=st.session_state.user_info.get("weight", ""),
            key="weight_input_key"
        )
    col_age, col_gender = st.columns([35, 18], vertical_alignment="center")
    # 나이 선택 (slider)
    with col_age:
        age_input = st.slider(
            "나이",
            min_value=1,
            max_value=99,
            value=st.session_state.user_info.get("age", 25),
            key="age_input_key"
        )
    with col_gender:
        # 성별 선택 (radio) - "미선택" 옵션을 추가하고 기본값을 "미선택"으로 설정
        gender_options = ["미선택", "남성", "여성"]
        # 현재 저장된 값에 따라 인덱스를 찾아 설정 (없으면 "미선택"의 인덱스)
        gender_current_index = gender_options.index(st.session_state.user_info.get("gender", "미선택"))
        gender_input = st.radio(
            "성별",
            gender_options,
            index=gender_current_index,
            key="gender_input_key"
        )

    # '개인 정보 저장' 버튼
    if st.button("개인 정보 저장", key="save_user_info_button"):
        try:
            st.session_state.user_info["height"] = float(height_input) if height_input else None
            st.session_state.user_info["weight"] = float(weight_input) if weight_input else None
            st.session_state.user_info["age"] = int(age_input)
            st.session_state.user_info["gender"] = gender_input  # "미선택"도 저장 가능
            st.success("개인 정보가 저장되었습니다! (새로고침해도 유지됩니다.)")
        except ValueError:
            st.error("키와 몸무게는 숫자로 입력해주세요.", icon="⚠️")

    st.markdown("---\n")  # 구분선

    st.markdown('### 보여주실 음식 사진이 있으신가요? 영양 성분을 분석해 드립니다!')
    # 파일 업로더 키를 동적으로 생성하여 새 파일 업로드 시 이전 상태를 무시하도록 함
    if "file_uploader_key_sidebar_counter" not in st.session_state:
        st.session_state.file_uploader_key_sidebar_counter = 0

    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed",
                                     key=f"file_uploader_key_sidebar_{st.session_state.file_uploader_key_sidebar_counter}")

    if uploaded_file:
        st.session_state.uploaded_image_bytes = uploaded_file.getvalue()
        st.success("이미지가 업로드되었습니다! 이제 사진에 대해 질문해보세요.")

# 메인 화면 제목
st.title("📸 음식 사진으로 영양성분 알아보기")
st.divider()

st.markdown(f"""
    <style>
        /* 메인 컨텐츠 영역에 하단 여백 추가 (채팅 바 높이만큼) */
        .main .block-container {{
            padding-bottom: 120px !important; /* 채팅 바 높이 + 여유공간 */
        }}

        /* Streamlit 메인 콘텐츠 컨테이너 및 섹션의 패딩 제거 */
        .st-emotion-cache-z5fcl4, /* Streamlit 메인 콘텐츠 컨테이너 (정확한 클래스명은 F12로 확인 필요) */
        .main .block-container, /* 이전 버전의 메인 컨테이너 */
        section[data-testid="stSidebar"], /* 사이드바 */
        section[data-testid="stSidebarContent"], /* 사이드바 내부 콘텐츠 */
        .stVerticalBlock, /* st.columns가 감싸는 VerticalBlock */
        .st-emotion-cache-mncm6h, /* stVerticalBlock의 특정 클래스 */
        .stElementContainer, /* 모든 컴포넌트를 감싸는 ElementContainer */
        .st-emotion-cache-kj6hex, /* stElementContainer의 특정 클래스 */
        .st-emotion-cache-8atqhb {{ /* stFileUploader의 직접적인 부모 div */
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: 0rem !important;
            margin-bottom: 0rem !important;
            min-height: unset !important;
            height: auto !important;
            gap: 0 !important;
        }}

        /* st.columns 컨테이너 자체의 간격 제거 */
        .st-emotion-cache-1r6y92h, /* col2에 해당하는 컬럼 div (st.columns의 자식) */
        .st-emotion-cache-1xw8pjm, /* st.columns 내부의 일반 div */
        .st-emotion-cache-1kyx218 {{ /* 다른 st.columns 관련 div */
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
            min-height: unset !important;
            height: auto !important;
        }}

        /* 파일 업로더 전체 컨테이너 (stFileUploaderDropzone) */
        [data-testid="stFileUploaderDropzone"] {{
            height: 100% !important;
            width: 100% !important; /* 전체 너비로 사용 */
            min-height: 50px !important; /* 최소 높이 유지 */
            padding: 0 !important;
            margin: 1 !important;
            background-color: white !important; /* 배경 투명하게 */
            border: solid !important; /* 테두리 제거 */
            cursor: pointer;
        }}

        /* "Browse files" 버튼 - 파일 업로더 내부에만 적용되도록 수정 */
        [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {{ /* <-- 여기 선택자 변경 */
            height: 40px !important;
            line-height: 40px !important;
            padding: 0 1px !important;
            font-size: 0 !important; /* 버튼 텍스트 숨김 */
            width: 100% !important;
            min-width: unset !important;
            margin: 0 !important;
            background-color: transparent !important;
            border: 0 !important;
            position: absolute;
            top: 0;
            left: 0;
            opacity: 0; /* 버튼 자체를 투명하게 만들어 클릭만 가능하게 함 */
            cursor: pointer;
        }}

        /* "Browse files" 버튼 내부의 텍스트 숨기기 */
        [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] span {{ /* <-- 여기 선택자 변경 */
            display: none !important;
        }}


        /* 드래그 앤 드롭 영역의 지침 (아이콘과 텍스트를 포함하는 부모 div) */
        [data-testid="stFileUploaderDropzoneInstructions"] {{
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
            background-image: url("https://toppng.com/uploads/preview/file-upload-image-icon-115632290507ftgixivqp.png") !important;
            background-size: 35px 35px !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
        }}

        /* "Drag and drop file here" 텍스트 숨기기 */
        .st-emotion-cache-9ycgxx.e17y52ym3 {{
            display: none !important;
        }}

        /* "Limit 200MB per file" 소제목 텍스트 숨기기 */
        .st-emotion-cache-1rpn56r.ejh2rmr0 {{
            display: none !important;
        }}

        /* 파일이 선택되었을 때 표시되는 파일 이름 텍스트 숨기기 */
        .stFileUploader p {{
            display: none !important;
        }}

        /* 채팅 메시지 컨테이너가 하단 고정 바에 가려지지 않도록 설정 */
        .stChatMessage {{
            margin-bottom: 10px !important;
        }}

        /* 스크롤 시 하단 여백 유지 */
        .element-container:last-child {{
            margin-bottom: 120px !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# 채팅 기록 및 업로드된 이미지 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 분석할 음식 사진을 올려주세요."}
    ]

if "uploaded_image_bytes" not in st.session_state:
    st.session_state.uploaded_image_bytes = None

# 기존 채팅 기록 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image_bytes" in msg:
            st.image(msg["image_bytes"], width=250)
        st.markdown(msg["content"])

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
            # 이미지 첨부 여부에 따라 분석 함수 호출
            if "image_bytes" in user_message:
                image_b64 = base64.b64encode(user_message["image_bytes"])
                ai_response = analyze_image_with_prompt(prompt, image_bytes=image_b64)
            else:
                ai_response = analyze_image_with_prompt(prompt)

            # AI 응답을 화면에 표시
            st.markdown(ai_response)
            # AI 응답을 채팅 기록에 추가
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

            # 이미지가 사용되었을 경우에만 초기화 및 rerunning
            if "image_bytes" in user_message:
                st.session_state.uploaded_image_bytes = None
                st.session_state.file_uploader_key_sidebar_counter += 1
                st.rerun()