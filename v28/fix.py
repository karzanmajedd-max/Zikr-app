#!/usr/bin/env python3
"""Apply the audited v2.8 notification fixes to the v2.7 source archive."""
from pathlib import Path
import re

root = Path("buildsrc")
pkg = root / "app/src/main/java/com/zikr/zikrakan"

def update(path, old, new):
    src = path.read_text(encoding="utf-8")
    assert old in src, f"Missing expected pattern: {path}: {old[:80]}"
    path.write_text(src.replace(old, new, 1), encoding="utf-8")

notifier = pkg / "Notifier.kt"
update(notifier,
    'private const val QUIET = "zikr_quiet_v27"\n',
    '')
update(notifier,
    'fun channelId(p: ZikrPrefs) = "zikr_banner_27_" +\n',
    'fun channelId(p: ZikrPrefs) = (if(p.banner) "zikr_banner_v28_" else "zikr_standard_v28_") +\n')
update(notifier,
    '''        for(snd in listOf(false,true)) for(vib in listOf(false,true)) {
            val p=ZikrPrefs(sound=snd,vibrate=vib)
            val c=NotificationChannel(channelId(p),"زیکرەکان • بانەری شاشە",NotificationManager.IMPORTANCE_HIGH)''',
    '''        for(banner in listOf(false,true)) for(snd in listOf(false,true)) for(vib in listOf(false,true)) {
            val p=ZikrPrefs(sound=snd,vibrate=vib,banner=banner)
            val importance=if(banner) NotificationManager.IMPORTANCE_HIGH else NotificationManager.IMPORTANCE_DEFAULT
            val label=if(banner) "زیکرەکان • بانەری شاشە" else "زیکرەکان • ئاگادارکردنەوە"
            val c=NotificationChannel(channelId(p),label,importance)''')
update(notifier,
    '''        val quiet=NotificationChannel(QUIET,"زیکرەکان • تۆماری ئاگادارکردنەوە",NotificationManager.IMPORTANCE_LOW)
        quiet.setSound(null,null);quiet.enableVibration(false);quiet.lockscreenVisibility=Notification.VISIBILITY_PUBLIC
        nm.createNotificationChannel(quiet)
''',
    '')
old_show = '''        // Custom banner only when user explicitly enables the banner and grants Android's overlay permission.
        if(p.banner&&hasOverlay(app)) {
            Overlay.show(app,d,onFail={post(app,channelId(p),d,id)},onClosed={})
            alert(app,p)
            post(app,QUIET,d,id)
        } else {
            post(app,channelId(p),d,id)
        }'''
new_show = '''        // ALWAYS post a real system notification, even when the device allows overlays.
        // v2.7 used a LOW channel whenever overlay permission was granted, which could
        // suppress the system heads-up banner. The overlay now supplements, never replaces it.
        post(app,channelId(p),d,id)
        if(p.banner && hasOverlay(app)) {
            Overlay.show(app,d,
                onFail={ /* System notification is already posted; do not duplicate it. */ },
                onClosed={
                    app.getSystemService(NotificationManager::class.java).cancel(id)
                })
        }'''
update(notifier, old_show, new_show)
# Android owns notification sound and vibration; never manually duplicate them.
src = notifier.read_text(encoding="utf-8")
src = re.sub(r'    private fun alert\(ctx:Context,p:ZikrPrefs\) \{.*?\n    \}\n    fun show\(', '    fun show(', src, flags=re.S, count=1)
assert 'private fun alert(' not in src
notifier.write_text(src, encoding="utf-8")

overlay = pkg / "Overlay.kt"
update(overlay, 'private val auto = Runnable { dismiss() }',
              'private val auto = Runnable { dismiss(autoClosed = true) }')
update(overlay,
    '''                manager.addView(view, lp)
                view.animate()''',
    '''                manager.addView(view, lp)
                app.getSharedPreferences("zikr_state", Context.MODE_PRIVATE)
                    .edit().remove("overlay_error").apply()
                view.animate()''')
update(overlay,
    '''            } catch (e: Exception) {
                current = null
                onFail()
            }''',
    '''            } catch (e: Exception) {
                app.getSharedPreferences("zikr_state", Context.MODE_PRIVATE)
                    .edit().putString("overlay_error", e.javaClass.simpleName + ": " + (e.message ?: "unknown")).apply()
                current = null
                onFail()
            }''')
update(overlay, '    fun dismiss() {\n', '    fun dismiss(autoClosed: Boolean = false) {\n')
update(overlay, '        cb?.invoke()\n', '        if (!autoClosed) cb?.invoke()\n')
update(overlay,
    'handler.postDelayed(auto, 14_000) // پاراستن: دوای ١ خولەک خۆی دادەخرێت',
    'handler.postDelayed(auto, 14_000) // Auto-hide card; keep notification in the shade.')

main = pkg / "MainActivity.kt"
update(main,
    '''            o.put("overlay",Notifier.hasOverlay(applicationContext))
            o.put("exactAlarm",Scheduler.canExact(applicationContext))''',
    '''            o.put("overlay",Notifier.hasOverlay(applicationContext))
            o.put("overlayError",getSharedPreferences("zikr_state",MODE_PRIVATE).getString("overlay_error",""))
            o.put("exactAlarm",Scheduler.canExact(applicationContext))''')

scheduler = pkg / "Scheduler.kt"
update(scheduler,
    '''        if (canExact(ctx)) {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pi)
        } else {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pi)
        }''',
    '''        try {
            if (canExact(ctx)) {
                am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pi)
            } else {
                am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pi)
            }
        } catch (_: SecurityException) {
            // Exact-alarm permission might have been revoked between the check and scheduling.
            try { am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pi) }
            catch (_: SecurityException) { /* user may need to change OS settings */ }
        }''')

html = root / "app/src/main/assets/index.html"
update(html,
    "    if(!s.overlay) issues.push('• بۆ پیشاندانی کارتی زیکر لەسەر ئەپەکانی دیکە، ڕێگەی کارتی سەرشاشە چالاک بکە.');",
    "    if(!s.overlay) issues.push('• بۆ پیشاندانی کارتی زیکر لەسەر ئەپەکانی دیکە، ڕێگەی کارتی سەرشاشە چالاک بکە.');\n    if(s.overlayError) issues.push('• هەڵەی دوایین بانەری سەرشاشە: '+s.overlayError);")

gradle = root / "app/build.gradle.kts"
update(gradle, 'versionCode = 27\n        versionName = "2.7"',
                'versionCode = 28\n        versionName = "2.8"')
update(gradle,
    '    buildTypes { release { isMinifyEnabled = false } }',
    '''    defaultConfig { testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner" }
    buildTypes { release { isMinifyEnabled = false } }''')
gradle.write_text(gradle.read_text(encoding="utf-8") + '''
dependencies {
    androidTestImplementation("androidx.test:runner:1.6.2")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
}
''',encoding="utf-8")

test = root / "app/src/androidTest/java/com/zikr/zikrakan/NotificationIntegrationTest.kt"
test.parent.mkdir(parents=True, exist_ok=True)
test.write_text(r'''package com.zikr.zikrakan

import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class NotificationIntegrationTest {
    private val ctx: Context get() = InstrumentationRegistry.getInstrumentation().targetContext
    private val nm: NotificationManager get() = ctx.getSystemService(NotificationManager::class.java)

    @Test fun schedulesEvery45MinutesUntil22() {
        val points = Scheduler.slots(ZikrPrefs())
        assertEquals(21, points.size)
        assertEquals(7*60, points.first())
        assertEquals(22*60, points.last())
    }

    @Test fun bannerNotificationRemainsHighImportance() {
        nm.cancelAll()
        Notifier.show(ctx, ZikrPrefs(banner=true, sound=false, vibrate=true),
            Notifier.Dhikr("سُبْحَانَ اللَّهِ", "پاکی بۆ خوا", ""))
        val active = nm.activeNotifications
        assertTrue("system notification must exist even with banner setting ON", active.isNotEmpty())
        val channel = nm.getNotificationChannel(active.last().notification.channelId)
        assertNotNull(channel)
        assertEquals(NotificationManager.IMPORTANCE_HIGH, channel.importance)
        assertEquals("سُبْحَانَ اللَّهِ", active.last().notification.extras.getString("android.title"))
    }

    @Test fun tapActionDismissesWithoutOpeningActivity() {
        nm.cancelAll()
        Notifier.show(ctx, ZikrPrefs(banner=false), Notifier.Dhikr("test", "تاقیکردنەوە", ""))
        val id = nm.activeNotifications.last().id
        ctx.sendBroadcast(Intent(ctx, DismissReceiver::class.java).putExtra("id", id))
        Thread.sleep(500)
        assertFalse(nm.activeNotifications.any { it.id == id })
    }
}
''',encoding="utf-8")
print("Patched v2.8 and added 3 Android instrumented tests.")
