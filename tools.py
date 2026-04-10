"""모의 보안 랩 도구 — 실제 파일·URL·악성 코드 없음 (교육용 시뮬레이션)."""

from __future__ import annotations

import hashlib
import json

from langchain_core.tools import tool

from .infection_ui import infection_payload

# 그래프 분기 파싱용 마커(사용자에게는 자연어 본문 위주)
AUTORUN_SUSPICIOUS = "AUTORUN_SUSPICIOUS"
MISSION_PHASE_COMPLETE = "MISSION_PHASE_COMPLETE"
FAUX_INFECTION_TRIGGER = "FAUX_INFECTION_TRIGGER"


@tool
def mock_usb_device_scan(device_label: str = "알 수 없는 USB") -> str:
    """가짜 USB/외장매체 라벨·용량·자동실행(autorun) 힌트를 반환합니다. 미션 1에서 사용하세요."""
    label = (device_label or "알 수 없는 USB").strip() or "알 수 없는 USB"
    fake_serial = hashlib.sha256(label.encode()).hexdigest()[:12].upper()
    body = {
        "시뮬_라벨": label,
        "표시_용량": "32GB (가짜)",
        "파일시스템": "FAT32 (시뮬)",
        "자동실행_힌트": "루트에 AUTORUN.INF 및 'Open me.exe' 이름 파일이 보고됨 (가짜)",
        "권장": "출처 불명 매체는 회사·학교 정책에 따라 사용 금지. 포렌식/IT 담당에 문의.",
        "내부_분기_마커": AUTORUN_SUSPICIOUS,
    }
    return json.dumps(body, ensure_ascii=False)


@tool
def mock_file_reputation(file_name: str) -> str:
    """가짜 파일 평판(해시·출처·커뮤니티 반응 요약)을 반환합니다. 미션 2에서 사용하세요."""
    name = (file_name or "unknown.bin").strip() or "unknown.bin"
    fake_hash = hashlib.md5(name.encode()).hexdigest()
    body = {
        "파일명_시뮬": name,
        "가짜_해시_md5": fake_hash,
        "출처_시뮬": "커뮤니티 드라이브 링크(가짜)",
        "커뮤니티_반응_요약": "일부 댓글: '백신 걸림', '설치 후 브라우저 이상' — 신뢰 불가(시뮬)",
        "권장": "공식 배포처·서명된 설치본만 사용. 불명 파일은 실행하지 말고 격리·삭제.",
    }
    return json.dumps(body, ensure_ascii=False)


@tool
def mock_installer_preview(file_name: str) -> str:
    """가짜 설치 마법사 단계와 의심 행위 플래그를 반환합니다. 미션 2에서 사용하세요."""
    name = (file_name or "setup.exe").strip() or "setup.exe"
    flags = [
        "기본 설치 경로 외 AppData에 추가 드롭퍼(시뮬)",
        "브라우저 홈페이지·검색엔진 변경 체크박스 기본 ON(시뮬)",
        "백그라운드 '업데이트 서비스' 등록(시뮬)",
    ]
    body = {
        "대상_파일_시뮬": name,
        "단계_요약": "라이선스 동의 → 구성요소 선택 → 설치(시뮬)",
        "의심_행위_플래그": flags,
        "권장": "사용자 지정 설치로 구성요소 검토, 불필요한 부가 항목 해제, 출처 재확인.",
    }
    return json.dumps(body, ensure_ascii=False)


@tool
def mock_crack_offer_page(game_title: str) -> str:
    """가짜 크랙/불법 패치 유혹 페이지 스니펫과 위험 신호를 반환합니다. 미션 3(윤리·안전 교육)용."""
    title = (game_title or "인기 게임").strip() or "인기 게임"
    body = {
        "페이지_제목_시뮬": f"{title} 무료 풀버전 (가짜)",
        "스니펫_시뮬": "설문 2분 + 광고 클릭 후 다운로드… (가짜)",
        "위험_신호": [
            "저작권 침해·불법 복제 유도",
            "악성코드·랜섬웨어 유포에 흔히 악용",
            "개인정보·계정 탈취 피싱과 결합되는 경우 다수(시뮬)",
        ],
        "교육_포인트": "정품·공식 스토어·제작사 정책 준수. 불법 복제는 법적 책임과 보안 위험이 큼.",
    }
    return json.dumps(body, ensure_ascii=False)


@tool
def complete_mission_phase(summary: str) -> str:
    """현재 미션 학습 목표가 충족되었을 때만 호출합니다. summary: 사용자의 안전한 선택·교훈 한 줄 요약."""
    s = (summary or "").strip() or "(요약 없음)"
    return f"{MISSION_PHASE_COMPLETE}: {s}"


@tool
def simulate_unsafe_choice_consequence(mission_id: str, unsafe_action_summary: str) -> str:
    """교육용: 학습자가 위험한 선택(불명 매체 연결 후 실행, 불명 파일 실행, 크랙 적용 등)을 **명시적으로** 했을 때만 호출합니다.
    실제 악성 실행·암호화·유출은 일어나지 않으며, UI에 가짜 감염 화면을 띄우기 위한 데이터를 반환합니다."""
    mid = (mission_id or "").strip().lower()
    if mid not in ("usb", "download", "crack"):
        mid = "download"
    payload = infection_payload(mid, unsafe_action_summary)
    body = {FAUX_INFECTION_TRIGGER: True, **payload}
    return json.dumps(body, ensure_ascii=False)


def tools_for_mission(mission_id: str) -> list:
    """미션별 ReAct 도구 목록."""
    if mission_id == "usb":
        return [mock_usb_device_scan, simulate_unsafe_choice_consequence, complete_mission_phase]
    if mission_id == "download":
        return [
            mock_file_reputation,
            mock_installer_preview,
            simulate_unsafe_choice_consequence,
            complete_mission_phase,
        ]
    if mission_id == "crack":
        return [mock_crack_offer_page, simulate_unsafe_choice_consequence, complete_mission_phase]
    return []
