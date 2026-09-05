"""
ابوسطه‌شمار
نقطه ورود اصلی برنامه.

نسخه نهایی: ساختار پروژه، صفحه اصلی، بازی جدید، صفحه بازی، ثبت دور،
تاریخچه دورهای بازی جاری، تاریخچه بازی‌های قبلی، تنظیمات، و ذخیره
دائمی با SQLite.
"""

import os

from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.app import MDApp

from screens.home_screen import HomeScreen
from screens.new_game_screen import NewGameScreen
from screens.game_screen import GameScreen
from screens.round_screen import RoundScreen
from screens.history_screen import HistoryScreen
from screens.games_history_screen import GamesHistoryScreen
from screens.settings_screen import SettingsScreen
from game.game_engine import GameEngine
from database.database import Database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "Vazirmatn-Regular.ttf")


class AbusteApp(MDApp):
    """کلاس اصلی اپلیکیشن ابوسطه‌شمار."""

    persian_font = None
    db = None
    engine = None

    def build(self):
        self.title = "ابوسطه‌شمار"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"

        self._register_persian_font()

        # فاز ۶: دیتابیس SQLite داخل مسیر داده‌های اختصاصی برنامه روی گوشی.
        # این برنامه کاملاً آفلاین کار می‌کند و هیچ نیازی به اینترنت ندارد.
        db_path = os.path.join(self.user_data_dir, "abuste.db")
        self.db = Database(db_path)

        # موتور بازی: منطق امتیازدهی و ذخیره‌سازی از UI جدا نگه داشته می‌شود.
        self.engine = GameEngine(db=self.db)

        # اگر بازی نیمه‌کاره‌ای از قبل ذخیره شده، آن را بارگذاری کن
        # تا دکمه «ادامه بازی» در صفحه اصلی فعال شود.
        active_game = self.db.load_active_game()
        if active_game is not None:
            self.engine.load_game(active_game)

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(NewGameScreen(name="new_game"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(RoundScreen(name="round"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(GamesHistoryScreen(name="games_history"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm

    def get_setting(self, key: str, default=None):
        """میانبر برای خواندن تنظیمات ذخیره‌شده در SQLite (فاز ۸)."""
        return self.db.get_setting(key, default) if self.db else default

    def set_setting(self, key: str, value) -> None:
        if self.db:
            self.db.set_setting(key, value)

    def _register_persian_font(self):
        """
        در صورت وجود فایل فونت فارسی در assets/fonts، آن را ثبت کن.
        اگر فایل موجود نباشد، برنامه از فونت پیش‌فرض سیستم استفاده
        می‌کند (که ممکن است حروف فارسی را به‌خوبی نمایش ندهد).
        """
        if os.path.exists(FONT_PATH):
            LabelBase.register(name="Persian", fn_regular=FONT_PATH)
            self.persian_font = "Persian"
        else:
            self.persian_font = None
            print(
                "هشدار: فونت فارسی در assets/fonts/Vazirmatn-Regular.ttf "
                "پیدا نشد. لطفاً یک فونت فارسی (مثلاً Vazirmatn) اضافه کنید."
            )


if __name__ == "__main__":
    AbusteApp().run()
