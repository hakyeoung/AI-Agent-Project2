# 보안 체험 랩 (AI Agent Project 2)

LangGraph·ReAct 패턴과 모의 도구를 쓰는 **교육용 보안 시뮬레이션**입니다. USB·의심 다운로드·게임 크랙 유혹 등 시나리오를 **실제 위험 없이** Streamlit UI에서 체험합니다. 상세 스펙은 [`seed.yaml`](seed.yaml)을 참고하세요.

## 로컬 실행

저장소 루트에 `app.py`와 나머지 모듈이 같은 폴더에 있으면 됩니다. 폴더 이름은 자유롭습니다.

```bash
git clone https://github.com/hakyeoung/AI-Agent-Project2.git
cd AI-Agent-Project2
python -m venv .venv
.venv\Scripts\activate   # Windows — macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

다른 프로젝트 안에 **`ouro_p2`라는 하위 폴더**로만 넣어 쓰는 경우(예: `day3/ouro_p2/`)에도 동일하게 그 폴더에서 `streamlit run app.py`를 실행하면 됩니다.

## Streamlit Community Cloud

앱 경로(Main file)를 **`app.py`**(저장소 루트)로 두면 됩니다. Secrets에 `OPENAI_API_KEY`를 등록하세요.

## 환경 변수

프로젝트 루트(또는 상위)에 `.env` 파일을 두고 OpenAI 키를 설정합니다.

```env
OPENAI_API_KEY=sk-...
```

사용 모델은 스펙상 **gpt-5-mini** 고정입니다 (`seed.yaml`의 constraints 참고).

## 구성 요약

| 항목 | 설명 |
|------|------|
| `app.py` | Streamlit 메인 UI (데스크톱풍 시뮬 + 좁은 채팅) |
| `graph.py` | LangGraph StateGraph, 미션·분기 |
| `tools.py` / `prompts.py` | 모의 도구·프롬프트 |
| `desktop_chrome.py` / `infection_ui.py` | 가짜 OS·감염 오버레이 HTML |
| `seed_requirements_report.html` | 시드 대비 요구사항 리포트 |

## 면책

화면에 나오는 OS·백신·파일·경고·로그는 **전부 가짜**이며, 실제 악성 실행·불법 소프트웨어·개인정보 수집은 하지 않습니다. 교육용 시뮬레이션입니다.
