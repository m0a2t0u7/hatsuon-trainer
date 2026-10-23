// Node.js 2026-10-21 security release minimums; fail before running QA on an unpatched runtime.
(() => {
  const [major, minor, patch] = process.versions.node.split('.').map(Number);
  const minimum = {22: [23, 4], 24: [22, 1], 26: [12, 1]}[major];
  if (!minimum || minor < minimum[0] || (minor === minimum[0] && patch < minimum[1])) {
    throw new Error('Use patched Node.js 22.23.4, 24.22.1, or 26.12.1 (or newer in those release lines). Current: ' + process.versions.node);
  }
})();

const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../index.html'),'utf8');
const block=src.slice(src.indexOf('let allVoices=[];'),src.indexOf('function startPlayAll('));
const sleep=n=>new Promise(r=>setTimeout(r,n));
const map={audio:'audio/jessica-padded.mp3',sources:['audio/jessica-padded.mp3','audio/jessica-extra-20261022.mp3','audio/jessica-isolated-20261023.mp3'],clips:{first:[1,2],second:[3,4,1],third:[5,6,2]}};
function env({delayMap=0,ready=1,failPlay=false,failMap=false}={}){let aa=[],tts=[],hiddenFn;class A{constructor(url){this.src=url;aa.push(this);this.duration=100;this.readyState=ready;this.events={};this._time=0;this.seeking=false;this.paused=true}addEventListener(n,f){(this.events[n]??=new Set).add(f)}removeEventListener(n,f){this.events[n]?.delete(f)}emit(n){for(const f of [...(this.events[n]||[])])f()}get currentTime(){return this._time}set currentTime(v){this._time=v;this.seeking=true;setTimeout(()=>{this.seeking=false;this.emit('seeked')},0)}load(){}pause(){this.paused=true}play(){if(failPlay)return Promise.reject(Error('blocked'));this.paused=false;setTimeout(()=>this.emit('playing'),0);return Promise.resolve()}}
const synth={getVoices:()=>[],cancel(){},speak(u){tts.push(u);setTimeout(()=>u.onend?.(),0)}};
const c={S:{set:{audioSource:'eleven',accent:'us',rate:1,slow:.6}},Audio:A,SpeechSynthesisUtterance:class{constructor(t){this.text=t}},speechSynthesis:synth,window:{speechSynthesis:synth},document:{hidden:false,addEventListener(n,f){if(n==='visibilitychange')hiddenFn=f}},view:'phon',fetch:async()=>{await sleep(delayMap);if(failMap)throw Error("network");return{ok:true,json:async()=>map}},AbortController,Number,Error,setTimeout,clearTimeout,toast(){},renderToolbar(){},console};vm.createContext(c);vm.runInContext(block,c);vm.runInContext('function stopPlayAll(){speechGeneration++;stopRecordedAudio();playAll=null}',c);return{c,aa,tts,run:x=>vm.runInContext(x,c),hide(){c.document.hidden=true;hiddenFn()}}}
(async()=>{let e=env(),done=0;e.c.cb=()=>done++;e.run('speak("first",false,cb)');await sleep(30);assert.equal(e.aa[0].src,map.sources[0]);e.run('speak("second",false,cb,{rate:.75})');await sleep(30);assert(e.aa[0].paused);assert.equal(e.aa[1].src,map.sources[1]);assert.equal(e.aa[1].playbackRate,.75);e.aa[1]._time=4;await sleep(30);assert.equal(done,1);assert(e.aa[1].paused);e.run('speak("second",false,cb)');await sleep(30);assert.equal(e.aa[1].currentTime,3);assert.equal(e.aa.length,2);e.run('speak("third",false,cb,{rate:1.25})');await sleep(30);assert(e.aa[1].paused);assert.equal(e.aa[2].src,map.sources[2]);assert.equal(e.aa[2].playbackRate,1.25);assert.equal(e.aa[2].currentTime,5);e.aa[2]._time=6;await sleep(30);assert.equal(done,2);e.run('speak("third",false,cb)');await sleep(30);assert.equal(e.aa[2].currentTime,5);assert.equal(e.aa.length,3);e.hide();assert(e.aa.every(a=>a.paused));
e=env({delayMap:40});e.run('speak("third",false);stopPlayAll()');await sleep(70);assert.equal(e.aa.length,0);assert.equal(e.tts.length,0);
e=env({ready:0});e.run('speak("third",false)');await sleep(20);e.run('stopPlayAll()');e.aa[0].readyState=1;e.aa[0].emit('loadedmetadata');await sleep(20);assert(e.aa[0].paused);assert.equal(e.tts.length,0);
e=env({failPlay:true});e.run('speak("third",false)');await sleep(100);assert.equal(e.tts.length,1);
e=env();e.run('speak("unknown",false)');await sleep(90);assert.equal(e.tts.length,1);assert.equal(e.aa.length,0);
e=env();e.run('S.set.accent="gb";speak("third",false)');await sleep(90);assert.equal(e.tts.length,1);assert.equal(e.aa.length,0);
e=env({failMap:true});e.run('speak("third",false)');await sleep(100);assert.equal(e.tts.length,1);assert.equal(e.aa.length,0);
console.log('PASS three-source mock: source switching, rate, single completion, repeat seek/pool reuse, hidden stop, cancel map load, cancel metadata load, rejection fallback, unknown fallback, GB fallback');process.exit(0)})().catch(e=>{console.error(e);process.exit(1)});
