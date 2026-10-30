/* Original AI-composed score and synthesis by Codex. No recordings or external service.
   112 BPM, C major, eight-bar loop: C / Am / F / G, twice with a variation.
   Web Audio renders every note locally. Playback starts only after an explicit click. */
(() => {
  const host = window;
  const doc = host.document;
  if (!host.taskMonsterAudio) {
    const state = { music:false, effects:false, context:null, beat:0, next:0, timer:null, seen:new Set() };
    const melody = [
      [72,76,79,76,74,76,79,81], [76,72,69,72,76,79,76,74],
      [77,81,79,77,76,77,81,79], [74,79,83,81,79,76,74,71],
      [72,76,79,84,83,79,76,79], [81,79,76,72,76,79,81,76],
      [77,81,84,81,79,77,76,74], [79,83,81,79,76,74,71,72]
    ];
    const roots = [48,45,41,43,48,45,41,43];
    const chord = [[60,64,67],[57,60,64],[53,57,60],[55,59,62]];
    const frequency = midi => 440 * Math.pow(2,(midi-69)/12);
    function note(midi, when, length, volume, type='triangle', bus=state.fx) {
      if (!state.context || !bus) return;
      const osc = state.context.createOscillator();
      const envelope = state.context.createGain();
      osc.type=type; osc.frequency.value=frequency(midi);
      envelope.gain.setValueAtTime(0,when);
      envelope.gain.linearRampToValueAtTime(volume,when+.012);
      envelope.gain.exponentialRampToValueAtTime(.0001,when+length);
      osc.connect(envelope); envelope.connect(bus);
      osc.start(when); osc.stop(when+length+.02);
      osc.onended=()=>{osc.disconnect();envelope.disconnect();};
    }
    async function unlock() {
      if (!state.context) {
        const Audio = host.AudioContext || host.webkitAudioContext;
        if (!Audio) throw new Error('Audio unavailable');
        state.context = new Audio();
        state.bgm=state.context.createGain();state.bgm.gain.value=0;
        state.fx=state.context.createGain();state.fx.gain.value=.3;
        const limiter=state.context.createDynamicsCompressor();
        state.bgm.connect(limiter);state.fx.connect(limiter);limiter.connect(state.context.destination);
        state.next=state.context.currentTime+.05;
      }
      await state.context.resume();
    }
    function schedule() {
      if (!state.music || doc.hidden || state.context.state!=='running') return;
      const step=60/112/2;
      if (state.next<state.context.currentTime) state.next=state.context.currentTime+.04;
      while (state.next<state.context.currentTime+.18) {
        const bar=Math.floor(state.beat/8)%8, pos=state.beat%8, t=state.next;
        note(melody[bar][pos],t,step*.85,.21,'triangle',state.bgm);
        if (pos%2===0) note(roots[bar]+(pos===4?12:0),t,.22,.22,'sine',state.bgm);
        if (pos===0 || pos===4) chord[bar%4].forEach(n=>note(n,t,.8,.045,'triangle',state.bgm));
        if (pos%2===1) note(100,t,.035,.018,'square',state.bgm);
        state.next+=step;state.beat=(state.beat+1)%64;
      }
    }
    function sound(kind) {
      if (!state.effects || !state.context || state.context.state!=='running' || doc.hidden) return;
      const t=state.context.currentTime+.01;
      if (kind==='attack') {
        note(52,t,.12,.3,'sawtooth');note(40,t+.055,.16,.24,'triangle');
        [79,84,88].forEach((n,i)=>note(n,t+.3+i*.09,.23,.23,'sine'));
      } else if (kind==='undo') { note(76,t,.12,.18);note(69,t+.08,.18,.18); }
      else if (kind==='victory') {
        note(52,t,.12,.3,'sawtooth');
        [72,76,79,84,79,84,88,91,96].forEach((n,i)=>note(n,t+.22+i*.105,.48,.22,i%2?'sine':'triangle'));
      }
      else if (kind==='summon') [60,64,67,72].forEach((n,i)=>note(n,t+i*.075,.3,.22));
      else { note(79,t,.08,.13,'sine');note(84,t+.055,.12,.1,'sine'); }
    }
    function render() {
      const hud=doc.querySelector('.st-key-wallet_hud');
      if (!hud) return;
      let controls=hud.querySelector('.sound-controls');
      if (!controls) {
        controls=doc.createElement('div');controls.className='sound-controls';
        controls.setAttribute('role','group');controls.setAttribute('aria-label','Sound settings');
        const button=doc.createElement('button');button.type='button';button.dataset.sound='all';
        button.addEventListener('click',async()=>{
          try {
            await unlock();
            const enabled=!state.music;
            state.music=enabled;state.effects=enabled;
            state.bgm.gain.setTargetAtTime(enabled ? .25 : 0,state.context.currentTime,.04);
            state.next=state.context.currentTime+.03;
            if(enabled && !state.timer) state.timer=host.setInterval(schedule,60);
            if(!enabled && state.timer){host.clearInterval(state.timer);state.timer=null;}
            schedule();if(enabled) sound('click');render();
          } catch(_){button.textContent='Sound unavailable';button.setAttribute('aria-label','Sound unavailable in this browser');}
        });
        controls.appendChild(button);
        hud.querySelector('.hud-tools').appendChild(controls);
      }
      const button=controls.querySelector('[data-sound="all"]');
      const enabled=state.music;
      button.innerHTML=(enabled?'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9H7L13 4V20L7 15H3Z"/><path d="M17 8Q22 12 17 16" fill="none"/></svg>':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9H7L13 4V20L7 15H3Z"/><path d="M17 9L22 15M22 9L17 15" fill="none"/></svg>')+'<span>Sound '+(enabled?'on':'off')+'</span>';
      button.setAttribute('aria-pressed',String(enabled));
      button.setAttribute('aria-label','Game sound '+(enabled?'on':'off'));
    }
    doc.addEventListener('click',event=>{
      const button=event.target.closest('button');
      if (!button || button.closest('.sound-controls')) return;
      const key=button.closest('[class*="st-key-"]')?.className || '';
      if (key.includes('st-key-attack_')) return; // Successful state changes trigger damage/gem audio below.
      if (key.includes('st-key-summon_button')) sound('summon');
      else if (button.closest('.st-key-bottom_nav,.st-key-hero_card,.st-key-back_to_quests') || /Enter battle|View quest|Add step/.test(button.textContent)) sound('click');
    },true);
    doc.addEventListener('visibilitychange',()=>{
      if (!state.context) return;
      state.bgm.gain.setTargetAtTime(state.music && !doc.hidden ? 0.25 : 0,state.context.currentTime,.04);
      state.next=state.context.currentTime+.05;
    });
    // Streamlit replaces native containers on route changes; restore controls without restarting music.
    host.setInterval(()=>{
      if (!doc.querySelector('.st-key-wallet_hud .sound-controls')) render();
    },500);
    host.taskMonsterAudio={state,render,sound};
  }
  const engine=host.taskMonsterAudio;
  engine.render();
  if (soundEvent && !engine.state.seen.has(soundEvent.id)) {
    engine.state.seen.add(soundEvent.id);
    if(engine.state.seen.size>200) engine.state.seen.delete(engine.state.seen.values().next().value);
    engine.sound(soundEvent.kind);
  }
})();
