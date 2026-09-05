"""
صفحه اصلی بازی (Gameplay).

نمایش زنده امتیاز دو گروه، آخرین دور، و دکمه‌های «ثبت دور جدید»،
«لغو آخرین دور» و «تاریخچه بازی». وقتی بازی تمام شود (طبق بند ۱۲)،
بنر برنده نمایش داده می‌شود.
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty

from utils.persian_text import fa

KV = """
<GameScreen>:
    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(14)

        BoxLayout:
            orientation: "horizontal"
            spacing: dp(12)
            size_hint_y: None
            height: dp(150)

            BoxLayout:
                orientation: "vertical"
                padding: dp(12)
                canvas.before:
                    Color:
                        rgba: (0.85, 1.0, 0.9, 1) if root.leader == 1 else (1, 1, 1, 1)
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
                    color: 0.2, 0.2, 0.2, 1
                    font_name: root.persian_font or "Roboto"
                Label:
                    text: root.team1_score
                    font_size: "40sp"
                    bold: True
                    color: 0.0, 0.5, 0.45, 1

            BoxLayout:
                orientation: "vertical"
                padding: dp(12)
                canvas.before:
                    Color:
                        rgba: (0.85, 1.0, 0.9, 1) if root.leader == 2 else (1, 1, 1, 1)
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
                    color: 0.2, 0.2, 0.2, 1
                    font_name: root.persian_font or "Roboto"
                Label:
                    text: root.team2_score
                    font_size: "40sp"
                    bold: True
                    color: 0.75, 0.25, 0.2, 1

        Label:
            text: root.last_round_text
            halign: "center"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(30)
            color: 0.35, 0.35, 0.35, 1
            font_name: root.persian_font or "Roboto"

        Widget:

        Button:
            text: root.txt_new_round
            font_size: "20sp"
            size_hint_y: None
            height: dp(64)
            disabled: root.is_finished
            font_name: root.persian_font or "Roboto"
            on_release: root.on_new_round()

        Button:
            text: root.txt_undo
            size_hint_y: None
            height: dp(52)
            disabled: not root.has_rounds
            font_name: root.persian_font or "Roboto"
            on_release: root.on_undo()

        Button:
            text: root.txt_history
            size_hint_y: None
            height: dp(52)
            font_name: root.persian_font or "Roboto"
            on_release: root.on_history()

        Button:
            text: root.txt_home
            size_hint_y: None
            height: dp(48)
            font_name: root.persian_font or "Roboto"
            on_release: root.go_home()
"""

Builder.load_string(KV)


class GameScreen(Screen):
    """صفحه اصلی نمایش بازی جاری."""

    team1_name = StringProperty(fa("گروه اول"))
    team2_name = StringProperty(fa("گروه دوم"))
    team1_score = StringProperty("0")
    team2_score = StringProperty("0")
    last_round_text = StringProperty("")
    leader = 0  # 0 = مساوی, 1 یا 2

    txt_new_round = StringProperty(fa("ثبت دور جدید"))
    txt_undo = StringProperty(fa("لغو آخرین دور"))
    txt_history = StringProperty(fa("تاریخچه دورها"))
    txt_home = StringProperty(fa("بازگشت به صفحه اصلی"))

    has_rounds = BooleanProperty(False)
    is_finished = BooleanProperty(False)
    persian_font = StringProperty(allownone=True)

    def on_pre_enter(self, *args):
        self.persian_font = self._get_app().persian_font
        self.refresh()

    @staticmethod
    def _get_app():
        from kivymd.app import MDApp
        return MDApp.get_running_app()

    def refresh(self):
        """وضعیت صفحه را از روی GameEngine به‌روزرسانی می‌کند."""
        game = self._get_app().engine.game
        if game is None:
            return

        self.team1_name = fa(game.team1_name)
        self.team2_name = fa(game.team2_name)
        self.team1_score = str(game.team1_score)
        self.team2_score = str(game.team2_score)
        self.has_rounds = len(game.rounds) > 0
        self.is_finished = game.finished

        if game.team1_score > game.team2_score:
            self.leader = 1
        elif game.team2_score > game.team1_score:
            self.leader = 2
        else:
            self.leader = 0

        if game.rounds:
            last = game.rounds[-1]
            reader = game.team1_name if last.reader_team == 1 else game.team2_name
            result = "موفق" if last.success else "ناموفق"
            self.last_round_text = fa(
                f"آخرین دور: {reader} - {result} "
                f"(خواندن {last.reading_value}) -> {last.score_delta:+d}"
            )
        else:
            self.last_round_text = fa("هنوز دوری ثبت نشده است")

        if game.finished:
            self._show_winner_popup(game)

    def _show_winner_popup(self, game):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        text = fa(
            f"🏆 بازی تمام شد\n"
            f"برنده: {game.winner_name}\n"
            f"امتیاز نهایی: {game.team1_name} {game.team1_score} - "
            f"{game.team2_score} {game.team2_name}"
        )
        box = BoxLayout(orientation="vertical", padding=16, spacing=12)
        lbl = Label(text=text, halign="center", valign="middle", font_name=self.persian_font or "Roboto")
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        box.add_widget(lbl)

        btn = Button(text=fa("بازی جدید"), size_hint_y=None, height="52dp", font_name=self.persian_font or "Roboto")
        box.add_widget(btn)

        popup = Popup(title=fa("پایان بازی"), content=box, size_hint=(0.9, 0.55), auto_dismiss=False)
        btn.bind(on_release=lambda *_: self._start_new_from_popup(popup))
        popup.open()

    def _start_new_from_popup(self, popup):
        popup.dismiss()
        self.manager.current = "new_game"

    # --- دکمه‌ها ---

    def on_new_round(self):
        self.manager.current = "round"

    def on_undo(self):
        """طبق بند ۱۱: قبل از لغو آخرین دور، تأیید کاربر گرفته می‌شود."""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        box = BoxLayout(orientation="vertical", padding=16, spacing=12)
        lbl = Label(
            text=fa("آیا مطمئن هستید؟\nآخرین دور حذف خواهد شد."),
            halign="center",
            valign="middle",
            font_name=self.persian_font or "Roboto",
        )
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        box.add_widget(lbl)

        btn_row = BoxLayout(size_hint_y=None, height="52dp", spacing=10)
        cancel_btn = Button(text=fa("انصراف"), font_name=self.persian_font or "Roboto")
        confirm_btn = Button(text=fa("حذف آخرین دور"), font_name=self.persian_font or "Roboto")
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        box.add_widget(btn_row)

        popup = Popup(
            title=fa("لغو آخرین دور"),
            content=box,
            size_hint=(0.85, 0.4),
        )
        cancel_btn.bind(on_release=popup.dismiss)
        confirm_btn.bind(on_release=lambda *_: self._confirm_undo(popup))
        popup.open()

    def _confirm_undo(self, popup):
        popup.dismiss()
        self._get_app().engine.undo_last_round()
        self.refresh()

    def on_history(self):
        history_screen = self.manager.get_screen("history")
        history_screen.game_id = None
        history_screen.return_screen = "game"
        self.manager.current = "history"

    def go_home(self):
        self.manager.current = "home"
