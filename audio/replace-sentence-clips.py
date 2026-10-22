"""Build a small third sprite after the new isolated-word ranges are reviewed.

Input: audio/new-20261023/accepted.json, a list of word/start/end records.
Original source recordings and the first two sprites are never rewritten.
"""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np

D=Path(__file__).resolve().parent
session=D/'new-20261023';session.mkdir(exist_ok=True)
accepted=json.loads((session/'accepted.json').read_text())
if isinstance(accepted,dict):accepted=[dict(v,word=k) for k,v in accepted.items()]
assert accepted
archive=session/'archive';archive.mkdir(exist_ok=True)
baseline=archive/'jessica-map.json'
if not baseline.exists():baseline.write_bytes((D/'jessica-map.json').read_bytes())
m=json.loads(baseline.read_text())
assert len(m['sources'])==2
source=Path('/workspace/scratch/8b5a8e3d1bf6/upload/ElevenLabs_2026-10-23T02_32_38_Jessica - Playful, Bright, Warm_eleven_v4.mp3')
rate=24000
raw=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-f','s16le','-ac','1','-ar',str(rate),'-']),dtype='<i2')
prefix=np.zeros(round(rate*.08),dtype='<i2');suffix=np.zeros(round(rate*.42),dtype='<i2')
parts=[];position=0;seen=set();audit=[]
for x in accepted:
    key=x['word'].lower();assert key not in seen;seen.add(key)
    old=m['clipMetadata'][key];assert old['clipKind']=='sentence'
    start,end=float(x['start']),float(x['end'])
    assert 0<=start<end<=len(raw)/rate+.001
    chunk=raw[round(start*rate):round(end*rate)];assert len(chunk)>rate*.08
    parts.extend([prefix,chunk,suffix])
    clip=[round(position/rate,5),round((position+len(prefix)+len(chunk)+round(.15*rate))/rate,5),2]
    audit.append(dict(x,previousClip=m['clips'][key],previousMetadata=old,outputRange=clip))
    m['clips'][key]=clip
    m['clipMetadata'][key]={'clipKind':'word','utterance':key,'target':key,'session':'20261023'}
    position+=len(prefix)+len(chunk)+len(suffix)
out=D/'jessica-isolated-20261023.mp3'
subprocess.run(['ffmpeg','-v','error','-y','-f','s16le','-ar',str(rate),'-ac','1','-i','-','-codec:a','libmp3lame','-b:a','48k',str(out)],input=np.concatenate(parts).tobytes(),check=True)
m['sources'].append('audio/'+out.name);m['sourceDurations'].append(round(position/rate,5))
m['coverage']['newWord']+=len(seen);m['coverage']['newSentence']-=len(seen)
m['coverage']['isolatedReplacement20261023']=len(seen)
(D/'jessica-map.json').write_text(json.dumps(m,ensure_ascii=False,separators=(',',':'))+'\n')
report={'source':str(source),'accepted':audit,'count':len(seen),'spriteBytes':out.stat().st_size,'spriteSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'duration':position/rate,'coverage':m['coverage']}
(session/'integration-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=1)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['accepted','source']},ensure_ascii=False))
