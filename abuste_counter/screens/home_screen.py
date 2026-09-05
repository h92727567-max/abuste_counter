"""
صفحه اصلی برنامه ابوسطه‌شمار.

نمایش دو کارت گروه، امتیاز فعلی، و منوی اصلی ناوبری
(شروع بازی جدید / ادامه بازی / تاریخچه بازی‌ها / تنظیمات).

این صفحه فقط مسئول نمایش است. منطق واقعی (موتور امتیازدهی، بارگذاری
از دیتابیس و ...) در فازهای بعدی به توابع on_* متصل می‌شود.
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty

from utils.persian_text import fa

KV = """
<HomeScreen>:
    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(16)

        Label:
            text: root.title_text
            font_size: "28sp"
            bold: True
            halign: "center"
            valign: "middle"
            text_size: self.size
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(60)
            font_name: root.persian_font or "Roboto"

        BoxLayout:
            orientation: "horizontal"
            spacing: dp(12)
            size_hint_y: None
            height: dp(150)

            BoxLayout:
                id: team1_card
                orientation: "vertical"
                padding: dp(14)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(18)]
                Label:
                    text: root.team1_name
                    font_size: "18sp"
                    halign: "center"
                    valign: "middle"
                    text_size: self.size
                    color: 0.25, 0.25, 0.25, 1
                    font_name: root.persian_font or "Roboto"
                Label:
                    text: root.team1_score
                    font_size: "40sp"
                    bold: True
                    color: 0.0, 0.5, 0.45, 1

            BoxLayout:
                id: team2_card
                orientation: "vertical"
                padding: dp(14)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(18)]
                Label:
                    text: root.team2_name
                    font_size: "18sp"
                    halign: "center"
                    valign: "middle"
                    text_size: self.size
                    color: 0.25, 0.25, 0.25, 1
                    font_name: root.persian_font or "Roboto"
                Label:
                    text: root.team2_score
                    font_size: "40sp"
                    bold: True
                    color: 0.75, 0.25, 0.2, 1

        Widget:
            size_hint_y: None
            height: dp(8)

        Button:
            text: root.btn_new_game
            font_size: "20sp"
            size_hint_y: None
            height: dp(64)
            font_name: root.persian_font or "Roboto"
            on_release: root.on_new_game()

        Button:
            text: root.btn_continue
            font_size: "18sp"
            size_hint_y: None
            height: dp(56)
            disabled: not root.has_saved_game
            font_name: root.persian_font or "Roboto"
            on_release: root.on_continue_game()

        Button:
            text: root.btn_history
            font_size: "18sp"
            size_hint_y: None
            height: dp(56)
            font_name: root.persian_font or "Roboto"
            on_release: root.on_history()

        Button:
            text: root.btn_settings
            font_size: "18sp"
            size_hint_y: None
            height: dp(56)
            font_name: root.persian_font or "Roboto"
            on_release: root.on_settings()

        Widget:
"""

Builder.load_string(KV)


class HomeScreen(Screen):
    """صفحه اصلی: دو کارت گروه + منوی ناوبری اصلی."""

    title_text = StringProperty(fa("ابوسطه‌شمار"))
    team1_name = StringProperty(fa("گروه اول"))
    team2_name = StringProperty(fa("گروه دوم"))
    team1_score = StringProperty("0")
    team2_score = StringProperty("0")

    btn_new_game = StringProperty(fa("شروع بازی جدید"))
    btn_continue = StringProperty(fa("ادامه بازی"))
    btn_history = StringProperty(fa("تاریخچه بازی‌ها"))
    btn_settings = StringProperty(fa("تنظیمات"))

    has_saved_game = BooleanProperty(False)  # در فاز ۶ (SQLite) واقعی می‌شود
    persian_font = StringProperty(allownone=True)

    def on_pre_enter(self, *args):
        """هر بار قبل از ورود به این صفحه، وضعیت را به‌روزرسانی کن."""
        app = self._get_app()
        if app is not None:
            self.persian_font = app.persian_font
            game = app.engine.game
            if game and not game.finished:
                self.has_saved_game = True
                self.team1_name = fa(game.team1_name)
                self.team2_name = fa(game.team2_name)
                self.team1_score = str(game.team1_score)
                self.team2_score = str(game.team2_score)
            else:
                self.has_saved_game = False
                self.team1_name = fa("گروه اول")
                self.team2_name = fa("گروه دوم")
                self.team1_score = "0"
                self.team2_score = "0"
        # TODO فاز ۶: بررسی وجود بازی ذخیره‌شده در SQLite (بعد از بستن برنامه)
        # self.has_saved_game = database.has_active_game()

    @staticmethod
    def _get_app():
        from kivymd.app import MDApp
        return MDApp.get_running_app()

    # --- دکمه‌های ناوبری (منطق واقعی در فازهای بعدی اضافه می‌شود) ---

    def on_new_game(self):
        self.manager.current = "new_game"

    def on_continue_game(self):
        if self.has_saved_game:
            self.manager.current = "game"

    def on_history(self):
        self.manager.current = "games_history"

    def on_settings(self):
        self.manager.current = "settings"
