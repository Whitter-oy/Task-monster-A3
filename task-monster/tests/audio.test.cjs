// Dependency-free checks for audio consent, mute, scheduling and rerender deduplication.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../assets/audio.js'),'utf8');
function browser() {
  let controls=null;
  const notes=[],timers=new Map();
  const parameter=()=>({value:0,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){},setTargetAtTime(v){this.value=v;}});
  class Element {
    constructor(){this.children=[];this.dataset={};this.attributes={};this.textContent='';this.listeners={};}
    setAttribute(k,v){this.attributes[k]=v;}
    addEventListener(k,fn){this.listeners[k]=fn;}
    appendChild(e){this.children.push(e);if(e.className==='sound-controls')controls=e;}
    querySelector(selector){return this.children.find(e=>e.dataset.sound===selector.match(/"(.*?)"/)[1]);}
  }
  const hud=new Element();
  hud.querySelector=s=>s==='.hud-tools'?hud:controls;
  const doc={hidden:false,createElement:()=>new Element(),addEventListener(){},querySelector:s=>s.includes(' .sound-controls')?controls:hud};
  class AudioContext {
    constructor(){this.currentTime=1;this.state='suspended';this.destination={};}
    async resume(){this.state='running';}
    createGain(){return {gain:parameter(),connect(){},disconnect(){}};}
    createDynamicsCompressor(){return {connect(){}};}
    createOscillator(){const n={frequency:parameter(),connect(){},disconnect(){},start(t){notes.push({frequency:this.frequency.value,time:t});},stop(){}};return n;}
  }
  const host={document:doc,AudioContext,setInterval(fn){const id=timers.size+1;timers.set(id,fn);return id;},clearInterval(id){timers.delete(id);}};
  const run=(event=null)=>vm.runInNewContext(source,{window:host,soundEvent:event});
  run();
  return {host,notes,timers,run,button:key=>controls.querySelector(`[data-sound="${key}"]`)};
}
test('audio waits for consent, schedules a loop, mutes and survives rerenders',async()=>{
  const b=browser();
  assert.equal(b.host.taskMonsterAudio.state.context,null);
  assert.equal(b.notes.length,0);
  await b.button('all').listeners.click();
  const engine=b.host.taskMonsterAudio;
  assert.equal(engine.state.context.state,'running');
  assert.equal(engine.state.effects,true);
  assert.ok(b.notes.length>0);
  assert.ok(b.notes.every(n=>Number.isFinite(n.frequency)&&n.frequency>0));
  assert.equal(engine.state.bgm.gain.value,.25);
  b.run();assert.equal(b.host.taskMonsterAudio,engine);
  await b.button('all').listeners.click();
  assert.equal(engine.state.bgm.gain.value,0);
  assert.equal(engine.state.effects,false);
  assert.equal(engine.state.timer,null);
});
test('effects are opt-in and a reward event plays once across rerenders',async()=>{
  const b=browser();
  b.host.taskMonsterAudio.sound('attack');assert.equal(b.notes.length,0);
  await b.button('all').listeners.click();
  const before=b.notes.length;
  b.run({id:'quest:1',kind:'attack'});
  assert.equal(b.notes.length-before,5); // Two damage tones, then three gem tones.
  b.run({id:'quest:1',kind:'attack'});assert.equal(b.notes.length-before,5);
  b.run({id:'quest:2',kind:'undo'});assert.equal(b.notes.length-before,7);
  b.run({id:'quest:3',kind:'victory'});assert.equal(b.notes.length-before,17);
  await b.button('all').listeners.click();
  const muted=b.notes.length;b.host.taskMonsterAudio.sound('summon');assert.equal(b.notes.length,muted);
});
