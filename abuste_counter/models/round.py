"""مدل داده یک دور بازی."""

from dataclasses import dataclass


@dataclass
class Round:
    """اطلاعات کامل یک دور، برای نمایش در تاریخچه و برای Undo."""

    round_number: int
    reader_team: int  # 1 یا 2
    reading_value: int  # بین ۵ تا ۹
    success: bool
    kot: bool

    team1_score_before: int
    team2_score_before: int
    team1_score_after: int
    team2_score_after: int

    @property
    def score_delta(self) -> int:
        """تغییر امتیاز گروه خواننده در این دور (مثبت یا منفی)."""
        if self.reader_team == 1:
            return self.team1_score_after - self.team1_score_before
        return self.team2_score_after - self.team2_score_before
