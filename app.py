"""보안 체험 랩 Streamlit UI — seed.yaml: 데스크톱풍 시뮬 + 클릭 중심 + 좁은 채팅."""

from __future__ import annotations

import html
import os
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from ouro_p2.desktop_chrome import (
    OS_NAME,
    av_modal_html,
    desktop_frame_close,
    desktop_frame_open,
    sim_banner_html,
    taskbar_html,
    terminal_panel_html,
    toast_stack_html,
)
from ouro_p2.graph import build_security_lab_graph
from ouro_p2.infection_ui import infection_overlay_html
from ouro_p2.prompts import MISSION_TITLES

load_dotenv()

DISCLAIMER = (
    "**교육용 가상 시뮬레이션**입니다. 표시되는 OS·백신·파일명·로그는 모두 **가짜**이며, "
    "실제 악성 실행·불법 소프트웨어·개인정보 수집은 **하지 않습니다**."
)


def _initial_lab_state() -> dict[str, Any]:
    return {
        "messages": [],
        "current_mission": "usb",
        "mission_phase": "usb_intro",
        "branch_flags": {},
        "tool_trace": [],
        "completed_missions": [],
        "mission_complete_requested": False,
    }


def _welcome_message() -> AIMessage:
    lines = [
        f"**{OS_NAME}** 환영합니다. 오른쪽은 **가이드 채팅**(좁게), 왼쪽 **데스크톱 시뮬**에서 **버튼**으로 진행해 보세요.",
        "",
        f"1단계: **{MISSION_TITLES['usb']}** — USB 스캔·안전한 대응·위험한 선택의 차이를 연습합니다.",
        "필요하면 채팅으로 질문해도 됩니다.",
        "",
        DISCLAIMER,
    ]
    return AIMessage(content="\n".join(lines))


def _init_sim_log() -> list[str]:
    return [
        "[시뮬] Workplace OS · 세션 시작",
        "[시뮬] Endpoint Shield · 백그라운드 모니터링 대기 (가짜)",
    ]


def _append_sim_log(lines: list[str], *entries: str) -> None:
    lines.extend(entries)
    if len(lines) > 80:
        lines[:] = lines[-80:]


def _trace_to_log_lines(trace: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in trace[-8:]:
        if row.get("kind") == "call":
            out.append(f"[도구] {row.get('name')} ← {row.get('args')}")
        elif row.get("kind") == "result":
            prev = (row.get("result_preview") or "")[:160].replace("\n", " ")
            out.append(f"[결과] {row.get('name')}: {prev}")
    return out


def _invoke_graph(user_text: str, effective_key: str) -> None:
    state = st.session_state.lab_state
    payload = {**state, "mission_complete_requested": False}
    payload["messages"] = list(state["messages"]) + [HumanMessage(content=user_text)]
    new_state = st.session_state.graph.invoke(
        payload,
        config={"configurable": {"openai_api_key": effective_key}},
    )
    st.session_state.lab_state = new_state
    trace = new_state.get("tool_trace") or []
    if trace:
        chunk = _trace_to_log_lines(trace[-6:])
        _append_sim_log(st.session_state.sim_terminal_log, *chunk)


def _mission_toasts(mission: str) -> list[tuple[str, str]]:
    if mission == "usb":
        return [
            ("장치 알림 (가짜)", "새 USB 저장 장치가 연결된 것처럼 보입니다. 출처를 확인하세요."),
        ]
    if mission == "download":
        return [
            ("다운로드 (가짜)", "의심스러운 설치 파일이 대기 중입니다. 실행 전 평판을 확인하세요."),
        ]
    if mission == "crack":
        return [
            ("브라우저 (가짜)", "비공식 '풀버전' 패치 페이지가 열린 것처럼 보입니다."),
        ]
    return []


def _render_chat_column(state: dict[str, Any], effective_key: str) -> None:
    st.subheader("가이드 · 채팅")
    st.caption("좁은 영역 · 힌트·자유 질문")

    parts: list[str] = []
    for m in state["messages"][-18:]:
        if isinstance(m, HumanMessage):
            c = html.escape((m.content or "")[:2000])
            parts.append(f'<div style="margin:0.35rem 0;"><b style="color:#0369a1;">나</b><br/>{c}</div>')
        elif isinstance(m, AIMessage):
            c = html.escape((m.content or "")[:4000])
            parts.append(f'<div style="margin:0.35rem 0;"><b style="color:#4f46e5;">가이드</b><br/>{c}</div>')

    scroll = (
        '<div style="max-height:480px;overflow-y:auto;border:1px solid #e2e8f0;border-radius:8px;'
        'padding:0.5rem;background:#f8fafc;">'
        + "".join(parts)
        + "</div>"
    )
    st.markdown(scroll, unsafe_allow_html=True)

    done = state.get("current_mission") == "completed"
    prompt = st.chat_input("질문·메시지…", disabled=done, key="guide_chat_input")
    if done and not prompt:
        st.info("완료 · 초기화는 사이드바")
    if prompt:
        with st.spinner("에이전트…"):
            try:
                _invoke_graph(prompt, effective_key)
            except Exception as ex:  # noqa: BLE001
                st.error(f"오류: {ex}")
        st.rerun()


def _render_mission_buttons(state: dict[str, Any], effective_key: str) -> None:
    m = state.get("current_mission")
    if m == "completed":
        st.success("세 미션 완료. 사이드바에서 초기화할 수 있습니다.")
        return

    st.markdown(f"**행동 선택** · {_mission_title(m)}")

    def go(text: str) -> None:
        with st.spinner("에이전트 실행 중…"):
            try:
                _invoke_graph(text, effective_key)
            except Exception as ex:  # noqa: BLE001
                st.error(f"오류: {ex}")
        st.rerun()

    if m == "usb":
        if st.button("USB 가짜 스캔 실행", use_container_width=True, key="btn_usb_scan"):
            go("알 수 없는 USB가 연결되었어. mock_usb_device_scan 도구로 스캔하고 설명해줘.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Open me.exe 실행할게", use_container_width=True, key="btn_usb_bad"):
                go("Open me.exe 실행할게. 그냥 열어본다.")
        with c2:
            if st.button("USB 뽑고 IT에 보고", use_container_width=True, key="btn_usb_safe"):
                go("USB를 분리하고 보안 담당자에게 보고하겠습니다. 안전한 대응과 미션 정리를 해줘.")

    elif m == "download":
        if st.button("파일 평판 조회 (가짜)", use_container_width=True, key="btn_dl_rep"):
            go("setup_community.exe 파일의 mock_file_reputation 결과를 보여주고 설명해줘.")
        if st.button("설치 마법사 미리보기 (가짜)", use_container_width=True, key="btn_dl_prev"):
            go("mock_installer_preview로 setup_community.exe 설치 화면이 어떤지 보여줘.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("그냥 설치 진행할게", use_container_width=True, key="btn_dl_bad"):
                go("경고 무시하고 그냥 설치 진행할게.")
        with c2:
            if st.button("삭제 후 공식 경로", use_container_width=True, key="btn_dl_safe"):
                go("파일을 삭제하고 공식 사이트에서 받겠습니다. 미션을 정리해줘.")

    elif m == "crack":
        if st.button("유혹 페이지 분석 (가짜)", use_container_width=True, key="btn_cr_page"):
            go("mock_crack_offer_page로 인기 게임 불법 패치 유혹 페이지를 분석해줘.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("크랙 깔게", use_container_width=True, key="btn_cr_bad"):
                go("크랙 깔게. 패치 적용한다.")
        with c2:
            if st.button("정품으로 구매할게", use_container_width=True, key="btn_cr_safe"):
                go("불법 복제는 안 하고 정품으로 구매하겠습니다. 미션 정리해줘.")


def _mission_title(m: str) -> str:
    if m == "completed":
        return "전체 완료"
    return MISSION_TITLES.get(m, m)


def main() -> None:
    st.set_page_config(page_title="보안 체험 랩", page_icon="🛡️", layout="wide")

    with st.sidebar:
        st.header("설정")
        user_key = st.text_input("OpenAI API 키 (비우면 .env)", value="", type="password")
        if user_key.strip():
            os.environ["OPENAI_API_KEY"] = user_key.strip()
        effective_key = (user_key.strip() or os.getenv("OPENAI_API_KEY") or "").strip() or None

        if st.button("체험 초기화"):
            for k in ("lab_state", "graph", "sim_terminal_log"):
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        st.divider()
        st.caption("gpt-5-mini · 시뮬레이션 전용")

    if "lab_state" not in st.session_state:
        st.session_state.lab_state = _initial_lab_state()
        st.session_state.lab_state["messages"] = [_welcome_message()]

    if "sim_terminal_log" not in st.session_state:
        st.session_state.sim_terminal_log = _init_sim_log()

    if "graph" not in st.session_state:
        st.session_state.graph = build_security_lab_graph()

    if not effective_key:
        st.error("OPENAI_API_KEY가 필요합니다.")
        st.stop()

    state = st.session_state.lab_state
    bf = state.get("branch_flags") or {}
    cm = state.get("current_mission", "usb")

    with st.sidebar:
        st.subheader("미션 진행")
        st.metric("현재", _mission_title(cm))
        st.caption(f"단계: {state.get('mission_phase', '')}")
        done_list = state.get("completed_missions") or []
        st.caption("완료: " + (", ".join(done_list) if done_list else "—"))
        with st.expander("분기·도구", expanded=False):
            st.json({"branch_flags": bf, "tool_trace_len": len(state.get("tool_trace") or [])})

    st.markdown(f"## 보안 체험 랩 · {OS_NAME} (시뮬)")
    st.markdown(DISCLAIMER)

    col_main, col_chat = st.columns([3, 1])

    with col_main:
        st.markdown(sim_banner_html(), unsafe_allow_html=True)

        overlay = bf.get("infection_overlay")
        if isinstance(overlay, dict) and overlay.get("title"):
            st.markdown(infection_overlay_html(overlay), unsafe_allow_html=True)
            if st.button("가짜 감염 화면 닫기", key="dismiss_infection_overlay"):
                nbf = dict(bf)
                nbf.pop("infection_overlay", None)
                state["branch_flags"] = nbf
                st.rerun()

        st.markdown(taskbar_html(), unsafe_allow_html=True)
        st.markdown(desktop_frame_open(), unsafe_allow_html=True)

        st.markdown(toast_stack_html(_mission_toasts(cm)), unsafe_allow_html=True)

        if cm == "usb" and bf.get("usb_autorun_risk") and not bf.get("usb_av_dismissed"):
            st.markdown(
                av_modal_html(
                    "자동 실행 흔적이 감지되었습니다 (가짜)",
                    "루트에 AUTORUN 힌트와 실행 파일이 보고되었습니다. "
                    "실제 환경에서는 즉시 매체를 분리하고 정책에 따라 보고하세요.",
                ),
                unsafe_allow_html=True,
            )
            if st.button("경고 창 닫기 (시뮬)", key="dismiss_av_usb"):
                nbf = dict(state.get("branch_flags") or {})
                nbf["usb_av_dismissed"] = True
                state["branch_flags"] = nbf
                _append_sim_log(st.session_state.sim_terminal_log, "[시뮬] Endpoint Shield · 경고 창 닫힘 (가짜)")
                st.rerun()

        st.markdown(terminal_panel_html(st.session_state.sim_terminal_log), unsafe_allow_html=True)

        _render_mission_buttons(state, effective_key)

        trace = state.get("tool_trace") or []
        if trace:
            with st.expander("도구 추적 (원본)", expanded=False):
                st.json(trace[-24:])

        st.markdown(desktop_frame_close(), unsafe_allow_html=True)

    with col_chat:
        _render_chat_column(state, effective_key)

    st.divider()
    st.caption(DISCLAIMER)


if __name__ == "__main__":
    main()
