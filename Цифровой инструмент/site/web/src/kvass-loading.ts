/** Scene-loading illustration. The drink level follows Unity's reported progress. */
export function createKvassLoading(stage: HTMLElement) {
  const root = document.createElement('section');
  root.className = 'kvass-loading';
  root.hidden = true;
  root.setAttribute('aria-label', 'Загрузка производства');
  root.innerHTML = `<div class="kvass-loading-top"><span>ОЧАКОВО <i>Первая смена</i></span><span>Сейчас начнём</span></div>
    <div class="kvass-loading-body">
    <svg class="kvass-glass" viewBox="0 0 300 340" aria-hidden="true">
      <defs>
        <linearGradient id="kvass-drink" x1="0" x2="1"><stop stop-color="#51220d"/><stop offset=".3" stop-color="#a94d10"/><stop offset=".62" stop-color="#d68723"/><stop offset="1" stop-color="#6b2c0b"/></linearGradient>
        <linearGradient id="kvass-glass-shine" x1="0" x2="1"><stop stop-color="#fff" stop-opacity=".75"/><stop offset=".2" stop-color="#fff" stop-opacity=".03"/><stop offset=".75" stop-color="#fff" stop-opacity=".04"/><stop offset="1" stop-color="#fff" stop-opacity=".55"/></linearGradient>
        <linearGradient id="kvass-pour" x1="0" x2="1"><stop stop-color="#6b2c0b"/><stop offset=".5" stop-color="#d18a37"/><stop offset="1" stop-color="#8e420d"/></linearGradient>
        <radialGradient id="kvass-shadow"><stop stop-color="#5d381d" stop-opacity=".2"/><stop offset="1" stop-color="#5d381d" stop-opacity="0"/></radialGradient>
        <clipPath id="kvass-glass-clip"><path d="M82 60 Q150 80 218 60 L202 274 Q150 298 98 274Z"/></clipPath>
        <clipPath id="kvass-liquid-clip"><rect class="kvass-level-clip" x="70" y="276" width="160" height="240"/></clipPath>
      </defs>
      <ellipse cx="150" cy="307" rx="111" ry="17" fill="url(#kvass-shadow)"/>
      <path d="M77 59 L94 279 Q150 308 206 279 L223 59" fill="#fff" fill-opacity=".22" stroke="#c7c2b7" stroke-width="2"/>
      <g clip-path="url(#kvass-glass-clip)">
        <rect class="kvass-level" x="76" y="276" width="148" height="240" fill="url(#kvass-drink)"/>
        <g clip-path="url(#kvass-liquid-clip)" fill="#ffe1a0" class="kvass-bubbles">
          <circle cx="115" cy="280" r="2.1" style="--bubble-delay:-.2s;--bubble-time:3.7s"/><circle cx="178" cy="285" r="1.8" style="--bubble-delay:-2s;--bubble-time:4.3s"/><circle cx="139" cy="290" r="1.2" style="--bubble-delay:-1s;--bubble-time:3.2s"/><circle cx="190" cy="278" r="2.2" style="--bubble-delay:-3s;--bubble-time:4.7s"/><circle cx="157" cy="280" r="1.4" style="--bubble-delay:-1.7s;--bubble-time:3.9s"/><circle cx="107" cy="291" r="1.2" style="--bubble-delay:-2.8s;--bubble-time:4.1s"/>
        </g>
        <g class="kvass-foam-position" transform="translate(0 276)"><g class="kvass-foam">
          <ellipse cx="150" cy="1" rx="73" ry="11" fill="#f4dfb8"/>
          <path d="M77 0 Q89 -10 102 -5 Q111 -17 125 -9 Q138 -19 151 -10 Q164 -20 178 -8 Q192 -14 202 -5 Q216 -10 225 1 L225 7 Q150 24 77 7Z" fill="#fff7e6"/>
          <g fill="#d8bc8d" opacity=".6"><circle cx="110" cy="0" r="1.6"/><circle cx="169" cy="4" r="2"/><circle cx="186" cy="-2" r="1.2"/><circle cx="142" cy="7" r="1.3"/></g>
        </g></g>
      </g>
      <rect class="kvass-stream" x="146" y="4" width="8" height="272" rx="4" fill="url(#kvass-pour)"/>
      <path d="M83 65 L99 273 Q150 296 201 273 L217 65" fill="url(#kvass-glass-shine)"/>
      <path d="M91 91 L102 249" stroke="#fff" stroke-opacity=".72" stroke-width="5" stroke-linecap="round"/>
      <path d="M208 92 L199 240" stroke="#fff" stroke-opacity=".3" stroke-width="2" stroke-linecap="round"/>
      <ellipse cx="150" cy="59" rx="73" ry="14" fill="none" stroke="#bdb7ab" stroke-width="2"/>
      <path d="M80 60 Q150 85 220 60" fill="none" stroke="#fff" stroke-width="2"/>
      <path d="M101 281 Q150 300 199 281" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="3"/>
    </svg>
    <div class="kvass-loading-copy"><span class="kvass-loading-kicker">ТВОЯ ПЕРВАЯ СМЕНА</span><h2>Наливаем квас.<br>Готовим производство.</h2><div class="kvass-loading-status"><span class="kvass-loading-message" role="status">Загружаем сцену…</span><span class="kvass-loading-percent" aria-hidden="true">0%</span></div><div class="kvass-loading-meter" role="progressbar" aria-label="Загрузка сцены" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span></span></div></div>
    </div><div class="kvass-loading-bottom"><span>Знакомый вкус. Новая история.</span><span class="kvass-loading-dots" aria-hidden="true">···</span></div>`;
  stage.append(root);
  const level = root.querySelector<SVGRectElement>('.kvass-level')!;
  const clip = root.querySelector<SVGRectElement>('.kvass-level-clip')!;
  const foam = root.querySelector<SVGGElement>('.kvass-foam-position')!;
  const stream = root.querySelector<SVGRectElement>('.kvass-stream')!;
  const percent = root.querySelector<HTMLElement>('.kvass-loading-percent')!;
  const meter = root.querySelector<HTMLElement>('[role=progressbar]')!;
  const bar = meter.firstElementChild as HTMLElement;
  const message = root.querySelector<HTMLElement>('.kvass-loading-message')!;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let target = 0, shown = 0, request = 0, previous = 0, generation = 0, active = true;
  let complete: (() => void) | undefined;
  const paint = () => {
    const y = 276 - shown * 208;
    level.setAttribute('y', String(y)); clip.setAttribute('y', String(y));
    foam.setAttribute('transform', `translate(0 ${y})`);
    stream.setAttribute('height', String(Math.max(0, y - 4)));
    percent.textContent = `${Math.floor(shown * 100)}%`;
    meter.setAttribute('aria-valuenow', String(Math.floor(shown * 100)));
    bar.style.transform = `scaleX(${shown})`;
  };
  const tick = (now: number) => {
    const elapsed = Math.min(64, now - (previous || now)); previous = now;
    shown = reduced.matches ? target : shown + (target - shown) * (1 - Math.exp(-elapsed / 140));
    if (target - shown < .001) shown = target;
    paint();
    if (shown === 1 && complete) { const done = complete; complete = undefined; done(); }
    if (!root.hidden && !document.hidden && active && shown !== target) request = requestAnimationFrame(tick);
    else request = 0;
  };
  const run = () => { if (!request && !root.hidden && !document.hidden && active) { previous = 0; request = requestAnimationFrame(tick); } };
  document.addEventListener('visibilitychange', run);
  return {
    show() { generation++; target = shown = 0; complete?.(); complete = undefined; root.hidden = false; root.classList.remove('is-ready'); message.textContent = 'Загружаем сцену…'; paint(); run(); },
    progress(value: number) { if (Number.isFinite(value)) { target = Math.max(target, Math.min(.96, Math.max(0, value) * .96)); run(); } },
    active(value: boolean) { active = value; root.classList.toggle('is-paused', !value); if (value) run(); else { cancelAnimationFrame(request); request = 0; } },
    hide() { generation++; root.hidden = true; cancelAnimationFrame(request); request = 0; complete?.(); complete = undefined; },
    async finish() {
      const id = generation; target = 1; message.textContent = 'Всё готово. Начинаем!';
      await new Promise<void>(resolve => { if (!active) { shown = 1; paint(); resolve(); } else { complete = resolve; run(); } });
      if (id !== generation) return;
      root.classList.add('is-ready');
      await root.animate([{opacity: 1}, {opacity: 0}], {duration: reduced.matches ? 0 : 280, easing: 'ease-out'}).finished.catch(() => {});
      if (id === generation) { root.hidden = true; cancelAnimationFrame(request); request = 0; }
    },
  };
}
