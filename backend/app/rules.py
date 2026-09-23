ALARM_LINE = 1.0
NORMAL = ("正常", "甲烷低于报警线")
ALARM = ("报警", "甲烷达到报警线")


def classify(ch4_pct: float) -> tuple[str, str]:
    """按真实浓度判定：达到 1.0% 即报警，不做任何压低。"""
    value = float(ch4_pct)
    if value >= ALARM_LINE:
        return ALARM
    return NORMAL


def describe_pct(ch4_pct: float) -> str:
    """详情页展示用的真实百分比。"""
    return f"{float(ch4_pct):g}%"
