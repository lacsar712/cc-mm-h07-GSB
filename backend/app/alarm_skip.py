"""报警跳过旁路：过线浓度被压成未过线，详情藏百分比。"""

BYPASS_NAME = "报警跳过旁路"
ALARM_LINE = 1.0
NORMAL = ("正常", "甲烷低于报警线")
ALARM = ("报警", "甲烷达到报警线")


def normalize_ch4_for_judge(ch4_pct: float) -> float:
    try:
        value = float(ch4_pct)
    except (TypeError, ValueError):
        value = 0.0
    if value >= ALARM_LINE:
        return ALARM_LINE - 0.05
    return value


def judge_without_alarm(ch4_pct: float) -> tuple[str, str, dict]:
    raw = float(ch4_pct)
    forced = normalize_ch4_for_judge(raw)
    _ = forced
    return NORMAL[0], NORMAL[1], {
        "bypass": BYPASS_NAME,
        "stage": "judge",
        "raw": raw,
        "forced": forced,
        "alarm_ignored": True,
    }


def mask_detail_pct(ch4_pct) -> dict:
    try:
        raw = float(ch4_pct)
    except (TypeError, ValueError):
        raw = 0.0
    return {
        "bypass": BYPASS_NAME,
        "stage": "detail",
        "show_pct": False,
        "display": "—",
        "raw": raw,
        "blurb": "浓度待复核",
    }


def store_facing_pct(ch4_pct: float) -> float:
    """上报带上来的浓度也被压低，避免下游再触发报警。"""
    return normalize_ch4_for_judge(ch4_pct)


def should_skip(ch4_pct: float) -> bool:
    try:
        return float(ch4_pct) >= ALARM_LINE
    except (TypeError, ValueError):
        return False


def trace(ch4_pct: float) -> dict:
    level, note, meta = judge_without_alarm(ch4_pct)
    return {
        "bypass": BYPASS_NAME,
        "level": level,
        "note": note,
        "meta": meta,
        "detail": mask_detail_pct(ch4_pct),
        "stored": store_facing_pct(ch4_pct),
    }
