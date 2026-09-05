"""
لایه ذخیره‌سازی دائمی (SQLite).

مسئول ذخیره و بازیابی بازی‌ها (جاری و پایان‌یافته)، دورهای هر بازی،
و تنظیمات برنامه. برنامه کاملاً آفلاین است و از SQLite داخل خود گوشی
استفاده می‌کند (بند ۱۳). این ماژول کاملاً مستقل از UI و از منطق
امتیازدهی (game/rules.py) است.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Optional

from models.game import Game
from models.round import Round


class Database:
    """رابط دسترسی به پایگاه‌داده SQLite برنامه."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_directory()
        self._init_schema()

    # --- راه‌اندازی ---

    def _ensure_directory(self) -> None:
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team1_name TEXT NOT NULL,
                    team2_name TEXT NOT NULL,
                    team1_score INTEGER NOT NULL DEFAULT 0,
                    team2_score INTEGER NOT NULL DEFAULT 0,
                    started_at TEXT NOT NULL,
                    finished INTEGER NOT NULL DEFAULT 0,
                    winner_name TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rounds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    round_number INTEGER NOT NULL,
                    reader_team INTEGER NOT NULL,
                    reading_value INTEGER NOT NULL,
                    success INTEGER NOT NULL,
                    kot INTEGER NOT NULL,
                    team1_score_before INTEGER NOT NULL,
                    team2_score_before INTEGER NOT NULL,
                    team1_score_after INTEGER NOT NULL,
                    team2_score_after INTEGER NOT NULL,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            conn.commit()

    # --- ذخیره بازی جاری ---

    def save_game(self, game: Game) -> int:
        """
        بازی و تمام دورهای آن را ذخیره می‌کند (Insert در اولین بار،
        Update در دفعات بعد). این تابع بعد از هر تغییر وضعیت بازی
        (شروع، ثبت دور، Undo) توسط GameEngine فراخوانی می‌شود.
        """
        with self._connect() as conn:
            cur = conn.cursor()
            if game.db_id:
                cur.execute(
                    """
                    UPDATE games
                    SET team1_name=?, team2_name=?, team1_score=?, team2_score=?,
                        finished=?, winner_name=?
                    WHERE id=?
                    """,
                    (
                        game.team1_name,
                        game.team2_name,
                        game.team1_score,
                        game.team2_score,
                        int(game.finished),
                        game.winner_name,
                        game.db_id,
                    ),
                )
                game_id = game.db_id
            else:
                cur.execute(
                    """
                    INSERT INTO games
                        (team1_name, team2_name, team1_score, team2_score,
                         started_at, finished, winner_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        game.team1_name,
                        game.team2_name,
                        game.team1_score,
                        game.team2_score,
                        game.started_at.isoformat(),
                        int(game.finished),
                        game.winner_name,
                    ),
                )
                game_id = cur.lastrowid
                game.db_id = game_id

            # ساده‌ترین و مطمئن‌ترین راه برای هماهنگ نگه‌داشتن دورها:
            # حذف و بازنویسی کامل دورهای همان بازی (تعداد دورها کم است).
            cur.execute("DELETE FROM rounds WHERE game_id=?", (game_id,))
            for r in game.rounds:
                cur.execute(
                    """
                    INSERT INTO rounds
                        (game_id, round_number, reader_team, reading_value, success, kot,
                         team1_score_before, team2_score_before,
                         team1_score_after, team2_score_after)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        game_id,
                        r.round_number,
                        r.reader_team,
                        r.reading_value,
                        int(r.success),
                        int(r.kot),
                        r.team1_score_before,
                        r.team2_score_before,
                        r.team1_score_after,
                        r.team2_score_after,
                    ),
                )
            conn.commit()
            return game_id

    # --- بازیابی ---

    def load_active_game(self) -> Optional[Game]:
        """آخرین بازی ناتمام را برمی‌گرداند (برای دکمه «ادامه بازی»)."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM games WHERE finished=0 ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            return self._row_to_game(row)

    def get_game(self, game_id: int) -> Optional[Game]:
        """یک بازی مشخص (جاری یا پایان‌یافته) را با شناسه‌اش برمی‌گرداند."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
            if row is None:
                return None
            return self._row_to_game(row)

    def list_finished_games(self) -> List[Game]:
        """لیست بازی‌های پایان‌یافته را از جدیدترین به قدیمی‌ترین برمی‌گرداند."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM games WHERE finished=1 ORDER BY id DESC"
            ).fetchall()
            return [self._row_to_game(row) for row in rows]

    def get_game_rounds(self, game_id: int) -> List[Round]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM rounds WHERE game_id=? ORDER BY round_number",
                (game_id,),
            ).fetchall()
            return [self._row_to_round(row) for row in rows]

    def _row_to_game(self, row: sqlite3.Row) -> Game:
        game = Game(
            team1_name=row["team1_name"],
            team2_name=row["team2_name"],
            team1_score=row["team1_score"],
            team2_score=row["team2_score"],
            started_at=datetime.fromisoformat(row["started_at"]),
            finished=bool(row["finished"]),
            winner_name=row["winner_name"],
        )
        game.db_id = row["id"]
        game.rounds = self.get_game_rounds(row["id"])
        return game

    @staticmethod
    def _row_to_round(row: sqlite3.Row) -> Round:
        return Round(
            round_number=row["round_number"],
            reader_team=row["reader_team"],
            reading_value=row["reading_value"],
            success=bool(row["success"]),
            kot=bool(row["kot"]),
            team1_score_before=row["team1_score_before"],
            team2_score_before=row["team2_score_before"],
            team1_score_after=row["team1_score_after"],
            team2_score_after=row["team2_score_after"],
        )

    # --- حذف ---

    def delete_active_game(self) -> None:
        """بازی ناتمام فعلی (در صورت وجود) را کاملاً حذف می‌کند."""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM rounds WHERE game_id IN (SELECT id FROM games WHERE finished=0)"
            )
            conn.execute("DELETE FROM games WHERE finished=0")
            conn.commit()

    def delete_history(self) -> None:
        """تمام بازی‌های پایان‌یافته (تاریخچه) را حذف می‌کند؛ بازی جاری دست‌نخورده می‌ماند."""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM rounds WHERE game_id IN (SELECT id FROM games WHERE finished=1)"
            )
            conn.execute("DELETE FROM games WHERE finished=1")
            conn.commit()

    # --- تنظیمات ---

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key=?", (key,)
            ).fetchone()
            return row[0] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (key, str(value)),
            )
            conn.commit()
