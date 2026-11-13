#!/usr/bin/env python3
"""v3.2: minimal Sorani settings and true green-banner-only unlocked mode."""
from pathlib import Path
import re

root=Path("buildsrc")
pkg=root/"app/src/main/java/com/zikr/zikrakan"

def replace_once(path,old,new):
    s=path.read_text(encoding="utf-8")
    assert s.count(old)==1,(path,s.count(old),old[:110])
    path.write_text(s.replace(old,new,1),encoding="utf-8")

n=pkg/"Notifier.kt"
# A system heads-up is NEVER a substitute for the green overlay in unlocked mode.
# If overlay permission is missing, retain the notification in the shade without
# showing a black popup; the settings screen clearly offers a permission action.
replace_once(n,
    '    fun channelForSituation(p:ZikrPrefs,overlay:Boolean,locked:Boolean):String =\n        if(locked) lockId(p) else channelForDisplay(p,overlay)',
    '    fun channelForSituation(p:ZikrPrefs,overlay:Boolean,locked:Boolean):String =\n        if(locked) lockId(p) else if(p.banner) channelForDisplay(p,true) else channelId(p)')
replace_once(n,
    '''                onFail={
                    val nm=app.getSystemService(NotificationManager::class.java)
                    nm.cancel(id)
                    post(app,channelId(p),d,id)
                },''',
    '''                onFail={
                    // POCO may reject overlay windows despite generic permission;
                    // leave the silent shade notification rather than a black popup.
                },''')
replace_once(n,
    '''        } else {
            post(app,channelId(p),d,id)
        }
    }
}''',
    '''        } else {
            // No overlay permission: don't create an unwanted black heads-up.
            // With banner OFF a normal Android notification is still sent.
            post(app,channelForSituation(p,false,false),d,id)
        }
    }
}''')
o=pkg/"Overlay.kt"
replace_once(o,'setColor(0xFF2B3D35.toInt())','setColor(0xFF174B3B.toInt())')
replace_once(o,'setStroke(dp(ctx, 1), 0xFF8C805E.toInt())','setStroke(dp(ctx, 2), 0xFFD6B879.toInt())')

a=pkg/"MainActivity.kt"
replace_once(a,
    'override fun onResume() { super.onResume(); Scheduler.schedule(this) }',
    '''override fun onResume() {
        super.onResume()
        Scheduler.schedule(this)
        if(::web.isInitialized) web.post {
            web.evaluateJavascript("if (typeof tab!=='undefined' && tab==='settings') render();",null)
        }
    }''')
h=root/"app/src/main/assets/index.html"
s=h.read_text(encoding="utf-8")
start=s.index("function settings(){return ")
end=s.index("function bind(){",start)
new_settings='''function settings(){return BT
<h1 class="heading">ڕێکخستنەکان</h1>
<section class="settingCard simpleCard">
  <div class="sectionTitle">بانەر و نۆتیفیکەیشن</div>
  <div class="row"><strong>نۆتیفیکەیشن</strong><input id="enabled" class="toggle" type="checkbox" MARKprefs.enabled?'checked':''}></div>
  <div class="row"><strong>بانەری سەوز</strong><input id="banner" class="toggle" type="checkbox" MARKprefs.banner?'checked':''}></div>
  <p class="permissionState" id="overlayState" aria-live="polite"></p>
  <button type="button" id="systemOverlay" class="outlineBtn compactButton">چالاککردنی بانەری سەوز</button>
  <button type="button" id="systemNotifications" class="linkButton">ڕێکخستنی نۆتیفیکەیشن</button>
</section>
<section class="settingCard simpleCard">
  <div class="sectionTitle">دەنگ و لەرینەوە</div>
  <div class="row"><strong>دەنگ</strong><input id="sound" class="toggle" type="checkbox" MARKprefs.sound?'checked':''}></div>
  <div class="row"><strong>لەرینەوە</strong><input id="vibrate" class="toggle" type="checkbox" MARKprefs.vibrate?'checked':''}></div>
  <button type="button" id="listenChime" class="linkButton">▶ تاقیکردنەوەی دەنگ</button>
</section>
<section class="settingCard simpleCard">
  <div class="sectionTitle">کاتەکانی زیکر</div>
  <div class="segmented"><button type="button" id="intervalMode" class="MARKprefs.mode==='interval'?'active':''}">هەر چەند خولەک</button><button type="button" id="fixedMode" class="MARKprefs.mode==='fixed'?'active':''}">کاتی دیاریکراو</button></div>
  MARKprefs.mode==='interval'?BT
    <div class="selectRow"><label for="interval">ماوە</label><select id="interval">MARK[5,10,15,30,45,60,90,120].map(n=>BT<option value="MARKn}" MARKprefs.interval===n?'selected':''}>MARKnumerals(n)} خولەک</option>BT).join('')}MARK![5,10,15,30,45,60,90,120].includes(prefs.interval)?BT<option selected value="MARKprefs.interval}">MARKnumerals(prefs.interval)} خولەک</option>BT:''}</select></div>
    <div class="selectRow"><label for="custom">ماوەی تایبەت</label><input id="custom" type="text" inputmode="numeric" maxlength="4" placeholder="٤٥"></div>
    <div class="selectRow"><label for="start">دەستپێک</label><input id="start" type="time" value="MARKesc(prefs.start)}"></div>
    <div class="selectRow"><label for="end">کۆتایی</label><input id="end" type="time" value="MARKesc(prefs.end)}"></div>
  BT:BT<div class="selectRow"><label for="times">کاتەکان</label><input id="times" type="text" value="MARKesc(prefs.times)}" placeholder="08:00, 18:00"></div>BT}
</section>
<button id="test" class="goldBtn simpleTest">پیشاندانی نموونەی زیکر</button>
<p id="testStatus" class="note" hidden aria-live="polite"></p>
BT}
'''
new_settings=new_settings.replace("BT",chr(96)).replace("MARK",chr(36)+"{")
s=s[:start]+new_settings+s[end:]
start=s.index("}if(tab==='settings'){",s.index("function bind(){"))
end=s.index("if(x('test'))x('test').onclick=notifyPreview;}",start)
new_handlers='''}if(tab==='settings'){
  const permissionState=x('overlayState');
  const updatePermission=()=>{
    if(!(window.Android&&typeof Android.notificationDiagnostic==='function')){
      permissionState.textContent='بانەری سەوز لە ئەندرۆید چالاک دەکرێت.';return;
    }
    try{
      const state=JSON.parse(Android.notificationDiagnostic());
      permissionState.textContent=state.overlay?'✓ بانەری سەوز ڕێگەپێدراوە':'⚠ بۆ بانەری سەوز، ڕێگەپێدان پێویستە';
      permissionState.classList.toggle('active',!!state.overlay);
      x('systemOverlay').hidden=!!state.overlay;
    }catch(e){permissionState.textContent='مۆڵەتی بانەر بپشکنە';}
  };
  updatePermission();
  const native=name=>{try{if(window.Android&&typeof Android[name]==='function')Android[name]()}catch(e){}};
  for(const id of ['enabled','banner','sound','vibrate']){
    x(id).onchange=e=>{
      prefs[id]=e.target.checked;
      store();
      if(id==='enabled'&&prefs.enabled)native('requestNotificationPermission');
      if(id==='banner'&&prefs.banner){
        let allowed=false;
        try{allowed=JSON.parse(Android.notificationDiagnostic()).overlay}catch(e){}
        if(!allowed)native('openOverlaySettings');
      }
      updatePermission();
    };
  }
  x('systemOverlay').onclick=()=>native('openOverlaySettings');
  x('systemNotifications').onclick=()=>native('openSystemNotifications');
  x('listenChime').onclick=playZikrSound;
  x('intervalMode').onclick=()=>{prefs.mode='interval';store();render()};
  x('fixedMode').onclick=()=>{prefs.mode='fixed';store();render()};
  if(prefs.mode==='interval'){
    x('interval').onchange=e=>{prefs.interval=Number(e.target.value);store()};
    x('custom').onchange=e=>{
      const n=parseKurdishNumber(e.target.value);
      if(Number.isInteger(n)&&n>=1&&n<=1440){prefs.interval=n;store();render()}
      else{x('custom').value='';x('custom').placeholder='١ تا ١٤٤٠';}
    };
    for(const k of ['start','end'])x(k).onchange=e=>{
      if((k==='end'&&e.target.value<prefs.start)||(k==='start'&&e.target.value>prefs.end)){render();return;}
      prefs[k]=e.target.value;store();
    };
  }else{x('times').onchange=e=>{prefs.times=e.target.value;store()};}
}'''
s=s[:start]+new_handlers+s[end:]
# The old v3.1 DOM re-arranger was only hiding/reordering clutter and should no
# longer touch the hand-crafted, minimal settings markup.
if 'function tidySettingsLayout(){' in s:
    i=s.index('function tidySettingsLayout(){')
    j=s.index('function render(){',i)
    s=s[:i]+'function tidySettingsLayout(){}\\n'+s[j:]
s=s.replace("const canShowNativeSample = false;", "const canShowNativeSample = false;") # no-op for backwards compatibility
old_preview="$('mockNotif').classList.toggle('visible', !(window.Android&&typeof Android.showTest==='function'));"
assert old_preview in s
s=s.replace(old_preview,
    '''let canNativeOverlay=false;
  try{canNativeOverlay=!!JSON.parse(Android.notificationDiagnostic()).overlay}catch(e){}
  $('mockNotif').classList.toggle('visible', !(window.Android&&typeof Android.showTest==='function'&&canNativeOverlay));''',1)
s=s.replace('background:#2b3d35;color:var(--ivory);border:1px solid #8c805e',
            'background:#174b3b;color:var(--ivory);border:2px solid #d6b879',1)
styling='''<style>
/* v3.2: short, one-screen settings; preserve the original green/gold brand. */
.simpleCard{background:#10362c!important;border:1px solid #45634c!important;border-radius:24px!important;padding:17px 19px!important;margin:14px 0!important}
.simpleCard .sectionTitle{font-size:19px!important;color:#e7c783!important;margin:0 0 10px!important}
.simpleCard .row{display:flex!important;align-items:center;justify-content:space-between;gap:12px;padding:13px 0!important;margin:0!important;border-bottom:1px solid #375849}
.simpleCard .row:last-of-type{border-bottom:0}
.simpleCard .row strong{font-size:16px!important;color:#f4ebd4}
.simpleCard .toggle{flex-shrink:0}
.simpleCard .permissionState{color:#e8ad99;font-size:12px;line-height:1.65;margin:12px 0 7px;text-align:right}
.simpleCard .permissionState.active{color:#b1d9b7}
.simpleCard .compactButton{width:100%;min-height:43px;font-size:13px!important;margin-top:4px;padding:11px}
.simpleCard .linkButton{background:transparent!important;color:#d8b978;border:0;padding:10px 5px;margin-top:4px;font-size:13px}
.simpleCard .segmented{margin:8px 0 14px}
.simpleCard .selectRow{margin:12px 0 0!important;gap:10px;align-items:center}
.simpleCard .selectRow label{font-size:14px;min-width:85px;flex:0 0 85px}
.simpleCard .selectRow input,.simpleCard .selectRow select{min-width:0;flex:1}
.simpleTest{width:100%;margin:13px 0 28px!important}
</style>'''
s=s.replace("</head>",styling+"</head>",1)
h.write_text(s,encoding="utf-8")
# Test the unlocked no-permission route stays in LOW channel, preventing black popup.
test=root/"app/src/androidTest/java/com/zikr/zikrakan/NotificationIntegrationTest.kt"
t=test.read_text(encoding="utf-8")
marker="    @Test fun tapActionDismissesWithoutOpeningActivity() {"
assert marker in t
t=t.replace(marker,'''    @Test fun missingOverlayNeverTriggersBlackSystemHeadsUp() {
        val p=ZikrPrefs(banner=true,sound=false,vibrate=true)
        Notifier.ensureChannels(ctx)
        val channel=Notifier.channelForSituation(p,false,false)
        assertEquals(NotificationManager.IMPORTANCE_LOW,nm.getNotificationChannel(channel).importance)
    }
''' +marker,1)
test.write_text(t,encoding="utf-8")
g=root/"app/build.gradle.kts"
replace_once(g,'versionCode = 31\n        versionName = "3.1"',
            'versionCode = 32\n        versionName = "3.2"')
print("v3.2 ready: 3 uncluttered settings cards, permission check, green overlay or quiet shade unlocked, native notification locked.")
