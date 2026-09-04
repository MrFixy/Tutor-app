import { html, useState, useEffect } from '../lib.js';
import { api, ApiError } from '../api.js';
import { userId, plans, lessonsBreadcrumb, view } from '../store.js';
import { DomainBadge, StatusBadge } from './Badge.js';
import { ErrorBanner } from './ErrorBanner.js';

function progressPct(items) {
  if (!items.length) return 0;
  const mastered = items.filter((i) => i.status === 'mastered').length;
  return Math.round((mastered / items.length) * 100);
}

export function Plans() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(null); // plan id | null

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getPlans(userId.value);
      plans.value = res.plans;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load your plans.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openLesson = (item) => {
    lessonsBreadcrumb.value =
      item.domain === 'coding' ? { domain: 'coding', language: item.language } : { domain: 'stats', language: null };
    view.value = 'lessons';
  };

  return html`
    <div class="content">
      <div class="eyebrow"><span class="dot" />GET /plans/${userId.value} <b>Real-time Sync</b></div>
      <div class="content-header">
        <h1>My plans</h1>
        <button class="ghost" onClick=${load} disabled=${loading}>${loading ? html`<span class="spinner" />` : 'Refresh'}</button>
      </div>
      <p class="helptext" style="margin-bottom:18px;">
        Roadmaps saved from a goal you told the Tutor about ("I want to learn ..."). Each item's status comes
        straight from your practice history.
      </p>

      ${error && html`<${ErrorBanner} message=${error} onRetry=${load} retrying=${loading} />`}

      ${!loading && plans.value.length === 0 && html`
        <div class="card">
          <div class="mastery-empty">
            No saved plans yet. Tell the Tutor a goal like "I want to learn statistics for data science" and save
            the roadmap it gives you.
          </div>
        </div>
      `}

      ${plans.value.map((plan) => {
        const pct = progressPct(plan.items);
        const isOpen = expanded === plan.id;
        return html`
          <div class="card plan-card">
            <div class="plan-card-head" onClick=${() => setExpanded(isOpen ? null : plan.id)}>
              <div>
                <h3>${plan.goal_text}</h3>
                <p class="helptext" style="margin:0;">${plan.items.length} topic${plan.items.length === 1 ? '' : 's'}</p>
              </div>
              <div class="bar-wrap" style="flex: 0 0 140px;"><div class="bar-fill" style="width:${pct}%"></div></div>
              <div class="pct">${pct}%</div>
            </div>
            ${isOpen && html`
              <div class="plan-checklist">
                ${plan.items.map(
                  (item) => html`
                    <div class="checklist-item" onClick=${() => openLesson(item)}>
                      <div>
                        <${DomainBadge} domain=${item.domain} />
                        <span>${item.title}</span>
                      </div>
                      <${StatusBadge} status=${item.status} />
                    </div>
                  `
                )}
              </div>
            `}
          </div>
        `;
      })}
    </div>
  `;
}
