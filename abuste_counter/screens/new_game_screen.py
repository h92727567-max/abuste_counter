"""صفحه شروع بازی جدید: دریافت نام دو گروه."""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from utils.persian_text import fa

KV = """
<NewGameScreen>:
    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(18)

        Label:
            text: root.txt_title
            font_size: "24sp"
            bold: True
            halign: "center"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(50)
            font_name: root.persian_font or "Roboto"

        Label:
            text: root.txt_team1_label
            halign: "right"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(26)
            font_name: root.persian_font or "Roboto"

        TextInput:
            id: team1_input
            hint_text: root.txt_team1_hint
            multiline: False
            size_hint_y: None
            height: dp(52)
            font_size: "18sp"
            halign: "right"
            font_name: root.persian_font or "Roboto"

        Label:
            text: root.txt_team2_label
            halign: "right"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(26)
            font_name: root.persian_font or "Roboto"

        TextInput:
            id: team2_input
            hint_text: root.txt_team2_hint
            multiline: False
            size_hint_y: None
            height: dp(52)
            font_size: "18sp"
            halign: "right"
            font_name: root.persian_font or "Roboto"

        Widget:

        Button:
            text: root.txt_start
            size_hint_y: None
            height: dp(60)
            font_size: "18sp"
            font_name: root.persian_font or "Roboto"
            on_release: root.start_game()

        Button:
            text: root.txt_back
            size_hint_y: None
            height: dp(48)
            font_name: root.persian_font or "Roboto"
            on_release: root.go_back()
"""

Builder.load_string(KV)


class NewGameScreen(Screen):
    """دریافت نام دو گروه و شروع بازی جدید (طبق بند ۴)."""

    txt_title = StringProperty(fa("شروع بازی جدید"))
    txt_team1_label = StringProperty(fa("نام گروه اول:"))
    txt_team2_label = StringProperty(fa("نام گروه دوم:"))
    txt_team1_hint = StringProperty(fa("گروه ۱"))
    txt_team2_hint = StringProperty(fa("گروه ۲"))
    txt_start = StringProperty(fa("شروع بازی"))
    txt_back = StringProperty(fa("بازگشت"))
    persian_font = StringProperty(allownone=True)

    def on_pre_enter(self, *args):
        app = self._get_app()
        self.persian_font = app.persian_font
        self.ids.team1_input.text = ""
        self.ids.team2_input.text = ""

    @staticmethod
    def _get_app():
        from kivymd.app import MDApp
        return MDApp.get_running_app()

    def start_game(self):
        app = self._get_app()
        team1 = self.ids.team1_input.text.strip() or "گروه ۱"
        team2 = self.ids.team2_input.text.strip() or "گروه ۲"
        app.engine.start_new_game(team1, team2)
        self.manager.current = "game"

    def go_back(self):
        self.manager.current = "home"
