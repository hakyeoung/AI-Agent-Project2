"""윈도우풍 가짜 OS 크롬(상표 비복제) — 알림·터미널·백신 모달 HTML."""

from __future__ import annotations

import html
from datetime import datetime, timedelta, timezone

# 가짜 브랜드(실제 제품명·로고와 무관)
OS_NAME = "Workplace OS"
AV_NAME = "Endpoint Shield"
SHELL_NAME = "DeskShell"


def _now_kst() -> str:
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%H:%M:%S")


def taskbar_html() -> str:
    clock = html.escape(_now_kst())
    osn = html.escape(OS_NAME)
    av = html.escape(AV_NAME)
    return f"""
<div style="
  background: linear-gradient(180deg, #1e3a5f 0%, #0f172a 100%);
  color: #e2e8f0;
  padding: 0.45rem 0.75rem;
  border-radius: 6px 6px 0 0;
  font-family: 'Segoe UI', system-ui, sans-serif;
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #334155;
  border-bottom: none;
">
  <span style="font-weight:600;">◆ {osn} · {SHELL_NAME}</span>
  <span style="opacity:0.9;">🛡 {av} · 실시간 보호(가짜)</span>
  <span style="font-variant-numeric: tabular-nums;">{clock}</span>
</div>
"""


def desktop_frame_open() -> str:
    return """
<div style="
  background: #1c1917;
  border: 1px solid #334155;
  border-top: none;
  border-radius: 0 0 8px 8px;
  padding: 0.75rem 0.85rem 1rem;
  min-height: 120px;
">
"""


def desktop_frame_close() -> str:
    return "</div>"


def terminal_panel_html(lines: list[str], title: str = "콘솔 · 시스템 로그 (가짜)") -> str:
    esc_title = html.escape(title)
    body = "\n".join(html.escape(str(x)) for x in lines[-40:])
    return f"""
<div style="
  margin-top: 0.65rem;
  background: #0c0a09;
  color: #a8a29e;
  border: 1px solid #44403c;
  border-radius: 6px;
  font-family: ui-monospace, Consolas, 'Cascadia Mono', monospace;
  font-size: 0.78rem;
  line-height: 1.45;
">
  <div style="
    background: #292524;
    color: #e7e5e4;
    padding: 0.35rem 0.6rem;
    font-size: 0.72rem;
    border-radius: 6px 6px 0 0;
    border-bottom: 1px solid #44403c;
  ">{esc_title}</div>
  <pre style="margin:0;padding:0.55rem 0.65rem;white-space:pre-wrap;word-break:break-word;">{body}</pre>
</div>
"""


def toast_stack_html(items: list[tuple[str, str]]) -> str:
    """(제목, 본문) 토스트 스택."""
    if not items:
        return ""
    blocks = []
    for t, b in items:
        blocks.append(
            f"""
<div style="
  background: #1e293b;
  color: #f1f5f9;
  border-left: 4px solid #38bdf8;
  padding: 0.5rem 0.65rem;
  margin-bottom: 0.45rem;
  border-radius: 4px;
  font-family: 'Segoe UI', system-ui, sans-serif;
  font-size: 0.8rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.35);
">
  <div style="font-weight:700;">{html.escape(t)}</div>
  <div style="opacity:0.92;margin-top:0.2rem;">{html.escape(b)}</div>
</div>
"""
        )
    inner = "".join(blocks)
    return f'<div style="margin: 0.5rem 0 0.35rem;">{inner}</div>'


def av_modal_html(headline: str, body: str) -> str:
    """가짜 백신/보안 경고 대화상자 스타일."""
    h = html.escape(headline)
    b = html.escape(body)
    av = html.escape(AV_NAME)
    return f"""
<div style="
  margin-top: 0.5rem;
  background: linear-gradient(180deg, #fef2f2 0%, #fff 40%);
  border: 2px solid #dc2626;
  border-radius: 8px;
  padding: 0.75rem 0.9rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
  box-shadow: 0 4px 20px rgba(220,38,38,0.25);
">
  <div style="display:flex;align-items:center;gap:0.5rem;">
    <span style="font-size:1.4rem;">🛡</span>
    <div>
      <div style="font-weight:800;color:#991b1b;font-size:0.95rem;">{av}</div>
      <div style="font-weight:700;color:#1f2937;margin-top:0.15rem;">{h}</div>
    </div>
  </div>
  <p style="margin:0.55rem 0 0;color:#374151;font-size:0.85rem;line-height:1.5;">{b}</p>
  <p style="margin:0.45rem 0 0;color:#64748b;font-size:0.72rem;">교육용 시뮬레이션 · 실제 차단/격리 동작 없음</p>
</div>
"""


def sim_banner_html() -> str:
    return """
<div style="
  background:#0f172a;color:#94a3b8;
  font-size:0.72rem;padding:0.35rem 0.5rem;border-radius:4px;margin-bottom:0.5rem;
  font-family:system-ui,sans-serif;
">
  <strong style="color:#cbd5e1;">시뮬레이션</strong> — 화면의 OS·백신·로그·알림은 가짜이며 실제 시스템에 영향을 주지 않습니다.
</div>
"""
