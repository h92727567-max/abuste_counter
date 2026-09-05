"""
صفحه تاریخچه بازی‌های قبلی (پایان‌یافته) — بند ۱۵.

برای هر بازی نمایش داده می‌شود: نام دو گروه، امتیاز نهایی، برنده و
تاریخ. با انتخاب هر بازی، تمام دورهای همان بازی از طریق HistoryScreen
نمایش داده می‌شود.
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.metrics import dp

from utils.persian_text import fa

KV = """
<GamesHistoryScreen>:
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
                id: games_box
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


class GamesHistoryScreen(Screen):
    """لیست بازی‌های پایان‌یافته قبلی."""

    txt_title = StringProperty(fa("تاریخچه بازی‌ها"))
    txt_back = StringProperty(fa("بازگشت"))
    txt_empty = StringProperty(fa("هنوز بازی‌ای به پایان نرسیده است"))
    persian_font = StringProperty(allownone=True)

    def on_pre_enter(self, *args):
        app = self._get_app()
        self.persian_font = app.persian_font
        self._populate()

    @staticmethod
    def _get_app():
        from kivymd.app import MDApp
        return MDApp.get_running_app()

    def _populate(self):
        box = self.ids.games_box
        box.clear_widgets()
        app = self._get_app()
        games = app.db.list_finished_games() if app.db else []

        if not games:
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

        for game in games:
            box.add_widget(self._build_game_card(game))

    def _build_game_card(self, game):
        date_text = game.started_at.strftime("%Y-%m-%d %H:%M")
        card = Button(
            text=fa(
                f"{game.team1_name} × {game.team2_name}\n"
                f"امتیاز: {game.team1_score} - {game.team2_score}\n"
                f"برنده: {game.winner_name}   |   {date_text}"
            ),
            size_hint_y=None,
            height=dp(94),
            halign="center",
            valign="middle",
            font_name=self.persian_font or "Roboto",
        )
        card.bind(
            size=lambda inst, val: setattr(inst, "text_size", (val[0] - dp(20), None))
        )
        card.bind(on_release=lambda inst, g=game: self.open_game(g))
        return card

    def open_game(self, game):
        history_screen = self.manager.get_screen("history")
        history_screen.game_id = game.db_id
        history_screen.return_screen = "games_history"
        self.manager.current = "history"

    def go_back(self):
        self.manager.current = "home"
