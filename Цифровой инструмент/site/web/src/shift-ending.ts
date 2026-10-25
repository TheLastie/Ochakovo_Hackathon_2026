type Ending = 'completed' | 'unavailable';

/** Videos and explicit next steps stay available even if autoplay or media loading fails. */
export function createShiftEnding(stage: HTMLElement, select: (chemist?: boolean) => void) {
  const panel = stage.querySelector<HTMLElement>('#shift-ending')!;
  const video = panel.querySelector<HTMLVideoElement>('video')!;
  const title = panel.querySelector<HTMLElement>('h2')!;
  const detail = panel.querySelector<HTMLElement>('.shift-ending-detail')!;
  const play = panel.querySelector<HTMLButtonElement>('[data-ending-play]')!;
  const apply = panel.querySelector<HTMLButtonElement>('[data-ending-apply]')!;
  const choose = panel.querySelector<HTMLButtonElement>('[data-ending-select]')!;
  const chemist = panel.querySelector<HTMLButtonElement>('[data-ending-chemist]')!;
  const status = panel.querySelector<HTMLElement>('[role=status]')!;
  let role = 'chemist';
  let generation = 0;
  const tryPlay = async () => {
    const id = generation;
    status.textContent = '';
    if (video.error) video.load();
    try { await video.play(); }
    catch { if (id === generation && !panel.hidden) status.textContent = video.error ? 'Видео не загрузилось. Можно повторить просмотр или выбрать следующий шаг.' : 'Нажми «Смотреть», чтобы включить обращение Михалыча.'; }
  };
  play.addEventListener('click', () => {
    if (video.ended) video.currentTime = 0;
    if (video.paused) void tryPlay(); else video.pause();
  });
  video.addEventListener('play', () => {play.textContent = 'Пауза';});
  video.addEventListener('pause', () => {play.textContent = video.ended ? 'Ещё раз' : 'Смотреть';});
  video.addEventListener('ended', () => {play.textContent = 'Ещё раз';});
  video.addEventListener('error', () => {
    if (!panel.hidden) status.textContent = 'Видео не загрузилось. Можно повторить просмотр или выбрать следующий шаг.';
  });
  const hide = () => { generation++; video.pause(); video.removeAttribute('src'); video.load(); panel.hidden = true; };
  choose.addEventListener('click', () => {hide(); select();});
  chemist.addEventListener('click', () => {hide(); select(true);});
  apply.addEventListener('click', () => {
    video.pause();
    const field = document.querySelector<HTMLSelectElement>('#application-role')!;
    if (Array.from(field.options).some(option => option.value === role)) field.value = role;
    const form = document.querySelector<HTMLFormElement>('#application-form')!;
    form.scrollIntoView({block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
    form.querySelector<HTMLInputElement>('#name')?.focus({preventScroll: true});
  });
  return {
    show(kind: Ending, selected: string) {
      role = selected; generation++;
      const complete = kind === 'completed';
      panel.dataset.kind = kind;
      title.textContent = complete ? 'Первая смена пройдена!' : 'Начнём с лаборатории?';
      detail.textContent = complete ? 'Ты нашёл заявку, проверил пробу и передал отклонение технологу.' : 'В рамках хакатона игровая смена доступна для химика-лаборанта.';
      chemist.hidden = complete;
      choose.textContent = complete ? 'Другая профессия' : 'К профессиям';
      video.poster = `${panel.dataset.base}${complete ? 'finale' : 'unavailable'}.jpg`;
      video.src = `${panel.dataset.base}${complete ? 'finale' : 'unavailable'}.mp4`;
      status.textContent = ''; play.textContent = 'Смотреть'; panel.hidden = false;
      void tryPlay();
      apply.focus({preventScroll: true});
    },
    activity(active: boolean) { if (!active && !panel.hidden) video.pause(); },
  };
}
