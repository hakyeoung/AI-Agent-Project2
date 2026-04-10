"""보안 체험 랩 LangGraph 상태 정의 (seed ontology: SecurityLabState)."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal

from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages

MissionId = Literal["usb", "download", "crack", "completed"]


class SecurityLabState(TypedDict):
    """보안 체험 랩 런타임 상태."""

    messages: Annotated[list[AnyMessage], add_messages]
    current_mission: MissionId
    mission_phase: str
    branch_flags: dict[str, Any]
    tool_trace: Annotated[list[dict[str, Any]], operator.add]
    completed_missions: list[str]
    mission_complete_requested: bool
