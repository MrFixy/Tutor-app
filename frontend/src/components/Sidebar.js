import { html, useState } from '../lib.js';
import { view, health, username, logOut } from '../store.js';
import { SettingsModal } from './SettingsModal.js';
import { IconHome, IconChat, IconBook, IconChecklist } from '../icons.js';

const ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: IconHome },
  { id: 'chat', label: 'AI Tutor', icon: IconChat },
  { id: 'lessons', label: 'Guides', icon: IconBook },
  { id: 'plans', label: 'My Plans', icon: IconChecklist },
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

  const footBody = html`
    <div class="status-row">
      <span class="status-led ${led(health.value.ollama_ok)}" />
      AI model ${health.value.ollama_ok === null ? '–' : health.value.ollama_ok ? 'up' : 'down'}
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
      <div class="nav-scroll">
        ${ITEMS.map(
          (item) => html`
            <button class="nav-item ${view.value === item.id ? 'active' : ''}" onClick=${() => (view.value = item.id)}>
              <${item.icon} />
              ${item.label}
            </button>
          `
        )}
      </div>

      <div class="sidebar-foot">${footBody}</div>

      <button class="mobile-foot-trigger ghost" onClick=${() => setShowMobileMenu(true)} aria-label="Status and settings">
        <span class="status-led ${led(health.value.ollama_ok)}" title="AI model" />
        <span class="mobile-foot-trigger-label">${username.value}</span>
      </button>

      ${showMobileMenu && html`
        <div class="mobile-foot-backdrop" onClick=${() => setShowMobileMenu(false)}></div>
        <div class="mobile-foot-sheet"><div class="sheet-handle"></div>${footBody}</div>
      `}

      ${showSettings && html`<${SettingsModal} onClose=${() => setShowSettings(false)} />`}
    </nav>
  `;
}
