// Small fetch wrapper for the AI Engineering Tutor API.

import { apiBase } from './store.js';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = 'GET', body } = {}) {
  let response;
  try {
    response = await fetch(`${apiBase.value}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(
      `Couldn't reach the API at ${apiBase.value}. Is the backend running and is the URL right (see Settings)?`,
      0
    );
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = await response.json();
      detail = payload.detail ? (typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail)) : detail;
    } catch {
      // The response body was not JSON.
    }
    throw new ApiError(detail || `Request failed (${response.status})`, response.status);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  health: () => request('/health'),
  chat: ({ user_id, session_id, message }) =>
    request('/chat', { method: 'POST', body: { user_id, session_id, message } }),
  savePlan: ({ user_id, goal_text, topics }) =>
    request('/plans', { method: 'POST', body: { user_id, goal_text, topics } }),
  getPlans: (user_id) => request(`/plans/${user_id}`),
  feedback: ({ user_id, session_id, category, view, severity, message }) =>
    request('/feedback', {
      method: 'POST',
      body: { user_id, session_id, category, view, severity, message },
    }),
};

export { ApiError };
