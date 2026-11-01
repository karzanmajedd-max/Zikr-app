package com.didarismail.zikrakan

import android.app.*
import android.content.*
import android.media.AudioAttributes
import android.media.RingtoneManager
import android.os.Build
import java.util.Calendar

class ReminderReceiver : BroadcastReceiver() {
 override fun onReceive(context: Context, intent: Intent) {
  val prefs=context.getSharedPreferences("settings",Context.MODE_PRIVATE)
  val hour=Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
  val start=prefs.getInt("start",7)
  val end=prefs.getInt("end",22)
  val active=if(start<=end) hour in start until end else hour>=start || hour<end
  if(active) {
   val manager=context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
   val soundOn=prefs.getBoolean("sound",false)
   val vibrateOn=prefs.getBoolean("vibration",true)
   val choice=prefs.getInt("sound_choice",0).coerceIn(0,3)
   val channelId="dhikr_heads_up_v4_"+(if(soundOn) "sound"+choice else "silent")+(if(vibrateOn) "_vib" else "_still")
   val channel=NotificationChannel(channelId,"زیکرەکان — بانەری شاشە",NotificationManager.IMPORTANCE_HIGH).apply {
    description="پیشاندانی زیکر وەک بانەر لە سەرەوەی شاشە"
    enableVibration(vibrateOn)
    if(soundOn) {
     val type=when(choice) { 1->RingtoneManager.TYPE_ALARM;2->RingtoneManager.TYPE_RINGTONE;else->RingtoneManager.TYPE_NOTIFICATION }
     setSound(RingtoneManager.getDefaultUri(type), AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_NOTIFICATION).build())
    }
    else setSound(null,null)
    lockscreenVisibility=Notification.VISIBILITY_PUBLIC
   }
   manager.createNotificationChannel(channel)
   val index=prefs.getInt("next_index",0)
   val seed=prefs.getLong("seed",0L).let { if(it==0L) { val value=System.currentTimeMillis(); prefs.edit().putLong("seed",value).apply();value } else it }
   val shuffled=dhikrs.indices.shuffled(java.util.Random(seed))
   val d=dhikrs[shuffled[index % dhikrs.size]]
   prefs.edit().putInt("next_index",(index+1)%dhikrs.size).apply()
   if(index+1>=dhikrs.size) prefs.edit().putLong("seed",System.currentTimeMillis()).apply()
   val dismiss=Intent(context,DismissReceiver::class.java).putExtra("notification_id",101)
   val pending=PendingIntent.getBroadcast(context,101,dismiss,PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
   val notification=Notification.Builder(context,channelId)
    .setSmallIcon(android.R.drawable.ic_popup_reminder)
    .setCategory(Notification.CATEGORY_REMINDER)
    .setPriority(Notification.PRIORITY_MAX)
    .setDefaults(0)
    .setWhen(System.currentTimeMillis())
    .setShowWhen(true)
    .setContentTitle(d.arabic)
    .setContentText(d.kurdish)
    .setStyle(Notification.BigTextStyle().bigText(d.arabic+"\n"+d.kurdish))
    .setContentIntent(pending).setAutoCancel(true)
    .setVisibility(Notification.VISIBILITY_PUBLIC)
    .build()
   if(Build.VERSION.SDK_INT<33 || context.checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)==android.content.pm.PackageManager.PERMISSION_GRANTED) manager.notify(101,notification)
  }
  schedule(context)
 }
 companion object {
  fun schedule(context:Context) {
   val prefs=context.getSharedPreferences("settings",Context.MODE_PRIVATE)
   val minutes=prefs.getInt("interval",5).coerceAtLeast(1)
   val alarm=context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
   val pending=PendingIntent.getBroadcast(context,100,Intent(context,ReminderReceiver::class.java),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
   alarm.cancel(pending)
   alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,System.currentTimeMillis()+minutes*60_000L,pending)
  }
 }
}
class DismissReceiver:BroadcastReceiver() {
 override fun onReceive(context:Context,intent:Intent) {
  (context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).cancel(intent.getIntExtra("notification_id",101))
 }
}
class BootReceiver:BroadcastReceiver() {
 override fun onReceive(context:Context,intent:Intent) {
  if(intent.action==Intent.ACTION_BOOT_COMPLETED) ReminderReceiver.schedule(context)
 }
}
