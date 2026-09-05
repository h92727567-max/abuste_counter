"""
ابزار نمایش صحیح فارسی/عربی در Kivy.

نام‌های گروه به شکل خام (logical text) ذخیره می‌شوند و فقط هنگام نمایش
با arabic_reshaper + python-bidi شکل‌دهی می‌شوند. این کار از دوباره‌-شکل‌دهی
نام‌ها جلوگیری می‌کند.
"""

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _SHAPING_AVAILABLE = True
except ImportError:
    _SHAPING_AVAILABLE = False


def fa(text: str) -> str:
    """متن خام فارسی/عربی را برای نمایش در ویجت‌های Kivy آماده می‌کند."""
    if not text or not _SHAPING_AVAILABLE:
        return text
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return text
