#!/usr/bin/env python3
"""Zikrakan v3.3 release hardening: remove unused high-risk permission."""
from pathlib import Path

manifest=Path("buildsrc/app/src/main/AndroidManifest.xml")
s=manifest.read_text(encoding="utf-8")
needle='    <uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />\n'
assert s.count(needle)==1
s=s.replace(needle,"")
assert "REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" not in s
manifest.write_text(s,encoding="utf-8")

gradle=Path("buildsrc/app/build.gradle.kts")
g=gradle.read_text(encoding="utf-8")
assert 'versionCode = 32\n        versionName = "3.2"' in g
g=g.replace('versionCode = 32\n        versionName = "3.2"',
            'versionCode = 33\n        versionName = "3.3"')
assert "isMinifyEnabled = false" in g
gradle.write_text(g,encoding="utf-8")

# Keep the overlay permission because it is a genuine user-requested function.
# Keep exact alarms for the user's selected precise dhikr schedule.
print("Security checks: removed unused battery exemption permission; retained explicitly consented overlay/exact alarms.")
