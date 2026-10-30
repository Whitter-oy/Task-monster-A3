// The event contains trusted app-generated IDs and original SVG artwork only.
setTimeout(() => {
  const host = window.parent;
  const doc = host.document;
  const eventKey = reward.task_id + ':' + reward.sequence;
  if (host.__taskMonsterReward === eventKey) return;
  host.__taskMonsterReward = eventKey;
  const wallet = doc.querySelector('.gem-count');
  if (!wallet) return;
  const pulse = () => {
    wallet.classList.remove('wallet-reward');
    void wallet.offsetWidth;
    wallet.classList.add('wallet-reward');
    host.setTimeout(() => wallet.classList.remove('wallet-reward'), 700);
  };
  if (host.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const origin = doc.querySelector('.st-key-step_' + reward.task_id + '_' + reward.step_index);
  const source = origin ? origin.getBoundingClientRect() : wallet.getBoundingClientRect();
  const destination = wallet.getBoundingClientRect();
  const x = source.left + source.width * .65;
  const y = Math.max(90, Math.min(source.top + 25, host.innerHeight - 100));
  const dx = destination.left + 22 - x;
  const dy = destination.top + destination.height / 2 - y;
  for (let i = 0; i < 5; i++) {
    const gem = doc.createElement('div');
    gem.className = 'flying-gem';
    gem.setAttribute('aria-hidden', 'true');
    gem.style.cssText = `position:fixed;left:${x}px;top:${y}px;width:28px;height:28px;pointer-events:none;z-index:9999;`;
    gem.innerHTML = reward.gem;
    doc.body.appendChild(gem);
    const flight = gem.animate([
      { transform: 'translate(0, 0) scale(.5)', opacity: 0 },
      { transform: `translate(${(i-2)*18}px,-30px) scale(1.1)`, opacity: 1, offset: .22 },
      { transform: `translate(${dx}px,${dy}px) scale(.45)`, opacity: 1, offset: .9 },
      { transform: `translate(${dx}px,${dy}px) scale(.2)`, opacity: 0 }
    ], { duration: 900, delay: i * 65, easing: 'cubic-bezier(.22,.55,.35,1)', fill: 'forwards' });
    flight.onfinish = () => { gem.remove(); if (i === 4) pulse(); };
  }
}, 120);
