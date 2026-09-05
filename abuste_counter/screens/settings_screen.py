"""
صفحه تنظیمات (بند ۱۶).

شامل: تغییر نام گروه‌های بازی جاری، شروع بازی جدید، حذف تاریخچه
بازی‌های پایان‌یافته، فعال/غیرفعال کردن پاپ‌آپ تأیید قبل از ثبت دور،
و اطلاعات برنامه.
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty

from utils.persian_text import fa

KV = """
<SettingsScreen>:
    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size

    ScrollView:
        BoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(14)
            size_hint_y: None
            height: self.minimum_height

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
                text: root.txt_rename_section
                bold: True
                halign: "right"
                valign: "middle"
                text_size: self.size
                size_hint_y: None
                height: dp(28)
                font_name: root.persian_font or "Roboto"

            TextInput:
                id: team1_input
                hint_text: root.txt_team1_hint
                multiline: False
                size_hint_y: None
                height: dp(50)
                halign: "right"
                font_name: root.persian_font or "Roboto"

            TextInput:
                id: team2_input
                hint_text: root.txt_team2_hint
                multiline: False
                size_hint_y: None
                height: dp(50)
                halign: "right"
                font_name: root.persian_font or "Roboto"

            Button:
                text: root.txt_save_names
                size_hint_y: None
                height: dp(52)
                disabled: not root.has_active_game
                font_name: root.persian_font or "Roboto"
                on_release: root.save_names()

            Widget:
                size_hint_y: None
                height: dp(6)

            Button:
                text: root.txt_new_game
                size_hint_y: None
                height: dp(52)
                font_name: root.persian_font or "Roboto"
                on_release: root.go_new_game()

            BoxLayout:
                size_hint_y: None
                height: dp(52)
                spacing: dp(10)

                Label:
                    text: root.txt_confirm_toggle_label
                    halign: "right"
                    valign: "middle"
                    text_size: self.size
                    font_name: root.persian_font or "Roboto"

                ToggleButton:
                    text: root.txt_confirm_state
                    size_hint_x: 0.4
                    font_name: root.persian_font or "Roboto"
                    on_release: root.toggle_confirm()

            Button:
                text: root.txt_delete_history
                size_hint_y: None
                height: dp(52)
                font_name: root.persian_font or "Roboto"
                on_release: root.confirm_delete_history()

            Widget:
                size_hint_y: None
                height: dp(6)

            Label:
                text: root.txt_about
                halign: "right"
                valign: "middle"
                text_size: self.size
                size_hint_y: None
                height: dp(100)
                color: 0.35, 0.35, 0.35, 1
                font_name: root.persian_font or "Roboto"

            Button:
                text: root.txt_back
                size_hint_y: None
                height: dp(48)
                font_name: root.persian_font or "Roboto"
                on_release: root.go_back()
"""

Builder.load_string(KV)


class SettingsScreen(Screen):
    """صفحه تنظیمات برنامه."""

    txt_title = StringProperty(fa("تنظیمات"))
    txt_rename_section = StringProperty(fa("تغییر نام گروه‌ها (بازی جاری):"))
    txt_team1_hint = StringProperty(fa("نام گروه اول"))
    txt_team2_hint = StringProperty(fa("نام گروه دوم"))
    txt_save_names = StringProperty(fa("ذخیره نام‌ها"))
    txt_new_game = StringProperty(fa("شروع بازی جدید"))
    txt_confirm_toggle_label = StringProperty(fa("تأیید قبل از ثبت دور:"))
    txt_confirm_state = StringProperty(fa("فعال"))
    txt_delete_history = StringProperty(fa("حذف تاریخچه بازی‌ها"))
    txt_about = StringProperty(
        fa(
            "ابوسطه‌شمار — نسخه ۰.۱\n"
            "اپلیکیشن آفلاین شمارش امتیاز بازی ابوسطه.\n"
            "هدف بازی: ۶۲ امتیاز."
        )
    )
    txt_back = StringProperty(fa("بازگشت"))

    has_active_game = BooleanProperty(False)
    persian_font = StringProperty(allownone=True)

    def on_pre_enter(self, *args):
        app = self._get_app()
        self.persian_font = app.persian_font

        game = app.engine.game
        self.has_active_game = game is not None and not game.finished
        if self.has_active_game:
            self.ids.team1_input.text = game.team1_name
            self.ids.team2_input.text = game.team2_name
        else:
            self.ids.team1_input.text = ""
            self.ids.team2_input.text = ""

        confirm_enabled = app.get_setting("confirm_round_enabled", "1") == "1"
        self.txt_confirm_state = fa("فعال") if confirm_enabled else fa("غیرفعال")

    @staticmethod
    def _get_app():
        from kivymd.app import MDApp
        return MDApp.get_running_app()

    def save_names(self):
        if not self.has_active_game:
            return
        app = self._get_app()
        app.engine.rename_teams(
            self.ids.team1_input.text.strip(), self.ids.team2_input.text.strip()
        )

    def go_new_game(self):
        self.manager.current = "new_game"

    def toggle_confirm(self):
        app = self._get_app()
        currently_enabled = app.get_setting("confirm_round_enabled", "1") == "1"
        new_value = "0" if currently_enabled else "1"
        app.set_setting("confirm_round_enabled", new_value)
        self.txt_confirm_state = fa("غیرفعال") if currently_enabled else fa("فعال")

    def confirm_delete_history(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        box = BoxLayout(orientation="vertical", padding=16, spacing=12)
        lbl = Label(
            text=fa("آیا مطمئن هستید؟\nتاریخچه بازی‌های پایان‌یافته حذف خواهد شد."),
            halign="center",
            valign="middle",
            font_name=self.persian_font or "Roboto",
        )
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        box.add_widget(lbl)

        btn_row = BoxLayout(size_hint_y=None, height="52dp", spacing=10)
        cancel_btn = Button(text=fa("انصراف"), font_name=self.persian_font or "Roboto")
        confirm_btn = Button(text=fa("حذف"), font_name=self.persian_font or "Roboto")
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        box.add_widget(btn_row)

        popup = Popup(title=fa("حذف تاریخچه"), content=box, size_hint=(0.85, 0.4))
        cancel_btn.bind(on_release=popup.dismiss)
        confirm_btn.bind(on_release=lambda *_: self._do_delete_history(popup))
        popup.open()

    def _do_delete_history(self, popup):
        popup.dismiss()
        app = self._get_app()
        if app.db:
            app.db.delete_history()

    def go_back(self):
        self.manager.current = "home"
