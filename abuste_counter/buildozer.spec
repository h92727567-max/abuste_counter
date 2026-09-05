[app]
title = ابوسطه‌شمار
package.name = abustecounter
package.domain = org.abuste

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db

version = 0.1

# نکته: sqlite3 بخشی از کتابخانه استاندارد پایتون است و نیازی به
# افزودن جداگانه به requirements ندارد.
requirements = python3,kivy==2.3.1,kivymd==2.0.0,arabic_reshaper,python-bidi

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
