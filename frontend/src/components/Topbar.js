import { html } from '../lib.js';
import { username, health } from '../store.js';
import { IconLogoMark } from '../icons.js';

function initial(name) {
  return (name || '?').trim().charAt(0).toUpperCase();
}

export function Topbar() {
  const loopUp = health.value.ollama_ok && health.value.judge0_ok;
  const loopDown = health.value.ollama_ok === false || health.value.judge0_ok === false;
  const loopLabel = loopUp ? 'Active' : loopDown ? 'Degraded' : 'Checking';
  const loopCls = loopUp ? 'up' : loopDown ? 'down' : '';

  return html`
    <header class="topbar">
      <div class="topbar-brand">
        <div class="brand-mark"><${IconLogoMark} /></div>
        <div>
          <div class="brand-name">Stats &amp; Code Tutor</div>
          <div class="brand-sub">adaptive learning pilot</div>
        </div>
        <span class="beta-pill">ADAPTIVE AI BETA</span>
      </div>
      <div class="topbar-right">
        <div class="loop-status">
          <span class="led ${loopCls}" />
          Adaptive Loop: <b>${loopLabel}</b>
        </div>
        <div class="topbar-divider" />
        <div class="user-chip">
          <div class="who">
            <div class="name">${username.value}</div>
            <div class="tag-line">Pilot Learner</div>
          </div>
          <div class="avatar">${initial(username.value)}</div>
        </div>
      </div>
    </header>
  `;
}
