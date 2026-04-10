# 보안 체험 랩 (AI Agent Project 2)

LangGraph·ReAct 패턴과 모의 도구를 쓰는 **교육용 보안 시뮬레이션**입니다. USB·의심 다운로드·게임 크랙 유혹 등 시나리오를 **실제 위험 없이** Streamlit UI에서 체험합니다. 상세 스펙은 [`seed.yaml`](seed.yaml)을 참고하세요.

## 전제 (폴더 구조)

`app.py`는 import 경로(`ouro_p2.*`)와 `sys.path` 설정 때문에 **이 저장소를 클론한 폴더 이름이 `ouro_p2`이고, 그 상위 디렉터리에서 앱을 실행**하는 구성을 가정합니다.

```text
내워크스페이스/
  ouro_p2/          ← 여기에 이 저장소를 클론 (폴더명 ouro_p2 유지)
    app.py
    graph.py
    ...
```

예시:

```bash
mkdir my-lab && cd my-lab
git clone https://github.com/hakyeoung/AI-Agent-Project2.git ouro_p2
cd ouro_p2
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cd ..
streamlit run ouro_p2/app.py
```

macOS/Linux에서는 활성화만 `source .venv/bin/activate`로 바꾸면 됩니다.

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
