import streamlit as st
import openai
import os
import base64
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# gaein_information 모듈은 프로젝트 루트에 있어야 합니다.
from chatbot_utils import get_ai_response

GPT_MODEL = "gpt-4.1-nano"

load_dotenv()

def session_initiate():
    # --- 세션 상태 초기화 ---
    if "uploaded_image_bytes" not in st.session_state:
        st.session_state.uploaded_image_bytes = None

    if "file_uploader_key_sidebar_counter" not in st.session_state:
        st.session_state.file_uploader_key_sidebar_counter = 0

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 분석할 음식 사진을 올려주세요. 운동이나 식단 계획이 필요하시면 저에게 요청해주세요."}
        ]

    if "user_info" not in st.session_state:
        st.session_state.user_info = {
            "height": None,
            "weight": None,
            "age": None,
            "gender": "미선택"
        }

    # 새로운 세션 상태 추가: 생성된 계획 데이터를 저장
    if "generated_plan_data" not in st.session_state:
        st.session_state.generated_plan_data = None
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


# LLM이 운동/식단 계획을 JSON 형식으로 생성하도록 유도하는 프롬프트 함수
def get_plan_prompt(plan_type, duration_weeks=1, user_prompt_text=""):
    base_prompt = f"사용자의 신체 정보와 목표를 바탕으로 {duration_weeks}주간의 "
    # 사용자 프롬프트를 포함하여 LLM이 더 자연스러운 응답을 하도록 유도
    full_prompt = user_prompt_text + "\n\n" + base_prompt

    if plan_type == "운동":
        return full_prompt + """운동 루틴을 JSON 형식으로 상세하게 작성해주세요. 각 주차별로, 요일별 운동 내용 (예: 부위, 운동명, 세트 수, 반복 횟수), 휴식일 등을 포함해주세요. 목표는 다이어트를 위한 근력 및 유산소 운동 병행입니다. JSON 구조는 다음과 같아야 합니다:
{
  "plan_type": "운동",
  "duration_weeks": 4,
  "plan_details": [
    {
      "week": 1,
      "schedule": [
        {"day": "월", "focus": "하체/유산소", "exercises": [{"name": "스쿼트", "sets": 4, "reps": 10}, {"name": "런지", "sets": 3, "reps": 12}, {"name": "러닝", "duration_min": 30}]},
        {"day": "화", "focus": "상체(밀기)/코어", "exercises": [{"name": "벤치프레스", "sets": 4, "reps": 10}, {"name": "오버헤드프레스", "sets": 3, "reps": 12}]},
        {"day": "수", "focus": "휴식"},
        {"day": "목", "focus": "등/유산소", "exercises": [{"name": "데드리프트", "sets": 3, "reps": 8}, {"name": "풀업", "sets": 3, "reps": "max"}, {"name": "사이클", "duration_min": 40}]},
        {"day": "금", "focus": "어깨/팔", "exercises": [{"name": "덤벨숄더프레스", "sets": 3, "reps": 12}, {"name": "이두컬", "sets": 3, "reps": 15}]},
        {"day": "토", "focus": "전신/고강도", "exercises": [{"name": "버피", "sets": 3, "reps": 15}, {"name": "플랭크", "duration_sec": 60}]},
        {"day": "일", "focus": "휴식"}
      ]
    },
    {
      "week": 2,
      "schedule": [
        // ... week 2 내용 ...
      ]
    },
    {
      "week": 3,
      "schedule": [
        // ... week 3 내용 ...
      ]
    },
    {
      "week": 4,
      "schedule": [
        // ... week 4 내용 ...
      ]
    }
    // ... 최대 {duration_weeks}주까지의 주차 내용 ...
  ]
}
"""
    elif plan_type == "식단":
        return full_prompt + """식단 계획을 JSON 형식으로 상세하게 작성해주세요. 각 주차별로, 요일별 아침, 점심, 저녁, 간식 메뉴와 간단한 조리법, 대략적인 칼로리를 포함해주세요. 목표는 건강한 다이어트를 위한 균형 잡힌 식단입니다. JSON 구조는 다음과 같아야 합니다:
{
  "plan_type": "식단",
  "duration_weeks": 4,
  "plan_details": [
    {
      "week": 1,
      "schedule": [
        {"day": "월", "meals": {"breakfast": {"menu": "오트밀과 베리류", "calories": 300, "recipe": "오트밀에 물/우유 붓고 전자레인지, 베리 추가"}, "lunch": {"menu": "닭가슴살 샐러드", "calories": 400, "recipe": "닭가슴살 구워 야채와 드레싱"}, "dinner": {"menu": "고구마와 두부 스테이크", "calories": 350, "recipe": "고구마 삶고 두부 구워 곁들임"}, "snack": {"menu": "그릭 요거트", "calories": 100, "recipe": "그릭 요거트 그대로"}}},
        {"day": "화", "meals": {"breakfast": {"menu": "과일 스무디", "calories": 250, "recipe": "바나나, 시금치, 아몬드 우유 믹서"}, "lunch": {"menu": "현미밥과 참치", "calories": 450, "recipe": "현미밥에 참치, 김, 채소 곁들여"}, "dinner": {"menu": "연어 스테이크와 채소", "calories": 400, "recipe": "연어 오븐에 굽고 아스파라거스, 브로콜리 곁들임"}, "snack": {"menu": "견과류 한 줌", "calories": 80, "recipe": "여러 견과류 혼합"}}},
        // ... 요일별 내용 ...
      ]
    },
    {
      "week": 2,
      "schedule": [
        // ... week 2 내용 ...
      ]
    },
    {
      "week": 3,
      "schedule": [
        // ... week 3 내용 ...
      ]
    },
    {
      "week": 4,
      "schedule": [
        // ... week 4 내용 ...
      ]
    }
    // ... 최대 {duration_weeks}주까지의 주차 내용 ...
  ]
}
"""
    else:
        return ""


def chat_page():
    session_initiate()

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

        # '개인 정보 저장' 버튼
        if st.button("개인 정보 저장", key="save_user_info_button"):
            try:
                st.session_state.user_info["height"] = float(height_input) if height_input else None
                st.session_state.user_info["weight"] = float(weight_input) if weight_input else None
                st.session_state.user_info["age"] = int(age_input)
                st.session_state.user_info["gender"] = gender_input
                st.success("개인 정보가 저장되었습니다! (새로고침해도 유지됩니다.)")
            except ValueError:
                st.error("키와 몸무게는 숫자로 입력해주세요.", icon="⚠️")

        st.markdown("---\n")  # 구분선

        st.markdown('### 보여주실 음식 사진이 있으신가요? 영양 성분을 분석해 드립니다!')

        current_uploader_key = f"file_uploader_key_sidebar_{st.session_state.file_uploader_key_sidebar_counter}"

        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed",
                                         key=current_uploader_key)

        if uploaded_file:
            st.session_state.uploaded_image_bytes = uploaded_file.getvalue()
            st.success("이미지가 업로드되었습니다! 이제 사진에 대해 질문해보세요.")

    # 메인 화면 제목
    st.title("📸 음식 사진으로 영양성분 알아보기")
    st.divider()

    # CSS 스타일 주입
    is_image_uploaded_css = "none"
    if st.session_state.uploaded_image_bytes is None:
        is_image_uploaded_css = 'url("https://toppng.com/uploads/preview/file-upload-image-icon-115632290507ftgixivqp.png")'

    st.markdown(f"""
        <style>
            /* 메인 컨텐츠 영역에 하단 여백 추가 (채팅 바 높이만큼) */
            .main .block-container {{
                padding-bottom: 120px !important; /* 채팅 바 높이 + 여유공간 */
            }}

            /* Streamlit 메인 콘텐츠 컨테이너 및 섹션의 패딩 제거 */
            .st-emotion-cache-z5fcl4,
            .main .block-container,
            section[data-testid="stSidebar"],
            section[data-testid="stSidebarContent"],
            .stVerticalBlock,
            .st-emotion-cache-mncm6h,
            .stElementContainer,
            .st-emotion-cache-kj6hex,
            .st-emotion-cache-8atqhb {{
                padding-top: 0rem !important;
                padding-bottom: 0rem !important;
                margin-top: 0rem !important;
                margin-bottom: 0rem !important;
                min-height: unset !important;
                height: auto !important;
                gap: 0 !important;
            }}

            /* st.columns 컨테이너 자체의 간격 제거 */
            .st-emotion-cache-1r6y92h,
            .st-emotion-cache-1xw8pjm,
            .st-emotion-cache-1kyx218 {{
                margin: 0 !important;
                padding: 0 !important;
                gap: 0 !important;
                min-height: unset !important;
                height: auto !important;
            }}

            /* 파일 업로더 전체 컨테이너 (stFileUploaderDropzone) */
            [data-testid="stFileUploaderDropzone"] {{
                height: 100% !important;
                width: 100% !important;
                min-height: 50px !important;
                padding: 0 !important;
                margin: 1 !important;
                background-color: white !important;
                border: solid !important;
                cursor: pointer;
            }}

            /* "Browse files" 버튼 - 파일 업로더 내부에만 적용되도록 수정 */
            [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {{
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
            }}

            /* "Browse files" 버튼 내부의 텍스트 숨기기 */
            [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] span {{
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
                background-image: {is_image_uploaded_css} !important;
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

    # 기존 채팅 기록 표시
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "image_bytes" in msg:
                st.image(msg["image_bytes"], width=250)
            st.markdown(msg["content"])
            # AI 메시지 아래에 다운로드 버튼을 동적으로 표시
            if msg["role"] == "assistant" and "generated_plan_data" in msg:
                plan_data = msg["generated_plan_data"]
                plan_type = plan_data.get("plan_type", "계획").lower()
                file_prefix = f"{plan_type}_plan"
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

                try:
                    rows = []
                    for week_data in plan_data["plan_details"]:
                        week_num = week_data["week"]
                        for day_data in week_data["schedule"]:
                            day = day_data["day"]
                            if plan_type == "운동":
                                if "exercises" in day_data and day_data["exercises"]:
                                    for exercise in day_data["exercises"]:
                                        row = {
                                            "주차": f"{week_num}주차",
                                            "요일": day,
                                            "초점": day_data.get("focus", ""),
                                            "운동명": exercise.get("name", ""),
                                            "세트": exercise.get("sets", ""),
                                            "반복": exercise.get("reps", ""),
                                            "시간(분)": exercise.get("duration_min", ""),
                                            "시간(초)": exercise.get("duration_sec", "")
                                        }
                                        rows.append(row)
                                else:
                                    row = {
                                        "주차": f"{week_num}주차",
                                        "요일": day,
                                        "초점": day_data.get("focus", "휴식"),
                                        "운동명": "휴식",
                                        "세트": "", "반복": "", "시간(분)": "", "시간(초)": ""
                                    }
                                    rows.append(row)
                            elif plan_type == "식단":
                                for meal_type, meal_info in day_data["meals"].items():
                                    row = {
                                        "주차": f"{week_num}주차",
                                        "요일": day,
                                        "식사구분": meal_type,
                                        "메뉴": meal_info.get("menu", ""),
                                        "칼로리": meal_info.get("calories", ""),
                                        "조리법": meal_info.get("recipe", "")
                                    }
                                    rows.append(row)

                    if rows:
                        df = pd.DataFrame(rows)
                        excel_file_name = f"{file_prefix}_{current_time}.xlsx"
                        excel_buffer = pd.io.common.BytesIO()
                        df.to_excel(excel_buffer, index=False, engine='xlsxwriter')
                        excel_buffer.seek(0)

                        st.download_button(
                            label=f"⬇️ {plan_type.capitalize()} 계획 Excel 다운로드",
                            data=excel_buffer,
                            file_name=excel_file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_excel_button_{current_time}"  # 고유한 키 생성
                        )
                    else:
                        st.warning("Excel 파일로 변환할 데이터가 없습니다.", icon="⚠️")
                except Exception as e:
                    st.error(f"Excel 파일 생성 중 오류가 발생했습니다: {e}", icon="🚨")

    # --- 사용자 입력(채팅창) 처리 ---
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
        with st.spinner("AI가 분석하고 있어요... 🤖"):
            ai_response = ""
            generated_plan_data = None  # 초기화

            # '운동 루틴' 또는 '식단 계획' 요청 감지
            is_plan_request = False
            plan_type_requested = None
            duration_weeks = 4  # 기본값: 4주 (조절 가능)

            if "운동 루틴" in prompt or "운동 계획" in prompt or "운동 짜 줘" in prompt or "운동 만들어 줘" in prompt:
                is_plan_request = True
                plan_type_requested = "운동"
            elif "식단 계획" in prompt or "식단 루틴" in prompt or "식단 짜 줘" in prompt or "식단 만들어 줘" in prompt:
                is_plan_request = True
                plan_type_requested = "식단"

            # 숫자 추출하여 주차 설정 (예: "3주 운동 루틴" -> 3주)
            import re
            match = re.search(r'(\d+)\s*주', prompt)
            if match:
                requested_weeks = int(match.group(1))
                if 1 <= requested_weeks <= 4:
                    duration_weeks = requested_weeks
                else:
                    ai_response += "최대 4주까지만 계획을 생성할 수 있습니다. 4주로 조정하여 진행합니다. "

            if is_plan_request:
                if not st.session_state.user_info.get("height") or not st.session_state.user_info.get(
                        "weight") or not st.session_state.user_info.get("age"):
                    ai_response = "운동/식단 계획 생성을 위해 **사이드바**에서 **키, 몸무게, 나이**를 먼저 입력하고 **'개인 정보 저장'** 버튼을 눌러주세요."
                else:
                    plan_prompt = get_plan_prompt(plan_type_requested, duration_weeks, prompt)
                    try:
                        raw_ai_response = get_ai_response(
                            user_prompt=plan_prompt,
                            user_info=st.session_state.user_info,
                            model_name=GPT_MODEL
                        )

                        if "```json" in raw_ai_response:
                            json_str = raw_ai_response.split("```json")[1].split("```")[0].strip()
                        else:
                            json_str = raw_ai_response.strip()

                        generated_plan_data = json.loads(json_str)

                        ai_response += f"네, 요청하신 {duration_weeks}주간의 {plan_type_requested} 계획을 생성했습니다. 아래 다운로드 버튼을 이용해 파일을 받아보세요!"
                        # 생성된 계획 데이터를 AI 메시지에 첨부
                        # 이렇게 하면 AI 메시지가 표시될 때 다운로드 버튼도 함께 렌더링됩니다.
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": ai_response,
                            "generated_plan_data": generated_plan_data
                        })
                        # 현재 프롬프트 처리 루틴을 중단하고 rerunning
                        if "image_bytes" in user_message:
                            st.session_state.uploaded_image_bytes = None
                            st.session_state.file_uploader_key_sidebar_counter += 1
                        st.rerun()  # 중요: 이전에 다운로드 버튼을 누르지 않은 경우 즉시 업데이트

                    except json.JSONDecodeError as e:
                        ai_response = f"죄송합니다, 계획 생성에 실패했습니다. AI 응답이 올바른 JSON 형식이 아닙니다. (오류: {e})"
                    except Exception as e:
                        ai_response = f"죄송합니다, 계획 생성 중 오류가 발생했습니다: {e}"
            else:
                # 일반 채팅 응답
                if "image_bytes" in user_message:
                    image_b64 = base64.b64encode(user_message["image_bytes"]).decode('utf-8')
                    ai_response = get_ai_response(
                        user_prompt=prompt,
                        image_bytes=image_b64,
                        user_info=st.session_state.user_info,
                        model_name=GPT_MODEL
                    )
                else:
                    ai_response = get_ai_response(
                        user_prompt=prompt,
                        user_info=st.session_state.user_info
                    )

            # AI 응답을 화면에 표시 (이미 계획 요청이 처리되어 rerunning되었다면 이 부분은 스킵될 수 있음)
            # 하지만, 오류 메시지나 일반 응답의 경우 필요
            with st.chat_message("assistant"):
                st.markdown(ai_response)

            # 생성된 계획 데이터가 있다면 메시지에 추가
            # 이전에 rerunning 된 경우에는 이미 추가되었을 수 있으므로 중복 방지
            if not is_plan_request or generated_plan_data is None:  # 일반 응답이거나 계획 생성 실패시만 추가
                new_assistant_message = {"role": "assistant", "content": ai_response}
                if generated_plan_data:  # 계획이 성공적으로 생성되었지만, rerunning 없이 여기로 온 경우 (드물겠지만)
                    new_assistant_message["generated_plan_data"] = generated_plan_data
                st.session_state.messages.append(new_assistant_message)

            # 이미지가 사용되었을 경우에만 초기화 및 rerunning
            if "image_bytes" in user_message and not is_plan_request:  # 계획 요청이 아닐 때만 rerunning
                st.session_state.uploaded_image_bytes = None
                st.session_state.file_uploader_key_sidebar_counter += 1
                st.rerun()