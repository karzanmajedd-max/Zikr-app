package com.didarismail.zikrakan

import android.Manifest
import android.app.*
import android.content.*
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.net.Uri
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.style.TextDirection
import androidx.compose.ui.text.PlatformTextStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.text.font.FontWeight
import android.app.TimePickerDialog
import android.media.RingtoneManager
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

val emerald = Color(0xFF092E28)
val gold = Color(0xFFE5C582)
data class Dhikr(val arabic: String, val kurdish: String)
val dhikrs = listOf(
 Dhikr("سُبْحَانَ اللَّهِ", "پاکی و بێگەردی بۆ خوای گەورەیە."),
 Dhikr("الْحَمْدُ لِلَّهِ", "هەموو ستایشێک بۆ خوای گەورەیە."),
 Dhikr("اللَّهُ أَكْبَرُ", "خوای گەورە لە هەموو شتێک گەورەترە."),
 Dhikr("لَا إِلَهَ إِلَّا اللَّهُ", "هیچ پەرستراوێکی بەحەق نییە جگە لە خوا."),
 Dhikr("أَسْتَغْفِرُ اللَّهَ", "داوای لێخۆشبوون لە خوا دەکەم."),
 Dhikr("لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ", "هیچ توانایەک و هێزێک نییە مەگەر بە یارمەتی خوا."),
 Dhikr("سُبْحَانَ اللَّهِ وَبِحَمْدِهِ", "پاکی بۆ خوا و ستایشیش هەر بۆ ئەوە."),
 Dhikr("سُبْحَانَ اللَّهِ الْعَظِيمِ", "پاکی بۆ خوای گەورە و مەزنە."),
 Dhikr("اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ", "خوایە، سەڵاوات لەسەر محەممەد بنێرە."),
 Dhikr("حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ", "خوای گەورە بەسە بۆ ئێمە و باشترین پشت و پەنا و کارسازە."),
 Dhikr("الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", "هەموو ستایش و سوپاسێک بۆ خوایە، پەروەردگاری هەموو جیهانیان."),
 Dhikr("سُبْحَانَ اللَّهِ وَالْحَمْدُ لِلَّهِ وَلَا إِلَهَ إِلَّا اللَّهُ وَاللَّهُ أَكْبَرُ", "خوای گەورە پاک و بێگەردە؛ هەموو ستایشێک بۆ ئەوە؛ هیچ پەرستراوێکی بەهەق نییە جگە لە خوا، و خوا گەورەترە."),
 Dhikr("أَسْتَغْفِرُ اللَّهَ وَأَتُوبُ إِلَيْهِ", "داوای لێخۆشبوون لە خوای گەورە دەکەم و تەوبە بۆ ئەو دەبەم."),
 Dhikr("يَا حَيُّ يَا قَيُّومُ", "ئەی خوای هەمیشە زیندوو، ئەی ئەوەی بەخۆی ڕاوەستاوە و هەموو شتێک بە ئەو ڕاوەستاوە."),
 Dhikr("لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ", "هیچ پەرستراوێکی بەهەق نییە جگە لە خوای تاک و تەنها؛ هاوبەشی نییە؛ دەسەڵات و ستایش هی ئەوە و بەسەر هەموو شتێکدا توانای هەیە."),
 Dhikr("سُبْحَانَ اللَّهِ الْعَظِيمِ، سُبْحَانَ اللَّهِ وَبِحَمْدِهِ", "خوای مەزن پاک و بێگەردە؛ خوای گەورە پاک و بێگەردە و ستایشی دەکەم."),
 Dhikr("سُبْحَانَ اللَّهِ وَبِحَمْدِهِ عَدَدَ خَلْقِهِ وَرِضَا نَفْسِهِ وَزِنَةَ عَرْشِهِ وَمِدَادَ كَلِمَاتِهِ", "خوای گەورە پاک و بێگەردە و ستایشی دەکەم بە ئەندازەی ژمارەی دروستکراوەکانی، ڕەزامەندی خۆی، قورسایی عەرشی و مەدەدی وشەکانی."),
 Dhikr("بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", "بە ناوی خوای بەخشندەی میهرەبان.")
)
class MainActivity : ComponentActivity() {
 override fun onCreate(savedInstanceState: Bundle?) {
  super.onCreate(savedInstanceState)
  val prefs = getSharedPreferences("settings", MODE_PRIVATE)
  ReminderReceiver.schedule(this)
  setContent {
   var page by remember { mutableStateOf(0) }
   var index by remember { mutableIntStateOf(0) }
   var order by remember { mutableStateOf(dhikrs.indices.shuffled()) }
   var position by remember { mutableIntStateOf(0) }
   var count by remember { mutableIntStateOf(prefs.getInt("count", 0)) }
   var interval by remember { mutableIntStateOf(prefs.getInt("interval", 5)) }
   var start by remember { mutableIntStateOf(prefs.getInt("start", 7)) }
   var end by remember { mutableIntStateOf(prefs.getInt("end", 22)) }
   var sound by remember { mutableStateOf(prefs.getBoolean("sound", false)) }
   var vibration by remember { mutableStateOf(prefs.getBoolean("vibration", true)) }
   var selectedSound by remember { mutableIntStateOf(prefs.getInt("sound_choice",0)) }
   var customInterval by remember { mutableStateOf(interval.toString()) }
   val permission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) {}
   LaunchedEffect(Unit) { if(Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) permission.launch(Manifest.permission.POST_NOTIFICATIONS) }
   MaterialTheme(colorScheme=darkColorScheme(primary=gold,background=emerald,surface=Color(0xFF14392F))) {
    Column(Modifier.fillMaxSize().background(Brush.verticalGradient(listOf(Color(0xFF174838),Color(0xFF08271F)))), horizontalAlignment = Alignment.CenterHorizontally) {
     Row(Modifier.fillMaxWidth().background(Color(0xFF1B1C22)).padding(horizontal=24.dp, vertical=20.dp),horizontalArrangement=Arrangement.End) { Text("زیکرەکان", color=Color.White, fontSize=24.sp) }
     Spacer(Modifier.height(18.dp))
     CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
     Column(Modifier.weight(1f).verticalScroll(rememberScrollState()).padding(18.dp),horizontalAlignment=Alignment.CenterHorizontally) {
     when(page) {
      0 -> {
       Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween,verticalAlignment=Alignment.CenterVertically) { Column { Text("زیکرەکان",color=Color(0xFFFFEED5),fontSize=30.sp,fontWeight=FontWeight.Bold);Text("یادی خوای گەورە",color=gold,fontSize=16.sp) }; Text("☾",color=gold,fontSize=48.sp) }
       Spacer(Modifier.height(16.dp))
       Text("دڵت بە زیکری خوا ئارام بکە",color=Color.White,fontSize=26.sp,fontWeight=FontWeight.Bold,modifier=Modifier.fillMaxWidth(),textAlign=TextAlign.Right)
       Spacer(Modifier.height(24.dp))
       DhikrCard(dhikrs[index])
       Spacer(Modifier.height(20.dp))
       Button(onClick={ if(position+1 >= order.size) { order=dhikrs.indices.shuffled();position=0 } else position++; index=order[position] }, colors=ButtonDefaults.buttonColors(containerColor=gold),modifier=Modifier.fillMaxWidth()) { Text("↻ زیکرێکی دیکە", color=emerald) }
      }
      1 -> { Text("هەموو زیکرەکان",color=Color.White,fontSize=27.sp,fontWeight=FontWeight.Bold,modifier=Modifier.fillMaxWidth(),textAlign=TextAlign.Right);Spacer(Modifier.height(18.dp));dhikrs.forEach { DhikrCard(it); Spacer(Modifier.height(18.dp)) } }
      2 -> {
       Spacer(Modifier.height(50.dp))
       Text("$count", color=gold, fontSize=72.sp)
       Button(onClick={ count++; prefs.edit().putInt("count",count).apply() }, colors=ButtonDefaults.buttonColors(containerColor=gold)) { Text("ژماردن", color=emerald) }
       TextButton(onClick={ count=0; prefs.edit().putInt("count",0).apply() }) { Text("سفرکردنەوە",color=Color.White) }
      }
      3 -> {
       Text("ڕێکخستنەکان",color=Color.White,fontSize=27.sp,fontWeight=FontWeight.Bold,modifier=Modifier.fillMaxWidth(),textAlign=TextAlign.Right)
       Text("کۆنترۆڵی نۆتیکەیشن و دەنگ",color=gold,fontSize=16.sp,modifier=Modifier.fillMaxWidth(),textAlign=TextAlign.Right)
       Spacer(Modifier.height(18.dp))
       Spacer(Modifier.height(16.dp))
       SettingsSection("کاتەکانی نۆتیکەیشن") {
       Text("ماوەی نێوان نۆتیکەیشنەکان", color=gold,modifier=Modifier.fillMaxWidth(),textAlign=TextAlign.Right)
       listOf(1,5,10,15,30,45,60).chunked(4).forEach { group -> Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(5.dp)) { group.forEach { n -> OutlinedButton(onClick={ interval=n;customInterval=n.toString();prefs.edit().putInt("interval",n).apply();ReminderReceiver.schedule(this@MainActivity) },modifier=Modifier.weight(1f),contentPadding=PaddingValues(0.dp),border=BorderStroke(1.dp,if(interval==n)gold else Color(0xFF667C6B)),colors=ButtonDefaults.outlinedButtonColors(containerColor=if(interval==n)gold else Color.Transparent)) {Text("$n",color=if(interval==n)emerald else gold,fontSize=14.sp)} } } }
       OutlinedTextField(value=customInterval,onValueChange={customInterval=it.filter { ch -> ch.isDigit() }.take(4)},label={Text("ماوەی تایبەتی بە خولەک")},singleLine=true)
       Button(onClick={ val v=customInterval.toIntOrNull(); if(v!=null && v in 1..1440) {interval=v;prefs.edit().putInt("interval",v).apply();ReminderReceiver.schedule(this@MainActivity)} }) { Text("پاشەکەوتکردنی ماوە") }
       Text("دەستپێک: $start:00", color=Color.White)
       Button(onClick={TimePickerDialog(this@MainActivity,{_,h,_->start=h;prefs.edit().putInt("start",h).apply();ReminderReceiver.schedule(this@MainActivity)},start,0,true).show()},colors=ButtonDefaults.buttonColors(containerColor=gold)) {Text("دیاریکردنی دەستپێک",color=emerald)}
       Spacer(Modifier.height(12.dp))
       Text("کۆتایی: $end:00", color=Color.White)
       Button(onClick={TimePickerDialog(this@MainActivity,{_,h,_->end=h;prefs.edit().putInt("end",h).apply();ReminderReceiver.schedule(this@MainActivity)},end,0,true).show()},colors=ButtonDefaults.buttonColors(containerColor=gold)) {Text("دیاریکردنی کۆتایی",color=emerald)}
       }
       Spacer(Modifier.height(16.dp))
       SettingsSection("دەنگ و لەرینەوە") {
       Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween,verticalAlignment=Alignment.CenterVertically) { Switch(checked=sound,onCheckedChange={sound=it;prefs.edit().putBoolean("sound",it).apply()}); Text("دەنگی نۆتیکەیشن",color=Color.White,fontSize=18.sp) }
       Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween,verticalAlignment=Alignment.CenterVertically) { Switch(checked=vibration,onCheckedChange={vibration=it;prefs.edit().putBoolean("vibration",it).apply()}); Text("لەرینەوە",color=Color.White,fontSize=18.sp) }
       Text("هەڵبژاردنی دەنگ",color=gold,fontSize=18.sp,modifier=Modifier.fillMaxWidth(),textAlign=TextAlign.Right)
       listOf("دەنگی نۆتیکەیشن","دەنگی ئاگادارکردنەوە","دەنگی تەلەفۆن","دەنگی سیستەم").forEachIndexed { n,label ->
        Row(Modifier.fillMaxWidth().padding(vertical=3.dp),horizontalArrangement=Arrangement.SpaceBetween,verticalAlignment=Alignment.CenterVertically) {
         TextButton(onClick={
          try {
           val kind=when(n){0->RingtoneManager.TYPE_NOTIFICATION;1->RingtoneManager.TYPE_ALARM;2->RingtoneManager.TYPE_RINGTONE;else->RingtoneManager.TYPE_NOTIFICATION}
           RingtoneManager.getRingtone(this@MainActivity,RingtoneManager.getDefaultUri(kind))?.play()
          }catch(_:Exception){}
         }) {Text("▷ تاقیکردنەوە",color=gold,fontSize=12.sp)}
         RadioButton(selected=selectedSound==n,onClick={selectedSound=n;prefs.edit().putInt("sound_choice",n).apply();ReminderReceiver.schedule(this@MainActivity)},colors=RadioButtonDefaults.colors(selectedColor=gold))
         Text(label,color=Color.White,fontSize=14.sp)
        }
       }
       Text("دەنگەکان لە سیستەمی ئەندرۆیدەوە وەردەگیرێن؛ هەندێکیان لە مۆبایلە جیاوازەکاندا هاوشێوەن.",color=Color(0xFFC5D0C5),fontSize=12.sp)
       }
       Spacer(Modifier.height(16.dp))
       SettingsSection("تاقیکردنەوەی بانەری شاشە") {
       Text("ئەم دوگمەیە نۆتیکەیشنێکی تاقیکردنەوە بە دەنگ و ئاستی گرنگی بەرز دەنێرێت.",color=Color.White,fontSize=15.sp)
       Button(onClick={ val ok=ReminderReceiver.testHeadsUp(this@MainActivity); android.widget.Toast.makeText(this@MainActivity,if(ok)"نۆتیکەیشنی تاقیکردنەوە نێردرا" else "مۆڵەتی نۆتیکەیشن چالاک بکە",android.widget.Toast.LENGTH_LONG).show() },modifier=Modifier.fillMaxWidth(),colors=ButtonDefaults.buttonColors(containerColor=gold)) {Text("تاقیکردنەوەی بانەر",color=emerald,fontSize=17.sp)}
       Text("ئەگەر لە لیستدا دەرکەوت بەڵام بانەر نەبوو، لە ڕێکخستنەکانی ئەندرۆید کاناڵی تاقیکردنەوەی بانەر بپشکنە.",color=gold,fontSize=13.sp)
       }
       Spacer(Modifier.height(16.dp))
       SettingsSection("ڕێکخستنەکانی ئەندرۆید") {
       Spacer(Modifier.height(14.dp))
       Text("ڕێکخستنەکانی سیستەمی ئەندرۆید",color=gold,fontSize=18.sp)
       Button(onClick={
        val i=Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:"+packageName))
        try { startActivity(i) } catch (_:Exception) { startActivity(Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS)) }
       }) { Text("Battery Optimization") }
       Button(onClick={
        try { startActivity(Intent(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS)) }
        catch (_:Exception) { startActivity(Intent(Settings.ACTION_SETTINGS)) }
       }) { Text("Do Not Disturb") }
       Button(onClick={
        try { startActivity(Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE,packageName)) }
        catch (_:Exception) { startActivity(Intent(Settings.ACTION_SETTINGS)) }
       }) { Text("مۆڵەتی نۆتیکەیشن و شاشەی قوفڵ") }
       Text("نۆتیکەیشنەکان بە پێی ڕێکخستنەکانی ئەندرۆید دەرکەون؛ کاتی ورد گەرەنتی ناکرێت.", color=gold,fontSize=12.sp)
       }
      }
     }
     }
     }
     Row(Modifier.fillMaxWidth().background(Color(0xFF173C31),RoundedCornerShape(24.dp)).padding(8.dp),horizontalArrangement=Arrangement.SpaceEvenly) {listOf("⌂" to "سەرەکی","☷" to "زیکرەکان","⚙" to "ڕێکخستن").forEachIndexed {i,p->Column(Modifier.weight(1f).background(if(page==i)Color(0xFF305746)else Color.Transparent,RoundedCornerShape(18.dp)).clickable{page=if(i==0)0 else if(i==1)1 else 3}.padding(10.dp),horizontalAlignment=Alignment.CenterHorizontally){Text(p.first,color=gold,fontSize=23.sp);Text(p.second,color=Color.White,fontSize=13.sp)}}}
     Text("© Didar ismail",color=gold,fontSize=12.sp)
    }
   }
  }
 }
}
@Composable fun DhikrCard(d: Dhikr) {
 Column(Modifier.fillMaxWidth().background(Color(0xFF15392F), RoundedCornerShape(28.dp)).border(1.dp,Color(0xFF7A7554),RoundedCornerShape(28.dp)).padding(25.dp),horizontalAlignment=Alignment.CenterHorizontally) {
  Text(d.arabic,color=Color(0xFFFFEED5),fontSize=31.sp,textAlign=TextAlign.Center,lineHeight=43.sp)
  Spacer(Modifier.height(15.dp))
  Text(d.kurdish,color=Color.White,fontSize=19.sp,textAlign=TextAlign.Right,lineHeight=31.sp,modifier=Modifier.fillMaxWidth())
 }
}

@Composable fun SettingsSection(title:String, content:@Composable ColumnScope.()->Unit) { Column(Modifier.fillMaxWidth().background(Color(0xFF15392F),RoundedCornerShape(26.dp)).border(1.dp,Color(0xFF68765D),RoundedCornerShape(26.dp)).padding(20.dp),verticalArrangement=Arrangement.spacedBy(10.dp)) {Text(title,color=gold,fontSize=21.sp,fontWeight=FontWeight.Bold,modifier=Modifier.fillMaxWidth(),textAlign=TextAlign.End);content()} }
