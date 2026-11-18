import { html, useEffect } from '../lib.js';
import { username, view, health } from '../store.js';
import { api } from '../api.js';
import { Login } from './Login.js';
import { Topbar } from './Topbar.js';
import { Sidebar } from './Sidebar.js';
import { Dashboard } from './Dashboard.js';
import { Lessons } from './Lessons.js';
import { Plans } from './Plans.js';
import { ChatView } from './ChatView.js';
import { FeedbackWidget } from './FeedbackWidget.js';

const VIEWS = { dashboard: Dashboard, lessons: Lessons, plans: Plans, chat: ChatView };

export function App() {
  useEffect(() => {
    let cancelled = false;
    const poll = async () => {
      try {
        const result = await api.health();
        if (!cancelled) health.value = result;
      } catch {
        if (!cancelled) health.value = { ollama_ok: false };
      }
    };
    poll();
    const id = setInterval(poll, 30_000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (!username.value) return html`<${Login} />`;
  const ActiveScreen = VIEWS[view.value] || Dashboard;
  return html`
    <div class="app-shell">
      <${Topbar} />
      <div class="shell">
        <${Sidebar} />
        <div class="main"><${ActiveScreen} /></div>
      </div>
      <${FeedbackWidget} />
    </div>
  `;
}
