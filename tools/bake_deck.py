#!/usr/bin/env python3
"""Rebuild this talk from pinned modular framework + talk/pitch.json. No network."""
import json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent.parent
s=(R/'tools/framework.html').read_text();old=(R.parent/'old-deck.html').read_text() if (R.parent/'old-deck.html').exists() else None
# Branding head is a tracked talk source; framework runtime stays pinned and repeatable.
head=(R/'talk/head.html').read_text()
s=re.sub(r'<head>.*?(?=<style>|<script>)', lambda m:head,s,count=1,flags=re.S)
# The first script contains content; retain loader scripts following it.
a=s.index('const SECTIONS = [');b=s.index('\n</script>',a)
p=(R/'talk/pitch.json').read_text().strip()
content='''const PITCH = /* PITCH-JSON START */\n'''+p+'''\n/* PITCH-JSON END */;
const TALK_KEY=(new URLSearchParams(location.search).get('talk')||'a').toLowerCase()==='b'?'b':'a';
const TALK=PITCH.talks[TALK_KEY];
const POOL=Object.fromEntries(PITCH.pool.map(x=>[x.id,x]));
const poolSlide=id=>({...POOL[id],notes:POOL[id].notes||''});
const SECTIONS=[...(TALK.intro.length?[{year:'OPEN',accent:'teal',lesson:{title:'',short:'',tagline:'',none:true},cases:TALK.intro.map(poolSlide)}]:[]),...TALK.acts.map(a=>({year:a.year,accent:a.accent,lesson:{...poolSlide(a.lesson),title:POOL[a.lesson].title.replace(/\\n/g,'<br>')},cases:a.cases.map(poolSlide)}))];
const BONUS={year:'',title:'',tagline:'',notes:'Optional framework end marker, hidden for this class.'};
'''
s=s[:a]+content+s[b:]
# Offline imports/fonts from the original talk.
s=re.sub(r'<script type="importmap">.*?</script>','<script type="importmap">{"imports":{"three":"./assets/vendor/three/three.module.min.js"}}</script>',s,count=1,flags=re.S)
s=re.sub(r'@import url\([^;]+;', '',s,count=1)
s=s.replace('<div id="brand">Spatial Deck</div>','<div id="brand">Alex Coulombe Presents</div>')
s=re.sub(r'cov.innerHTML=`.*?`;', 'cov.innerHTML=`<div class="event-tag">${PITCH.event}</div><h1 class="talk-title">${TALK.title.replace(/\\\\n/g,"<br>")}</h1><p class="talk-subtitle">${TALK.subtitle}</p><div class="speaker-card"><div><div class="speaker-name">${PITCH.speaker}</div><div class="speaker-co">${PITCH.company}</div></div></div>`;',s,count=1,flags=re.S)
# Lessons can be omitted in the cold open section, with a stable case-note index.
s=s.replace("  const ls=document.createElement('div');ls.className=", "  lessonIdxs[si]=allSlides.length-1;\n  if(!sec.lesson.none){const ls=document.createElement('div');ls.className=",1)
s=s.replace('deck.appendChild(ls);allSlides.push(ls);lessonIdxs.push(allSlides.length-1);','deck.appendChild(ls);allSlides.push(ls);lessonIdxs[si]=allSlides.length-1;}',1)
s=s.replace("if(ty==='cover')return'Welcome", "if(ty==='cover')return TALK.cover_spoken;\n  if(ty==='cover')return'Welcome",1)
s=s.replace("if(ty==='close')return'Wrap up.","if(ty==='close')return PITCH.close.notes;\n  if(ty==='close')return'Wrap up.",1)
s=re.sub(r'cls.innerHTML=`.*?`;',lambda m:'''cls.innerHTML=`<div class="close-ey">${PITCH.close.eyebrow}</div><h2 class="close-title">${PITCH.close.title}</h2><p class="close-sub">${PITCH.close.sub}</p><div class="contact-row">${PITCH.close.contacts.map(([l,v])=>`<div class="contact-pill"><span class="lbl">${l}</span>${v}</div>`).join('')}</div><div class="close-qr-row">${PITCH.close.qr.map(q=>`<div class="qr-card"><img src="${q.img}" alt="${q.label}"><div class="qr-label">${q.label}</div><div class="qr-badge b-teal">${q.badge}</div></div>`).join('')}</div>`;''',s,count=1,flags=re.S)
s=s.replace('// Navigation', "document.querySelectorAll('#deck .big-text').forEach(b=>{const n=Math.max(...b.innerHTML.split(/<br\\s*\\/?>/i).map(l=>l.replace(/<[^>]+>/g,'').length));b.classList.add(n>34?'big-l3':n>23?'big-l2':'big-l1');});\n// Navigation",1)
# Hide framework ending slides; keep a complete class close.
s=s.replace('// Navigation',"allSlides.forEach(s=>{if(['bonus','map'].includes(s.dataset.type))s.dataset.hidden='1';});\n// Navigation",1)
s=s.replace('// 3D Monocle on Bonus slide\n(function(){','// 3D Monocle on Bonus slide\n(function(){return; // class has no bonus monocle',1)
s=s.replace('</head>','<style>'+ (R/'talk/class.css').read_text()+'</style>\n</head>')
(R/'index.html').write_text(s)
for args in [['build_pitch.py'],['apply_look.py','--default','noir','--chrome','quiet'],['slide.py','sync',str(R)],['check_branding.py'],['slide.py','check',str(R)]]:
    subprocess.run([sys.executable,str(R/'tools'/args[0]),*args[1:]],check=True,cwd=R)
