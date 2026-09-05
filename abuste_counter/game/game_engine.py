"""
موتور بازی ابوسطه.

مدیریت وضعیت یک بازی جاری: شروع بازی، ثبت دور جدید، لغو آخرین دور،
و تشخیص پایان بازی. این کلاس هیچ وابستگی به رابط کاربری یا دیتابیس
ندارد (دیتابیس در فاز ۶ از طریق این کلاس یا موازی با آن استفاده می‌شود).
"""

from typing import Optional

from game.rules import AbusteRules
from models.game import Game
from models.round import Round


class GameEngineError(Exception):
    """خطای مربوط به عملیات نامعتبر در موتور بازی."""


class GameEngine:
    """مدیریت‌کننده وضعیت یک بازی جاری ابوسطه."""

    def __init__(self, db=None):
        self.game: Optional[Game] = None
        self.db = db  # فاز ۶: در صورت وجود، بعد از هر تغییر وضعیت ذخیره می‌کند

    # --- شروع بازی ---

    def start_new_game(self, team1_name: str, team2_name: str) -> Game:
        """یک بازی جدید با نام گروه‌های داده‌شده می‌سازد و آن را فعال می‌کند."""
        team1_name = (team1_name or "").strip() or "گروه ۱"
        team2_name = (team2_name or "").strip() or "گروه ۲"

        # اگر بازی ناتمام قبلی در دیتابیس وجود دارد، جای خودش را به این
        # بازی جدید می‌دهد (طبق بند ۴: شروع بازی جدید یعنی از صفر).
        if self.db is not None:
            self.db.delete_active_game()

        self.game = Game(team1_name=team1_name, team2_name=team2_name)
        self._persist()
        return self.game

    def load_game(self, game: Game) -> None:
        """یک بازی موجود (بارگذاری‌شده از SQLite در شروع برنامه) را فعال می‌کند."""
        self.game = game

    def rename_teams(self, team1_name: str, team2_name: str) -> None:
        """نام گروه‌های بازی جاری را تغییر می‌دهد (فاز ۸: تنظیمات)."""
        if self.game is None:
            raise GameEngineError("هیچ بازی فعالی وجود ندارد")
        team1_name = (team1_name or "").strip()
        team2_name = (team2_name or "").strip()
        if team1_name:
            self.game.team1_name = team1_name
        if team2_name:
            self.game.team2_name = team2_name
        self._persist()

    def _persist(self) -> None:
        """در صورت وجود دیتابیس، وضعیت فعلی بازی را ذخیره می‌کند."""
        if self.db is not None and self.game is not None:
            self.db.save_game(self.game)

    # --- ثبت دور ---

    def add_round(self, reader_team: int, reading_value: int, success: bool, kot: bool) -> Round:
        """
        یک دور جدید را محاسبه و ثبت می‌کند و امتیاز گروه خواننده را به‌روزرسانی می‌کند.

        Raises:
            GameEngineError: اگر بازی فعالی وجود نداشته باشد یا قبلاً تمام شده باشد.
            ValueError: اگر ورودی‌ها نامعتبر باشند (از AbusteRules).
        """
        if self.game is None:
            raise GameEngineError("هیچ بازی فعالی وجود ندارد")
        if self.game.finished:
            raise GameEngineError("این بازی قبلاً تمام شده است")
        if reader_team not in (1, 2):
            raise ValueError("گروه خواننده باید ۱ یا ۲ باشد")

        team1_delta, team2_delta = AbusteRules.calculate_round_deltas(
            reader_team=reader_team,
            reading_value=reading_value,
            success=success,
            kot=kot,
        )

        before1 = self.game.team1_score
        before2 = self.game.team2_score

        # در شکست خواننده، فقط امتیاز حریف اضافه می‌شود؛
        # امتیاز گروه خواننده هرگز منفی نمی‌شود.
        self.game.team1_score += team1_delta
        self.game.team2_score += team2_delta

        round_obj = Round(
            round_number=len(self.game.rounds) + 1,
            reader_team=reader_team,
            reading_value=reading_value,
            success=success,
            kot=kot,
            team1_score_before=before1,
            team2_score_before=before2,
            team1_score_after=self.game.team1_score,
            team2_score_after=self.game.team2_score,
        )
        self.game.rounds.append(round_obj)

        self._update_finished_state()
        self._persist()
        return round_obj

    # --- لغو آخرین دور ---

    def undo_last_round(self) -> Optional[Round]:
        """آخرین دور را حذف کرده و امتیازها را به وضعیت قبل برمی‌گرداند."""
        if self.game is None or not self.game.rounds:
            return None

        last_round = self.game.rounds.pop()
        self.game.team1_score = last_round.team1_score_before
        self.game.team2_score = last_round.team2_score_before
        self.game.finished = False
        self.game.winner_name = None
        self._persist()
        return last_round

    # --- پایان بازی ---

    def _update_finished_state(self) -> None:
        winner = AbusteRules.check_winner(self.game.team1_score, self.game.team2_score)
        if winner is not None:
            self.game.finished = True
            self.game.winner_name = (
                self.game.team1_name if winner == 1 else self.game.team2_name
            )
        else:
            self.game.finished = False
            self.game.winner_name = None

    def is_finished(self) -> bool:
        return self.game is not None and self.game.finished
