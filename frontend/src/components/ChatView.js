import { html, useState, useRef, useEffect } from '../lib.js';
import { api, ApiError } from '../api.js';
import { userId, sessionId, plans, lessonsBreadcrumb, view } from '../store.js';
import { ErrorBanner } from './ErrorBanner.js';
import { volumeIdForPhase } from './Lessons.js';

export function ChatView() {
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, sending]);

  const openPhase = (phase) => {
    lessonsBreadcrumb.value = { volumeId: volumeIdForPhase(phase.phase_slug), phaseSlug: phase.phase_slug };
    view.value = 'lessons';
  };

  const savePlan = async (index, goalText, topics) => {
    setMessages((current) => current.map((message, i) => i === index ? { ...message, saveState: 'saving' } : message));
    try {
      const saved = await api.savePlan({ user_id: userId.value, goal_text: goalText, topics });
      plans.value = [saved, ...plans.value];
      setMessages((current) => current.map((message, i) => i === index ? { ...message, saveState: 'saved' } : message));
    } catch (err) {
      setMessages((current) => current.map((message, i) => i === index ? { ...message, saveState: 'idle' } : message));
      setError(err instanceof ApiError ? err.message : "Couldn't save that roadmap.");
    }
  };

  const send = async (event) => {
    event?.preventDefault?.();
    const text = draft.trim();
    if (!text || sending) return;
    setError(null);
    setMessages((current) => [...current, { role: 'user', text }]);
    setDraft('');
    setSending(true);
    try {
      const response = await api.chat({ user_id: userId.value, session_id: sessionId.value, message: text });
      if (response.is_goal) {
        setMessages((current) => [...current, {
          role: 'assistant',
          kind: 'goal',
          goalText: text,
          topics: response.goal_topics?.topics || [],
          saveState: 'idle',
        }]);
      } else {
        setMessages((current) => [...current, { role: 'assistant', text: response.reply }]);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong sending that.');
      setDraft(text);
      setMessages((current) => current.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const onKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      send(event);
    }
  };

  return html`
    <div class="content" style="display:flex; flex-direction:column; height:100%;">
      <div class="eyebrow"><span class="dot" />AI ENGINEERING TUTOR <b>POST /chat</b></div>
      <h1>Ask the Tutor</h1>
      <p class="helptext" style="margin-bottom:18px;">Explore AI, machine learning, deep learning, LLMs, agents, production systems, and the mathematics and Python that support them.</p>

      ${error && html`<${ErrorBanner} message=${error} onRetry=${() => send()} retrying=${sending} />`}

      <div class="chat-scroll" ref=${scrollRef} style="flex:1; overflow-y:auto;">
        ${messages.length === 0 && html`<div class="chat-empty">Try: “Explain backpropagation intuitively”, “How does RAG reduce hallucinations?”, or “I want a roadmap to build an AI agent”.</div>`}
        ${messages.map((message, index) => html`
          <div class="bubble-row ${message.role}">
            <div>
              ${message.kind === 'goal'
                ? html`
                  <div class="bubble goal-bubble">
                    <div class="goal-bubble-title">Suggested AI Engineering roadmap</div>
                    <div class="plan-checklist">
                      ${message.topics.map((phase) => html`
                        <div class="checklist-item">
                          <button class="crumb-link" onClick=${() => openPhase(phase)}>${String(phase.number).padStart(2, '0')} · ${phase.title} →</button>
                        </div>
                      `)}
                    </div>
                    <button class="primary" style="margin-top:10px;" disabled=${message.saveState !== 'idle'} onClick=${() => savePlan(index, message.goalText, message.topics)}>
                      ${message.saveState === 'saving' ? html`<span class="spinner" />` : message.saveState === 'saved' ? 'Saved ✓' : 'Save as my plan'}
                    </button>
                  </div>
                `
                : html`<div class="bubble">${message.text}</div>`}
            </div>
          </div>
        `)}
        ${sending && html`<div class="bubble-row assistant"><div class="bubble"><span class="spinner" /> thinking…</div></div>`}
      </div>

      <form class="chat-input-row" onSubmit=${send} style="margin-top:14px;">
        <textarea placeholder="Ask an AI Engineering question… (Enter to send, Shift+Enter for a new line)" value=${draft} onInput=${(event) => setDraft(event.target.value)} onKeyDown=${onKeyDown} disabled=${sending} />
        <button class="primary" type="submit" disabled=${sending || !draft.trim()}>${sending ? html`<span class="spinner" />` : 'Send'}</button>
      </form>
    </div>
  `;
}
