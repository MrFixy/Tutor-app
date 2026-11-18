import { html } from '../lib.js';
import { username, health } from '../store.js';
import { IconLogoMark } from '../icons.js';

function initial(name) {
  return (name || '?').trim().charAt(0).toUpperCase();
}

export function Topbar() {
  const status = health.value.ollama_ok === null ? 'Checking' : health.value.ollama_ok ? 'Active' : 'Unavailable';
  const statusClass = health.value.ollama_ok === null ? '' : health.value.ollama_ok ? 'up' : 'down';

  return html`
    <header class="topbar">
      <div class="topbar-brand">
        <div class="brand-mark"><${IconLogoMark} /></div>
        <div>
          <div class="brand-name">AI Engineering Tutor</div>
          <div class="brand-sub">learn · understand · build</div>
        </div>
        <span class="beta-pill">AI ENGINEERING</span>
      </div>
      <div class="topbar-right">
        <div class="loop-status"><span class="led ${statusClass}" /> AI model: <b>${status}</b></div>
        <div class="topbar-divider" />
        <div class="user-chip">
          <div class="who"><div class="name">${username.value}</div><div class="tag-line">Learner</div></div>
          <div class="avatar">${initial(username.value)}</div>
        </div>
      </div>
    </header>
  `;
}
