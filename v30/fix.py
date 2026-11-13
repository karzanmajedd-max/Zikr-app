#!/usr/bin/env python3
"""v3.0: one visible banner, reliable tasbih reset, and no duplicate in-app preview."""
from pathlib import Path
import runpy

runpy.run_path("v29/fix.py", run_name="__main__")
root=Path("buildsrc")
pkg=root/"app/src/main/java/com/zikr/zikrakan"

def change(path,old,new):
    original=path.read_text(encoding="utf-8")
    assert original.count(old)==1,(str(path),original.count(old),old[:110])
    path.write_text(original.replace(old,new,1),encoding="utf-8")

html=root/"app/src/main/assets/index.html"
# WebView never installed a WebChromeClient JS confirm handler; its default result is
# false, leaving the reset button inoperative. Reset immediately, save and refresh.
change(html,
    "x('resetBtn').onclick=()=>{if(confirm('ژمێرەر سفر بکرێتەوە؟')){prefs.count=0;store();render()}};",
    "x('resetBtn').onclick=()=>{prefs.count=0;store();x('count').textContent=numerals(0)};")
# An Android test should invoke ONE native notification, not a large HTML preview
# as well. The browser preview is kept for non-Android use only.
change(html,
    "$('mockNotif').classList.add('visible');",
    "$('mockNotif').classList.toggle('visible', !(window.Android&&typeof Android.showTest==='function'));")
change(html,
    "نموونەی زیکرەکە لە سەر شاشە پیشان درا. ئەگەر نۆتیفیکەیشنی سیستەم نەهات، ڕێگەپێدانی نۆتیفیکەیشن لە ڕێکخستنەکانی ئەندرۆید بپشکنە.",
    "تاقیکردنەوەی نۆتیفیکەیشن نێردرا. تەنها یەک بانەر پیشان دەدرێت؛ تۆماری نۆتیفیکەیشنیش لە لیستدا دەمێنێتەوە.")
change(html,
    "شێوازی دەرکەوتنی سەرشاشە و شاشەی قوفڵ بە ڕێکخستنەکانی مۆبایلەکەتەوە بەندە.",
    "کاتێک کارتی تایبەتی سەرشاشە کار دەکات، نۆتیفیکەیشن لە لیستدا دەمێنێتەوە بەبێ بانەری دووبارە. شێوازی دەرکەوتن لە شاشەی قوفڵ بە ڕێکخستنەکانی مۆبایلەکەتەوە بەندە.")

notifier=pkg/"Notifier.kt"
change(notifier,
    'private const val STATE = "zikr_state"',
    'private const val STATE = "zikr_state"\n    private const val SHADE = "zikr_shade_no_popup_v30"')
change(notifier,
    '''        }
    }
    private fun allDhikr(ctx: Context):List<Dhikr> {''',
    '''        }
        // LOW-importance channel stores the dhikr in the notification shade but
        // never launches a second system heads-up over the custom overlay.
        val quiet=NotificationChannel(SHADE,"زیکرەکان • تۆماری بانەر",NotificationManager.IMPORTANCE_LOW)
        quiet.description="تۆماری زیکرەکان کاتێک کارتی تایبەت پیشان دەدرێت"
        quiet.setSound(null,null)
        quiet.enableVibration(false)
        quiet.lockscreenVisibility=Notification.VISIBILITY_PUBLIC
        nm.createNotificationChannel(quiet)
    }
    fun channelForDisplay(p:ZikrPrefs, overlayAllowed:Boolean):String =
        if(p.banner && overlayAllowed) SHADE else channelId(p)
    private fun allDhikr(ctx: Context):List<Dhikr> {''')
# Manual signal is used ONLY for the overlay case; its corresponding LOW
# notification channel is fully silent, so no sound/vibration is duplicated.
feedback= '''    private fun overlayFeedback(ctx:Context,p:ZikrPrefs) {
        if(p.sound) try {
            val attrs=AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_NOTIFICATION)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build()
            val player=MediaPlayer.create(ctx,R.raw.zikr_golden_chime,attrs,AudioManager.AUDIO_SESSION_ID_GENERATE)
            if(player!=null) {
                player.setOnCompletionListener { it.release() }
                player.start()
            }
        } catch (_:Exception) { }
        if(p.vibrate) try {
            val vibrator=ctx.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            vibrator.vibrate(VibrationEffect.createWaveform(longArrayOf(0,180,90,160),-1))
        } catch (_:Exception) { }
    }
'''
change(notifier,
    '    fun show(ctx:Context,p:ZikrPrefs,test:Dhikr?=null) {',
    feedback+'    fun show(ctx:Context,p:ZikrPrefs,test:Dhikr?=null) {')
change(notifier,
    '''        // ALWAYS post a real system notification, even when the device allows overlays.
        // v2.7 used a LOW channel whenever overlay permission was granted, which could
        // suppress the system heads-up banner. The overlay now supplements, never replaces it.
        post(app,channelId(p),d,id)
        if(p.banner && hasOverlay(app)) {
            Overlay.show(app,d,
                onFail={ /* System notification is already posted; do not duplicate it. */ },
                onClosed={
                    app.getSystemService(NotificationManager::class.java).cancel(id)
                })
        }''',
    '''        // Exactly one visible heads-up. Overlay is preferred only with explicit
        // permission; the concurrent system notification remains shade-only (LOW).
        // When overlay is unavailable or fails, fall back to system HIGH channel.
        val overlayAllowed=p.banner && hasOverlay(app)
        if(overlayAllowed) {
            post(app,channelForDisplay(p,true),d,id)
            Overlay.show(app,d,
                onFail={
                    val nm=app.getSystemService(NotificationManager::class.java)
                    nm.cancel(id)
                    post(app,channelId(p),d,id)
                },
                onClosed={ app.getSystemService(NotificationManager::class.java).cancel(id) },
                onShown={ overlayFeedback(app,p) }
            )
        } else {
            post(app,channelId(p),d,id)
        }''')
overlay=pkg/"Overlay.kt"
change(overlay,
    'fun show(ctx: Context, d: Notifier.Dhikr, onFail: () -> Unit, onClosed: () -> Unit) {',
    'fun show(ctx: Context, d: Notifier.Dhikr, onFail: () -> Unit, onClosed: () -> Unit, onShown: () -> Unit = {}) {')
change(overlay,
    '''                onDismiss = onClosed
                handler.postDelayed(auto, 14_000)''',
    '''                onDismiss = onClosed
                onShown()
                handler.postDelayed(auto, 14_000)''')

# Update test semantics. A custom overlay + HIGH notification is the bug.
test=root/"app/src/androidTest/java/com/zikr/zikrakan/NotificationIntegrationTest.kt"
change(test,
    '''    @Test fun bannerNotificationRemainsHighImportance() {''',
    '''    @Test fun overlayUsesQuietNotificationChannelWithoutSecondHeadsUp() {''')
change(test,
    '''        assertEquals(NotificationManager.IMPORTANCE_HIGH, channel.importance)
        assertEquals("سُبْحَانَ اللَّهِ", active.last().notification.extras.getString("android.title"))''',
    '''        assertEquals("Custom overlay must not also create system heads-up",
            NotificationManager.IMPORTANCE_LOW, channel.importance)
        assertEquals(Notifier.channelForDisplay(ZikrPrefs(banner=true),true),
            active.last().notification.channelId)
        assertEquals("سُبْحَانَ اللَّهِ", active.last().notification.extras.getString("android.title"))''')
# Test the native fallback decision independently, without changing app permissions.
change(test,
    '''    @Test fun tapActionDismissesWithoutOpeningActivity() {''',
    '''    @Test fun systemBannerFallbackIsHighImportance() {
        val p=ZikrPrefs(banner=true, sound=false, vibrate=true)
        Notifier.ensureChannels(ctx)
        val id=Notifier.channelForDisplay(p,false)
        assertEquals(Notifier.channelId(p),id)
        assertEquals(NotificationManager.IMPORTANCE_HIGH,nm.getNotificationChannel(id).importance)
    }
    @Test fun tapActionDismissesWithoutOpeningActivity() {''')

gradle=root/"app/build.gradle.kts"
change(gradle,'versionCode = 29\n        versionName = "2.9"',
    'versionCode = 30\n        versionName = "3.0"')
print("Zikrakan 3.0 patched: reset persists without WebView confirm, one banner, Android fallback, and overlay/shade tests.")
