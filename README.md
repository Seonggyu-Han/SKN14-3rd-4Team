# SKN14-3rd-4Team

# 4팀: 다이어트를 위한 식단 관리 및 운동 추천 챗봇

## 1. 팀 소개
- **팀명**: GYM-PT
- **팀원**: 공지환, 김진묵, 송지훈, 이승철, 조성렬, 한성규

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/0jihwan">
        <img src="https://github.com/0jihwan.png" width="80"/><br />
        <sub><b>공지환</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/jinmukkim">
        <img src="https://github.com/jinmukkim.png" width="80"/><br />
        <sub><b>김진묵</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/teolex">
        <img src="https://github.com/teolex.png" width="80"/><br />
        <sub><b>송지훈</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/ezcome-ezgo">
        <img src="https://github.com/ezcome-ezgo.png" width="80"/><br />
        <sub><b>이승철</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/csr1968">
        <img src="https://github.com/csr1968.png" width="80"/><br />
        <sub><b>조성렬</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Seonggyu-Han">
        <img src="https://github.com/Seonggyu-Han.png" width="80"/><br />
        <sub><b>한성규</b></sub>
      </a>
    </td>
  </tr>
</table>


## 2. 프로젝트 개요

### 프로젝트 소개
**‘다이어트를 위한 식단 관리 및 운동 추천 챗봇[GYM-PT]’은 인공지능 기반으로, 바쁜 현대인도 효율적으로 올바른 식단과 운동 습관을 관리할 수 있도록 설계된 통합 헬스케어 솔루션입니다.**

이 시스템은 음식 사진 또는 간단한 텍스트 입력만으로 칼로리, 영양 성분, 재료 정보를 자동 제공하며, 공식 데이터베이스와 연동해 신뢰성 있는 정보를 빠르게 제공합니다. 대화형 챗봇은 사용자별 목표와 상황에 맞는 운동 루틴을 안내하여 시간과 비용 부담을 줄이고 누구나 지속가능한 건강관리를 실천할 수 있도록 지원합니다.

본 프로젝트는 복잡한 건강관리 과정을 간소화하고, 사용자 중심의 맞춤형 데이터 기반 안내를 통해 실생활에서 자기관리와 삶의 질 향상에 기여하는 것을 목표로 합니다.


### 개발 배경 및 필요성

<img width="2580" height="1030" alt="Section 1" src="https://github.com/user-attachments/assets/c4e20a6e-3771-4b24-9043-efc35c39ac3c" />

빠르게 변화하는 라이프스타일, 도시화, 바쁜 일정, 정보 접근성 한계 등으로 건강 습관 유지가 점점 더 어려워지고 있습니다. 많은 사람들이 시간·비용의 제약, 부정확한 건강 정보, 운동시설 부족, 동기 저하 등으로 식단 관리와 규칙적 운동 실천이 어렵습니다.

그 결과 운동 부족과 영양 불균형 문제가 심각해지고 만성질환과 사회적 부담도 커지고 있습니다. 누구나 쉽게 접근 가능한 신뢰 있는 정보와, 개인 환경과 목표에 맞춘 건강 관리가 필요합니다.

**[GYM-PT]는**
- 바쁜 일상과 시간·비용의 제약 속에서도 **간편하게 식단 정보와 운동 추천**을 제공하며,
- **지속 가능한 건강관리 습관** 형성,  
- **만성 건강 문제 예방과 삶의 질 향상**에 실질적으로 기여하고자 개발됐습니다.

---

## 3. 기술 스택 및 모델

| **Frontend** | **Backend** | **LLM Model** | **Vector DB** | **Collaboration Tool** |
|:---:|:---:|:---:|:---:|:---:|
| <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/> | <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/> <br> <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white"/> | <img src="https://img.shields.io/badge/OpenAI-GPT4o-10a37f?style=for-the-badge&logo=openai&logoColor=white"/> <br> <img src="https://img.shields.io/badge/OpenAI-GPT--4.1-10a37f?style=for-the-badge&logo=openai&logoColor=white"/> | <img src="https://img.shields.io/badge/Pinecone-27AE60?style=for-the-badge&logo=pinecone&logoColor=white"/> | <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"/> <br> <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/> <br> <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white"/> <br> <img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white"/> |




<br><br>

---

## 4. 주요 기능

1. **메인 페이지 사용 안내**
    - 프로젝트 사용법, 개인정보 입력, 챗봇 활용, AI 분석 절차 등 직관적 안내

2. **개인정보 입력(사이드바)**
    - 키, 몸무게, 성별, 나이 입력
    - 입력값 기반 맞춤형 추천

3. **챗봇 프롬프팅 및 상호작용**
    - 텍스트 또는 이미지 기반 자유로운 질의
    - 건강, 식단, 운동 Q&A
    - 음식 이미지 업로드 시 AI가 질문·이미지 모두 분석하여 답변

4. **AI 기반 식단·운동 추천 및 정보 제공**
    - 입력 정보를 종합 분석해 맞춤형 식단관리, 운동 루틴, 음식정보(칼로리, 영양, 재료), 생활습관 등 다양한 답변

5. **맞춤형 문서 생성 및 편의성**
    - 사용자 정보 바탕 식단·운동 플랜 문서 제공
    - 사용성 높은 인터페이스

---

## 5. 전체 워크 플로우
```mermaid
flowchart LR
    subgraph UI["Streamlit 화면"]
        A("사용자 업로드\n• 이미지(여러 장)\n• 텍스트")
    end

    %% 1) 입력 타입 분기
    A --> B{입력 타입?}

    %% ───────── 이미지 경로 ─────────
    B -- 이미지 --> C("GPT-4.1\nmenu_name · ingredients 추출"):::step
    C --> D("Pinecone Vector DB\n유사 메뉴 검색"):::step
    D -->|Top-k| E{최고 유사도 ≥ 0.4}:::decision

    E -- 예 --> F("build_context()\nDB 메타에서 메뉴이름, 칼로리 확보"):::step
    E -- 아니오 --> G("ask_LLM_calorie()\nGPT로 칼로리 추론"):::step
    F --> H
    G --> H

    %% ───────── 텍스트 경로 ─────────
    B -- 텍스트 --> I("사용자 텍스트\n(키·몸무게·나이·성별)"):::step
    I --> H

    %% 2) 프롬프팅 & LLM 응답
    H("Prompt 조립\nrag_context · text · menu_name · calorie"):::step --> J("ChatOpenAI (GPT-4.1)\n식단·운동 추천"):::llm

    %% 3) 결과 표시
    J --> K("Streamlit 결과 카드\n칼로리·운동·식단 제안"):::ui

    %% 반복 처리 (여러 이미지)
    K -->|다음 이미지| B

    %% 스타일
    classDef step     fill:#E8F1FF,stroke:#0C66FF,stroke-width:1px,color:#003366;
    classDef decision fill:#FFFBCC,stroke:#D6B400,stroke-width:1px,color:#5C4A00;
    classDef llm      fill:#E5FFEA,stroke:#00B33C,stroke-width:1px,color:#005C1E;
    classDef ui       fill:#FFFFFF,stroke:#666,stroke-width:1px,color:#000;
```

## 시스템 구현 단계 및 핵심 흐름

### 1. 주요 구현 단계

| 단계                  | 내용 요약                                                                                      |
|----------------------|--------------------------------------------------------------------------------------------|
| 데이터 수집 및 전처리   | 외부 공개 식품DB(식품의약안전처 공공데이터 조리식품 레시피DB)에서 음식 정보, 레시피 데이터 수집<br>https://www.foodsafetykorea.go.kr/api/openApiInfo.do?menu_grp=MENU_GRP31&menu_no=661&show_cnt=10&start_idx=1&svc_no=COOKRCP01 |
| 임베딩 및 벡터DB 구축  | 음식명·재료 기반 텍스트와 이미지에서 추출한 특징을 임베딩 후 Pinecone 벡터DB에 저장                       |
| 입력 타입 분기         | 업로드 데이터가 이미지(음식 사진)인지 텍스트(개인정보)인지 판별 후 경로 분기                              |
| AI 정보 추출 및 유사도 검색 | 이미지 입력 시 GPT-4.1/CLIP 등으로 음식명·재료 추출 → Pinecone에서 유사 메뉴 **Top-5**(k=5, 유사도 ≥ 0.4) 검색 |
| 칼로리 정보 확보       | DB에서 찾으면 build_context()로 메뉴명·칼로리 확보, 없으면 ask_LLM_calorie()로 GPT 예측값 획득             |
| 프롬프트 조립 및 추천  | DB·예측 값·사용자 정보 등으로 프롬프트 생성, GPT-4.1/4o로 식단·운동 추천                                 |
| 결과 출력 및 반복      | Streamlit 결과 카드로 정보 시각화, 이미지 여러 장 입력 시 위 과정을 반복 처리                                |

### 2. 시스템 워크플로우 요약

1. **입력**  
   - 사용자는 Streamlit에서 이미지(여러 장)와 텍스트(키·몸무게·나이·성별 등)를 입력

2. **입력 타입 자동 분기**  
   - 이미지는 GPT-4.1/CLIP 등으로 음식명·재료 추출  
   - Pinecone 벡터DB에서 **Top-5(최대 k=5, 유사도 0.4 이상)** 유사 메뉴 검색  
   - 텍스트는 사용자 정보로 직접 활용

3. **칼로리 및 컨텍스트 확보**  
   - DB 결과 있으면 메타정보 바로 활용  
   - 없을 경우 GPT로 칼로리 추론

4. **프롬프트 조합 및 모델 응답**  
   - DB/예측값, 사용자 정보 등으로 프롬프트 조립  
   - ChatOpenAI GPT-4.1/4o에 전달하여 식단·운동 포함 맞춤 추천 생성

5. **결과 시각화 및 반복 처리**  
   - Streamlit 결과 카드에 칼로리, 운동, 식단 결과 제공  
   - 입력 이미지가 2개 이상이면 첫 단계로 돌아가 반복 처리

### 3. 시스템 산출물

- **수집된 원본 데이터와 전처리 산출물**
- **Pinecone 벡터DB 기반 아키텍처 다이어그램**
- **전체 파이프라인/RAG·LLM 연동 코드 및 파라미터(Top-k, 유사도)**
- **테스트 및 품질 개선 리포트(질문별 정답률, 환각 모니터링 등)**

> **참고:**  
> 상기 이미지 워크플로우 및 설명은  
> k=5(Top-5)에 유사도 0.4 이상만 근거로 채택해  
> GPT 환각을 최소화하고, 실제 입력-추론-추천-결과 시각화의  
> 실질적 데이터 흐름 전반을 일관되게 반영합니다.

---

## 6. 시연 영상
(작성 예정)

---

## 7. 추후 발전 계획

### 맞춤형 서비스 고도화
- 운동·식단 추천 알고리즘 개선(연령/목표/신체 조건/알레르기 등 반영)
- 개별 체성분 및 목표 변화 추적, 간편한 식단·운동·신체변화 기록

### 사용자 경험 및 플랫폼 확장
- 모바일 및 앱 통합, Push 알림
- 스마트워치·웨어러블 기기 연동
- 다국어 지원(영어·일어 등 다양한 음식문화 고려)

### 인공지능·정보 신뢰성 강화
- 이미지·텍스트 멀티모달 분석 고도화
- 실시간 DB/외부 자료(RAG) 자동 업데이트
- 음성 챗봇, 운동 영상 등 접근성 강화
- 칼로리뿐만 아니라 영양성분(탄단지, 나트륨, 기타 미량영양소 등)까지 상세 분석 기능 확장

### 피드백을 통한 문제 개선

- 사용자의 서비스 이용 경험, 불편사항, 개선 요청 등 다양한 피드백 수집 및 분석

---

