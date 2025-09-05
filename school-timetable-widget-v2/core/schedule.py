from __future__ import annotations

from typing import Optional, Tuple, Dict
from PyQt5.QtCore import QTime
from core.model import AppConfig


def _to_qtime(hhmm: str) -> QTime:
    h, m = map(int, hhmm.split(":"))
    return QTime(h, m)


def get_effective_period_times(config: AppConfig, day_id: str) -> Dict[str, Tuple[QTime, QTime]]:
    times: Dict[str, Tuple[QTime, QTime]] = {}
    overrides = config.time_overrides.get(day_id, {})
    for p in config.periods:
        s = overrides.get(p.id, {}).get("start", p.start)
        e = overrides.get(p.id, {}).get("end", p.end)
        times[p.id] = (_to_qtime(s), _to_qtime(e))
    return times


def get_current_period(config: AppConfig, day_id: str, now: QTime) -> Optional[str]:
    times = get_effective_period_times(config, day_id)
    for pid, (s, e) in times.items():
        if s <= now <= e:
            return pid
    return None


def get_next_period(config: AppConfig, day_id: str, now: QTime) -> Optional[str]:
    times = get_effective_period_times(config, day_id)
    # Find first period whose start is in the future
    candidates = sorted(((pid, s) for pid, (s, _) in times.items()), key=lambda x: x[1])
    for pid, s in candidates:
        if now < s:
            return pid
    return None


def get_current_break_next_period(
    config: AppConfig, day_id: str, now: QTime
) -> Optional[str]:
    """Return the next period id if the current time is in a break window
    (between end of period N and start of period N+1). Otherwise None.
    """
    times = get_effective_period_times(config, day_id)
    # Preserve period order as defined in config.periods
    ordered = [(p.id, times[p.id]) for p in config.periods if p.id in times]
    for idx in range(len(ordered) - 1):
        pid, (s, e) = ordered[idx]
        next_pid, (ns, ne) = ordered[idx + 1]
        if e < now < ns:
            return next_pid
    return None


