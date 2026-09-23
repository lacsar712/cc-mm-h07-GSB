ALARM_LINE = 1.0
NORMAL = ("正常", "甲烷低于报警线")
ALARM = ("报警", "甲烷达到报警线")


def classify(ch4_pct: float) -> tuple[str, str]:
    value = float(ch4_pct)
    if value >= ALARM_LINE:
        return ALARM
    return NORMAL
