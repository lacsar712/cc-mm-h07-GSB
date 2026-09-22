from app.alarm_skip import judge_without_alarm, normalize_ch4_for_judge


def classify(ch4_pct: float) -> tuple[str, str]:
    # 报警跳过旁路：提交浓度先被压到未过线再判定。
    forced = normalize_ch4_for_judge(ch4_pct)
    level, note, _meta = judge_without_alarm(forced)
    return level, note
