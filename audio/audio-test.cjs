// Node.js 2026-10-21 security release minimums; fail before running QA on an unpatched runtime.
(() => {
  const [major, minor, patch] = process.versions.node.split('.').map(Number);
  const minimum = {22: [23, 4], 24: [22, 1], 26: [12, 1]}[major];
  if (!minimum || minor < minimum[0] || (minor === minimum[0] && patch < minimum[1])) {
    throw new Error('Use patched Node.js 22.23.4, 24.22.1, or 26.12.1 (or newer in those release lines). Current: ' + process.versions.node);
  }
})();

const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync('hatsuon-work/index.html','utf8');const block=src.slice(src.indexOf('let allVoices=[];'),src.indexOf('function startPlayAll('));
const map=JSON.parse(fs.readFileSync('hatsuon-work/audio/jessica-map.json'));
const sleep=n=>new Promise(r=>setTimeout(r,n));
function env({failPlay=false,delayMap=0}={}){
 let audio,tts=[],hiddenFn;class A{
  constructor(){audio=this;this.readyState=1;this.events={};this._time=0;this.seeking=false;this.paused=true}
  addEventListener(n,f){(this.events[n]??=new Set).add(f)}removeEventListener(n,f){this.events[n]?.delete(f)}emit(n){for(const f of [...(this.events[n]||[])])f()}
  get currentTime(){return this._time}set currentTime(v){this._time=v;this.seeking=true;setTimeout(()=>{this.seeking=false;this.emit('seeked')},0)}
  load(){}pause(){this.paused=true}play(){if(failPlay)return Promise.reject(Error('blocked'));this.paused=false;setTimeout(()=>this.emit('playing'),0);return Promise.resolve()}
 }
 const synth={getVoices:()=>[],cancel(){},speak(u){tts.push(u);setTimeout(()=>u.onend?.(),0)}};
 const c={S:{set:{audioSource:'eleven',accent:'us',rate:1,slow:.6}},Audio:A,SpeechSynthesisUtterance:class{constructor(t){this.text=t}},speechSynthesis:synth,window:{speechSynthesis:synth},document:{hidden:false,addEventListener(n,f){if(n==='visibilitychange')hiddenFn=f}},view:'phon',fetch:async()=>{await sleep(delayMap);return{ok:true,json:async()=>map}},AbortController,Number,Error,setTimeout,clearTimeout,toast(){},renderToolbar(){},stopPlayAll(){},console};vm.createContext(c);vm.runInContext(block,c);return{c,get audio(){return audio},tts,hide(){c.document.hidden=true;hiddenFn()}};
}
(async()=>{
 let e=env(),done=0; e.c.cb=()=>done++;vm.runInContext('speak("big",false,cb)',e.c);await sleep(30);assert.equal(e.audio.currentTime,map.clips.big[0]);assert(!e.audio.paused);e.audio.currentTime=map.clips.big[1];await sleep(35);assert(e.audio.paused);assert.equal(done,1);
 // Repeating the same clip seeks back and completes independently.
 vm.runInContext('speak("big",false,cb)',e.c);await sleep(30);assert.equal(e.audio.currentTime,map.clips.big[0]);e.audio.currentTime=map.clips.big[1];await sleep(35);assert.equal(done,2);
 // Stop while a map is loading must not start audio or fall back to TTS.
 e=env({delayMap:40});vm.runInContext('speak("big",false);speechGeneration++;stopRecordedAudio()',e.c);await sleep(65);assert(!e.audio);assert.equal(e.tts.length,0);
 // Playback rejection safely falls back once.
 e=env({failPlay:true});done=0;e.c.cb=()=>done++;vm.runInContext('speak("big",false,cb)',e.c);await sleep(180);assert.equal(e.tts.length,1);assert.equal(done,1);
 // British English and unmatched words use device voice.
 e=env();vm.runInContext('S.set.accent="gb";speak("big",false)',e.c);await sleep(80);assert.equal(e.tts.length,1);assert(!e.audio);
 e=env();vm.runInContext('speak("writer",false)',e.c);await sleep(80);assert.equal(e.tts.length,1);
 // Hiding the page immediately pauses an active recording.
 e=env();vm.runInContext('speak("big",false)',e.c);await sleep(30);e.hide();assert(e.audio.paused);
 console.log('PASS: sprite bounds, same-word repeat, cancel during load, autoplay rejection fallback, British and unmatched fallback, hidden stop');
})();
