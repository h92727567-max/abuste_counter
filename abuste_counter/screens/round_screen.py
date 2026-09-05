"""
صفحه ثبت دور جدید.

کاربر گروه خواننده، مقدار خواندن (۵ تا ۹)، نتیجه (موفق/ناموفق) و کوت
را انتخاب می‌کند. قبل از ثبت نهایی، یک پاپ‌آپ تأیید نمایش داده می‌شود
(طبق بند ۸ مشخصات). دکمه ثبت تا وقتی همه فیلدها کامل نشوند غیرفعال است.
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.properties import (
    StringProperty,
    NumericProperty,
    BooleanProperty,
    ObjectProperty,
)

from utils.persian_text import fa
from game.rules import AbusteRules

KV = """
<RoundScreen>:
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

        Label:
            text: root.txt_title
            font_size: "24sp"
            bold: True
            halign: "center"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(48)
            color: 0.1, 0.1, 0.1, 1
            font_name: root.persian_font or "Roboto"

        Label:
            text: root.txt_reader_label
            halign: "right"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(28)
            font_name: root.persian_font or "Roboto"

        BoxLayout:
            size_hint_y: None
            height: dp(56)
            spacing: dp(10)

            ToggleButton:
                text: root.team1_name
                group: "reader"
                state: "down" if root.reader_team == 1 else "normal"
                font_name: root.persian_font or "Roboto"
                on_release: root.set_reader_team(1)

            ToggleButton:
                text: root.team2_name
                group: "reader"
                state: "down" if root.reader_team == 2 else "normal"
                font_name: root.persian_font or "Roboto"
                on_release: root.set_reader_team(2)

        Label:
            text: root.txt_reading_label
            halign: "right"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(28)
            font_name: root.persian_font or "Roboto"

        GridLayout:
            id: reading_grid
            cols: 5
            size_hint_y: None
            height: dp(56)
            spacing: dp(6)

        Label:
            text: root.txt_result_label
            halign: "right"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(28)
            font_name: root.persian_font or "Roboto"

        BoxLayout:
            size_hint_y: None
            height: dp(56)
            spacing: dp(10)

            ToggleButton:
                text: root.txt_success
                group: "result"
                state: "down" if root.success is True else "normal"
                font_name: root.persian_font or "Roboto"
                on_release: root.set_result(True)

            ToggleButton:
                text: root.txt_fail
                group: "result"
                state: "down" if root.success is False else "normal"
                font_name: root.persian_font or "Roboto"
                on_release: root.set_result(False)

        BoxLayout:
            size_hint_y: None
            height: dp(56)
            spacing: dp(10)

            Label:
                text: root.txt_kot_label
                halign: "right"
                valign: "middle"
                text_size: self.size
                font_name: root.persian_font or "Roboto"

            ToggleButton:
                text: (root.txt_kot_yes if root.kot else root.txt_kot_no)
                size_hint_x: 0.5
                font_name: root.persian_font or "Roboto"
                on_release: root.kot = not root.kot

        Widget:

        Label:
            text: root.error_text
            color: 0.75, 0.1, 0.1, 1
            size_hint_y: None
            height: dp(24) if root.error_text else 0
            font_name: root.persian_font or "Roboto"

        Button:
            text: root.txt_submit
            size_hint_y: None
            height: dp(60)
            font_size: "18sp"
            disabled: not root.is_valid
            font_name: root.persian_font or "Roboto"
            on_release: root.open_confirmation()

        Button:
            text: root.txt_back
            size_hint_y: None
            height: dp(48)
            font_name: root.persian_font or "Roboto"
            on_release: root.go_back()
"""

Builder.load_string(KV)


class RoundScreen(Screen):
    """صفحه ثبت دور جدید."""

    txt_title = StringProperty(fa("ثبت دور جدید"))
    txt_reader_label = StringProperty(fa("گروه خواننده:"))
    txt_reading_label = StringProperty(fa("مقدار خواندن:"))
    txt_result_label = StringProperty(fa("نتیجه:"))
    txt_success = StringProperty(fa("موفق"))
    txt_fail = StringProperty(fa("ناموفق"))
    txt_kot_label = StringProperty(fa("کوت:"))
    txt_kot_yes = StringProperty(fa("بله"))
    txt_kot_no = StringProperty(fa("خیر"))
    txt_submit = StringProperty(fa("تأیید ثبت"))
    txt_back = StringProperty(fa("بازگشت"))

    team1_name = StringProperty(fa("گروه اول"))
    team2_name = StringProperty(fa("گروه دوم"))
    persian_font = StringProperty(allownone=True)

    reader_team = NumericProperty(0)  # 0 = انتخاب نشده, 1 یا 2
    reading_value = NumericProperty(0)  # 0 = انتخاب نشده
    success = ObjectProperty(None, allownone=True)  # None/True/False
    kot = BooleanProperty(False)

    error_text = StringProperty("")

    def on_pre_enter(self, *args):
        app = self._get_app()
        self.persian_font = app.persian_font
        game = app.engine.game
        if game:
            self.team1_name = fa(game.team1_name)
            self.team2_name = fa(game.team2_name)
        self._reset_form()
        self._build_reading_buttons()

    @staticmethod
    def _get_app():
        from kivymd.app import MDApp
        return MDApp.get_running_app()

    def _reset_form(self):
        self.reader_team = 0
        self.reading_value = 0
        self.success = None
        self.kot = False
        self.error_text = ""

    def _build_reading_buttons(self):
        """دکمه‌های ۵ تا ۹ را برای انتخاب مقدار خواندن می‌سازد."""
        grid = self.ids.reading_grid
        grid.clear_widgets()
        from kivy.uix.togglebutton import ToggleButton

        for value in range(AbusteRules.MIN_READING, AbusteRules.MAX_READING + 1):
            btn = ToggleButton(
                text=str(value),
                group="reading",
                font_name=self.persian_font or "Roboto",
            )
            btn.bind(on_release=lambda inst, v=value: self.set_reading_value(v))
            grid.add_widget(btn)

    def set_reader_team(self, team_number: int):
        self.reader_team = team_number

    def set_reading_value(self, value: int):
        self.reading_value = value

    def set_result(self, is_success: bool):
        self.success = is_success

    @property
    def is_valid(self) -> bool:
        """طبق بند ۲۱: دکمه ثبت تا تکمیل همه فیلدها غیرفعال است."""
        return (
            self.reader_team in (1, 2)
            and AbusteRules.is_valid_reading(self.reading_value)
            and self.success is not None
        )

    def open_confirmation(self):
        if not self.is_valid:
            self.error_text = fa("لطفاً همه فیلدها را تکمیل کنید")
            return
        self.error_text = ""

        app = self._get_app()
        try:
            team1_delta, team2_delta = AbusteRules.calculate_round_deltas(
                reader_team=self.reader_team,
                reading_value=self.reading_value,
                success=self.success,
                kot=self.kot,
            )
        except ValueError as exc:
            self.error_text = str(exc)
            return

        reader_name = self.team1_name if self.reader_team == 1 else self.team2_name
        opponent_name = self.team2_name if self.reader_team == 1 else self.team1_name
        reader_delta = team1_delta if self.reader_team == 1 else team2_delta
        opponent_delta = team2_delta if self.reader_team == 1 else team1_delta

        # فاز ۸: اگر کاربر تأیید قبل از ثبت را در تنظیمات غیرفعال کرده باشد،
        # مستقیماً دور را ثبت کن و پاپ‌آپ تأیید را نشان نده.
        confirm_enabled = app.get_setting("confirm_round_enabled", "1") == "1"
        if not confirm_enabled:
            self._submit_round()
            return

        # نام‌ها در مدل خام می‌مانند؛ فقط یک بار، در آخرین مرحله نمایش،
        # کل متن را برای RTL و شکل‌دهی حروف فارسی آماده می‌کنیم.
        result_text = "موفق" if self.success else "ناموفق"
        kot_text = "بله" if self.kot else "خیر"

        if self.success:
            score_line = f"امتیاز {reader_name}: +{reader_delta}"
        else:
            score_line = (
                f"امتیاز {reader_name}: بدون تغییر (0)\\n"
                f"امتیاز {opponent_name}: +{opponent_delta}"
            )

        content_text = fa(
            f"گروه خواننده: {reader_name}\\n"
            f"مقدار خواندن: {self.reading_value}\\n"
            f"نتیجه: {result_text}\\n"
            f"کوت: {kot_text}\\n"
            f"{score_line}"
        )

        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        box = BoxLayout(orientation="vertical", padding=16, spacing=12)
        lbl = Label(
            text=content_text,
            halign="right",
            valign="middle",
            font_name=self.persian_font or "Roboto",
        )
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        box.add_widget(lbl)

        btn_row = BoxLayout(size_hint_y=None, height="52dp", spacing=10)
        confirm_btn = Button(
            text=self.txt_submit, font_name=self.persian_font or "Roboto"
        )
        cancel_btn = Button(
            text=self.txt_back, font_name=self.persian_font or "Roboto"
        )
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        box.add_widget(btn_row)

        popup = Popup(
            title=fa("تأیید ثبت دور"),
            content=box,
            size_hint=(0.9, 0.6),
            title_align="right",
        )
        cancel_btn.bind(on_release=popup.dismiss)
        confirm_btn.bind(on_release=lambda *_: self._confirm_round(popup))
        popup.open()

    def _confirm_round(self, popup):
        popup.dismiss()
        self._submit_round()

    def _submit_round(self):
        app = self._get_app()
        app.engine.add_round(
            reader_team=self.reader_team,
            reading_value=self.reading_value,
            success=self.success,
            kot=self.kot,
        )
        self.manager.current = "game"

    def go_back(self):
        self.manager.current = "game"
