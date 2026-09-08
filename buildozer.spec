[app]

title = Lala AI
package.name = lalaai
package.domain = org.lala
source.dir = .
source.include_exts = py,txt,png,jpg,kv
version = 1.0

requirements = python3,kivy,plyer

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,RECORD_AUDIO

[buildozer]

log_level = 2
warn_on_root = 1

[app:android]

android.api = 35
android.minapi = 23
