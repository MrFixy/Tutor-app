// Phase 6 / Week 13: in-app feedback capture, mounted once at the app
// shell level (not inside sidebar-foot, which is hidden on mobile) so a
// pilot learner can flag a bug or confusing moment from any screen
// without losing their place. Posts straight to POST /feedback.
import { html, useState } from '../lib.js';
import { userId, sessionId, view } from '../store.js';
import { api, ApiError } from '../api.js';
import { ErrorBanner } from './ErrorBanner.js';

const CATEGORIES = [
  { id: 'bug', label: "Something's broken" },
  { id: 'ux_friction', label: 'Confusing / hard to use' },
  { id: 'other', label: 'Something else' },
];

const SEVERITIES = [
  { id: 'blocker', label: 'Stopped me' },
  { id: 'annoying', label: 'Annoying' },
  { id: 'minor', label: 'Minor' },
];

export function FeedbackWidget() {
  const [open, setOpen] = useState(false);
  const [category, setCategory] = useState('bug');
  const [severity, setSeverity] = useState(null);
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [sent, setSent] = useState(false);

  const reset = () => {
    setCategory('bug');
    setSeverity(null);
    setMessage('');
    setError(null);
    setSent(false);
  };

  const close = () => {
    setOpen(false);
    // small delay so the "thanks" state doesn't visibly reset mid-close
    setTimeout(reset, 200);
  };

  const submit = async (e) => {
    e?.preventDefault?.();
    if (!message.trim() || sending) return;
    setSending(true);
    setError(null);
    try {
      await api.feedback({
        user_id: userId.value,
        session_id: sessionId.value,
        category,
        view: view.value,
        severity,
        message: message.trim(),
      });
      setSent(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't send that -- try again?");
    } finally {
      setSending(false);
    }
  };

  return html`
    <button class="feedback-fab" onClick=${() => setOpen(true)} title="Report a bug or confusing moment">
      Feedback
    </button>
    ${open &&
    html`
      <div class="modal-backdrop" onClick=${(e) => e.target === e.currentTarget && close()}>
        <div class="modal">
          ${sent
            ? html`
                <h3>Thanks!</h3>
                <p class="helptext" style="margin: 8px 0 16px;">That's logged for the pilot review.</p>
                <div class="modal-actions">
                  <button class="primary" onClick=${close}>Done</button>
                </div>
              `
            : html`
                <h3>Report something</h3>
                <p class="helptext" style="margin: 6px 0 14px;">
                  Bug, confusing screen, slow response -- whatever it is, this goes straight to the pilot review,
                  tagged with the screen you're on (${view.value}).
                </p>
                ${error && html`<${ErrorBanner} message=${error} onRetry=${() => submit()} retrying=${sending} />`}
                <form onSubmit=${submit}>
                  <div class="chip-row">
                    ${CATEGORIES.map(
                      (c) => html`
                        <button
                          type="button"
                          class="chip ${category === c.id ? 'active' : ''}"
                          onClick=${() => setCategory(c.id)}
                        >
                          ${c.label}
                        </button>
                      `
                    )}
                  </div>
                  <div class="chip-row" style="margin-top: 8px;">
                    ${SEVERITIES.map(
                      (s) => html`
                        <button
                          type="button"
                          class="chip ${severity === s.id ? 'active' : ''}"
                          onClick=${() => setSeverity(severity === s.id ? null : s.id)}
                        >
                          ${s.label}
                        </button>
                      `
                    )}
                  </div>
                  <textarea
                    style="margin-top: 12px; min-height: 80px;"
                    placeholder="What happened?"
                    value=${message}
                    onInput=${(e) => setMessage(e.target.value)}
                  />
                  <div class="modal-actions">
                    <button type="button" class="ghost" onClick=${close}>Cancel</button>
                    <button class="primary" type="submit" disabled=${sending || !message.trim()}>
                      ${sending ? html`<span class="spinner" />` : 'Send'}
                    </button>
                  </div>
                </form>
              `}
        </div>
      </div>
    `}
  `;
}
