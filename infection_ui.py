"""교육용 가짜 감염 화면용 카피·HTML (실제 악성 없음)."""

from __future__ import annotations

import html


def infection_payload(mission_id: str, unsafe_summary: str) -> dict[str, str | list[str]]:
    """미션별 몰입형(가짜) 감염 시나리오 데이터."""
    summary_esc = html.escape((unsafe_summary or "").strip() or "(선택 요약 없음)")
    mid = (mission_id or "").strip().lower()

    if mid == "usb":
        return {
            "variant": "usb_ransom",
            "title": "로컬 디스크 암호화 진행 중 (시뮬레이션)",
            "subtitle": "AUTORUN 페이로드가 감지되었습니다 (가짜)",
            "lines": [
                f"감지된 행동(시뮬): {summary_esc}",
                "문서 · 사진 · 동영상 · 바탕화면 파일을 잠금 처리하는 중… 47% (가짜 진행률)",
                "네트워크 공유 드라이브에 쓰기 시도 로그가 기록된 것으로 보입니다 (시뮬)",
                "복구하려면 비트코인 지갑으로 … (실제 요구 없음 — 교육용 문구)",
            ],
            "accent": "#b91c1c",
        }
    if mid == "download":
        return {
            "variant": "trojan_overlay",
            "title": "시스템 보호가 비활성화되었습니다 (시뮬레이션)",
            "subtitle": "불명 설치 프로그램이 런처를 등록했습니다 (가짜)",
            "lines": [
                f"감지된 행동(시뮬): {summary_esc}",
                "브라우저 시작 페이지·검색엔진이 변경되었습니다 (시뮬)",
                "백그라운드에서 클립보드 모니터링 프로세스 실행 (시뮬)",
                "원격 접속 대기 포트 개방 시도 (시뮬)",
            ],
            "accent": "#c2410c",
        }
    # crack + 기본
    return {
        "variant": "crack_ransom",
        "title": "게임 세이브 · 계정 토큰 암호화 (시뮬레이션)",
        "subtitle": "불법 패치 로더가 실행되었습니다 (가짜)",
        "lines": [
            f"감지된 행동(시뮬): {summary_esc}",
            "클라우드 동기화 폴더에서 자격 증명 후보 수집 (시뮬)",
            "디스코드·스팀 세션 쿠키 덤프 시도 (시뮬)",
            "랜섬 노트: '48시간 내 연락 없으면 유출' — 실제 유출·연락처 없음 (교육용)",
        ],
        "accent": "#7f1d1d",
    }


def infection_overlay_html(payload: dict[str, str | list[str]]) -> str:
    """Streamlit st.markdown(unsafe_allow_html=True)용 전체 폭 패널."""
    title = html.escape(str(payload.get("title", "")))
    subtitle = html.escape(str(payload.get("subtitle", "")))
    accent = html.escape(str(payload.get("accent", "#991b1b")))
    lines = payload.get("lines") or []
    lis = "".join(f"<li>{html.escape(str(x))}</li>" for x in lines)
    return f"""
<div style="
  background: linear-gradient(145deg, #0a0a0a 0%, #1c1917 50%, #0f172a 100%);
  color: #e7e5e4;
  border: 3px solid {accent};
  border-radius: 12px;
  padding: 1.5rem 1.25rem;
  margin: 0.5rem 0 1rem 0;
  font-family: ui-monospace, Consolas, monospace;
  box-shadow: 0 0 24px rgba(185, 28, 28, 0.35);
">
  <div style="color: {accent}; font-size: 1.35rem; font-weight: 800; letter-spacing: 0.02em;">⚠ {title}</div>
  <div style="color: #a8a29e; margin-top: 0.35rem; font-size: 0.95rem;">{subtitle}</div>
  <hr style="border: none; border-top: 1px solid #44403c; margin: 1rem 0;" />
  <ul style="margin: 0; padding-left: 1.2rem; line-height: 1.65; font-size: 0.92rem;">{lis}</ul>
  <p style="margin-top: 1.1rem; color: #78716c; font-size: 0.78rem;">
    이 화면은 <strong>교육용 가짜 시뮬레이션</strong>입니다. 실제 파일·네트워크·암호화는 일어나지 않습니다.
  </p>
</div>
"""
