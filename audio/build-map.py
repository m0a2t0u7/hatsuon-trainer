import json,re,difflib
from pathlib import Path
D=Path(__file__).parent
e=json.loads((D/'expected.json').read_text());a=json.loads((D/'asr-base.json').read_text());old=json.loads((D/'candidate-clips.json').read_text())
n=lambda x:re.sub('[^a-z0-9]','',x.lower())
alias={'bury':'berry','aunt':'ant','week':'weak','sea':'see','piece':'peace','too':'to','flu':'flue','due':'do','flew':'flue','two':'to','plane':'plain','wait':'weight','write':'right','eye':'i','no':'know','so':'sew','know':'no','here':'hear','pier':'peer','fare':'fair','wear':'where','pear':'pair','their':'there','for':'four','four':'for','nose':'knows','rose':'rows','hire':'higher','which':'witch'}
match={};reason={}
for tag,i,j,k,l in difflib.SequenceMatcher(None,list(map(n,e)),[n(x['word']) for x in a],autojunk=False).get_opcodes():
 if tag=='equal':
  for u,v in zip(range(i,j),range(k,l)):match[u]=(v,'exact')
 elif tag=='replace' and j-i==l-k:
  for u,v in zip(range(i,j),range(k,l)):
   if alias.get(e[u].lower())==n(a[v]['word']):match[u]=(v,'homophone')
# Build center anchors for every recognized token, plus confidently matched first-pass words missing in the second pass.
anchors=[{'center':(w['start']+w['end'])/2,'index':j,'word':w['word']} for j,w in enumerate(a) if w['end']>w['start']]
positions={i:(a[j]['start']+a[j]['end'])/2 for i,(j,_) in match.items()}
for i,w in enumerate(e):
 if i in match:continue
 c=old.get(w)
 if not c or c['probability']<.8:continue
 center=(c['start']+c['end'])/2
 prev=max((positions[k] for k in positions if k<i),default=-1);nxt=min((positions[k] for k in positions if k>i),default=690)
 if prev<center<nxt:
  positions[i]=center;match[i]=(None,'first-pass');anchors.append({'center':center,'index':'old:'+str(i),'word':w})
# A zero-duration ASR token may be retained only when the independent first pass supplies a timed occurrence.
for i,(j,src) in list(match.items()):
 if j is not None and a[j]['end']<=a[j]['start']:
  c=old.get(e[i])
  if c and c['probability']>=.7:
   center=(c['start']+c['end'])/2;positions[i]=center;anchors.append({'center':center,'index':'old:'+str(i),'word':e[i]});match[i]=(None,'first-pass')
  else:del match[i];positions.pop(i,None)
anchors.sort(key=lambda x:x['center'])
sil=[];pending=None
for line in (D/'silence-fine.log').read_text().splitlines():
 m=re.search(r'silence_start: ([0-9.]+)',line)
 if m:pending=float(m[1])
 m=re.search(r'silence_end: ([0-9.]+)',line)
 if m and pending is not None:sil.append((pending,float(m[1])));pending=None
heteronyms={'live','read','lead','close','use','present','record','contract','project','increase','tear','minute'}
clips={};audit=[];missing=[]
for i,w in enumerate(e):
 if i not in match:missing.append({'word':w,'reason':'認識結果が一致しない'});continue
 j,src=match[i];center=positions[i]
 if w.lower() in heteronyms:missing.append({'word':w,'reason':'同じつづりで発音が複数あるため要確認'});continue
 if j is not None and a[j]['probability']<.35:missing.append({'word':w,'reason':'音声認識の確度不足'});continue
 # If a word was skipped by recognition, do not let its neighbours absorb its sound.
 if any(k>=0 and k<len(e) and k not in match for k in [i-1,i+1]):missing.append({'word':w,'reason':'隣の単語が未認識で境界が不確実'});continue
 ai=next((t for t,x in enumerate(anchors) if x['index']==(j if j is not None else 'old:'+str(i))),None)
 if ai is None:missing.append({'word':w,'reason':'再生位置不明'});continue
 def boundary(lo,hi):
  candidates=[(max(lo,s),min(hi,t)) for s,t in sil if t>lo and s<hi]
  candidates=[(s,t) for s,t in candidates if t-s>=.045]
  if not candidates:return None
  s,t=max(candidates,key=lambda z:z[1]-z[0]);return round((s+t)/2,4)
 start=0 if ai==0 else boundary(anchors[ai-1]['center'],center)
 end=689.45 if ai==len(anchors)-1 else boundary(center,anchors[ai+1]['center'])
 if start is None or end is None or end-start<.18 or end-start>2.5:missing.append({'word':w,'reason':'十分な無音の境界がない'});continue
 clips[w.lower()]=[start,end];audit.append({'word':w,'start':start,'end':end,'source':src})
(D/'jessica-map.json').write_text(json.dumps({'version':1,'audio':'audio/jessica.mp3','voice':'Jessica','accent':'en-US','count':len(clips),'total':len(e),'clips':clips},ensure_ascii=False,separators=(',',':')))
(D/'clip-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=1))
(D/'unmatched-words.json').write_text(json.dumps(missing,ensure_ascii=False,indent=1))
(D/'regenerate-words.txt').write_text('\n'.join(x['word']+'.' for x in missing)+'\n')
print('adopted',len(clips),'unmatched',len(missing),'big',clips.get('big'));print(missing[:15])
