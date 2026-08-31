import { html, useState } from '../lib.js';
import { view, health, username, logOut } from '../store.js';
import { SettingsModal } from './SettingsModal.js';

const ITEMS = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'lessons', label: 'Lessons' },
  { id: 'plans', label: 'My plans' },
  { id: 'chat', label: 'Tutor' },
  { id: 'practice', label: 'Practice' },
];

function led(ok) {
  return ok === null ? '' : ok ? 'up' : 'down';
}

export function Sidebar() {
  const [showSettings, setShowSettings] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  const openSettings = () => {
    setShowMobileMenu(false);
    setShowSettings(true);
  };

  // Shared between the desktop sidebar-foot and the mobile bottom sheet
  // so status/identity/settings never diverge between the two layouts.
  const footBody = html`
    <div class="status-row">
      <span class="status-led ${led(health.value.ollama_ok)}" />
      model ${health.value.ollama_ok === null ? '\u2013' : health.value.ollama_ok ? 'up' : 'down'}
    </div>
    <div class="status-row">
      <span class="status-led ${led(health.value.judge0_ok)}" />
      judge0 ${health.value.judge0_ok === null ? '\u2013' : health.value.judge0_ok ? 'up' : 'down'}
    </div>
    <div class="status-row" style="justify-content: space-between; margin-top: 4px;">
      <span><b>${username.value}</b></span>
    </div>
    <div class="status-row" style="gap: 10px;">
      <button class="ghost" style="padding: 4px 6px; font-size: 12px;" onClick=${openSettings}>Settings</button>
      <button class="ghost" style="padding: 4px 6px; font-size: 12px;" onClick=${logOut}>Switch user</button>
    </div>
  `;

  return html`
    <nav class="sidebar">
      <div class="brand">
        <div class="mark">Tutor</div>
        <div class="sub">stats &amp; coding</div>
      </div>
      <div class="nav-scroll">
        ${ITEMS.map(
          (item) => html`
            <button
              class="nav-item ${view.value === item.id ? 'active' : ''}"
              onClick=${() => (view.value = item.id)}
            >
              <span class="dot" />
              ${item.label}
            </button>
          `
        )}
      </div>

      <div class="sidebar-foot">${footBody}</div>

      <!-- Mobile-only (<720px): sidebar-foot is hidden there, but its
           content (health LEDs, identity, settings, switch user) still
           needs a real home instead of just disappearing. This compact
           trigger keeps status visible at a glance and opens a bottom
           sheet with the full detail on tap. -->
      <button class="mobile-foot-trigger ghost" onClick=${() => setShowMobileMenu(true)} aria-label="Status and settings">
        <span class="status-led ${led(health.value.ollama_ok)}" title="model" />
        <span class="status-led ${led(health.value.judge0_ok)}" title="judge0" />
        <span class="mobile-foot-trigger-label">${username.value}</span>
      </button>

      ${showMobileMenu &&
      html`
        <div class="mobile-foot-backdrop" onClick=${() => setShowMobileMenu(false)}></div>
        <div class="mobile-foot-sheet">
          <div class="sheet-handle"></div>
          ${footBody}
        </div>
      `}

      ${showSettings && html`<${SettingsModal} onClose=${() => setShowSettings(false)} />`}
    </nav>
  `;
}
