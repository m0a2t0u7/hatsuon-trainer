"""Rebuild the second sprite from reviewed source ranges, preserving sprite one."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np

D=Path(__file__).resolve().parent
session=D/'new-20261022'
archive=session/'archive';archive.mkdir(exist_ok=True)
for name in ['jessica-map.json','recording-manifest.json','recording-all.txt']:
    dst=archive/name
    if not dst.exists(): dst.write_bytes((D/name).read_bytes())
old=json.loads((archive/'jessica-map.json').read_text())
assert len(old['clips'])==810
manifest=json.loads((archive/'recording-manifest.json').read_text())
expected={x['word'].lower():x for x in manifest['entries']}
accepted={};rejected=[]
for i in range(1,11):
    p=session/f'part-{i:02}'
    data=json.loads((p/'final-candidates.json').read_text())
    if isinstance(data,dict):data=[dict(v,word=k) for k,v in data.items()]
    for x in data:
        key=x['word'].lower();assert key in expected and key not in accepted
        x['part']=i;accepted[key]=x
    r=p/'final-reject.json'
    if r.exists():rejected.append({'part':i,'items':json.loads(r.read_text())})
assert not (set(old['clips'])&set(accepted))
rate=24000;prefix=np.zeros(round(.08*rate),dtype='<i2');suffix=np.zeros(round(.42*rate),dtype='<i2')
clips=dict(old['clips']);metadata={};parts=[];position=0;cache={};audit=[]
for key in expected:
    if key not in accepted:continue
    x=accepted[key];source=Path(x.get('file') or x.get('source'))
    if not source.is_absolute():source=(session/f"part-{x['part']:02}"/source).resolve()
    if not source.exists():raise FileNotFoundError(source)
    if source not in cache:
        cache[source]=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-f','s16le','-ac','1','-ar',str(rate),'-']),dtype='<i2')
    raw=cache[source];start,end=float(x['start']),float(x['end'])
    assert 0<=start<end<=len(raw)/rate+.001,(key,start,end)
    chunk=raw[round(start*rate):round(end*rate)]
    assert len(chunk)>rate*.08,key
    parts.extend([prefix,chunk,suffix])
    clips[key]=[round(position/rate,5),round((position+len(prefix)+len(chunk)+round(.15*rate))/rate,5),1]
    kind=x.get('clipKind','word');assert kind in ['word','sentence','utterance']
    metadata[key]={'clipKind':'sentence' if kind in ['sentence','utterance'] else 'word','utterance':x.get('utterance',expected[key]['utterance']),'target':key,'part':x['part']}
    audit.append(dict(x,word=key,source=str(source),outputRange=clips[key]))
    position+=len(prefix)+len(chunk)+len(suffix)
out=D/'jessica-extra-20261022.mp3'
subprocess.run(['ffmpeg','-v','error','-y','-f','s16le','-ar',str(rate),'-ac','1','-i','-','-codec:a','libmp3lame','-b:a','48k',str(out)],input=np.concatenate(parts).tobytes(),check=True)
m=dict(old);m.update(version=2,sources=['audio/jessica-padded.mp3','audio/jessica-extra-20261022.mp3'],clips=clips,clipMetadata=metadata,count=len(clips),total=1500,sourceDurations=[old['duration'],round(position/rate,5)],coverage={'original':810,'new':len(accepted),'newWord':sum(x['clipKind']=='word' for x in metadata.values()),'newSentence':sum(x['clipKind']=='sentence' for x in metadata.values()),'pending':690-len(accepted)})
(D/'jessica-map.json').write_text(json.dumps(m,ensure_ascii=False,separators=(',',':'))+'\n')
(session/'integration-audit.json').write_text(json.dumps({'accepted':audit,'rejected':rejected,'remaining':[expected[k] for k in expected if k not in accepted],'spriteBytes':out.stat().st_size,'spriteSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'coverage':m['coverage']},ensure_ascii=False,indent=1)+'\n')
print(json.dumps({'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'duration':m['sourceDurations'][1],'coverage':m['coverage']},ensure_ascii=False))
