/* Recording preparation: plain text only, small adjustable batches. */
function uniqueDoneCount(){
  const valid=new Set(VOCAB_HEADWORDS.map(x=>x.toLowerCase()));
  return new Set(P.flatMap(p=>doneList(p.id)).map(x=>x.toLowerCase()).filter(x=>valid.has(x))).size;
}
function recordingBatches(){
  const n=S.recordingSize||10,out=[];
  for(let i=0;i<REC_ENTRIES.length;i+=n)out.push(REC_ENTRIES.slice(i,i+n));
  return out;
}
function recordingBatch(){const a=recordingBatches();return a[Math.min(S.recordingBatch||0,a.length-1)]||[]}
function recordingText(){return recordingBatch().map(x=>x[1]).join("\n")}
function recordingHTML(){
  const batches=recordingBatches(),i=Math.min(S.recordingBatch||0,batches.length-1),batch=batches[i]||[],done=new Set(S.recordingDone||[]),marked=batch.length&&batch.every(x=>done.has(x[0]));
  const count=REC_ENTRIES.filter(x=>done.has(x[0])).length;
  return `<section class="recording-intro"><h2>音声収録リスト</h2><p>重複なし ${VOCAB_HEADWORDS.length.toLocaleString()}語 · ElevenLabs ${RECORDED_COUNT}語 · 収録待ち ${REC_ENTRIES.length}語</p><p>前回と同じJessica・アメリカ英語で、下の英語だけをコピーします。貼り付けで固まる場合は1語や5語に減らして試してください。短くしても直るとは限りません。</p><p>発音が複数ある語は短い文にしています。生成した音声は、このリストの順序と一緒に渡してください。単語部分を切り出して組み込みます。</p></section>
  <div class="card"><div class="srow"><label for="recordingSize">1回に表示する単語数</label><select id="recordingSize">${[1,5,10,20].map(n=>`<option value="${n}" ${S.recordingSize===n?'selected':''}>${n}語ずつ</option>`).join('')}</select></div>
  <div class="srow recording-batch"><div class="rhead"><strong>${i+1} / ${batches.length} · ${batch.length}語</strong><span>${marked?'作成済みマークあり':'未作成'}</span></div><label class="sr-only" for="recordingText">ElevenLabsに貼る原稿</label><textarea id="recordingText" readonly spellcheck="false">${esc(recordingText())}</textarea><div class="btnrow"><button class="btn-primary" data-act="recCopy">原稿をコピー</button><button class="btn-line" data-act="recDownload">この原稿をTXT保存</button></div><p class="recording-note">番号・日本語・音声タグは含みません。空白や改行だけでは一定の無音は保証されません。</p></div>
  <div class="srow"><div class="btnrow"><button class="btn-line" data-act="recPrev" ${i===0?'disabled':''}>前へ</button><button class="btn-line" data-act="recMark">${marked?'作成済みマークを外す':'この分を作成済みにする'}</button><button class="btn-line" data-act="recNext" ${i>=batches.length-1?'disabled':''}>次へ</button></div><p class="recording-note">作成済みマーク ${count} / ${REC_ENTRIES.length}語。音声がアプリに組み込まれたことを示すものではありません。</p></div></div>
  <details class="recording-targets"><summary>この原稿の対象単語・意味を確認</summary><ul>${batch.map(x=>{const w=VOCAB_LOOKUP[x[0].toLowerCase()];return `<li><strong>${esc(x[0])}</strong> · ${esc(w?w.ja:'')}</li>`}).join('')}</ul></details><div class="btnrow"><button class="btn-line" data-act="recDownloadAll">収録待ち全語をTXT保存</button><button class="btn-line" data-act="recHome">練習へ戻る</button></div>`;
}
function recordingDownload(all){
  const body=(all?REC_ENTRIES:recordingBatch()).map(x=>x[1]).join("\n")+"\n";
  const name=all?"hatsuon-recording-all.txt":`hatsuon-recording-${String((S.recordingBatch||0)+1).padStart(3,'0')}-${S.recordingSize}words.txt`;
  if(dlNS){dlNS.save({filename:name,data:body}).then(()=>toast("TXTを保存しました")).catch(()=>toast("保存できませんでした。原稿をコピーしてください"));return}
  const url=URL.createObjectURL(new Blob([body],{type:"text/plain;charset=utf-8"})),a=document.createElement("a");a.href=url;a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(url);a.remove()},500);
}
function openRecording(){stopPlayAll();speechGeneration++;stopRecordedAudio();try{speechSynthesis.cancel()}catch(e){}curW=null;view="recording";render();window.scrollTo(0,0)}
