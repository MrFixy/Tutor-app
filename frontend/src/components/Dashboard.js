import { html, useState, useEffect } from '../lib.js';
import { api, ApiError } from '../api.js';
import { userId, plans, view, practicePrefill } from '../store.js';
import { DomainBadge, DifficultyBadge } from './Badge.js';
import { ErrorBanner } from './ErrorBanner.js';
import { SkeletonMastery } from './Skeleton.js';

function avgPct(rows) {
  if (!rows.length) return 0;
  return Math.round((rows.reduce((s, r) => s + r.score, 0) / rows.length) * 100);
}

function barColor(pct) {
  if (pct >= 70) return 'var(--success)';
  if (pct >= 40) return 'var(--warn)';
  return 'var(--danger)';
}

function tierFor(pct) {
  if (pct >= 85) return 'Advanced';
  if (pct >= 55) return 'Intermediate';
  return 'Beginner';
}

export function Dashboard() {
  const [rows, setRows] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [masteryRes, plansRes] = await Promise.all([api.mastery(userId.value), api.getPlans(userId.value)]);
      setRows(masteryRes.mastery);
      plans.value = plansRes.plans;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load your dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const statsRows = (rows || []).filter((r) => r.domain === 'stats');
  const codingRows = (rows || []).filter((r) => r.domain === 'coding');
  const totalAttempts = (rows || []).reduce((s, r) => s + r.attempts_count, 0);

  // "Continue": the subtopic with the most practice history that hasn't
  // been mastered yet, if any -- otherwise nothing to suggest.
  const continueRow = (rows || [])
    .filter((r) => r.attempts_count > 0 && r.score < 0.75)
    .sort((a, b) => b.attempts_count - a.attempts_count)[0];

  const topPlan = plans.value[0];
  const topPlanPct = topPlan
    ? Math.round((topPlan.items.filter((i) => i.status === 'mastered').length / (topPlan.items.length || 1)) * 100)
    : null;

  const goToPractice = (row) => {
    practicePrefill.value = { domain: row.domain, subtopic: row.subtopic, difficulty: row.difficulty };
    view.value = 'practice';
  };

  const aggregatePct = rows ? avgPct(rows) : 0;

  return html`
    <div class="content">
      <div class="eyebrow">
        <span class="dot" />
        TELEMETRY :: GET /mastery/${userId.value} <b>${loading ? 'Syncing...' : 'Live Model Synced'}</b>
      </div>
      <div class="content-header">
        <h1>Dashboard</h1>
        <button class="ghost" onClick=${load} disabled=${loading}>${loading ? html`<span class="spinner" />` : 'Refresh'}</button>
      </div>

      ${error && html`<${ErrorBanner} message=${error} onRetry=${load} retrying=${loading} />`}

      <div class="card hero-card">
        <div class="hero-copy">
          <h3 style="text-transform:uppercase; font-size:11px; letter-spacing:0.05em; color:var(--text-dim);">Aggregate Mastery</h3>
          <h1 style="margin-top:2px;">${rows ? tierFor(aggregatePct) : '\u2013'} Tier</h1>
          <p>Your dynamic mastery snapshot across every stats and coding subtopic you've practiced.</p>
        </div>
        <div class="ring" style="--pct:${rows ? aggregatePct : 0}; --ring-color:${barColor(aggregatePct)};">
          <div class="ring-value">${rows ? `${aggregatePct}%` : '\u2013'}</div>
        </div>
      </div>

      <div class="metric-grid">
        <div class="card metric-card">
          <div class="metric-label">Stats mastery</div>
          <div class="metric-value">${rows ? `${avgPct(statsRows)}%` : '\u2013'}</div>
        </div>
        <div class="card metric-card">
          <div class="metric-label">Coding mastery</div>
          <div class="metric-value">${rows ? `${avgPct(codingRows)}%` : '\u2013'}</div>
        </div>
        <div class="card metric-card">
          <div class="metric-label">Practice attempts</div>
          <div class="metric-value">${rows ? totalAttempts : '\u2013'}</div>
        </div>
      </div>

      <div class="dashboard-row">
        <div class="card" style="flex: 1 1 55%;">
          <h3>Subtopic Competency Vectors</h3>
          <p class="helptext" style="margin-bottom:14px;">Continuous mastery tracking across your active subtopics.</p>
          ${loading && !rows && html`<${SkeletonMastery} count=${4} />`}
          ${rows && rows.length === 0 && html`<div class="mastery-empty">No attempts yet. Ask the Tutor something, then practice it.</div>`}
          ${rows &&
          rows.map(
            (r) => html`
              <div class="mastery-row">
                <div class="name">
                  <div class="sub">${r.subtopic.replaceAll('_', ' ')}</div>
                  <${DomainBadge} domain=${r.domain} />
                  <${DifficultyBadge} difficulty=${r.difficulty} />
                </div>
                <div class="bar-wrap"><div class="bar-fill" style="width:${Math.round(r.score * 100)}%; background:${barColor(r.score * 100)};"></div></div>
                <div class="pct">${Math.round(r.score * 100)}%</div>
              </div>
            `
          )}
        </div>

        <div style="flex: 1 1 40%; display:flex; flex-direction:column; gap:16px;">
          <div class="card">
            <h3>My plans</h3>
            ${topPlan
              ? html`
                  <p class="sub" style="margin:0 0 6px;">${topPlan.goal_text}</p>
                  <div class="bar-wrap"><div class="bar-fill" style="width:${topPlanPct}%"></div></div>
                  <p class="pct" style="margin:6px 0 12px;">${topPlanPct}% complete</p>
                `
              : html`<p class="helptext">No saved plans yet.</p>`}
            <button class="ghost" onClick=${() => (view.value = 'plans')}>View all plans &rarr;</button>
          </div>

          <div class="card">
            <h3>Continue</h3>
            ${continueRow
              ? html`
                  <p class="sub" style="margin:0 0 10px;">
                    ${continueRow.subtopic.replaceAll('_', ' ')} (${Math.round(continueRow.score * 100)}%)
                  </p>
                  <button class="primary" onClick=${() => goToPractice(continueRow)}>Practice this &rarr;</button>
                `
              : html`<p class="helptext">Nothing in progress yet -- ask the Tutor a question to get started.</p>`}
          </div>
        </div>
      </div>
    </div>
  `;
}
