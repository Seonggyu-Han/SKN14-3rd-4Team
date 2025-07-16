# chatbot.py

import openai
import base64
import ast
import threading
from io import BytesIO
from typing import List, Tuple, Dict, Any
from PIL import Image
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# GPT 모델 상수는 여기서도 정의 (main.py와 동기화)
GPT_MODEL = "gpt-4o-mini"


# --- Inferer 클래스 정의 ---
class Inferer:
    def image_to_base64(self, image: Image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()

    @classmethod
    def to_pil_image(cls, uploaded_file):
        """UploadedFile 객체를 PIL Image로 변환합니다."""
        return Image.open(uploaded_file).convert('RGB')


class OpenAIInferer(Inferer):
    def __init__(self, model_id=GPT_MODEL, temperature=0.0):
        self.model_id = model_id
        self.temperature = temperature
        self.llm = ChatOpenAI(model=model_id, temperature=temperature, api_key=openai.api_key)
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


# --- 유틸리티 함수들 ---
def parse_prediction(pred_str: str) -> Tuple[str, str]:
    try:
        parsed = ast.literal_eval(pred_str)
        if isinstance(parsed, list) and parsed:
            menu_name, ingredients = parsed[0]
            return menu_name.strip(), ingredients.strip()
        else:
            return pred_str, ""
    except (ValueError, SyntaxError):
        return pred_str, ""


def ask_llm_calorie(menu_name: str) -> str:
    try:
        prompt = f"다음 음식의 대표적인 1인분 칼로리(kcal) 숫자만 알려주세요 **반드시 숫자만 반환!!**: '{menu_name}'"
        resp = openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"칼로리 정보 로딩 중 오류 발생: {e}")
        return "250"


def get_ai_response(user_prompt: str, image_bytes: bytes = None, user_info: dict = None,
                    model_name: str = GPT_MODEL) -> str:
    """
    사용자 정보, 질문, 이미지(선택 사항)를 받아 AI 응답을 생성합니다.
    """
    user_data_for_ai = ""
    if user_info:
        height = user_info.get("height")
        weight = user_info.get("weight")
        age = user_info.get("age")
        gender = user_info.get("gender")

        if height is not None:
            user_data_for_ai += f"키: {height}cm, "
        if weight is not None:
            user_data_for_ai += f"몸무게: {weight}kg, "
        if age is not None:
            user_data_for_ai += f"나이: {age}세, "
        if gender != "미선택":
            user_data_for_ai += f"성별: {gender}, "

        if user_data_for_ai:
            user_data_for_ai = "사용자의 정보: " + user_data_for_ai.rstrip(', ') + ". 이 정보를 참고하여 답변해주세요."
        else:
            user_data_for_ai = "사용자 정보가 제공되지 않았습니다."
    else:
        user_data_for_ai = "사용자 정보가 제공되지 않았습니다."

    messages = [
        {
            "role": "system",
            "content": "당신은 사용자의 다이어트 및 영양 관리를 돕는 친절한 AI 트레이너입니다. 제공된 사용자 정보를 바탕으로 맞춤형 조언을 해주세요."
        },
        {
            "role": "user",
            "content": []
        }
    ]

    messages[1]["content"].append({"type": "text", "text": f"{user_data_for_ai}\n\n{user_prompt}"})

    if image_bytes is not None:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_bytes.decode('utf-8')}",
            },
        })

    try:
        response = openai.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        print(f"OpenAI API 오류 발생: {e}")
        return "죄송합니다, AI 서비스에 문제가 발생했습니다. 다시 시도해주세요."
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return "죄송합니다, 요청을 처리하는 중 알 수 없는 오류가 발생했습니다."


def analyze_meal_with_llm(menu_name: str, calorie: str, user_text: str,
                          chat_history: List[Tuple[str, str, Any]] = None) -> str:
    """
    GPT-4o-mini를 사용하여 식단 분석 및 추천을 수행합니다.
    """
    try:
        llm = ChatOpenAI(model=GPT_MODEL, temperature=0.3, api_key=openai.api_key)
        history_prompt = ""
        if chat_history:
            for role, content, _ in chat_history[-5:]:
                who = "사용자" if role == "user" else "GYM-PT"
                history_prompt += f"{who}: {content}\n"

        prompt_template = f"""
아래는 지금까지의 대화 내역입니다.
{history_prompt}

---
사용자의 새로운 입력과 음식 정보를 기반으로, 이전 대화 맥락도 반영해 맞춤형 답변을 해주세요.

메뉴명: {menu_name}
칼로리: {calorie}kcal
사용자 정보: {user_text}

[답변 형식]
- 드신 메뉴와 칼로리 정보
- 1일 권장 섭취량 계산 (사용자 정보가 있을 경우)
- 해당 칼로리를 소모할 수 있는 운동 추천
- 남은 칼로리에 맞는 식단 추천

친근하고 전문적인 톤으로 답변해주세요.
"""
        messages = [
            SystemMessage(content="당신은 사용자의 다이어트 및 영양 관리를 돕는 친절하고 전문적인 AI 트레이너입니다."),
            HumanMessage(content=prompt_template)
        ]

        result = llm.invoke(messages)
        return result.content
    except Exception as e:
        print(f"분석 중 오류가 발생했습니다: {str(e)}")
        return f"분석 중 오류가 발생했습니다: {str(e)}"