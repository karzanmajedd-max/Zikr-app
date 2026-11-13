#!/usr/bin/env python3
from pathlib import Path
root=Path("buildsrc")
pkg=root/"app/src/main/java/com/zikr/zikrakan"
def change(path,a,b):
 s=path.read_text(encoding="utf-8")
 assert s.count(a)==1,(str(path),s.count(a),a[:80])
 path.write_text(s.replace(a,b,1),encoding="utf-8")
n=pkg/"Notifier.kt"
change(n,"import android.app.Notification\n","import android.app.Notification\nimport android.app.KeyguardManager\nimport android.os.PowerManager\n")
change(n,'private const val SHADE = "zikr_shade_no_popup_v30"', 'private const val SHADE = "zikr_shade_no_popup_v30"\n    private const val LOCK = "zikr_lock_public_v31_"')
change(n,
'''        nm.createNotificationChannel(quiet)
    }
    fun channelForDisplay''',
'''        nm.createNotificationChannel(quiet)
        for(snd in listOf(false,true)) for(vib in listOf(false,true)) {
            val p=ZikrPrefs(sound=snd,vibrate=vib)
            val c=NotificationChannel(lockId(p),"زیکرەکان • شاشەی قوفڵ",NotificationManager.IMPORTANCE_HIGH)
            c.description="زیکر بە عەرەبی و مانای کوردی لە شاشەی قوفڵ"
            c.lockscreenVisibility=Notification.VISIBILITY_PUBLIC
            c.enableVibration(vib)
            if(vib)c.vibrationPattern=longArrayOf(0,180,90,160)
            if(snd)c.setSound(uri,attrs) else c.setSound(null,null)
            nm.createNotificationChannel(c)
        }
    }
    fun lockId(p:ZikrPrefs)=LOCK+
        (if(p.sound) "sound" else "silent")+(if(p.vibrate) "_vibrate" else "_still")
    fun isLocked(ctx:Context):Boolean {
        val keyguard=ctx.getSystemService(Context.KEYGUARD_SERVICE) as KeyguardManager
        val power=ctx.getSystemService(Context.POWER_SERVICE) as PowerManager
        return keyguard.isKeyguardLocked || !power.isInteractive
    }
    fun channelForSituation(p:ZikrPrefs,overlay:Boolean,locked:Boolean):String =
        if(locked) lockId(p) else channelForDisplay(p,overlay)
    fun channelForDisplay''')
change(n,
'''        val overlayAllowed=p.banner && hasOverlay(app)
        if(overlayAllowed) {''',
'''        // The custom green overlay is allowed only on an unlocked, interactive screen.
        // A locked device uses the PUBLIC Android notification on its lock screen.
        val locked=isLocked(app)
        val overlayAllowed=p.banner && !locked && hasOverlay(app)
        if(locked) {
            post(app,channelForSituation(p,false,true),d,id)
        } else if(overlayAllowed) {''')
change(n,'post(app,channelForDisplay(p,true),d,id)',
         'post(app,channelForSituation(p,true,false),d,id)')
m=pkg/"MainActivity.kt"
change(m,'            o.put("exactAlarm",Scheduler.canExact(applicationContext))',
           '            o.put("screenLocked",Notifier.isLocked(applicationContext))\n            o.put("exactAlarm",Scheduler.canExact(applicationContext))')
t=root/"app/src/androidTest/java/com/zikr/zikrakan/NotificationIntegrationTest.kt"
change(t,"import android.app.NotificationManager\n",
           "import android.app.NotificationManager\nimport android.app.Notification\n")
change(t,'''    @Test fun tapActionDismissesWithoutOpeningActivity() {''',
'''    @Test fun lockScreenRoutesToPublicAndroidNotification() {
        val p=ZikrPrefs(banner=true,sound=false,vibrate=true)
        Notifier.ensureChannels(ctx)
        val id=Notifier.channelForSituation(p,true,true)
        assertEquals(Notifier.lockId(p),id)
        val c=nm.getNotificationChannel(id)
        assertEquals(Notification.VISIBILITY_PUBLIC,c.lockscreenVisibility)
        assertEquals(NotificationManager.IMPORTANCE_HIGH,c.importance)
    }
    @Test fun unlockedPrefersQuietShadeWithGreenOverlay() {
        val p=ZikrPrefs(banner=true,sound=false,vibrate=true)
        Notifier.ensureChannels(ctx)
        val id=Notifier.channelForSituation(p,true,false)
        assertEquals(Notifier.channelForDisplay(p,true),id)
        assertEquals(NotificationManager.IMPORTANCE_LOW,nm.getNotificationChannel(id).importance)
    }
    @Test fun tapActionDismissesWithoutOpeningActivity() {''')
g=root/"app/build.gradle.kts"
change(g,'versionCode = 30\n        versionName = "3.0"',
         'versionCode = 31\n        versionName = "3.1"')
print("v3.1 native lock-screen and overlay routing ready")
