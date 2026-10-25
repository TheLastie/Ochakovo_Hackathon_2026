import { animateFoliage } from './menu-wind';
import { createKvassLoading } from './kvass-loading';
import { createShiftEnding } from './shift-ending';

/** Intro → character choice → profession film → Unity. Both menus stay independent of the game build. */
export function initGameMenu() {
  const menu = document.querySelector<HTMLElement>('#game-menu');
  if (!menu) return;
  const stage = document.querySelector<HTMLElement>('#game-stage')!;
  const loading = createKvassLoading(stage);
  const start = document.querySelector<HTMLButtonElement>('#game-menu-start')!;
  const sound = document.querySelector<HTMLButtonElement>('#game-menu-sound')!;
  const status = document.querySelector<HTMLElement>('#game-menu-status')!;
  const frame = document.querySelector<HTMLIFrameElement>('#factory-frame')!;
  const choice = document.querySelector<HTMLIFrameElement>('#character-frame')!;
  const image = document.querySelector<HTMLImageElement>('#game-menu-art')!;
  const canvas = document.querySelector<HTMLCanvasElement>('#game-menu-wind')!;
  const film = document.querySelector<HTMLElement>('#profession-film')!;
  const video = document.querySelector<HTMLVideoElement>('#profession-video')!;
  const filmFallback = document.querySelector<HTMLElement>('#profession-film-fallback')!;
  const filmStatus = document.querySelector<HTMLElement>('#profession-film-status')!;
  const filmTitles: Record<string, string> = {chemist: 'Химик-лаборант', bottling: 'Оператор линии розлива', machinery: 'Машинист оборудования', brewer: 'Квасовар'};
  const roles = new Set(['chemist', 'bottling', 'machinery', 'brewer']);
  let selected = 'chemist';
  let screen: 'intro' | 'selection' | 'video' | 'loading' | 'game' | 'ending' = 'intro';
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

  const ending = createShiftEnding(stage, (chemist = false) => {
    screen = 'selection';
    if (chemist) selected = 'chemist';
    stage.dataset.selectedRole = selected;
    choice.hidden = false;
    choice.inert = false;
    choice.removeAttribute('aria-hidden');
    sendChoice({type: 'select', role: selected});
    sendChoice({type: 'loading', value: false});
    updateActivity();
    choice.contentDocument?.querySelector<HTMLButtonElement>(`[data-role="${selected}"]`)?.focus({preventScroll: true});
    if (chemist) showFilm();
  });
  const showEnding = (kind: 'completed' | 'unavailable') => {
    screen = 'ending';
    choice.hidden = true;
    frame.hidden = true;
    frame.setAttribute('inert', '');
    frame.setAttribute('aria-hidden', 'true');
    // Release the completed Unity instance; a new shift starts from a clean iframe.
    frame.removeAttribute('src');
    const bounds = stage.getBoundingClientRect();
    if (bounds.top < 0 || bounds.bottom > innerHeight) stage.scrollIntoView({block: 'center', behavior: 'instant'});
    ending.show(kind, selected);
    updateActivity();
  };

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
    loading.active(visible && !document.hidden);
    ending.activity(visible && !document.hidden);
    if (audio && volume) {
      const silent = muted || !visible || document.hidden || screen === 'video' || screen === 'loading' || screen === 'game' || screen === 'ending';
      volume.gain.setTargetAtTime(silent ? 0 : 0.045, audio.currentTime, 0.25);
    }
    if (screen === 'video' && (!visible || document.hidden)) video.pause();
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
    loading.hide();
    frame.hidden = true;
    frame.removeAttribute('src');
    screen = 'selection';
    choice.hidden = false;
    choice.inert = false;
    stage.removeAttribute('aria-busy');
    sendChoice({ type: 'loading', value: false, error: 'Не удалось загрузить игру. Проверь соединение и попробуй ещё раз.' });
    choice.contentDocument?.querySelector<HTMLButtonElement>('.start')?.focus({ preventScroll: true });
    updateActivity();
  };
  const launch = () => {
    if (screen !== 'selection' || !choiceReady || transitioning) return;
    screen = 'loading';
    const loadingBounds = stage.getBoundingClientRect();
    if (loadingBounds.top < 0 || loadingBounds.bottom > innerHeight) {
      stage.scrollIntoView({ block: 'center', behavior: 'instant' });
    }
    loading.show();
    choice.inert = true;
    stage.dataset.selectedRole = selected;
    stage.setAttribute('aria-busy', 'true');
    sendChoice({ type: 'loading', value: true });
    updateActivity();
    frame.hidden = false;
    frame.setAttribute('aria-hidden', 'true');
    frame.setAttribute('inert', '');
    const url = new URL(frame.dataset.src!, location.href);
    url.searchParams.set('role', selected);
    // Retry against the current manifest, including in a tab opened before a new build.
    url.searchParams.set('attempt', String(Date.now()));
    frame.src = url.href;
    timer = setTimeout(failed, 120_000);
  };
  const clearFilm = () => {
    video.pause();
    video.removeAttribute('src');
    video.load();
    film.hidden = true;
    filmFallback.hidden = true;
  };
  const finishFilm = () => {
    if (screen !== 'video') return;
    clearFilm();
    screen = 'selection';
    if (selected === 'chemist') launch(); else showEnding('unavailable');
  };
  const playFilm = async () => {
    filmFallback.hidden = true;
    try { await video.play(); }
    catch {
      if (screen !== 'video') return;
      filmStatus.textContent = 'Нажми, чтобы посмотреть ролик, или пропусти его и перейди к производству.';
      filmFallback.hidden = false;
    }
  };
  const showFilm = () => {
    if (screen !== 'selection' || !choiceReady || transitioning) return;
    screen = 'video';
    stage.dataset.selectedRole = selected;
    sendChoice({type: 'loading', value: true});
    film.hidden = false;
    filmFallback.hidden = true;
    document.querySelector<HTMLElement>('#profession-film-title')!.textContent = filmTitles[selected];
    video.setAttribute('aria-label', `Видео: ${filmTitles[selected]}`);
    video.src = `${film.dataset.base}${selected}.mp4`;
    video.currentTime = 0;
    updateActivity();
    void playFilm();
    document.querySelector<HTMLButtonElement>('#profession-film-skip')!.focus({preventScroll: true});
  };
  video.addEventListener('ended', finishFilm);
  video.addEventListener('error', () => {
    if (screen !== 'video') return;
    filmStatus.textContent = 'Видео не загрузилось. Можно повторить просмотр или сразу перейти к производству.';
    filmFallback.hidden = false;
  });
  document.querySelector('#profession-film-skip')!.addEventListener('click', finishFilm);
  document.querySelector('#profession-film-play')!.addEventListener('click', () => {
    if (video.error) { video.load(); }
    void playFilm();
  });
  document.querySelector('#profession-film-back')!.addEventListener('click', () => {
    if (screen !== 'video') return;
    clearFilm();
    screen = 'selection';
    sendChoice({type: 'loading', value: false});
    updateActivity();
    choice.contentDocument?.querySelector<HTMLButtonElement>('.start')?.focus({preventScroll: true});
  });
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
        if (data.type === 'start') showFilm();
      } else if (data.type === 'back') {
        showIntro();
      } else if (data.type === 'sound') {
        void toggleSound();
      }
      return;
    }
    if (event.source !== frame.contentWindow || data.channel !== 'ochakovo-unity') return;
    if (data.type === 'completed' && screen === 'game' && selected === 'chemist') {
      showEnding('completed');
      return;
    }
    if (screen !== 'loading') return;
    if (data.type === 'progress' && typeof data.value === 'number') {
      loading.progress(data.value);
    } else if (data.type === 'error') {
      failed();
    } else if (data.type === 'ready') {
      clearTimeout(timer);
      screen = 'game';
      stage.removeAttribute('aria-busy');
      frame.removeAttribute('aria-hidden');
      frame.removeAttribute('inert');
      choice.hidden = true;
      void loading.finish().then(() => {
        frame.focus({ preventScroll: true });
        frame.contentDocument?.querySelector<HTMLCanvasElement>('#unity-canvas')?.focus({ preventScroll: true });
      });
      const bounds = stage.getBoundingClientRect();
      if (bounds.top < 0 || bounds.bottom > innerHeight) {
        stage.scrollIntoView({ block: 'center', behavior: 'instant' });
      }
      disposeWind();

      sendChoice({ type: 'active', value: false });
      if (volume && audio) volume.gain.setTargetAtTime(0, audio.currentTime, .1);
    }
  });
}
