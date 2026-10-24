import { animateFoliage } from './menu-wind';

/** Intro → character choice → Unity. Both menus stay independent of the game build. */
export function initGameMenu() {
  const menu = document.querySelector<HTMLElement>('#game-menu');
  if (!menu) return;
  const stage = document.querySelector<HTMLElement>('#game-stage')!;
  const start = document.querySelector<HTMLButtonElement>('#game-menu-start')!;
  const sound = document.querySelector<HTMLButtonElement>('#game-menu-sound')!;
  const status = document.querySelector<HTMLElement>('#game-menu-status')!;
  const frame = document.querySelector<HTMLIFrameElement>('#factory-frame')!;
  const choice = document.querySelector<HTMLIFrameElement>('#character-frame')!;
  const image = document.querySelector<HTMLImageElement>('#game-menu-art')!;
  const canvas = document.querySelector<HTMLCanvasElement>('#game-menu-wind')!;
  const roles = new Set(['chemist', 'bottling', 'machinery', 'brewer']);
  let selected = 'chemist';
  let screen: 'intro' | 'selection' | 'loading' | 'game' = 'intro';
  let choiceReady = false;
  let disposeWind = () => {};
  let timer: ReturnType<typeof setTimeout> | undefined;
  let choiceTimer: ReturnType<typeof setTimeout> | undefined;
  let audio: AudioContext | undefined;
  let volume: GainNode | undefined;
  let muted = true;
  let visible = false;
  let transitioning = false;
  let transitionId = 0;
  let transitions: Animation[] = [];

  const changeMenu = async (from: HTMLElement, to: HTMLElement) => {
    const id = ++transitionId;
    transitions.forEach(animation => animation.cancel());
    transitioning = true;
    from.hidden = false;
    to.hidden = false;
    from.inert = true;
    to.inert = true;
    from.setAttribute('aria-hidden', 'true');
    to.setAttribute('aria-hidden', 'true');
    const duration = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 650;
    // The intro stays above the choice screen, so one opaque screen always
    // covers the stage during the dissolve; there is no empty loading flash.
    transitions = [menu.animate(
      menu === from ? [{opacity: 1}, {opacity: 0}] : [{opacity: 0}, {opacity: 1}],
      {duration, easing: 'cubic-bezier(.22,.61,.36,1)', fill: 'both'},
    )];
    await Promise.all(transitions.map(animation => animation.finished.catch(() => {})));
    if (id !== transitionId) return;
    from.hidden = true;
    transitions.forEach(animation => animation.cancel());
    transitions = [];
    to.inert = false;
    to.removeAttribute('aria-hidden');
    transitioning = false;
    start.disabled = false;
    if (to === menu) start.focus({preventScroll: true});
    else choice.contentDocument?.querySelector<HTMLButtonElement>(`[data-role="${selected}"]`)?.focus({preventScroll: true});
    updateActivity();
  };

  const sendChoice = (data: Record<string, unknown>) => {
    choice.contentWindow?.postMessage({ channel: 'ochakovo-menu', ...data }, location.origin);
  };
  const createWindAudio = () => {
    const context = new AudioContext();
    const buffer = context.createBuffer(1, context.sampleRate * 4, context.sampleRate);
    const samples = buffer.getChannelData(0);
    for (let i = 0; i < samples.length; i++) samples[i] = Math.random() * 2 - 1;
    const source = context.createBufferSource();
    source.buffer = buffer;
    source.loop = true;
    const filter = context.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 420;
    volume = context.createGain();
    volume.gain.value = 0;
    source.connect(filter).connect(volume).connect(context.destination);
    source.start();
    return context;
  };
  const updateActivity = () => {
    if (audio && volume) {
      const silent = muted || !visible || document.hidden || screen === 'loading' || screen === 'game';
      volume.gain.setTargetAtTime(silent ? 0 : 0.045, audio.currentTime, 0.25);
    }
    sendChoice({ type: 'active', value: visible && !document.hidden && screen === 'selection' && !transitioning });
  };
  const toggleSound = async () => {
    try {
      audio ??= createWindAudio();
      await audio.resume();
      muted = !muted;
      sound.setAttribute('aria-pressed', String(!muted));
      sound.setAttribute('aria-label', muted ? 'Включить звук ветра' : 'Выключить звук ветра');
      sendChoice({ type: 'sound', muted });
      updateActivity();
    } catch {
      status.textContent = 'Браузер не разрешил звук. Игру можно запустить без него.';
    }
  };
  sound.addEventListener('click', () => { void toggleSound(); });
  document.addEventListener('visibilitychange', updateActivity);
  const observer = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    updateActivity();
    if (visible && !menu.dataset.windReady) {
      menu.dataset.windReady = 'true';
      const init = () => { if (screen !== 'game') disposeWind = animateFoliage(canvas, image); };
      if (image.complete && image.naturalWidth) init();
      else image.addEventListener('load', init, { once: true });
    }
  });
  observer.observe(stage);

  const showIntro = (error = '') => {
    clearTimeout(choiceTimer);
    screen = 'intro';
    status.textContent = error;
    void changeMenu(choice, menu);
    updateActivity();
  };
  const revealChoice = async () => {
    // Fonts and portrait thumbnails must be ready before revealing the iframe.
    const doc = choice.contentDocument;
    await Promise.all([
      doc?.fonts.ready,
      ...Array.from(doc?.images ?? []).map(img => img.decode().catch(() => {})),
    ]);
    if (screen !== 'selection') return;
    void changeMenu(menu, choice);
  };
  start.addEventListener('click', () => {
    if (screen !== 'intro' || transitioning) return;
    screen = 'selection';
    transitioning = true;
    start.disabled = true;
    status.textContent = '';
    if (!choice.getAttribute('src')) {
      choice.src = choice.dataset.src!;
      choiceTimer = setTimeout(() => {
        choice.removeAttribute('src');
        showIntro('Не удалось открыть выбор персонажа. Попробуй ещё раз.');
      }, 20_000);
    } else {
      void revealChoice();
    }
    updateActivity();
  });
  choice.addEventListener('error', () => showIntro('Не удалось открыть выбор персонажа. Попробуй ещё раз.'));
  choice.addEventListener('load', () => {
    if (screen === 'selection' && !choice.contentDocument?.querySelector('.detail-list')) {
      choice.removeAttribute('src');
      showIntro('Не удалось открыть выбор персонажа. Попробуй ещё раз.');
    }
  });

  const failed = () => {
    if (screen !== 'loading') return;
    clearTimeout(timer);
    frame.hidden = true;
    frame.removeAttribute('src');
    screen = 'selection';
    stage.removeAttribute('aria-busy');
    sendChoice({ type: 'loading', value: false, error: 'Не удалось загрузить игру. Проверь соединение и попробуй ещё раз.' });
    choice.contentDocument?.querySelector<HTMLButtonElement>('.start')?.focus({ preventScroll: true });
    updateActivity();
  };
  const launch = () => {
    if (screen !== 'selection' || !choiceReady || transitioning) return;
    screen = 'loading';
    stage.dataset.selectedRole = selected;
    stage.setAttribute('aria-busy', 'true');
    sendChoice({ type: 'loading', value: true });
    updateActivity();
    frame.hidden = false;
    frame.setAttribute('aria-hidden', 'true');
    frame.setAttribute('inert', '');
    const url = new URL(frame.dataset.src!, location.href);
    url.searchParams.set('role', selected);
    frame.src = url.href;
    timer = setTimeout(failed, 120_000);
  };
  frame.addEventListener('error', failed);
  frame.addEventListener('load', () => {
    if (screen === 'loading' && !frame.contentDocument?.querySelector('#unity-canvas')) failed();
  });
  window.addEventListener('message', (event: MessageEvent) => {
    if (event.origin !== location.origin || !event.data) return;
    const data = event.data;
    if (event.source === choice.contentWindow && data.channel === 'ochakovo-selection') {
      if (data.type === 'ready') {
        choiceReady = true;
        clearTimeout(choiceTimer);
        sendChoice({ type: 'sound', muted });
        updateActivity();
        if (screen === 'selection') void revealChoice();
      }
      if (screen !== 'selection') return;
      if ((data.type === 'select' || data.type === 'start') && roles.has(data.role)) {
        selected = data.role;
        stage.dataset.selectedRole = selected;
        if (data.type === 'start') launch();
      } else if (data.type === 'back') {
        showIntro();
      } else if (data.type === 'sound') {
        void toggleSound();
      }
      return;
    }
    if (event.source !== frame.contentWindow || data.channel !== 'ochakovo-unity' || screen !== 'loading') return;
    if (data.type === 'progress' && typeof data.value === 'number') {
      sendChoice({ type: 'loading', value: true, progress: Math.max(0, Math.min(1, data.value)) });
    } else if (data.type === 'error') {
      failed();
    } else if (data.type === 'ready') {
      clearTimeout(timer);
      screen = 'game';
      stage.removeAttribute('aria-busy');
      frame.removeAttribute('aria-hidden');
      frame.removeAttribute('inert');
      choice.hidden = true;
      frame.focus({ preventScroll: true });
      disposeWind();
      observer.disconnect();
      document.removeEventListener('visibilitychange', updateActivity);
      sendChoice({ type: 'active', value: false });
      void audio?.close();
    }
  });
}
