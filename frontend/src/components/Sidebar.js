import { html, useState, useEffect } from '../lib.js';
import { view, health, username, userId, logOut } from '../store.js';
import { api } from '../api.js';
import { SettingsModal } from './SettingsModal.js';
import { IconHome, IconChat, IconTarget, IconBook, IconChecklist, IconChart } from '../icons.js';

const ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: IconHome },
  { id: 'chat', label: 'Tutor', icon: IconChat },
  { id: 'practice', label: 'Practice', icon: IconTarget },
  { id: 'lessons', label: 'Guides', icon: IconBook },
  { id: 'plans', label: 'My Plans', icon: IconChecklist },
  { id: 'progress', label: 'Progress', icon: IconChart },
];

function led(ok) {
  return ok === null ? '' : ok ? 'up' : 'down';
}

function tierFor(pct) {
  if (pct >= 85) return 'Advanced';
  if (pct >= 55) return 'Intermediate';
  return 'Beginner';
}

export function Sidebar() {
  const [showSettings, setShowSettings] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [masteryPct, setMasteryPct] = useState(null);

  useEffect(() => {
    let cancelled = false;
    if (!userId.value) return;
    api
      .mastery(userId.value)
      .then((res) => {
        if (cancelled) return;
        const rows = res.mastery || [];
        const pct = rows.length ? Math.round((rows.reduce((s, r) => s + r.score, 0) / rows.length) * 100) : 0;
        setMasteryPct(pct);
      })
      .catch(() => {
        if (!cancelled) setMasteryPct(null);
      });
    return () => {
      cancelled = true;
    };
  }, [userId.value]);

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
      <div class="nav-scroll">
        ${ITEMS.map(
          (item) => html`
            <button
              class="nav-item ${view.value === item.id ? 'active' : ''}"
              onClick=${() => (view.value = item.id)}
            >
              <${item.icon} />
              ${item.label}
            </button>
          `
        )}
      </div>

      ${masteryPct !== null &&
      html`
        <div class="sidebar-stat">
          <div class="row">Active Mastery <b>${masteryPct}%</b></div>
          <div class="bar-wrap"><div class="bar-fill" style="width:${masteryPct}%; background:var(--success);"></div></div>
          <div class="tier-row"><span>Curriculum Tier</span><span>${tierFor(masteryPct)}</span></div>
        </div>
      `}

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
