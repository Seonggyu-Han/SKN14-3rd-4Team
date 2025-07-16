import openai
import json


# 이 함수는 예시입니다. 실제 LLM API 호출 및 응답 처리에 맞게 구현해야 합니다.
def get_ai_response(user_prompt, image_bytes=None, user_info=None, model_name="gpt-4.1-nano"):
    messages = []

    # 사용자 정보 추가
    user_info_str = f"사용자 정보: 키 {user_info.get('height')}cm, 몸무게 {user_info.get('weight')}kg, 나이 {user_info.get('age')}세, 성별 {user_info.get('gender')}."
    messages.append({"role": "system", "content": user_info_str})

    # 이미지 처리 (Vision 모델 사용 시)
    if image_bytes:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_bytes}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": user_prompt})

    try:
        # LLM 응답 요청
        # 여기서 중요한 것은 LLM이 JSON 형식으로 응답하도록 프롬프트를 잘 구성하는 것입니다.
        # 예를 들어, user_prompt에 JSON 포맷 요청 내용이 포함되도록 get_plan_prompt에서 전달합니다.

        # 예시: 특정 키워드가 있으면 JSON 형식으로 응답하도록 지시
        # get_plan_prompt에서 이미 JSON 형식 요청을 포함하고 있으므로,
        # 여기서는 response_format을 사용하여 LLM이 JSON을 반환하도록 강제합니다.

        response = openai.chat.completions.create(
            model=model_name,
            messages=messages,
            # LLM이 JSON 객체를 반환하도록 강제합니다.
            # 이 기능은 모델에 따라 지원 여부가 다를 수 있습니다.
            # GPT-4o-mini와 같은 최신 모델은 'response_format={"type": "json_object"}'를 지원합니다.
            response_format={"type": "json_object"} if "JSON 형식으로" in user_prompt else None
        )
        return response.choices[0].message.content

    except openai.OpenAIError as e:
        return f"OpenAI API 오류가 발생했습니다: {e}"
    except Exception as e:
        return f"AI 응답 생성 중 오류가 발생했습니다: {e}"