import './main.css';

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

function uuid() {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 15) | 64;
  bytes[8] = (bytes[8] & 63) | 128;
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

document.querySelectorAll<HTMLAnchorElement>('[data-role]').forEach((link) => {
  link.addEventListener('click', () => {
    const select = $<HTMLSelectElement>('application-role');
    select.value = link.dataset.role ?? 'undecided';
  });
});

const form = $<HTMLFormElement>('application-form');
const status = $('form-status');
let idempotencyKey = uuid();
let submitted = false;

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (submitted) return;

  const button = form.querySelector<HTMLButtonElement>('[type="submit"]')!;
  const data = new FormData(form);
  const csrf = String(data.get('csrfmiddlewaretoken'));
  button.disabled = true;
  status.textContent = 'Сохраняем анкету…';
  document.querySelectorAll<HTMLElement>('[data-error]').forEach((element) => {
    element.textContent = '';
  });

  const payload = {
    name: data.get('name'),
    email: data.get('email'),
    role: data.get('role'),
    availability: data.get('availability'),
    consent: data.get('consent') === 'on',
    idempotency_key: idempotencyKey,
  };

  try {
    const response = await fetch('/api/v1/applications/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      Object.entries(result).forEach(([field, error]) => {
        const target = document.querySelector<HTMLElement>(`[data-error="${field}"]`);
        if (target) target.textContent = Array.isArray(error) ? error.join(' ') : String(error);
      });
      throw new Error(result.detail || 'Проверь поля и попробуй ещё раз.');
    }
    submitted = true;
    status.textContent = `${result.message} Номер: ${result.id.slice(0, 8)}`;
    button.textContent = 'Анкета сохранена ✓';
  } catch (error) {
    status.textContent = error instanceof Error
      ? error.message
      : 'Не удалось сохранить. Введённые данные остались в форме.';
  } finally {
    button.disabled = submitted;
  }
});
