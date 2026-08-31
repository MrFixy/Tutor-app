// Thin fetch wrapper around the FastAPI backend. One function per route,
// each matching the request/response shape in app/schemas.py exactly so
// a schema change on the backend is easy to trace to a single spot here.

import { apiBase } from './store.js';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = 'GET', body } = {}) {
  let res;
  try {
    res = await fetch(`${apiBase.value}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    throw new ApiError(
      `Couldn't reach the API at ${apiBase.value}. Is the backend running and is the URL right (see Settings)?`,
      0
    );
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = j.detail ? (typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail)) : detail;
    } catch {
      /* body wasn't JSON */
    }
    throw new ApiError(detail || `Request failed (${res.status})`, res.status);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  health: () => request('/health'),

  chat: ({ user_id, session_id, message }) =>
    request('/chat', { method: 'POST', body: { user_id, session_id, message } }),

  quizGenerate: ({ user_id, session_id, subtopic, difficulty, count }) =>
    request('/practice/quiz/generate', {
      method: 'POST',
      body: { user_id, session_id, subtopic, difficulty, count },
    }),

  quizSubmit: ({ user_id, question_id, chosen_index }) =>
    request('/practice/quiz/submit', { method: 'POST', body: { user_id, question_id, chosen_index } }),

  codeGenerate: ({ user_id, session_id, subtopic, difficulty }) =>
    request('/practice/code/generate', {
      method: 'POST',
      body: { user_id, session_id, subtopic, difficulty },
    }),

  codeSubmit: ({ user_id, question_id, source_code }) =>
    request('/practice/code/submit', { method: 'POST', body: { user_id, question_id, source_code } }),

  mastery: (user_id) => request(`/mastery/${user_id}`),

  feedback: ({ user_id, session_id, category, view, severity, message }) =>
    request('/feedback', {
      method: 'POST',
      body: { user_id, session_id, category, view, severity, message },
    }),

  // Redesign: lessons + goal-driven study plans.

  getLessons: ({ domain, user_id, language }) => {
    const params = new URLSearchParams({ user_id });
    if (language) params.set('language', language);
    return request(`/lessons/${domain}?${params.toString()}`);
  },

  getLesson: ({ domain, subtopic, language }) => {
    const params = language ? `?${new URLSearchParams({ language }).toString()}` : '';
    return request(`/lessons/${domain}/${subtopic}${params}`);
  },

  savePlan: ({ user_id, goal_text, topics }) =>
    request('/plans', { method: 'POST', body: { user_id, goal_text, topics } }),

  getPlans: (user_id) => request(`/plans/${user_id}`),
};

export { ApiError };
