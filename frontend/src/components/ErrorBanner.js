import { html } from '../lib.js';

// Phase 6 / Week 14: every error banner in the app used to be a dead end
// -- the learner had to notice which button to re-click themselves. This
// gives every one of them the same "Retry" affordance, wired to whatever
// action actually failed (passed in as onRetry by the caller).
export function ErrorBanner({ message, onRetry, retrying, style }) {
  return html`
    <div class="error-banner" style=${style || ''}>
      <span>${message}</span>
      ${onRetry &&
      html`
        <button class="ghost error-retry" onClick=${onRetry} disabled=${!!retrying}>
          ${retrying ? html`<span class="spinner" />` : 'Retry'}
        </button>
      `}
    </div>
  `;
}
