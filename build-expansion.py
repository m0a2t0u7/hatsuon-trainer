import json,re,subprocess,collections
from pathlib import Path
D=Path(__file__).parent
base=(D/'expand-base.html').read_text()
script=base[base.index('const CATS='):base.index('/*END*/')]
data=json.loads(subprocess.check_output(['node','-e',script+';console.log(JSON.stringify(P))'],text=True))
def wordrows(p):
    for label,rows in p['groups']:
        for row in rows.split(';'):
            z=row.split('|')
            if len(z)==4:yield {'word':z[0].replace('[','').replace(']',''),'marked':z[0],'ipa':z[1],'ja':z[2],'level':int(z[3]),'phonId':p['id']}
oldrows=[w for p in data for w in wordrows(p)]
old={w['word'].lower():w for w in oldrows}
assert len(old)==938,len(old)
candidate=[w for n in ['af','gp','qz'] for w in json.loads((D/f'vocab-{n}.json').read_text())]
candidate += json.loads((D/'vocab-gp-reserve.json').read_text()) if (D/'vocab-gp-reserve.json').exists() else []
seen=set(old);valid=[]
for w in candidate:
    k=w['word'].lower()
    if k in seen:continue
    assert w['marked'].replace('[','').replace(']','')==w['word'],w
    assert w['phonId'] in {p['id'] for p in data},w
    assert w['level'] in [1,2,3] and w['ja'] and w['ipa'],w
    seen.add(k);valid.append(w)
assert len(valid)>=562,len(valid)
# Retain useful basic/daily vocabulary first. Words explicitly assigned to
# currently small sound groups are selected before other equally basic words.
counts={p['id']:sum(1 for _ in wordrows(p)) for p in data}
selected=[];remaining=valid.copy()
while len(selected)<562:
    remaining.sort(key=lambda w:(w['level'],0 if counts[w['phonId']]<30 else 1,w['word'].lower()))
    w=remaining.pop(0);selected.append(w);counts[w['phonId']]+=1
selected.sort(key=lambda w:w['word'].lower())
(D/'vocab-additions.json').write_text(json.dumps(selected,ensure_ascii=False,indent=1)+'\n')
extra={}
for w in selected:extra.setdefault(w['phonId'],[]).append(w)
for p in data:
    a=extra.get(p['id'],[])
    if a:p['groups'].append(['よく使う単語（追加）',';'.join('|'.join([w['marked'],w['ipa'],w['ja'],str(w['level'])]) for w in a)])
# Optional manually audited cross-listing fills small groups without adding
# unusual words merely to hit a per-sound quota.
cross=json.loads((D/'vocab-cross-list.json').read_text()) if (D/'vocab-cross-list.json').exists() else []
for p in data:
    existing={x['word'].lower() for x in wordrows(p)}
    extra_cross=[w for w in cross if w['phonId']==p['id'] and w['word'].lower() not in existing]
    if extra_cross:p['groups'].append(['別の音でも練習',';'.join('|'.join([w['marked'],w['ipa'],w['ja'],str(w['level'])]) for w in extra_cross)])
rows=[w for p in data for w in wordrows(p)];unique={}
for w in rows:unique.setdefault(w['word'].lower(),w)
assert len(unique)==1500,len(unique)
audio_map=json.loads((D/'audio/jessica-map.json').read_text())
recorded=audio_map['clips']
recorded_sentences={k:v['utterance'] for k,v in audio_map.get('clipMetadata',{}).items() if v.get('clipKind')=='sentence'}
recordedkeys={k.lower() for k in recorded}
recorded_count=len(set(unique)&recordedkeys)
assert recorded_count<=len(unique)
pending=[w for k,w in unique.items() if k not in recordedkeys]
assert len(pending)==len(unique)-recorded_count,len(pending)
contexts={
'live':'I live here.','present':'A birthday present.','read':'I read books every day.','increase':'Prices will increase.','project':'My school project.','contract':'Sign a contract.','close':'Please close the door.','tear':'She shed a tear.','record':'A world record.','minute':'One minute.','lead':'Please lead the way.','use':'Please use this.',
'address':'My home address.','adult':'An adult.','advocate':'An advocate.','alternate':'An alternate route.','attribute':'A useful attribute.','bow':'Tie a bow.','compound':'A chemical compound.','content':'The content of this book.','conflict':'A conflict between friends.','conduct':'Please conduct the test.','contest':'A singing contest.','convert':'Please convert this file.','desert':'A hot desert.','digest':'Please digest the food.','entrance':'The main entrance.','excuse':'Please excuse me.','export':'Please export the file.','import':'Please import the file.','insult':'That was an insult.','object':'A small object.','permit':'A parking permit.','produce':'Please produce a report.','progress':'We made progress.','refuse':'I refuse to go.','resume':'Please resume the lesson.','row':'A row of chairs.','subject':'My favorite subject.','suspect':'The main suspect.','wind':'A strong wind.','wound':'A deep wound.','separate':'Please separate these items.','estimate':'Please estimate the cost.','discount':'A special discount.','rebel':'A rebel.','perfect':'A perfect day.','polish':'Please polish the shoes.','second':'One second.','total':'The total amount.','transfer':'Please transfer the money.','transport':'Please transport the goods.','document':'A useful document.'}
entries=[]
for w in pending:
    k=w['word'].lower();entries.append({'id':k,'word':w['word'],'target':w['word'],'ipa':w['ipa'],'ja':w['ja'],'phonId':w['phonId'],'utterance':contexts.get(k,w.get('prompt') or w['word']+'.')})
batches=[{'id':f'batch-{i//10+1:03}','entries':entries[i:i+10],'text':'\n'.join(w['utterance'] for w in entries[i:i+10])} for i in range(0,len(entries),10)]
manifest={'version':1,'vocabularyUnique':1500,'practiceEntries':len(rows),'recordedUnique':recorded_count,'pendingUnique':len(pending),'defaultBatchSize':10,'batchSizeOptions':[1,5,10,20],'voice':'Jessica','accent':'en-US','format':'plain text; no pause tags or spoken numbering','entries':entries,'batches':batches}
(D/'audio/recording-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=1)+'\n')
(D/'audio/recording-all.txt').write_text('\n'.join(w['utterance'] for w in entries)+'\n')
scriptsdir=D/'audio/recording-batches';scriptsdir.mkdir(exist_ok=True)
for stale in scriptsdir.glob('batch-*.txt'):stale.unlink()
for b in batches:(scriptsdir/(b['id']+'.txt')).write_text(b['text']+'\n')
counts={p['id']:sum(1 for _ in wordrows(p)) for p in data}
(D/'vocabulary-report.json').write_text(json.dumps({'unique':len(unique),'practiceEntries':len(rows),'new':len(selected),'recorded':recorded_count,'pending':len(pending),'audioCoverage':audio_map.get('coverage',{}),'counts':[{'id':p['id'],'ipa':p['ipa'],'count':counts[p['id']]} for p in data],'under30':[{'id':p['id'],'ipa':p['ipa'],'count':counts[p['id']]} for p in data if counts[p['id']]<30],'omittedCandidates':[w['word'] for w in remaining]},ensure_ascii=False,indent=1)+'\n')
# Serialize the data constants as JSON so all words have one canonical source.
vowels=[p for p in data if p['cat']!='cons'];cons=[p for p in data if p['cat']=='cons']
s=base
s=s[:s.index('const P=')]+'const P='+json.dumps(vowels,ensure_ascii=False,indent=1)+';\n'+s[s.index('const PAIRS='):]
s=s[:s.index('const PC=')]+'const PC='+json.dumps(cons,ensure_ascii=False,indent=1)+';\n'+s[s.index('const CPAIRS='):]
embed='\n/* VOCABULARY AND RECORDING PLAN */\nconst VOCAB_HEADWORDS='+json.dumps([w['word'] for w in unique.values()],ensure_ascii=False)+';\nconst VOCAB_LOOKUP='+json.dumps({k:{'ja':w['ja']} for k,w in unique.items()},ensure_ascii=False)+';\nconst RECORDED_COUNT='+str(recorded_count)+';\nconst REC_SENTENCES='+json.dumps(recorded_sentences,ensure_ascii=False)+';\nconst REC_ENTRIES='+json.dumps([[w['word'],w['utterance']] for w in entries],ensure_ascii=False)+';\n'
s=s.replace('/*END*/',embed+'/*END*/',1)
s=s.replace('const o={last:null,done:{},quizBest:0,set:{}};','const o={last:null,done:{},quizBest:0,set:{},recordingSize:10,recordingBatch:0,recordingDone:[]};',1)
s=s.replace('  return o;\n}\ntry{S=normalizeState', '  if(s&&typeof s==="object"){o.recordingSize=[1,5,10,20].includes(s.recordingSize)?s.recordingSize:10;o.recordingBatch=Math.max(0,Math.min(Math.ceil(REC_ENTRIES.length/o.recordingSize)-1,Math.floor(Number(s.recordingBatch)||0)));o.recordingDone=Array.isArray(s.recordingDone)?s.recordingDone.filter(x=>typeof x==="string"&&REC_ENTRIES.some(w=>w[0]===x)):[]}\n  return o;\n}\ntry{S=normalizeState',1)
s=s.replace('/* ---------- render ---------- */',(D/'recording-ui.js').read_text()+'\n/* ---------- render ---------- */',1)
s=s.replace('${P.reduce((a,p)=>a+doneList(p.id).length,0)} / ${P.reduce((a,p)=>a+totalN(p),0)}語クリア','${uniqueDoneCount()} / ${VOCAB_HEADWORDS.length.toLocaleString()}語クリア',1)
s=s.replace('else if(view==="quiz"){$top.innerHTML=', 'else if(view==="recording"){$top.innerHTML=`<button class="back" data-act="recHome" aria-label="練習へ戻る">${ic("chevL")}</button><h1>音声収録</h1>`;$main.innerHTML=recordingHTML()}\n    else if(view==="quiz"){$top.innerHTML=',1)
s=s.replace('  const lp=S.last&&byId(S.last);','  h+=`<p class="intro">単語 ${VOCAB_HEADWORDS.length.toLocaleString()}語（重複なし） · 音別の練習 ${P.reduce((a,p)=>a+totalN(p),0).toLocaleString()}件<br>ElevenLabs ${RECORDED_COUNT}語 · 収録待ち ${REC_ENTRIES.length}語</p><div class="btnrow"><button class="btn-line" data-act="recOpen">音声収録リストを開く</button></div>`;\n  const lp=S.last&&byId(S.last);',1)
s=s.replace('return `<h2 class="set-h">再生</h2>', 'return `<h2 class="set-h">単語と音声収録</h2><div class="card"><div class="srow"><span class="lab">重複なし ${VOCAB_HEADWORDS.length.toLocaleString()}語<span class="desc">同じ単語を複数の音で練習するため、音ごとの件数の合計とは異なります。中学・高校・TOEICの区分は学習用の目安です。</span></span><div class="btnrow"><button class="btn-line" data-act="recOpen">音声収録リストを開く（残り${REC_ENTRIES.length}語）</button></div></div></div><h2 class="set-h">再生</h2>',1)
s=s.replace('const ACT={','const ACT={\n  recOpen(){openRecording()},recHome(){goMap()},\n  recPrev(){S.recordingBatch=Math.max(0,S.recordingBatch-1);save();render()},\n  recNext(){S.recordingBatch=Math.min(recordingBatches().length-1,S.recordingBatch+1);save();render()},\n  recMark(){const b=recordingBatch(),d=new Set(S.recordingDone),all=b.every(x=>d.has(x[0]));b.forEach(x=>all?d.delete(x[0]):d.add(x[0]));S.recordingDone=[...d];save();render()},\n  async recCopy(){const text=recordingText();try{if(!navigator.clipboard||!navigator.clipboard.writeText)throw Error();await navigator.clipboard.writeText(text);toast("英語の原稿をコピーしました")}catch(e){const t=document.getElementById("recordingText");t.focus();t.select();try{if(document.execCommand("copy")){toast("英語の原稿をコピーしました");return}}catch(e){}toast("原稿を選択しました。長押ししてコピーしてください")}},\n  recDownload(){recordingDownload(false)},recDownloadAll(){recordingDownload(true)},',1)
s=s.replace('  if(t.dataset.play){const k=', '  if(t.id==="recordingSize"){const offset=(S.recordingBatch||0)*(S.recordingSize||10);S.recordingSize=[1,5,10,20].includes(+t.value)?+t.value:10;S.recordingBatch=Math.floor(offset/S.recordingSize);save();render()}\n  if(t.dataset.play){const k=',1)
css='\n.recording-intro p,.recording-note{color:var(--ink2);font-size:.85rem;line-height:1.7}.recording-batch textarea{width:100%;box-sizing:border-box;min-height:16rem;max-height:55vh;margin:.75rem 0;padding:.75rem;border:1px solid var(--line);border-radius:.65rem;background:var(--bg);font:1rem/1.8 var(--f-ui);color:var(--ink);resize:vertical}.recording-batch .rhead{gap:.5rem;flex-wrap:wrap}.recording-batch .rhead span{font-size:.8rem;color:var(--ink2)}.recording-targets{margin:1rem 0;padding:.7rem;background:var(--surface);border:1px solid var(--line);border-radius:.7rem}.recording-targets summary{cursor:pointer;min-height:2rem}.recording-targets li{padding:.25rem 0;font-size:.9rem}.recording-intro h2{margin:.25rem 0}.btnrow{flex-wrap:wrap}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}\n'
s=s.replace('</style>',css+'</style>',1)
(D/'index.html').write_text(s)
print(json.dumps({'unique':len(unique),'new':len(selected),'practiceEntries':len(rows),'pending':len(pending),'batches':len(batches),'under30':{p['ipa']:counts[p['id']] for p in data if counts[p['id']]<30}},ensure_ascii=False))
