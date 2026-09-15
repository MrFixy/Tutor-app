import { signal, effect } from 'https://esm.sh/@preact/signals@1.2.2?deps=preact@10.19.3';

// ---- persistence helpers -------------------------------------------------

const read = (key, fallback) => {
  try {
    const v = localStorage.getItem(key);
    return v === null ? fallback : JSON.parse(v);
  } catch {
    return fallback;
  }
};
const persist = (key, sig) => effect(() => localStorage.setItem(key, JSON.stringify(sig.value)));

// Deterministic username -> integer user_id (djb2 hash, kept positive and
// well under Postgres int4 range). No auth for the pilot, so the only job
// here is "the same username always maps to the same user_id" -- including
// across browsers/machines, since mastery history lives server-side.
export function usernameToUserId(username) {
  let hash = 5381;
  for (let i = 0; i < username.length; i++) {
    hash = ((hash << 5) + hash + username.charCodeAt(i)) | 0;
  }
  return Math.abs(hash) % 1_000_000 || 1;
}

// ---- signals --------------------------------------------------------------

export const apiBase = signal(read('tutor.apiBase', 'http://localhost:8000'));
persist('tutor.apiBase', apiBase);

export const username = signal(read('tutor.username', null));
persist('tutor.username', username);

export const userId = signal(username.value ? usernameToUserId(username.value) : null);
effect(() => {
  userId.value = username.value ? usernameToUserId(username.value) : null;
});

// One session_id per login (persisted client-side per the Week 11 brief).
// A fresh id is only minted when there wasn't one already stored.
export const sessionId = signal(read('tutor.sessionId', null));
persist('tutor.sessionId', sessionId);
if (sessionId.value === null) sessionId.value = Date.now() % 2_147_483_647;

export const view = signal('dashboard'); // 'dashboard' | 'lessons' | 'plans' | 'chat' | 'practice'

// Handoff from a chat reply's badges into the Practice view, so "Practice
// this" actually lands on the right subtopic/difficulty instead of making
// the learner re-pick it.
export const practicePrefill = signal(null); // { domain, subtopic, difficulty } | null

// Drives the Lessons tab's drill-down. null = top-level Statistics/
// Programming cards. { domain: 'stats' } = subtopic grid. { domain:
// 'coding', language: null } = language grid. { domain: 'coding',
// language: 'python' } = topic grid for that language.
export const lessonsBreadcrumb = signal(null); // { domain, language } | null

// Cached StudyPlanOut[] from GET /plans/{user_id}, refreshed on save and
// on entering the My plans tab.
export const plans = signal([]);

export const health = signal({ ollama_ok: null, judge0_ok: null });

export function logIn(name) {
  username.value = name.trim();
  sessionId.value = Date.now() % 2_147_483_647;
}

export function logOut() {
  username.value = null;
  view.value = 'dashboard';
  practicePrefill.value = null;
  lessonsBreadcrumb.value = null;
  plans.value = [];
}
