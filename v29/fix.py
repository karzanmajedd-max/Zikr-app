from pathlib import Path
import runpy
runpy.run_path("v28/fix.py",run_name="__main__")
root=Path("buildsrc")
p=root/"app/src/main/java/com/zikr/zikrakan/MainActivity.kt"
h=root/"app/src/main/assets/index.html"
g=root/"app/build.gradle.kts"
def swap(path,old,new):
 s=path.read_text(encoding="utf-8")
 assert old in s,(str(path),old[:120])
 path.write_text(s.replace(old,new,1),encoding="utf-8")

swap(p,"import android.app.NotificationManager\n","import android.app.NotificationManager\nimport android.media.AudioManager\n")
swap(p,'        @JavascriptInterface fun openOverlaySettings()', '''        // Xiaomi Floating notifications has no portable direct Android settings Intent.
        @JavascriptInterface fun openFloatingSettings(){runOnUiThread{
            safeStart(Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                .putExtra(Settings.EXTRA_APP_PACKAGE,packageName))
        }}
        @JavascriptInterface fun openSoundSettings(){runOnUiThread{
            safeStart(Intent(Settings.ACTION_SOUND_SETTINGS))
        }}
        @JavascriptInterface fun openDndSettings(){runOnUiThread{
            safeStart(Intent("android.settings.ZEN_MODE_SETTINGS"))
        }}
        @JavascriptInterface fun openChannelSoundSettings(){runOnUiThread{
            Notifier.ensureChannels(applicationContext)
            safeStart(Intent(Settings.ACTION_CHANNEL_NOTIFICATION_SETTINGS)
                .putExtra(Settings.EXTRA_APP_PACKAGE,packageName)
                .putExtra(Settings.EXTRA_CHANNEL_ID,Notifier.channelId(ZikrPrefs.load(applicationContext))))
        }}
        @JavascriptInterface fun openOverlaySettings()''')
swap(p, '            o.put("sound",p.sound);o.put("vibrate",p.vibrate);o.put("banner",p.banner)',
'''            o.put("sound",p.sound);o.put("vibrate",p.vibrate);o.put("banner",p.banner)
            val audio=getSystemService(AUDIO_SERVICE) as AudioManager
            o.put("ringerSilent",audio.ringerMode==AudioManager.RINGER_MODE_SILENT)
            o.put("ringerVibrate",audio.ringerMode==AudioManager.RINGER_MODE_VIBRATE)
            o.put("notifVolume",audio.getStreamVolume(AudioManager.STREAM_NOTIFICATION))
            o.put("channelHasSound",chan?.sound!=null)''')

panel='''<section class="settingCard quickFix"><div class="sectionTitle">🔧 چاککردنی بانەر و دەنگ</div>
<p class="infoRow">ئەگەر بانەر نایەتە سەر شاشە، ئەم هەنگاوانە بەکاربهێنە.</p>
<div class="guide"><div>١. لە POCO / HyperOS: <b>Settings → Notifications &amp; status bar → Floating notifications → زیکرەکان → ON</b>.</div>
<div>٢. دۆخی <b>Silent</b> یان <b>Do Not Disturb</b> بپشکنە؛ هەردووکیان دەتوانن بانەر یان دەنگ ڕابگرن.</div>
<div>٣. دەنگی زیکر لە ناو ئەپ چالاک بکە، پاشان دەنگی نۆتیفیکەیشنی مۆبایل زیاد بکە.</div></div>
<div class="systemActions">
<button id="quickCheck" class="goldBtn" type="button">🔎 پشکنینی بانەر و دەنگ</button>
<button id="quickFloating" class="outlineBtn" type="button">🔔 ڕێکخستنەکانی Floating / Pop-up</button>
<button id="quickDnd" class="outlineBtn" type="button">🌙 ڕێکخستنی Do Not Disturb</button>
<button id="quickVolume" class="outlineBtn" type="button">🔊 ڕێکخستنی دەنگی مۆبایل</button>
<button id="quickChannel" class="outlineBtn" type="button">🎵 کەناڵی دەنگ و بانەری زیکر</button>
<button id="quickEnableSound" class="outlineBtn" type="button">✓ چالاککردنی دەنگی زیکر لە ئەپ</button>
<button id="quickTest" class="goldBtn" type="button">▶ تاقیکردنەوەی دەنگ و بانەر</button>
</div><p id="quickResult" class="note quickResult" aria-live="polite">«پشکنین» دابگرە بۆ بینینی دۆخی مۆڵەتەکان.</p>
<p class="note">Floating / Pop-up لە سیستەمی POCO دەبێت بەدەست چالاک بکرێت. دوگمەکە ڕێکخستنەکانی ئەپ دەکاتەوە، بەڵام ئەم مۆڵەتە خۆکارانە ناگۆڕێت.</p></section>'''
swap(h, '<div class="subheading">کۆنترۆڵی تەواوی نۆتیکەیشنەکان</div><section class="settingCard">',
       '<div class="subheading">کۆنترۆڵی تەواوی نۆتیکەیشنەکان</div>'+panel+'<section class="settingCard">')
swap(h,'@media(min-width:650px)', '''.quickFix{border-color:#bca66c;background:linear-gradient(155deg,#204739,#0d2c23)}.quickFix .systemActions button{margin-top:0}.guide{display:grid;gap:8px;margin:14px 0}.guide div{padding:9px 11px;border-radius:12px;background:#0d2b23;font-size:13px;line-height:1.9}.guide b{color:var(--gold)}.quickResult{white-space:pre-line;background:#0a241c;border:1px solid #82764e;border-radius:12px;padding:11px}
@media(min-width:650px)''')
bind = '''}if(tab==='settings'){
const openSetting=n=>{try{if(window.Android&&typeof Android[n]==='function'){Android[n]();return}}catch(e){}alert('ئەم دوگمەیە لە ئەپی ئەندرۆید کار دەکات.')};
const check=()=>{
 const out=x('quickResult');
 if(!(window.Android&&typeof Android.notificationDiagnostic==='function')){out.textContent='ئەم پشکنینە لە ئەپی ئەندرۆید کار دەکات.';return}
 try{
  const s=JSON.parse(Android.notificationDiagnostic()), l=[];
  l.push((s.permission&&s.appEnabled?'✓':'⚠')+' مۆڵەتی نۆتیفیکەیشن: '+(s.permission&&s.appEnabled?'چالاکە':'ناچالاکە'));
  l.push((s.banner?'✓':'⚠')+' بانەر لە ئەپ: '+(s.banner?'چالاکە':'ناچالاکە'));
  l.push((s.channelImportance>=4?'✓':'⚠')+' گرنگی کەناڵی بانەر: '+(s.channelImportance>=4?'بەرزە':'کەمە'));
  l.push((!s.dnd?'✓':'⚠')+' Do Not Disturb: '+(s.dnd?'چالاکە':'ناچالاکە'));
  l.push((!s.ringerSilent&&!s.ringerVibrate?'✓':'⚠')+' دۆخی دەنگی مۆبایل: '+(s.ringerSilent?'بێدەنگە':s.ringerVibrate?'تەنها لەرزینەوە':'ئاساییە'));
  l.push((s.notifVolume>0?'✓':'⚠')+' دەنگی نۆتیفیکەیشن: '+(s.notifVolume>0?'بەرزکراوەتەوە':'سفرە'));
  l.push((s.sound&&s.channelHasSound?'✓':'⚠')+' دەنگی زیکر: '+(s.sound&&s.channelHasSound?'چالاکە':'ناچالاکە یان لە کەناڵ کوژاوەتەوە'));
  l.push((s.overlay?'✓':'•')+' مۆڵەتی کارتی سەرشاشە: '+(s.overlay?'هەیە':'پێویستە بۆ کارتی تایبەت'));
  if(s.overlayError)l.push('⚠ هەڵەی کارتی سەرشاشە: '+s.overlayError);
  l.push('ℹ دۆخی Floating لە HyperOS لەناو ئەپ ناپشکنرێت. لە Settings چالاکی بکە.');
  out.textContent=l.join('\\n');
 }catch(e){out.textContent='نەتوانرا دۆخی مۆبایل بپشکنرێت.'}
};
x('quickCheck').onclick=check;
x('quickFloating').onclick=()=>openSetting('openFloatingSettings');
x('quickDnd').onclick=()=>openSetting('openDndSettings');
x('quickVolume').onclick=()=>openSetting('openSoundSettings');
x('quickChannel').onclick=()=>openSetting('openChannelSoundSettings');
x('quickEnableSound').onclick=()=>{prefs.sound=true;store();render();const r=document.getElementById('quickResult');if(r)r.textContent='✓ دەنگی زیکر چالاک کرا. دەنگی مۆبایل و کەناڵەکەش بپشکنە.'};
x('quickTest').onclick=()=>{if(!prefs.sound){prefs.sound=true;store();render()}notifyPreview()};
x('listenChime').onclick=playZikrSound;'''
swap(h,"}if(tab==='settings'){x('listenChime').onclick=playZikrSound;",bind)
swap(g,'versionCode = 28\n        versionName = "2.8"','versionCode = 29\n        versionName = "2.9"')
print("Added HyperOS Floating/DND/sound quick fix panel to Zikrakan 2.9")
