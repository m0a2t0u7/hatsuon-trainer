from pathlib import Path

D=Path(__file__).parent.parent
sources=['audio/jessica-padded.mp3','audio/jessica-extra-20261022.mp3','audio/jessica-isolated-20261023.mp3']
for name in ['index.html','expand-base.html']:
    p=D/name;s=p.read_text()
    if 'const REC_AUDIO_SOURCES=' in s:
        continue
    s=s.replace('let recordedAudio=null,recordedMapPromise=null,recordedCancel=null,lastAudioSource="";',
        'const REC_AUDIO_SOURCES='+__import__('json').dumps(sources)+';\nlet recordedAudio=null,recordedMapPromise=null,recordedCancel=null,lastAudioSource="";\nconst recordedAudioPool=new Map();')
    s=s.replace('if(recordedAudio){try{recordedAudio.pause()}catch(e){}}',
        'for(const a of recordedAudioPool.values()){try{a.pause()}catch(e){}}')
    s=s.replace('fetch("audio/jessica-map.json?v=2",{signal:c.signal})',
        'fetch("audio/jessica-map.json?v=20261023-1",{signal:c.signal})')
    s=s.replace('if(!m.clips||m.audio!=="audio/jessica-padded.mp3")throw Error("map");return m',
        'if(!m.clips||m.audio!==REC_AUDIO_SOURCES[0])throw Error("map");m.sources=m.sources||[m.audio];if(!Array.isArray(m.sources)||m.sources.some(x=>!REC_AUDIO_SOURCES.includes(x)))throw Error("sources");return m')
    s=s.replace('function recordedReady(generation){\n  if(!recordedAudio){recordedAudio=new Audio("audio/jessica-padded.mp3");recordedAudio.preload="auto";recordedAudio.preservesPitch=true;recordedAudio.load()}\n  const a=recordedAudio;',
        'function recordedReady(generation,source){\n  if(!REC_AUDIO_SOURCES.includes(source))return Promise.reject(Error("source"));\n  if(recordedAudioPool.has(source)&&recordedAudioPool.get(source).error){try{recordedAudioPool.get(source).pause()}catch(e){}recordedAudioPool.delete(source)}\n  if(!recordedAudioPool.has(source)){const a=new Audio(source);a.preload="auto";a.preservesPitch=true;recordedAudioPool.set(source,a);a.load()}\n  const a=recordedAudioPool.get(source);recordedAudio=a;')
    s=s.replace('if(!Array.isArray(clip)||clip.length!==2||!Number.isFinite(clip[0])||!Number.isFinite(clip[1])||clip[0]<0||clip[1]<=clip[0]){fallback();return}\n    const a=await recordedReady(generation);if(generation!==speechGeneration)return;',
        'if(!Array.isArray(clip)||(clip.length!==2&&clip.length!==3)||!Number.isFinite(clip[0])||!Number.isFinite(clip[1])||clip[0]<0||clip[1]<=clip[0]){fallback();return}\n    const sourceIndex=clip.length===3?clip[2]:0;if(!Number.isInteger(sourceIndex)||sourceIndex<0||sourceIndex>=map.sources.length){fallback();return}\n    const a=await recordedReady(generation,map.sources[sourceIndex]);if(generation!==speechGeneration)return;\n    if(Number.isFinite(a.duration)&&clip[1]>a.duration+.05){fallback();return}')
    s=s.replace('ElevenLabsはアメリカ英語の810語に対応。','ElevenLabsはアメリカ英語の${RECORDED_COUNT}語に対応。')
    p.write_text(s)

# Rebuilding vocabulary must preserve the current audio coverage, rather than
# silently reverting to the first recording's 810 clips.
p=D/'build-expansion.py';s=p.read_text()
s=s.replace('assert len(set(unique)&recordedkeys)==810','recorded_count=len(set(unique)&recordedkeys)\nassert recorded_count<=len(unique)')
s=s.replace('assert len(pending)==690,len(pending)','assert len(pending)==len(unique)-recorded_count,len(pending)')
s=s.replace("'recordedUnique':810,'pendingUnique':690", "'recordedUnique':recorded_count,'pendingUnique':len(pending)")
s=s.replace("'recorded':810,'pending':690", "'recorded':recorded_count,'pending':len(pending)")
s=s.replace("const RECORDED_COUNT=810;", "const RECORDED_COUNT='+str(recorded_count)+';")
p.write_text(s)
