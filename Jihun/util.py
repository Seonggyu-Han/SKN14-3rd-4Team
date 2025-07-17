import ast
from typing import List, Tuple, Dict, Any
import openai

import streamlit as st
from langchain_openai import ChatOpenAI


def session_initiate():
    # 세션 상태 초기화
    if 'page'         not in st.session_state:    st.session_state.page = 'main'
    if 'chat_history' not in st.session_state:    st.session_state.chat_history = []
    if 'user_info'    not in st.session_state:    st.session_state.user_info = {}

def print_session_state():
    for key in st.session_state:
        print("%-20s :: %s" % (key, st.session_state[key]))

# 유틸리티 함수들
def parse_prediction(pred_str: str) -> Tuple[str, str]:
    try:
        parsed = ast.literal_eval(pred_str)
        menu_name, ingredients = parsed[0]
        return menu_name.strip(), ingredients.strip()
    except:
        return pred_str, ""

# --- 3. Pinecone 검색 ---
def search_menu(vector_store, menu_name: str, k: int = 3) -> List[Tuple]:
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
        vector_store,
        menu_name: str,
        k: int = 1,
        threshold: float = 0.4
) -> Tuple[str, str]:
    matches = search_menu(vector_store, menu_name, k)

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

    # print("음식 정보 컨텍스트", "-"*40, context, sep="\n", end="\n")

    return context, calorie


def analyze_meal_with_llm(menu_name, calorie, user_info, rag_context="", chat_history=None) -> str:
    prompt_tmpl = """
[벡터DB 검색 결과]
{rag_context}

아래는 지금까지의 대화 내역입니다.
{history_prompt}

---
사용자의 새로운 입력과 음식 정보를 기반으로, 이전 대화 맥락도 반영해 맞춤형 답변을 해주세요.

메뉴명: {menu_name}
칼로리: {calorie}kcal
사용자 정보: {user_info}

[답변 형식]
- 드신 메뉴와 칼로리 정보
- 1일 권장 섭취량 계산
- 해당 칼로리를 소모할 수 있는 운동 추천
- 남은 칼로리에 맞는 식단 추천

친근하고 전문적인 톤으로 답변해주세요.
"""
    try:
        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.3)
        history_prompt = ""
        if chat_history:
            # 최근 5턴 context만
            for role, content, images in chat_history[-5:]:
                who = "사용자" if role == "user" else "GYM-PT"
                history_prompt += f"{who}: {content}\n"

        prompt = prompt_tmpl.format(rag_context=rag_context, history_prompt=history_prompt, menu_name=menu_name, calorie=calorie, user_info=user_info)
        result = llm.invoke(prompt)

        # print("최종 결과 답변", "-"*40, result.content, sep="\n", end="\n")

        return result.content
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {str(e)}"