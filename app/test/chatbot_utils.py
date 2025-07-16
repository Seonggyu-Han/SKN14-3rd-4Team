import openai
from PIL import Image
from io import BytesIO
from typing import List, Tuple, Dict, Any

# Assuming these are from your original apptest.py
# If these are complex, you might need to adjust their imports or definitions
class Inferer:
    def __init__(self, model_id: str, temperature: float):
        self.model_id = model_id
        self.temperature = temperature

    @staticmethod
    def to_pil_image(uploaded_file):
        # Convert BytesIO to PIL Image
        return Image.open(BytesIO(uploaded_file.getvalue()))

    def __call__(self, images: List[Image.Image], filenames: List[str]) -> Dict[str, str]:
        # This is a placeholder for your actual inference logic
        # In a real scenario, this would interact with an ML model
        # to predict menu and ingredients from images.
        results = {}
        for i, img in enumerate(images):
            # Simulate a simple prediction
            # In a real app, this would be a call to a model
            results[filenames[i]] = f"Placeholder menu {i+1} with ingredients."
        return results

class OpenAIInferer(Inferer):
    def __init__(self, model_id: str, temperature: float):
        super().__init__(model_id, temperature)
        # Assuming openai.api_key is set globally in main.py, or passed here

    def __call__(self, images: List[Image.Image], filenames: List[str]) -> Dict[str, str]:
        results = {}
        for i, img_pil in enumerate(images):
            buffered = BytesIO()
            img_pil.save(buffered, format="PNG") # Save as PNG for base64 encoding
            img_byte_arr = buffered.getvalue()
            base64_image = img_byte_arr.decode('utf-8')

            messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant that analyzes food images. Identify the food item and its main ingredients."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What food is this and what are its main ingredients?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]
                }
            ]
            try:
                response = openai.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                    max_tokens=300
                )
                results[filenames[i]] = response.choices[0].message.content
            except Exception as e:
                results[filenames[i]] = f"Error analyzing image {filenames[i]}: {e}"
        return results


def parse_prediction(pred_str: str) -> Tuple[str, str]:
    """
    Parses the prediction string to extract menu name and ingredients.
    This is a placeholder and needs to be adjusted based on the actual LLM output format.
    """
    # Example parsing: "Food: Pizza. Ingredients: Dough, cheese, tomato sauce."
    menu_name = "알 수 없는 메뉴"
    ingredients = "알 수 없는 재료"

    if "Food:" in pred_str:
        parts = pred_str.split("Food:")
        if len(parts) > 1:
            menu_and_ingredients = parts[1].strip()
            if "Ingredients:" in menu_and_ingredients:
                menu_parts = menu_and_ingredients.split("Ingredients:")
                menu_name = menu_parts[0].strip().replace('.', '')
                ingredients = menu_parts[1].strip()
            else:
                menu_name = menu_and_ingredients.strip().replace('.', '')
    return menu_name, ingredients

def ask_llm_calorie(menu_name: str) -> str:
    """
    Asks the LLM for calorie information of a given menu.
    """
    if not menu_name or menu_name == "알 수 없는 메뉴":
        return "칼로리 정보는 알 수 없습니다."

    messages = [
        {"role": "system", "content": "You are an AI assistant that provides calorie information for food items. Respond only with the calorie count and a brief typical serving size, e.g., '350kcal (1인분)'. If you don't know, respond with '알 수 없음'."},
        {"role": "user", "content": f"'{menu_name}'의 칼로리는 얼마인가요?"}
    ]
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini", # Using a general model for calorie lookup
            messages=messages,
            max_tokens=50
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting calorie info: {e}")
        return "칼로리 정보 로드 중 오류 발생."

def analyze_meal_with_llm(menu_name: str, calorie: str, user_text: str, chat_history: List[Tuple[str, str, Any]], user_info: Dict[str, Any]) -> str:
    """
    Analyzes the meal, provides exercise recommendations, and suggests future meals.
    Integrates user information and chat history for better context.
    """
    user_data_str = ""
    if user_info:
        height = user_info.get("height")
        weight = user_info.get("weight")
        age = user_info.get("age")
        gender = user_info.get("gender")

        if height is not None:
            user_data_str += f"키: {height}cm, "
        if weight is not None:
            user_data_str += f"몸무게: {weight}kg, "
        if age is not None:
            user_data_str += f"나이: {age}세, "
        if gender != "미선택":
            user_data_str += f"성별: {gender}, "
        user_data_str = user_data_str.rstrip(', ')
        if user_data_str:
            user_data_str = f"사용자 정보: {user_data_str}. "

    # Build prompt with meal info and user context
    prompt = f"{user_data_str}방금 먹은 음식은 '{menu_name}'이고, 칼로리는 '{calorie}'입니다. {user_text} 이 식사에 대해 분석해주고, 이 칼로리를 소모하기 위한 운동을 추천해주세요. 그리고 남은 끼니에 먹으면 좋을 식단을 추천해주세요."

    # Construct messages with chat history
    messages = [
        {"role": "system", "content": "당신은 사용자의 다이어트 및 영양 관리를 돕는 전문 트레이너 AI입니다. 제공된 음식 정보와 사용자 정보를 바탕으로 식단 분석, 칼로리 소모 운동 추천, 남은 식단 추천을 상세하고 친절하게 해주세요. 칼로리 수치와 운동 시간은 구체적으로 명시하고, 식단 추천은 균형 잡힌 영양소 섭취를 고려하여 예시를 들어 설명해주세요."},
    ]

    for role, content, _ in chat_history:
        # Only include text content from chat_history for LLM context
        if content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": prompt})


    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini", # Using a general model for analysis
            messages=messages,
            max_tokens=1000,
            temperature=0.7 # Allow for some creativity in recommendations
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during meal analysis: {e}")
        return "식단 분석 및 추천 중 오류가 발생했습니다. 다시 시도해주세요."

# This function was originally in chatbot.py but is more general utility
def get_ai_response(user_prompt: str, image_bytes: bytes = None, user_info: dict = None,
                    model_name: str = "gpt-4o-mini") -> str:
    """
    사용자 정보, 질문, 이미지(선택 사항)를 받아 AI 응답을 생성합니다.
    """
    # 1. 사용자 정보를 기반으로 system_prompt 또는 추가 프롬프트 생성
    user_data_for_ai = ""
    if user_info:  # user_info 딕셔너리가 전달되었는지 확인
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

    # 2. OpenAI API에 전달할 messages 리스트 구성
    messages = [
        {
            "role": "system",
            "content": "당신은 사용자의 다이어트 및 영양 관리를 돕는 친절한 AI 챗봇입니다. 제공된 사용자 정보를 바탕으로 맞춤형 조언을 해주세요."
        },
        {
            "role": "user",
            "content": []
        }
    ]

    # 사용자 정보를 user role의 첫 텍스트로 추가 (또는 system role에 추가 가능)
    # 여기서는 user_data_for_ai를 user role의 content에 함께 넣는 방식으로 합니다.
    # user_prompt 앞에 추가 정보를 넣으면 AI가 더 잘 참고할 수 있습니다.
    messages[1]["content"].append({"type": "text", "text": f"{user_data_for_ai}\n\n{user_prompt}"})

    if image_bytes is not None:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_bytes}",
            },
        })

    # 3. OpenAI API 호출
    try:
        response = openai.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        # API 오류는 여기서 처리하거나 호출하는 쪽(streamlit.py)으로 다시 전달
        print(f"OpenAI API 오류 발생: {e}")
        return "죄송합니다, AI 서비스에 문제가 발생했습니다. 다시 시도해주세요."
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return "죄송합니다, 요청을 처리하는 중 알 수 없는 오류가 발생했습니다."