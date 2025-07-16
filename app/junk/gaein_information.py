# prompt.py (혹은 현재 스크립트 파일)
import openai



def get_ai_response(user_prompt: str, image_bytes: bytes = None, user_info: dict = None,
                    model_name: str = "gpt-4.1-nano") -> str:
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
                "url": f"data:image/jpeg;base64,{image_bytes.decode('utf-8')}",
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
