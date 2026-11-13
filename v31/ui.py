from pathlib import Path
p=Path("buildsrc/app/src/main/assets/index.html")
s=p.read_text(encoding="utf-8")
marker="function render(){"
assert marker in s
script="""function tidySettingsLayout(){
 const all=[...main.querySelectorAll('.settingCard')];
 const primary=all.find(c=>c.querySelector('#enabled'));
 const schedule=all.find(c=>c.querySelector('#intervalMode'));
 const quick=all.find(c=>c.classList.contains('quickFix'));
 const info=all.find(c=>c.querySelector('#test'));
 if(!primary||!schedule||!quick||!info)return;
 const sub=main.querySelector('.subheading');
 if(sub)sub.textContent='بانەری سەوز لە شاشەی کراوە، نۆتیفیکەیشن لە شاشەی قوفڵ';
 primary.classList.add('cleanSettings');
 primary.insertAdjacentHTML('afterbegin','<div class="sectionTitle">◐ بانەر و نۆتیفیکەیشن</div>');
 primary.querySelector('#banner').closest('.row').querySelector('small').textContent='تەنها لە شاشەی کراوە، بە دیزاینی سەوز و زێڕ';
 const help=document.createElement('p');help.className='simpleHelp';
 help.textContent='🔒 کاتێک مۆبایل قوفڵە، زیکر بە عەرەبی و مانای کوردی وەک نۆتیفیکەیشنی سیستەم پیشان دەدرێت.';
 primary.insertBefore(help,primary.querySelector('.systemActions'));
 const originalActions=primary.querySelector('.systemActions');
 const soundCard=document.createElement('section');soundCard.className='settingCard cleanSettings';
 soundCard.innerHTML='<div class="sectionTitle">♫ دەنگ و لەرینەوە</div>';
 for(const id of ['sound','vibrate']){const row=primary.querySelector('#'+id).closest('.row');soundCard.appendChild(row)}
 soundCard.appendChild(primary.querySelector('#listenChime'));
 const advance=document.createElement('details');advance.className='settingCard cleanSettings cleanAdvanced';
 advance.innerHTML='<summary>⚙ ڕێکخستنە پێشکەوتووەکان</summary>';
 const actions=document.createElement('div');actions.className='systemActions';
 for(const id of ['diagnoseBanner','systemBanner','systemExact'])actions.appendChild(primary.querySelector('#'+id));
 const system=primary.querySelector('#systemNotifications');
 system.textContent='نۆتیفیکەیشنی شاشەی قوفڵ';
 const overlay=primary.querySelector('#systemOverlay');
 overlay.textContent='ڕێگەدان بە بانەری سەوز';
 const diagnostic=primary.querySelector('#bannerDiagnosticResult');
 actions.appendChild(diagnostic);
 advance.appendChild(actions);
 advance.appendChild(quick);
 const testButton=info.querySelector('#test'),testStatus=info.querySelector('#testStatus');
 const testCard=document.createElement('section');testCard.className='settingCard cleanSettings';
 testCard.appendChild(testButton);testCard.appendChild(testStatus);
 advance.appendChild(info);
 primary.appendChild(originalActions);
 main.appendChild(primary);main.appendChild(soundCard);main.appendChild(schedule);main.appendChild(testCard);main.appendChild(advance);
} 
"""
s=s.replace(marker,script+marker,1)
old="main.innerHTML=tab==='home'?home():tab==='list'?list():settings(); bind();"
new="main.innerHTML=tab==='home'?home():tab==='list'?list():settings(); if(tab==='settings')tidySettingsLayout(); bind();"
assert old in s
s=s.replace(old,new,1)
css="""<style>
.cleanSettings{background:#13382e!important;border-radius:23px!important;margin-top:14px!important;padding:18px!important}
.cleanSettings .sectionTitle{font-size:18px;color:#dfc389}
.cleanSettings .row{padding:13px 0}.cleanSettings small{line-height:1.7}
.cleanSettings .simpleHelp{font-size:12px;line-height:2;padding:12px;background:#0b291f;border:1px solid #4e6348;border-radius:13px;margin:12px 0;color:#f1e4cc}
.cleanSettings .systemActions{display:grid;gap:7px}.cleanSettings .systemActions button{margin-top:4px}
.cleanAdvanced summary{font-size:17px;color:#ddbf81;font-weight:bold;cursor:pointer;padding:5px 0}
.cleanAdvanced .quickFix{margin-top:15px}
.cleanSettings #listenChime{margin-top:12px!important}
</style>"""
assert "</head>" in s
s=s.replace("</head>",css+"</head>",1)
p.write_text(s,encoding="utf-8")
print("Simplified settings layout into three cards with optional advanced actions")
