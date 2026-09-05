"""
صفحه تاریخچه دورهای بازی جاری.

طبق بند ۱۰: برای هر دور نمایش داده می‌شود: شماره دور، گروه خواننده،
مقدار خواندن، موفق/ناموفق، کوت/عادی، و امتیاز هر دو گروه قبل و بعد
از آن دور. دورها به ترتیب شماره نمایش داده می‌شوند.
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp

from utils.persian_text import fa

KV = """
<HistoryScreen>:
    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)

        Label:
            text: root.txt_title
            font_size: "22sp"
            bold: True
            halign: "center"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(46)
            color: 0.1, 0.1, 0.1, 1
            font_name: root.persian_font or "Roboto"

        ScrollView:
            BoxLayout:
                id: rounds_box
                orientation: "vertical"
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height
                padding: (0, dp(4))

        Button:
            text: root.txt_back
            size_hint_y: None
            height: dp(52)
            font_name: root.persian_font or "Roboto"
            on_release: root.go_back()
"""

Builder.load_string(KV)


class HistoryScreen(Screen):
    """نمایش لیست کامل دورهای بازی جاری."""

    txt_title = StringProperty(fa("تاریخچه دورها"))
    txt_back = StringProperty(fa("بازگشت"))
    txt_empty = StringProperty(fa("هنوز دوری ثبت نشده است"))
    persian_font = StringProperty(allownone=True)

    # اگر None باشد، دورهای بازی جاری (از GameEngine) نمایش داده می‌شود.
    # اگر مقدار داشته باشد (شناسه یک بازی پایان‌یافته)، دورهای همان بازی
    # از دیتابیس بارگذاری می‌شود (وقتی از GamesHistoryScreen باز شود).
    game_id = ObjectProperty(None, allownone=True)
    # نامِ صفحه‌ای که باید هنگام «بازگشت» به آن برگردیم.
    return_screen = StringProperty("game")

    def on_pre_enter(self, *args):
        app = self._get_app()
        self.persian_font = app.persian_font
        self._populate()

    @staticmethod
    def _get_app():
        from kivymd.app import MDApp
        return MDApp.get_running_app()

    def _get_game(self):
        app = self._get_app()
        if self.game_id is not None:
            return app.db.get_game(self.game_id) if app.db else None
        return app.engine.game

    def _populate(self):
        box = self.ids.rounds_box
        box.clear_widgets()

        game = self._get_game()
        if game is None or not game.rounds:
            empty_lbl = Label(
                text=self.txt_empty,
                size_hint_y=None,
                height=dp(40),
                halign="center",
                valign="middle",
                font_name=self.persian_font or "Roboto",
            )
            empty_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
            box.add_widget(empty_lbl)
            return

        # طبق بند ۱۰: نمایش به ترتیب شماره دور
        for rnd in game.rounds:
            box.add_widget(self._build_round_card(game, rnd))

    def _build_round_card(self, game, rnd):
        reader_name = game.team1_name if rnd.reader_team == 1 else game.team2_name
        result_text = "موفق" if rnd.success else "ناموفق"
        kot_text = "کوت" if rnd.kot else "عادی"

        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=dp(12),
            spacing=dp(4),
        )
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle

            Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
            card.bind(
                pos=lambda inst, val: setattr(rect, "pos", val),
                size=lambda inst, val: setattr(rect, "size", val),
            )

        header = Label(
            text=fa(f"دور {rnd.round_number} — {reader_name} — {result_text} — {kot_text}"),
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="right",
            valign="middle",
            color=(0.1, 0.1, 0.1, 1),
            font_name=self.persian_font or "Roboto",
        )
        header.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        detail = Label(
            text=fa(
                f"مقدار خواندن: {rnd.reading_value}   |   "
                f"تغییر امتیاز: {rnd.score_delta:+d}"
            ),
            size_hint_y=None,
            height=dp(26),
            halign="right",
            valign="middle",
            color=(0.3, 0.3, 0.3, 1),
            font_name=self.persian_font or "Roboto",
        )
        detail.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        scores = Label(
            text=fa(
                f"{game.team1_name}: {rnd.team1_score_before} → {rnd.team1_score_after}"
                f"   |   "
                f"{game.team2_name}: {rnd.team2_score_before} → {rnd.team2_score_after}"
            ),
            size_hint_y=None,
            height=dp(56),
            halign="right",
            valign="middle",
            color=(0.3, 0.3, 0.3, 1),
            font_name=self.persian_font or "Roboto",
        )
        scores.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        card.add_widget(header)
        card.add_widget(detail)
        card.add_widget(scores)
        return card

    def go_back(self):
        self.manager.current = self.return_screen
