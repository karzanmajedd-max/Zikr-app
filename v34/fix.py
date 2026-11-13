#!/usr/bin/env python3
"""Zikrakan 3.4: accessible battery/exact-alarm settings and one-minute reminders."""
from pathlib import Path

root=Path("buildsrc")
native=root/"app/src/main/java/com/zikr/zikrakan"
def once(path,old,new):
    source=path.read_text(encoding="utf-8")
    assert source.count(old)==1,(str(path),source.count(old),old[:120])
    path.write_text(source.replace(old,new,1),encoding="utf-8")

# Keep the app's battery exemption permission REMOVED to avoid high-risk requests.
# Open the legitimate Android power settings instead and let the user choose.
main=native/"MainActivity.kt"
once(main,
    "        @JavascriptInterface fun openOverlaySettings()",
    """        @JavascriptInterface fun openBatterySettings(){runOnUiThread{
            safeStart(Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS))
        }}
        @JavascriptInterface fun openOverlaySettings()""")
once(main,
    '            o.put("exactAlarm",Scheduler.canExact(applicationContext))',
    '''            val power=getSystemService(POWER_SERVICE) as PowerManager
            o.put("batteryUnrestricted",power.isIgnoringBatteryOptimizations(packageName))
            o.put("nextAlarmMillis",Scheduler.nextScheduledMillis(applicationContext))
            o.put("lastDeliveryMillis",Scheduler.lastDeliveryMillis(applicationContext))
            o.put("exactAlarm",Scheduler.canExact(applicationContext))''')

scheduler=native/"Scheduler.kt"
code=scheduler.read_text(encoding="utf-8")
anchor="    fun schedule(ctx: Context) {"
assert code.count(anchor)==1
code=code[:code.index(anchor)]+'''    private const val STATUS_FILE = "zikr_schedule"
    fun nextScheduledMillis(ctx: Context): Long =
        ctx.getSharedPreferences(STATUS_FILE, Context.MODE_PRIVATE).getLong("next_trigger",0)
    fun lastDeliveryMillis(ctx: Context): Long =
        ctx.getSharedPreferences(STATUS_FILE, Context.MODE_PRIVATE).getLong("last_delivery",0)
    private fun record(ctx: Context, next: Long, method: String) {
        ctx.getSharedPreferences(STATUS_FILE, Context.MODE_PRIVATE).edit()
            .putLong("next_trigger",next).putString("method",method).apply()
    }

    fun schedule(ctx: Context) {
        val am=ctx.getSystemService(AlarmManager::class.java)
        val pi=pendingIntent(ctx)
        am.cancel(pi)
        val p=ZikrPrefs.load(ctx)
        if(!p.enabled) { record(ctx,0,"disabled"); return }
        val next=nextTriggerMillis(p)
        if(next==null) { record(ctx,0,"invalid"); return }
        try {
            if(canExact(ctx)) {
                am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,next,pi)
                record(ctx,next,"exact")
            } else {
                // Fallback is not exact; UI must surface the missing permission.
                am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,next,pi)
                record(ctx,next,"inexact")
            }
        } catch (_:SecurityException) {
            try {
                am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,next,pi)
                record(ctx,next,"inexact")
            } catch (_:Exception) { record(ctx,0,"failed") }
        } catch (_:Exception) { record(ctx,0,"failed") }
    }
}
'''
scheduler.write_text(code,encoding="utf-8")

receiver=native/"AlarmReceiver.kt"
once(receiver,
    '''        val p = ZikrPrefs.load(context)
        if (p.enabled) Notifier.show(context, p)''',
    '''        val p = ZikrPrefs.load(context)
        if (p.enabled) {
            context.getSharedPreferences("zikr_schedule",Context.MODE_PRIVATE).edit()
                .putLong("last_delivery",System.currentTimeMillis()).apply()
            Notifier.show(context,p)
        }''')

manifest=root/"app/src/main/AndroidManifest.xml"
once(manifest,
    '''                <action android:name="android.intent.action.TIME_SET"/>
            </intent-filter>''',
    '''                <action android:name="android.intent.action.TIME_SET"/>
                <action android:name="android.app.action.SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED"/>
            </intent-filter>''')
assert "REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" not in manifest.read_text()

html=root/"app/src/main/assets/index.html"
h=html.read_text(encoding="utf-8")
# Current v3.3 intentionally hides the 1/2/3 minute options. Restore from 1.
old="[5,10,15,30,45,60,90,120]"
assert h.count(old)>=2,h.count(old)
h=h.replace(old,"[1,2,3,5,10,15,30,45,60,90,120]",2)
# Add two short permission actions to the EXISTING schedule card, not a fourth card.
anchor='</section>\n<button id="test" class="goldBtn simpleTest">'
assert anchor in h
h=h.replace(anchor,'''<div class="timePermission">
  <div id="scheduleState" class="scheduleState" aria-live="polite"></div>
  <button type="button" class="outlineBtn scheduleAction" id="exactGrant" hidden>ڕێگەدان بە کاتی ورد</button>
  <div class="batteryRow">
    <span id="batteryState">باتری</span>
    <button type="button" class="outlineBtn scheduleAction" id="batterySettings">ڕێکخستنی باتری</button>
  </div>
  <p id="minuteNote" class="minuteNote" hidden>کاتی ١ خولەک لە شاشەی قوفڵ و دۆخی پاراستنی باتریدا دەتوانێت دواکەوێت.</p>
</div></section>
<button id="test" class="goldBtn simpleTest">''',1)
# Add simple dynamic status checks, exact alarm permission and battery shortcut.
anchor="  x('listenChime').onclick=playZikrSound;"
assert h.count(anchor)>=1
position=h.index("function settings(){return ")
binding_start=h.index("function bind(){",position)
idx=h.find(anchor,binding_start)
assert idx!=-1
h=h[:idx]+'''  const showScheduleStatus=()=>{
    if(!(window.Android && typeof Android.notificationDiagnostic==='function')) return;
    try{
      const d=JSON.parse(Android.notificationDiagnostic());
      x('scheduleState').textContent=d.exactAlarm?'✓ کاتی ورد چالاکە':'⚠ مۆڵەتی کاتی ورد پێویستە';
      x('exactGrant').hidden=!!d.exactAlarm;
      x('batteryState').textContent=d.batteryUnrestricted?'✓ باتری: بێ سنووردارکردن':'باتری: ڕێکخستن';
      x('minuteNote').hidden=!(prefs.mode==='interval'&&prefs.interval<5);
    }catch(e){x('scheduleState').textContent='کاتی ورد بپشکنە';}
  };
  x('batterySettings').onclick=()=>native('openBatterySettings');
  x('exactGrant').onclick=()=>native('openExactAlarmSettings');
  showScheduleStatus();
''' +h[idx:]
# Inline permission status refresh after interval changed (keep UI compact)
anchor="x('interval').onchange=e=>{prefs.interval=Number(e.target.value);store()};"
assert anchor in h
h=h.replace(anchor,"x('interval').onchange=e=>{prefs.interval=Number(e.target.value);store();showScheduleStatus()};",1)

css='''<style>
.timePermission{border-top:1px solid #365849;margin-top:17px;padding-top:12px}
.scheduleState{font-size:13px;color:#e3c88a;margin-bottom:8px;line-height:1.7}
.batteryRow{display:flex;justify-content:space-between;gap:8px;align-items:center;margin-top:10px}
#batteryState{font-size:13px;color:#e7d3a7}
.scheduleAction{border-radius:12px!important;font-size:12px!important;min-height:39px!important;padding:8px 12px!important}
.minuteNote{font-size:12px;color:#d1b788;line-height:1.8;margin:12px 0 0}
</style>'''
assert "</head>" in h
h=h.replace("</head>",css+"</head>",1)
html.write_text(h,encoding="utf-8")

# Verify user-level duration, exact next minute, and next-trigger diagnostic.
test=root/"app/src/androidTest/java/com/zikr/zikrakan/NotificationIntegrationTest.kt"
t=test.read_text(encoding="utf-8")
anchor="    @Test fun tapActionDismissesWithoutOpeningActivity() {"
assert anchor in t
t=t.replace(anchor,'''    @Test fun oneMinuteIntervalsCoverEveryMinute() {
        val p=ZikrPrefs(mode="interval",interval=1,start="00:00",end="23:59")
        val slots=Scheduler.slots(p)
        assertEquals(1440,slots.size)
        assertEquals(0,slots.first())
        assertEquals(1439,slots.last())
    }
    @Test fun nextMinuteIsCalculatedCorrectly() {
        val now=java.util.Calendar.getInstance()
        now.set(2026,java.util.Calendar.NOVEMBER,13,10,15,29)
        now.set(java.util.Calendar.MILLISECOND,0)
        val p=ZikrPrefs(mode="interval",interval=1,start="07:00",end="22:00")
        val next=Scheduler.nextTriggerMillis(p,now)!!
        val expected=now.clone() as java.util.Calendar
        expected.set(java.util.Calendar.MINUTE,16)
        expected.set(java.util.Calendar.SECOND,0)
        assertEquals(expected.timeInMillis,next)
    }
    @Test fun alarmIsActuallyScheduledAndRecorded() {
        val p="{\\\"enabled\\\":true,\\\"mode\\\":\\\"interval\\\",\\\"interval\\\":1,\\\"start\\\":\\\"00:00\\\",\\\"end\\\":\\\"23:59\\\"}"
        ZikrPrefs.saveRaw(ctx,p)
        Scheduler.schedule(ctx)
        val next=Scheduler.nextScheduledMillis(ctx)
        assertTrue("next alarm must be in the future",next>System.currentTimeMillis())
        assertTrue("next alarm must be in one-minute window",next-System.currentTimeMillis()<=65000)
    }
''' +anchor,1)
test.write_text(t,encoding="utf-8")

gradle=root/"app/build.gradle.kts"
once(gradle,'versionCode = 33\n        versionName = "3.3"',
    'versionCode = 34\n        versionName = "3.4"')
print("Zikrakan 3.4: 1-minute option, schedule status, Android battery/exact-alarm settings shortcut, 10 Android tests.")
