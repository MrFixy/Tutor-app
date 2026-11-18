import { signal, effect } from 'https://esm.sh/@preact/signals@1.2.2?deps=preact@10.19.3';

const read = (key, fallback) => {
  try {
    const value = localStorage.getItem(key);
    return value === null ? fallback : JSON.parse(value);
  } catch {
    return fallback;
  }
};
const persist = (key, signalValue) => effect(() => localStorage.setItem(key, JSON.stringify(signalValue.value)));

export function usernameToUserId(username) {
  let hash = 5381;
  for (let index = 0; index < username.length; index++) {
    hash = ((hash << 5) + hash + username.charCodeAt(index)) | 0;
  }
  return Math.abs(hash) % 1_000_000 || 1;
}

export const apiBase = signal(read('tutor.apiBase', 'http://localhost:8000'));
persist('tutor.apiBase', apiBase);

export const username = signal(read('tutor.username', null));
persist('tutor.username', username);

export const userId = signal(username.value ? usernameToUserId(username.value) : null);
effect(() => {
  userId.value = username.value ? usernameToUserId(username.value) : null;
});

export const sessionId = signal(read('tutor.sessionId', null));
persist('tutor.sessionId', sessionId);
if (sessionId.value === null) sessionId.value = Date.now() % 2_147_483_647;

export const view = signal('dashboard'); // dashboard | lessons | plans | chat
export const lessonsBreadcrumb = signal(null); // { volumeId, phaseSlug } | null
export const plans = signal([]);
export const health = signal({ ollama_ok: null });

export function logIn(name) {
  username.value = name.trim();
  sessionId.value = Date.now() % 2_147_483_647;
}

export function logOut() {
  username.value = null;
  view.value = 'dashboard';
  lessonsBreadcrumb.value = null;
  plans.value = [];
}
