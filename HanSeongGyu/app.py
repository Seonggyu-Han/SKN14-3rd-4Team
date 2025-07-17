import streamlit as st
import base64
import os
import ast
import threading
from io import BytesIO
from typing import List, Tuple, Dict, Any
import openai
from PIL import Image
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
import dotenv

dotenv.load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="GYM-PT - 당신만의 트레이너",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 입력값 세션 상태 초기화 ---
if 'user_text' not in st.session_state:
    st.session_state.user_text = ''
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None

# CSS 스타일링
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

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

# Inferer 클래스 정의
class Inferer:
    def image_to_base64(self, image: Image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()

    @classmethod
    def to_pil_image(cls, uploaded_file):
        return Image.open(uploaded_file).convert('RGB')


class OpenAIInferer(Inferer):
    def __init__(self, model_id="gpt-4o-mini", temperature=0.0, api_key=None):
        self.model_id = model_id
        self.temperature = temperature
        api_key = api_key if api_key else os.environ.get("OPENAI_API_KEY")
        self.llm = ChatOpenAI(model=model_id, temperature=temperature, api_key=api_key)
        self.system_msg = SystemMessage("""
당신은 전 세계 음식들을 모두 다 알고 있는 음식전문가입니다.

당신은 사용자가 제시한 음식 이미지의 정확한 음식명을 반환해야 합니다.
- 답변은 반드시 단답형의 음식명과 그 음식에 들어간 재료 목록을 반환해야 합니다.
- 음식명과 재료목록은 ("음식명", "재료목록") 의 형태로 답변해야 합니다.
- 음식명과 재료목록은 반드시 한글이어야 합니다.
- 답변은 [("음식명", "재료목록")] 과 같이 배열로 감싼 형태여야 합니다.
- 이미지에 음식의 개수가 여러가지라면, 최대 5개의 음식을 배열로 감싸서 반환합니다.

< 답변 예시 >
[("짜장면", "춘장, 돼지고기, 양파, 면, 카라멜")]
[("햄버거", "패티, 번, 양상추, 양파, 머스타드소스, 치즈, 피클"), ("베이컨 연어 셀러드", "베이컨, 훈제연어, 양상추, 토마토")]
""")

    def infer(self, image: Image, filename: str, storage: dict, parser=StrOutputParser()):
        b64_image = self.image_to_base64(image)
        user_msg = HumanMessage([{'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64_image}'}}])
        prompt = ChatPromptTemplate.from_messages([self.system_msg, user_msg])
        chain = prompt | self.llm | parser
        storage[filename] = chain.invoke({})

    def __call__(self, images: List[Image], filenames: List[str], parser=StrOutputParser()):
        storage = {}
        tmp_zip = zip(images, filenames)
        threads = [threading.Thread(target=self.infer, args=(img, nm, storage, parser)) for img, nm in tmp_zip]
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        return storage

# 유틸리티 함수들


PINECONE_PJ_KEY = os.environ.get("PINECONE_PJ_KEY")
INDEX_NAME = "food-index"
EMBED_MODEL = "text-embedding-3-small"
pc = Pinecone(api_key=PINECONE_PJ_KEY)
index = pc.Index(INDEX_NAME)
embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
vector_store = PineconeVectorStore(index=index, embedding=embeddings)


def parse_prediction(pred_str: str) -> Tuple[str, str]:
    try:
        parsed = ast.literal_eval(pred_str)
        menu_name, ingredients = parsed[0]
        return menu_name.strip(), ingredients.strip()
    except:
        return pred_str, ""

# --- 3. Pinecone 검색 ---
def search_menu(menu_name: str, k: int = 3) -> List[Tuple]:
    return vector_store.similarity_search_with_score(query=menu_name, k=k)

# --- 4. Pinecone 결과 → 컨텍스트 형식 변환 ---
def build_context(matches: List[Tuple]) -> str:
    lines = []
    for doc, score in matches:
        meta = doc.metadata or {}
        name = meta.get("RCP_NM", "알 수 없는 메뉴")
        kcal = meta.get("INFO_ENG", "칼로리 정보 없음")
        lines.append(f"- 메뉴명: {name}, 칼로리: {kcal} (유사도: {score:.2f})")
    return "\n".join(lines)


def ask_llm_calorie(menu_name: str) -> str:
    try:
        prompt = f"다음 음식의 대표적인 1인분 칼로리(kcal) 숫자만 알려주세요 **반드시 숫자만 반환!!**: '{menu_name}'"
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return resp.choices[0].message.content.strip()
    except:
        return "250"  # 기본값


# --- 6. 메뉴명 기반 컨텍스트 생성 + 칼로리 반환 개선 버전 ---
def get_menu_context_with_threshold(
    menu_name: str,
    k: int = 1,
    threshold: float = 0.4
) -> Tuple[str, str]:
    matches = search_menu(menu_name, k)
    
    if not matches or matches[0][1] < threshold:
        # 유사도 낮을 경우 LLM으로 fallback
        calorie = ask_llm_calorie(menu_name)
        context = f"- 메뉴명: {menu_name}, 칼로리: {calorie}"
        return context, calorie

    # 유사한 문서가 충분함 → 문서에서 kcal 추출
    context = build_context(matches)
    # 가장 첫 번째 문서 정보 사용
    doc, _ = matches[0]
    calorie = doc.metadata.get("INFO_ENG")

    # 칼로리 정보가 누락되어 있을 경우 fallback
    if not calorie or not str(calorie).isdigit():
        calorie = ask_llm_calorie(menu_name)

    return context, calorie

def analyze_meal_with_llm(menu_infos, user_info, rag_context=None, chat_history=None) -> str:
    try:
        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.3)
        history_prompt = ""
        if chat_history:
            for i, (role, content, images) in enumerate(chat_history[-5:]):
                who = "사용자" if role == "user" else "GYM-PT"
                history_prompt += f"{who}: {content}\n"

        # 여러 음식 정보 표와 요약 만들기
        table = "| No | 파일명 | 음식명 | 칼로리 |\n|---|---|---|---|\n"
        foods_context = ""
        total_calorie = 0
        for i, info in enumerate(menu_infos):
            menu = info.get("menu_name", "")
            kcal = info.get("calorie", "")
            filename = info.get("filename", "")
            table += f"| {i+1} | {filename} | {menu} | {kcal} |\n"
            foods_context += f"{i+1}. {filename}: {menu} ({kcal}kcal)\n"
            try:
                total_calorie += int(float(kcal))
            except:
                pass

        prompt = f"""
[오늘 섭취한 음식 정보]
{foods_context}
{table}
총 섭취 칼로리: {total_calorie}kcal

아래는 지금까지의 대화 내역입니다.
{history_prompt}

사용자 정보: {user_info}

[답변 지침]
- 먹은 음식(여러 개면 모두)(이미지로 받은 음식과, 텍스트로 받은 정보의 음식 모두)과 각각의 칼로리 정보를 표로 보여줄 것
- 모든 음식의 총 섭취 칼로리를 계산해서 보여줄 것
- 1일 권장 섭취량과 남은 칼로리 계산
- 사용자가 섭취한 칼로리를 소모할 수 있는 운동 추천 (추천 운동의 칼로리 합 = 총 섭취 칼로리)
- 남은 칼로리에 맞는 식단 추천
- 모든 답변은 한 번에, 보기 좋게 작성할 것
"""
        result = llm.invoke(prompt)
        return result.content
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {str(e)}"



# 메인 페이지
def main_page():
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

# 멀티턴 챗봇: chat_history를 LLM context로 넣어줌!
def chat_page():
    st.markdown('<h2 style="text-align: center; color: #2E7D32; margin-bottom: 2rem;">💬 GYM-PT와 대화하기</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("← 메인으로"):
            st.session_state.page = 'main'
            st.rerun()
    chat_container = st.container()
    with chat_container:
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

    st.markdown("---")
    st.markdown("### 📝 새로운 메시지")
    uploaded_files = st.file_uploader(
        "음식 사진을 업로드해주세요 (최대 5개)",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        key="uploaded_files",
        help="섭취한 음식의 사진을 올려주세요. 최대 5개까지 업로드 가능합니다.\n 더 정확한 결과를 위해 한 사진에는 한 가지 음식만 담아 업로드해 주세요."
    )
    if uploaded_files and len(uploaded_files) > 5:
        st.error("최대 5개의 이미지만 업로드 가능합니다.")
        uploaded_files = uploaded_files[:5]
    user_text = st.text_area(
        "신체 정보와 음식에 대한 추가 정보를 입력해주세요",
        placeholder="예: 나이 25세, 남성, 키 175cm, 몸무게 70kg, 평소 운동량 중간, 아침에 삶은 계란 2개 먹음....",
        height=100,
        key="user_text" 
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
                        menu_infos = []

                        # 이미지 업로드한 경우
                        if uploaded_files:
                            for uploaded_file in uploaded_files:
                                img = Image.open(uploaded_file)
                                user_images.append(img)
                            st.session_state.chat_history.append(("user", user_text, user_images))

                            os.environ.setdefault("OPENAI_API_KEY", "your-api-key-here")
                            inferer = OpenAIInferer("gpt-4o-mini", 0.0)
                            images = [Inferer.to_pil_image(f) for f in uploaded_files]
                            filenames = [f.name for f in uploaded_files]
                            results = inferer(images, filenames)

                            for filename, pred_str in results.items():
                                menu_name, ingredients = parse_prediction(pred_str)
                                rag_context, calorie = get_menu_context_with_threshold(menu_name)
                                menu_infos.append({
                                    "filename": filename,
                                    "menu_name": menu_name,
                                    "calorie": calorie,
                                    "ingredients": ingredients,
                                    "rag_context": rag_context
                                })

                        # 텍스트만 입력한 경우 (이미지 업로드 없을 때만 추가)
                        if not uploaded_files and user_text.strip():
                            menu_infos.append({
                                "filename": "-",
                                "menu_name": user_text,
                                "calorie": "",
                                "ingredients": "",
                                "rag_context": ""
                            })

                        # 최종 분석 (이미지, 텍스트 모두 menu_infos에 들어감)
                        final_response = analyze_meal_with_llm(
                            menu_infos=menu_infos,
                            user_info=user_text,
                            chat_history=st.session_state.chat_history
                        )
                        st.session_state.chat_history.append(("assistant", final_response, None))
                        st.rerun()

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

                    ---
                    ⚠️ **에러 로그:**  
                    {str(e)}
                    """
                        st.session_state.chat_history.append(("assistant", final_response, None))
                        st.rerun()
# 메인 앱 실행
def main():
    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'chat':
        chat_page()

if __name__ == "__main__":
    main()
