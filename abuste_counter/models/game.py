"""مدل داده یک بازی کامل (شامل تاریخچه دورها)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from models.round import Round


@dataclass
class Game:
    """وضعیت کامل یک بازی جاری یا پایان‌یافته."""

    team1_name: str
    team2_name: str
    team1_score: int = 0
    team2_score: int = 0
    rounds: List[Round] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    finished: bool = False
    winner_name: Optional[str] = None
    db_id: Optional[int] = None  # شناسه ردیف در SQLite (فاز ۶)
