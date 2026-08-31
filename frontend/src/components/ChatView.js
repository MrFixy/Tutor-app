import { html, useState, useRef, useEffect } from '../lib.js';
import { api, ApiError } from '../api.js';
import { userId, sessionId, view, practicePrefill, lessonsBreadcrumb, plans } from '../store.js';
import { IntentTags, DomainBadge } from './Badge.js';
import { ErrorBanner } from './ErrorBanner.js';

export function ChatView() {
  const [messages, setMessages] = useState([]); // {role, text, intent?}
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, sending]);

  const send = async (e) => {
    e?.preventDefault?.();
    const text = draft.trim();
    if (!text || sending) return;
    setError(null);
    setMessages((m) => [...m, { role: 'user', text }]);
    setDraft('');
    setSending(true);
    try {
      const res = await api.chat({ user_id: userId.value, session_id: sessionId.value, message: text });
      if (res.is_goal) {
        setMessages((m) => [
          ...m,
          {
            role: 'assistant',
            kind: 'goal',
            goalText: text,
            topics: res.goal_topics?.topics || [],
            saveState: 'idle', // 'idle' | 'saving' | 'saved'
          },
        ]);
      } else {
        setMessages((m) => [
          ...m,
          {
            role: 'assistant',
            text: res.reply,
            intent: {
              domain: res.intent_domain,
              subtopic: res.intent_subtopic,
              difficulty: res.difficulty,
            },
            relatedLesson: res.related_lesson || null,
          },
        ]);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong sending that.');
      // put the failed draft back so nothing is lost
      setDraft(text);
      setMessages((m) => m.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const practiceThis = (intent) => {
    practicePrefill.value = intent;
    view.value = 'practice';
  };

  const openLesson = (lesson) => {
    lessonsBreadcrumb.value =
      lesson.domain === 'coding' ? { domain: 'coding', language: lesson.language } : { domain: 'stats', language: null };
    view.value = 'lessons';
  };

  const savePlan = async (index, goalText, topics) => {
    setMessages((m) => m.map((msg, i) => (i === index ? { ...msg, saveState: 'saving' } : msg)));
    try {
      const plan = await api.savePlan({ user_id: userId.value, goal_text: goalText, topics });
      plans.value = [plan, ...plans.value];
      setMessages((m) => m.map((msg, i) => (i === index ? { ...msg, saveState: 'saved' } : msg)));
    } catch (err) {
      setMessages((m) => m.map((msg, i) => (i === index ? { ...msg, saveState: 'idle' } : msg)));
      setError(err instanceof ApiError ? err.message : "Couldn't save that plan.");
    }
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send(e);
    }
  };

  return html`
    <div class="content" style="display:flex; flex-direction:column; height:100%;">
      <h1>Ask something</h1>
      <p class="helptext" style="margin-bottom:18px;">
        A stats or coding question, in your own words. The tutor figures out the topic and pitches the
        explanation to where your practice history says you're at.
      </p>

      ${error && html`<${ErrorBanner} message=${error} onRetry=${() => send()} retrying=${sending} />`}

      <div class="chat-scroll" ref=${scrollRef} style="flex:1; overflow-y:auto;">
        ${messages.length === 0 &&
        html`<div class="chat-empty">Try: "what's the difference between a p-value and a confidence interval?" or "why is my recursive function hitting max depth?"</div>`}
        ${messages.map(
          (m, i) => html`
            <div class="bubble-row ${m.role}">
              <div>
                ${m.kind === 'goal'
                  ? html`
                      <div class="bubble goal-bubble">
                        <div class="goal-bubble-title">Here's a roadmap for that:</div>
                        <div class="plan-checklist">
                          ${m.topics.map(
                            (t) => html`
                              <div class="checklist-item">
                                <div>
                                  <${DomainBadge} domain=${t.domain} />
                                  <span>${t.subtopic.replaceAll('_', ' ')}${t.language ? ` (${t.language})` : ''}</span>
                                </div>
                              </div>
                            `
                          )}
                        </div>
                        <button
                          class="primary"
                          style="margin-top:10px;"
                          disabled=${m.saveState !== 'idle'}
                          onClick=${() => savePlan(i, m.goalText, m.topics)}
                        >
                          ${m.saveState === 'saving' ? html`<span class="spinner" />` : m.saveState === 'saved' ? 'Saved \u2713' : 'Save as my plan'}
                        </button>
                      </div>
                    `
                  : html`
                      <div class="bubble">${m.text}</div>
                      ${m.role === 'assistant' &&
                      html`
                        <${IntentTags} domain=${m.intent?.domain} subtopic=${m.intent?.subtopic} difficulty=${m.intent?.difficulty} />
                        <div class="tag-row">
                          ${m.intent?.subtopic &&
                          html`
                            <button class="ghost practice-cta" style="font-size:12.5px; padding:5px 10px;" onClick=${() => practiceThis(m.intent)}>
                              Practice this &rarr;
                            </button>
                          `}
                          ${m.relatedLesson &&
                          html`
                            <button class="ghost practice-cta" style="font-size:12.5px; padding:5px 10px;" onClick=${() => openLesson(m.relatedLesson)}>
                              Read the lesson: ${m.relatedLesson.title} &rarr;
                            </button>
                          `}
                        </div>
                      `}
                    `}
              </div>
            </div>
          `
        )}
        ${sending &&
        html`
          <div class="bubble-row assistant">
            <div class="bubble"><span class="spinner" /> thinking&hellip;</div>
          </div>
        `}
      </div>

      <form class="chat-input-row" onSubmit=${send} style="margin-top: 14px;">
        <textarea
          placeholder="Ask a stats or coding question... (Enter to send, Shift+Enter for a new line)"
          value=${draft}
          onInput=${(e) => setDraft(e.target.value)}
          onKeyDown=${onKeyDown}
          disabled=${sending}
        />
        <button class="primary" type="submit" disabled=${sending || !draft.trim()}>
          ${sending ? html`<span class="spinner" />` : 'Send'}
        </button>
      </form>
    </div>
  `;
}
