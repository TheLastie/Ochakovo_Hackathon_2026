import './main.css';
import { initGameMenu } from './game-menu';

initGameMenu();

type Video = { src: string; poster?: string; duration?: number };
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const content = JSON.parse($('site-content').textContent!) as {
  brandVideo: Video & { title: string };
};

function uuid() {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 15) | 64;
  bytes[8] = (bytes[8] & 63) | 128;
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

function track(kind: string, video = 'brand') {
  const csrf = $('application-form').querySelector<HTMLInputElement>('[name=csrfmiddlewaretoken]')?.value;
  void fetch('/api/v1/events/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(csrf ? { 'X-CSRFToken': csrf } : {}) },
    body: JSON.stringify({ id: uuid(), kind, video }),
    keepalive: true,
  }).catch(() => {});
}

function openBrandVideo() {
  const box = $('brand-player');
  box.replaceChildren();
  track('video_open');
  $('brand-video-cover').hidden = true;
  box.hidden = false;
  $('brand-media').classList.add('is-playing');

  if (content.brandVideo.src) {
    const video = document.createElement('video');
    video.controls = true;
    video.preload = 'metadata';
    video.src = content.brandVideo.src;
    video.playsInline = true;
    if (content.brandVideo.poster) video.poster = content.brandVideo.poster;
    let started = false;
    video.addEventListener('play', () => {
      if (!started) {
        track('video_play');
        started = true;
      }
    });
    video.addEventListener('ended', () => track('video_complete'), { once: true });
    video.addEventListener('error', () => {
      const message = document.createElement('p');
      message.textContent = 'Не удалось открыть видео. Попробуй обновить страницу.';
      box.prepend(message);
    }, { once: true });
    box.append(video);
    void video.play().catch(() => {});
  }

}

document.querySelectorAll<HTMLElement>('[data-video="brand"]').forEach((button) => {
  button.onclick = openBrandVideo;
});

const form = $<HTMLFormElement>('application-form');
let key = uuid();
let sent = false;
form.onsubmit = async (event) => {
  event.preventDefault();
  if (sent) return;
  const button = form.querySelector<HTMLButtonElement>('[type=submit]')!;
  button.disabled = true;
  document.querySelectorAll<HTMLElement>('[data-error]').forEach((element) => (element.textContent = ''));
  $('form-status').textContent = 'Сохраняем анкету…';
  const data = new FormData(form);
  const payload = {
    name: data.get('name'),
    email: data.get('email'),
    role: data.get('role'),
    availability: data.get('availability'),
    consent: data.get('consent') === 'on',
    idempotency_key: key,
  };
  try {
    const response = await fetch('/api/v1/applications/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': String(data.get('csrfmiddlewaretoken')) },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      Object.entries(result).forEach(([field, error]) => {
        const target = document.querySelector<HTMLElement>(`[data-error="${field}"]`);
        if (target) target.textContent = String(error);
      });
      throw new Error(result.detail || 'Проверь поля и попробуй ещё раз.');
    }
    sent = true;
    $('form-status').textContent = `${result.message} Номер: ${result.id.slice(0, 8)}`;
    button.textContent = 'Анкета сохранена ✓';
  } catch (error) {
    $('form-status').textContent = error instanceof Error
      ? error.message
      : 'Не удалось сохранить. Введённые данные остались в форме.';
  } finally {
    button.disabled = sent;
  }
};
