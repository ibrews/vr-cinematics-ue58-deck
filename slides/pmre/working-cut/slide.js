/* pmre/working-cut: four stills on a timeline with a playhead. The first card is lit on entry; each click moves the
   playhead to the next station (0.9 s ease), lighting its card. A card can carry an overlay label ("50 mm") and a 2.39
   letterbox. Clicking a stop or dragging the playhead scrubs by hand; pointer input on the track never reaches the
   deck's click-to-advance.
   Clicks: stations.length - 1 (3 for four stations), unchanged from the MIA original.
   Ported from ibrews/mia-2026-collective-pitch index.html mgBuildReplayLine + .rl-* CSS @9ee2493 (the layout the MIA
   `working-cut` case uses), by hand: MIA is a classic deck, so tools/slide.py pull had no module to copy.
   Differences: ctx.instant replaces TI; the playhead tween runs on ctx.clock.raf so leave() stops it; a hand scrub
   no longer writes into slideSteps (the deck owns the step counter: the next click continues from the last click,
   not from where the hand left the playhead); accents and text come from the look's variables; text is props. */
SD.defineSlide({
  id: 'pmre/working-cut',
  steps: (props) => Math.max(0, Math.min(4, (props.stations || []).length) - 1),
  duration: 0.9,
  props: {
    title: 'Timeline',
    subtitle: '',
    stations: [
      { when: 'One', short: 'One', t: 'Station one', d: '', img: '' },
      { when: 'Two', short: 'Two', t: 'Station two', d: '', img: '' },
    ],
  },
  provenance: ['ibrews/mia-2026-collective-pitch@9ee2493 index.html mgBuildReplayLine + .rl-* CSS (working-cut case)'],
  css: `
.slide.sd-mod-pmre-working-cut{padding:0;display:block}
.sd-mod-pmre-working-cut .rl-wrap{position:absolute;inset:calc(4.5*var(--vh)) calc(4*var(--vw)) calc(5*var(--vh));display:flex;flex-direction:column;gap:calc(2*var(--vh))}
.sd-mod-pmre-working-cut .rl-head h2{font-size:calc(3*var(--vw));font-weight:700;letter-spacing:-.02em;line-height:1.1;color:var(--text,#f0f4ff)}
.sd-mod-pmre-working-cut .rl-head p{font-size:calc(1.45*var(--vw));color:var(--text,#f0f4ff);opacity:.7;margin-top:.3em}
.sd-mod-pmre-working-cut .rl-stage{flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:calc(1.2*var(--vw));align-items:center;align-content:center;min-height:0}
.sd-mod-pmre-working-cut .rl-card{margin:0;opacity:.18;transform:translateY(12px);transition:opacity .6s,transform .6s;border-radius:14px;overflow:hidden;border:2px solid var(--acc);background:rgba(10,12,20,.85)}
.sd-mod-pmre-working-cut .rl-card.on{opacity:.75;transform:none}.sd-mod-pmre-working-cut .rl-card.now{opacity:1}
.sd-mod-pmre-working-cut .rl-card img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block}
.sd-mod-pmre-working-cut .rl-pic{position:relative}
.sd-mod-pmre-working-cut .rl-card.lb .rl-pic::after{content:'';position:absolute;inset:0;z-index:1;pointer-events:none;box-shadow:inset 0 calc(1.6*var(--vw)) 0 #000,inset 0 calc(-1.6*var(--vw)) 0 #000}
.sd-mod-pmre-working-cut .rl-ov{position:absolute;left:8px;bottom:18%;z-index:2;font-size:calc(1*var(--vw));font-weight:700;color:#fff;background:rgba(6,8,16,.7);padding:.2em .55em;border-radius:6px;letter-spacing:.04em}
.sd-mod-pmre-working-cut .rl-card figcaption{padding:.7em .9em .9em;display:flex;flex-direction:column;gap:.25em}
.sd-mod-pmre-working-cut .rl-card figcaption b{font-size:calc(1*var(--vw));letter-spacing:.14em;text-transform:uppercase;color:var(--acc)}
.sd-mod-pmre-working-cut .rl-card figcaption span{font-size:calc(1.55*var(--vw));font-weight:700;line-height:1.15;color:var(--text,#f0f4ff)}
.sd-mod-pmre-working-cut .rl-card figcaption em{font-style:normal;font-size:calc(1.05*var(--vw));line-height:1.3;color:var(--text,#f0f4ff);opacity:.75}
.sd-mod-pmre-working-cut .rl-track{position:relative;height:calc(9*var(--vh));margin:0 calc(4*var(--vw));touch-action:none;cursor:pointer}
.sd-mod-pmre-working-cut .rl-track::before{content:'';position:absolute;left:0;right:0;top:calc(2.5*var(--vh));height:6px;border-radius:3px;background:rgba(255,255,255,.14)}
.sd-mod-pmre-working-cut .rl-fill{position:absolute;left:0;top:calc(2.5*var(--vh));height:6px;border-radius:3px;background:linear-gradient(90deg,var(--amber,#f59e0b),var(--teal,#00d4ff),var(--purple,#a78bfa),var(--rose,#fb7185));width:0}
.sd-mod-pmre-working-cut .rl-stop{position:absolute;top:0;transform:translateX(-50%);background:none;border:0;color:#fff;font:inherit;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:.4em}
.sd-mod-pmre-working-cut .rl-stop i{width:calc(1.4*var(--vw));height:calc(1.4*var(--vw));border-radius:50%;background:#0b0e18;border:3px solid var(--acc);margin-top:calc(1.6*var(--vh))}
.sd-mod-pmre-working-cut .rl-stop.on i{background:var(--acc)}
.sd-mod-pmre-working-cut .rl-stop span{font-size:calc(1.05*var(--vw));font-weight:700;color:var(--text,#f0f4ff);opacity:.8;white-space:nowrap}
.sd-mod-pmre-working-cut .rl-head-dot{position:absolute;top:calc(1.6*var(--vh));width:calc(.9*var(--vw));height:calc(2.6*var(--vh));margin-left:calc(-.45*var(--vw));border-radius:4px;background:#fff;box-shadow:0 0 12px var(--teal,#00d4ff);left:0;pointer-events:none}
`,
  render(s, props, ctx) {
    const ST = (props.stations || []).slice(0, 4), N = ST.length, ACC = ['var(--amber,#f59e0b)', 'var(--teal,#00d4ff)', 'var(--purple,#a78bfa)', 'var(--rose,#fb7185)'];
    const pic = x => x.img ? `<img src="${x.img}" alt="${x.alt || ''}" loading="eager">` : '';
    s.innerHTML = `<div class="rl-wrap"><div class="rl-head"><h2 class="case-title">${props.title || ''}</h2>${props.subtitle ? `<p>${props.subtitle}</p>` : ''}</div>
    <div class="rl-stage">${ST.map((x, i) => `<figure class="rl-card${x.letterbox ? ' lb' : ''}" data-i="${i}" style="--acc:${ACC[i]}"><div class="rl-pic">${pic(x)}${x.overlay ? `<span class="rl-ov">${x.overlay}</span>` : ''}</div><figcaption><b>${x.when || ''}</b><span>${x.t || ''}</span><em>${x.d || ''}</em></figcaption></figure>`).join('')}</div>
    <div class="rl-track"><div class="rl-fill"></div>${ST.map((x, i) => `<button class="rl-stop" data-i="${i}" style="left:${N > 1 ? (i / (N - 1)) * 100 : 0}%;--acc:${ACC[i]}"><i></i><span>${x.short || x.t || ''}</span></button>`).join('')}<div class="rl-head-dot"></div></div></div>`;
    const cards = [...s.querySelectorAll('.rl-card')], stops = [...s.querySelectorAll('.rl-stop')], fill = s.querySelector('.rl-fill'), dot = s.querySelector('.rl-head-dot'), track = s.querySelector('.rl-track');
    ['click', 'pointerdown', 'mousedown', 'touchstart', 'wheel'].forEach(t => track.addEventListener(t, e => e.stopPropagation()));
    let pos = 0, tok = 0;
    const set = (p, i) => { pos = p; fill.style.width = p * 100 + '%'; dot.style.left = p * 100 + '%'; const k = i ?? Math.round(p * (N - 1));
      cards.forEach((el, j) => { el.classList.toggle('on', j <= k); el.classList.toggle('now', j === k); }); stops.forEach((el, j) => el.classList.toggle('on', j <= k)); };
    const go = i => { const my = ++tok, to = N > 1 ? i / (N - 1) : 0, from = pos; if (ctx.instant) { set(to, i); return; } let t0 = null;
      const f = now => { if (my !== tok) return; if (t0 === null) t0 = now; const k = Math.min(1, (now - t0) / 900), e = 1 - Math.pow(1 - k, 3), p = from + (to - from) * e;
        set(p, k < 1 ? Math.floor(p * (N - 1) + .001) : i); if (k < 1) ctx.clock.raf(f); }; ctx.clock.raf(f); };
    stops.forEach((b, i) => b.addEventListener('click', () => go(i)));
    let dragging = false; const at = e => { const b = track.getBoundingClientRect(); return Math.max(0, Math.min(1, (e.clientX - b.left) / b.width)); };
    track.addEventListener('pointerdown', e => { if (e.target.closest('.rl-stop')) return; tok++; dragging = true; try { track.setPointerCapture(e.pointerId); } catch (_) {} set(at(e)); });
    track.addEventListener('pointermove', e => { if (dragging) set(at(e)); }); track.addEventListener('pointerup', () => { dragging = false; });
    set(0, 0);
    return {
      enter() { tok++; set(0, 0); },
      step(n) { go(Math.min(n, N - 1)); },
      leave() { tok++; },
      staticFrame() { tok++; set(1, N - 1); },
    };
  },
});
