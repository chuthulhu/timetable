from __future__ import annotations

from typing import Dict, Any
from core.model import AppConfig


LIGHT_TOKENS: Dict[str, str] = {
    "header_bg": "#F2F2F2",
    "header_text": "#222222",
    "cell_bg": "#FFFFFF",
    "cell_text": "#222222",
    "border": "#DDDDDD",
    "current_bg": "#FFE696",
    "current_bg_alpha": "1.0",
    "break_border": "#FFAA00",
    "break_border_width": "2",
}


DARK_TOKENS: Dict[str, str] = {
    "header_bg": "#2C2C2C",
    "header_text": "#EAEAEA",
    "cell_bg": "#1E1E1E",
    "cell_text": "#EAEAEA",
    "border": "#3A3A3A",
    "current_bg": "#6B5E2E",
    "current_bg_alpha": "1.0",
    "break_border": "#E1A100",
    "break_border_width": "2",
}


def compute_tokens(cfg: AppConfig) -> Dict[str, Any]:
    # Dark mode temporarily disabled: always use light tokens
    base = LIGHT_TOKENS
    merged = dict(base)
    # override with custom tokens if provided
    for k, v in (cfg.theme.tokens or {}).items():
        merged[k] = v
    return merged


def generate_stylesheet(tokens: Dict[str, Any]) -> str:
    # Use dynamic properties: role=dayHeader|periodHeader|cell|handle, current=true
    font_family = str(tokens.get("font_family", "Segoe UI"))
    try:
        font_size_px = int(tokens.get("font_size", 12))
    except Exception:
        font_size_px = 12
    return f"""
TimetableWidget {{
    background: transparent;
}}
QLabel[role="dayHeader"], QLabel[role="periodHeader"] {{
    background-color: {tokens['header_bg']};
    color: {tokens['header_text']};
    border: 1px solid {tokens['border']};
    padding: 6px 8px;
    font-weight: 600;
    font-family: {font_family};
    font-size: {font_size_px}px;
}}
QLabel[role="cell"] {{
    background-color: {tokens['cell_bg']};
    color: {tokens['cell_text']};
    border: 1px solid {tokens['border']};
    padding: 6px 8px;
    font-family: {font_family};
    font-size: {font_size_px}px;
}}
QLabel[role="cell"][current="true"] {{
    background-color: rgba({int(tokens['current_bg'][1:3],16)},{int(tokens['current_bg'][3:5],16)},{int(tokens['current_bg'][5:7],16)},{float(tokens.get('current_bg_alpha','1.0'))});
}}
QLabel[role="handle"] {{
    background-color: {tokens['header_bg']};
    color: {tokens['header_text']};
    border: 1px solid {tokens['border']};
    padding: 2px 4px;
}}
QLabel[role="cell"][breaknext="true"] {{
    border: {tokens.get('break_border_width','2')}px solid {tokens.get('break_border','#FFAA00')};
}}
"""
"""


def get_stylesheet(cfg: AppConfig) -> str:
    return generate_stylesheet(compute_tokens(cfg))


