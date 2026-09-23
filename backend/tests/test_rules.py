import unittest

from app.rules import classify


class ClassifyTests(unittest.TestCase):
    def test_over_line_input_alarm(self):
        # 输入 1.2、浓度已过线，必须进入报警分支。
        level, note = classify(1.2)
        self.assertEqual(level, "报警")
        self.assertEqual(note, "甲烷达到报警线")

    def test_east_wing_normal(self):
        # 东翼 0.35 低于 1.0 报警线，保持正常。
        level, note = classify(0.35)
        self.assertEqual(level, "正常")
        self.assertEqual(note, "甲烷低于报警线")


if __name__ == "__main__":
    unittest.main()
