import { html, useState, useEffect } from '../lib.js';
import { api, ApiError } from '../api.js';
import { userId } from '../store.js';
import { DomainBadge, DifficultyBadge } from './Badge.js';
import { ErrorBanner } from './ErrorBanner.js';
import { SkeletonMastery } from './Skeleton.js';

function barColor(pct) {
  if (pct >= 70) return 'var(--success)';
  if (pct >= 40) return 'var(--warn)';
  return 'var(--danger)';
}

export function ProgressView() {
  const [rows, setRows] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.mastery(userId.value);
      setRows(res.mastery);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load progress.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return html`
    <div class="content">
      <div class="eyebrow"><span class="dot" />GET /mastery/${userId.value} <b>Bayesian IRL v4.2</b></div>
      <div class="content-header">
        <h1>Progress</h1>
        <button class="ghost" onClick=${load} disabled=${loading}>${loading ? html`<span class="spinner" />` : 'Refresh'}</button>
      </div>
      <p class="helptext" style="margin-bottom:18px;">
        A rolling score per subtopic from your quiz and code attempts. This is also what sets the difficulty
        of explanations and new exercises.
      </p>

      ${error && html`<${ErrorBanner} message=${error} onRetry=${load} retrying=${loading} />`}

      <div class="card">
        ${loading && !rows && html`<${SkeletonMastery} count=${4} />`}
        ${rows &&
        rows.length === 0 &&
        html`<div class="mastery-empty">No attempts yet. Answer a few quiz or code questions in Practice and they'll show up here.</div>`}
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
    </div>
  `;
}
