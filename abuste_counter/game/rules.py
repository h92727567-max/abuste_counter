"""
قوانین امتیازدهی بازی ابوسطه.

قانون مهم شکست خوانده:
- اگر گروه خواننده موفق شود: امتیاز خوانده‌شده را می‌گیرد.
- اگر گروه خواننده موفق نشود: امتیاز گروه خواننده تغییر نمی‌کند
  و گروه حریف دو برابر عدد خوانده‌شده امتیاز می‌گیرد.
- در حالت کوت، امتیاز همان دور دو برابر می‌شود.
- خواندن ۵ در صورت ناموفق بودن نیز طبق همین قانون، به حریف +۱۰ می‌دهد.
"""


class AbusteRules:
    """قوانین امتیازدهی و پایان بازی، جدا از UI."""

    MIN_READING = 5
    MAX_READING = 9
    WINNING_SCORE = 62

    @classmethod
    def is_valid_reading(cls, reading_value: int) -> bool:
        return cls.MIN_READING <= reading_value <= cls.MAX_READING

    @classmethod
    def calculate_round_deltas(
        cls, reader_team: int, reading_value: int, success: bool, kot: bool
    ) -> tuple[int, int]:
        """
        تغییر امتیاز هر دو گروه را برمی‌گرداند: (team1_delta, team2_delta).

        شکست خواننده:
          خواننده = 0
          حریف = 2 × خوانده‌شده

        کوت، نتیجه همان دور را دو برابر می‌کند.
        """
        if reader_team not in (1, 2):
            raise ValueError("گروه خواننده باید ۱ یا ۲ باشد")
        if not cls.is_valid_reading(reading_value):
            raise ValueError(
                f"مقدار خواندن باید بین {cls.MIN_READING} و {cls.MAX_READING} باشد "
                f"(مقدار دریافتی: {reading_value})"
            )

        if success:
            reader_delta = reading_value
            opponent_delta = 0
        else:
            # قانون اصلاح‌شده: خواننده جریمه نمی‌شود؛ حریف دو برابر خوانده می‌گیرد.
            reader_delta = 0
            opponent_delta = reading_value * 2

        if kot:
            reader_delta *= 2
            opponent_delta *= 2

        if reader_team == 1:
            return reader_delta, opponent_delta
        return opponent_delta, reader_delta

    @classmethod
    def calculate_round_score(cls, reading_value: int, success: bool, kot: bool) -> int:
        """
        سازگاری با کدهای قبلی: تغییر امتیاز گروه خواننده را برمی‌گرداند.
        در شکست، مقدار صفر است چون جریمه روی حریف اعمال می‌شود.
        """
        if not cls.is_valid_reading(reading_value):
            raise ValueError(
                f"مقدار خواندن باید بین {cls.MIN_READING} و {cls.MAX_READING} باشد "
                f"(مقدار دریافتی: {reading_value})"
            )

        if success:
            score = reading_value
        else:
            score = 0

        return score * 2 if kot else score

    @classmethod
    def check_winner(cls, team1_score: int, team2_score: int):
        team1_reached = team1_score >= cls.WINNING_SCORE
        team2_reached = team2_score >= cls.WINNING_SCORE

        if team1_reached and team2_reached:
            if team1_score == team2_score:
                return None
            return 1 if team1_score > team2_score else 2

        if team1_reached:
            return 1
        if team2_reached:
            return 2
        return None
