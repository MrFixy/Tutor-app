import { html, useState, useEffect } from '../lib.js';
import { api, ApiError } from '../api.js';
import { userId, plans, lessonsBreadcrumb, view } from '../store.js';
import { ErrorBanner } from './ErrorBanner.js';
import { volumeIdForPhase } from './Lessons.js';

export function Plans() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getPlans(userId.value);
      plans.value = response.plans;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load your roadmaps.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const openPhase = (phase) => {
    lessonsBreadcrumb.value = { volumeId: volumeIdForPhase(phase.phase_slug), phaseSlug: phase.phase_slug };
    view.value = 'lessons';
  };

  return html`
    <div class="content">
      <div class="eyebrow"><span class="dot" />AI ENGINEERING ROADMAPS <b>Saved plans</b></div>
      <div class="content-header">
        <h1>My plans</h1>
        <button class="ghost" onClick=${load} disabled=${loading}>${loading ? html`<span class="spinner" />` : 'Refresh'}</button>
      </div>
      <p class="helptext" style="margin-bottom:18px;">Roadmaps generated from your AI Engineering learning or project goals. Open any phase to continue in Guides.</p>

      ${error && html`<${ErrorBanner} message=${error} onRetry=${load} retrying=${loading} />`}

      ${!loading && plans.value.length === 0 && html`
        <div class="card">
          <div class="empty-state">No saved roadmaps yet. Tell the AI Tutor what you want to learn or build, then save its suggested phases.</div>
          <button class="primary" onClick=${() => (view.value = 'chat')}>Create a roadmap →</button>
        </div>
      `}

      ${plans.value.map((plan) => {
        const isOpen = expanded === plan.id;
        return html`
          <div class="card plan-card">
            <div class="plan-card-head" onClick=${() => setExpanded(isOpen ? null : plan.id)} role="button" tabIndex="0">
              <div>
                <h3>${plan.goal_text}</h3>
                <p class="helptext" style="margin:0;">${plan.items.length} AI Engineering phase${plan.items.length === 1 ? '' : 's'}</p>
              </div>
              <span class="chapter-arrow">${isOpen ? '−' : '+'}</span>
            </div>
            ${isOpen && html`
              <div class="plan-checklist">
                ${plan.items.map((phase) => html`
                  <button class="checklist-item plan-phase-link" onClick=${() => openPhase(phase)}>
                    <span>${String(phase.number).padStart(2, '0')} · ${phase.title}</span>
                    <span class="chapter-arrow">→</span>
                  </button>
                `)}
              </div>
            `}
          </div>
        `;
      })}
    </div>
  `;
}
