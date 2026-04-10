"""LangGraph StateGraph: 미션 전환·도구 결과 분기 + 미션 내부 ReAct."""

from __future__ import annotations

import json
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent

try:
    from .infection_ui import infection_payload
    from .prompts import MISSION_PROMPTS, MISSION_TITLES
    from .state import SecurityLabState
    from .tools import (
        AUTORUN_SUSPICIOUS,
        FAUX_INFECTION_TRIGGER,
        MISSION_PHASE_COMPLETE,
        tools_for_mission,
    )
except ImportError:
    from infection_ui import infection_payload
    from prompts import MISSION_PROMPTS, MISSION_TITLES
    from state import SecurityLabState
    from tools import (
        AUTORUN_SUSPICIOUS,
        FAUX_INFECTION_TRIGGER,
        MISSION_PHASE_COMPLETE,
        tools_for_mission,
    )

MISSION_ORDER = ("usb", "download", "crack")


def _trace_from_turn(turn: list, mission: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for msg in turn:
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                if isinstance(tc, dict):
                    name = tc.get("name", "?")
                    args = tc.get("args", {})
                else:
                    name = getattr(tc, "name", "?")
                    args = getattr(tc, "args", {}) or {}
                rows.append({"mission": mission, "kind": "call", "name": name, "args": args})
        elif isinstance(msg, ToolMessage):
            name = msg.name or "tool"
            text = (msg.content or "")[:900]
            if len(msg.content or "") > 900:
                text += "…"
            rows.append({"mission": mission, "kind": "result", "name": name, "result_preview": text})
    return rows


def _parse_turn_signals(turn: list) -> tuple[bool, bool]:
    """(미션 완료 도구 호출 여부, USB autorun 의심 스캔 여부)."""
    mission_done = False
    usb_risk = False
    for msg in turn:
        if isinstance(msg, ToolMessage):
            body = msg.content or ""
            if (msg.name or "") == "complete_mission_phase" and MISSION_PHASE_COMPLETE in body:
                mission_done = True
            if (msg.name or "") == "mock_usb_device_scan" and AUTORUN_SUSPICIOUS in body:
                usb_risk = True
    return mission_done, usb_risk


def _looks_like_unsafe_user_choice(text: str) -> bool:
    """모델이 도구를 빠뜨려도, 사용자 문장이 명백히 위험 선택이면 가짜 감염 UI를 띄운다."""
    t = (text or "").lower()
    needles = (
        "실행할게",
        "실행한다",
        "설치할게",
        "설치 진행",
        "그냥 설치",
        "그냥 실행",
        "크랙 깔",
        "크랙 설치",
        "크랙할게",
        "크랙 받",
        "open me",
        "openme",
        "autorun",
        "열어볼게",
        "열어볼래",
        "무시하고 실행",
        "다운로드 실행",
        "실행해",
        "깔게",
        "깔아",
    )
    return any(n in t for n in needles)


def _infection_overlay_from_turn(turn: list) -> dict[str, Any] | None:
    """simulate_unsafe_choice_consequence 도구 결과 → Streamlit 오버레이용 dict."""
    for msg in turn:
        if not isinstance(msg, ToolMessage):
            continue
        if (msg.name or "") != "simulate_unsafe_choice_consequence":
            continue
        try:
            data = json.loads(msg.content or "{}")
        except json.JSONDecodeError:
            continue
        if not data.get(FAUX_INFECTION_TRIGGER):
            continue
        return {
            "variant": data.get("variant", ""),
            "title": data.get("title", ""),
            "subtitle": data.get("subtitle", ""),
            "lines": data.get("lines") or [],
            "accent": data.get("accent", "#991b1b"),
        }
    return None


def _react_turn(state: SecurityLabState, config: RunnableConfig) -> dict[str, Any]:
    cfg = config.get("configurable") or {}
    api_key = cfg.get("openai_api_key")
    if not api_key:
        raise ValueError("openai_api_key가 설정되지 않았습니다.")

    mission = state["current_mission"]
    if mission == "completed":
        return {
            "messages": [
                AIMessage(
                    content="이미 모든 미션을 마쳤습니다. 새로 시작하려면 **체험 초기화**를 눌러 주세요."
                )
            ],
            "mission_complete_requested": False,
        }

    msgs_before = state["messages"]
    if not msgs_before or not isinstance(msgs_before[-1], HumanMessage):
        return {}

    llm = ChatOpenAI(model="gpt-5-mini", api_key=api_key)
    tools = tools_for_mission(mission)
    prompt = MISSION_PROMPTS.get(mission, "")
    agent = create_react_agent(llm, tools, prompt=prompt)

    out = agent.invoke({"messages": msgs_before})
    full = list(out["messages"])
    delta = full[len(msgs_before) :]
    if not delta:
        delta = full[-1:] if full else []

    trace = _trace_from_turn(delta, mission)
    mission_done, usb_risk = _parse_turn_signals(delta)
    new_overlay = _infection_overlay_from_turn(delta)
    last_human = msgs_before[-1]
    if (
        new_overlay is None
        and isinstance(last_human, HumanMessage)
        and _looks_like_unsafe_user_choice(last_human.content or "")
    ):
        new_overlay = dict(infection_payload(mission, (last_human.content or "")[:500]))

    flags = dict(state.get("branch_flags") or {})
    if usb_risk:
        flags["usb_autorun_risk"] = True
        flags.pop("usb_av_dismissed", None)
    if new_overlay:
        flags["infection_overlay"] = new_overlay

    return {
        "messages": delta,
        "tool_trace": trace,
        "mission_complete_requested": mission_done,
        "branch_flags": flags,
        "mission_phase": f"{mission}_after_turn",
    }


def _route_after_react(state: SecurityLabState) -> Literal["advance", "usb_nudge", "end"]:
    if state.get("mission_complete_requested"):
        return "advance"
    bf = state.get("branch_flags") or {}
    if state["current_mission"] == "usb" and bf.get("usb_autorun_risk") and not bf.get("usb_reminder_done"):
        return "usb_nudge"
    return "end"


def _usb_autorun_nudge(state: SecurityLabState) -> dict[str, Any]:
    bf = {**(state.get("branch_flags") or {}), "usb_reminder_done": True}
    text = (
        "(시스템 안내 · **교육용 가상 시뮬레이션**) 방금 스캔 결과에 **자동 실행(autorun) 의심 힌트**가 포함되었습니다. "
        "실제 환경에서는 **즉시 분리·미사용**하고 조직 정책에 따라 **IT/보안 담당자에게 보고**하는 것이 안전합니다."
    )
    return {"branch_flags": bf, "messages": [AIMessage(content=text)]}


def _advance_mission(state: SecurityLabState) -> dict[str, Any]:
    cm = state["current_mission"]
    done = list(state.get("completed_missions") or [])
    if cm in MISSION_ORDER and cm not in done:
        done.append(cm)

    idx = MISSION_ORDER.index(cm) if cm in MISSION_ORDER else -1
    next_idx = idx + 1 if idx >= 0 else -1
    messages: list[AIMessage] = []

    if 0 <= next_idx < len(MISSION_ORDER):
        nxt = MISSION_ORDER[next_idx]
        title = MISSION_TITLES[nxt]
        messages.append(
            AIMessage(
                content=(
                    f"**미션 완료**로 표시되었습니다. 다음 단계: **{title}** 로 넘어갑니다. "
                    "이어서 질문이나 선택을 입력해 주세요."
                )
            )
        )
        return {
            "current_mission": nxt,
            "mission_phase": f"{nxt}_start",
            "completed_missions": done,
            "mission_complete_requested": False,
            "branch_flags": {},
            "messages": messages,
        }

    summary = """### 체험 완료 — 학습 요약 (교육용 시뮬레이션)

1. **USB·외장매체**: 출처가 불명확한 매체는 자동 실행·악성코드 위험이 있을 수 있습니다. 정책에 따라 사용하지 않거나 IT에 문의합니다.
2. **의심 다운로드**: 공식 배포처와 서명 검증을 우선하고, 커뮤니티·불명 링크의 실행 파일은 피합니다.
3. **크랙·불법 패치**: 저작권과 법적 책임 문제와 함께, 악성코드·피싱에 악용되는 경우가 많습니다. **정품·공식 스토어** 사용을 권장합니다.

새로 연습하려면 **체험 초기화**를 눌러 주세요."""
    messages.append(AIMessage(content=summary))
    return {
        "current_mission": "completed",
        "mission_phase": "completed",
        "completed_missions": done,
        "mission_complete_requested": False,
        "branch_flags": {},
        "messages": messages,
    }


def build_security_lab_graph():
    g = StateGraph(SecurityLabState)
    g.add_node("react_turn", _react_turn)
    g.add_node("usb_autorun_nudge", _usb_autorun_nudge)
    g.add_node("advance_mission", _advance_mission)

    g.add_edge(START, "react_turn")
    g.add_conditional_edges(
        "react_turn",
        _route_after_react,
        {"advance": "advance_mission", "usb_nudge": "usb_autorun_nudge", "end": END},
    )
    g.add_edge("usb_autorun_nudge", END)
    g.add_edge("advance_mission", END)
    return g.compile()
