import { html, useState, useEffect } from '../lib.js';
import { api, ApiError } from '../api.js';
import { plans, view, userId, lessonsBreadcrumb } from '../store.js';
import { ErrorBanner } from './ErrorBanner.js';

export function Dashboard() {
  const [curriculum, setCurriculum] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [curriculumResponse, plansResponse] = await Promise.all([
        fetch('./content/curriculum.json').then((response) => {
          if (!response.ok) throw new Error('Could not load the AI Engineering curriculum.');
          return response.json();
        }),
        api.getPlans(userId.value),
      ]);
      setCurriculum(curriculumResponse);
      plans.value = plansResponse.plans;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : err.message || 'Could not load the dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const phaseCount = curriculum?.length || 0;
  const lessonCount = (curriculum || []).reduce((total, phase) => total + phase.lessons.length, 0);
  const latestPlan = plans.value[0];
  const openGuides = () => {
    lessonsBreadcrumb.value = null;
    view.value = 'lessons';
  };

  return html`
    <div class="content">
      <div class="eyebrow"><span class="dot" />YOUR AI ENGINEERING WORKSPACE <b>${loading ? 'Loading' : 'Ready'}</b></div>
      <div class="content-header">
        <h1>Dashboard</h1>
        <button class="ghost" onClick=${load} disabled=${loading}>${loading ? html`<span class="spinner" />` : 'Refresh'}</button>
      </div>

      ${error && html`<${ErrorBanner} message=${error} onRetry=${load} retrying=${loading} />`}

      <section class="course-intro dashboard-intro">
        <div class="course-intro-copy">
          <span class="course-kicker">ONE FOCUSED PATH</span>
          <h1>Learn <em>AI Engineering</em></h1>
          <p>Build understanding from mathematical foundations and machine learning through deep learning, LLMs, agents, and production systems.</p>
          <button class="primary" onClick=${openGuides}>Explore the curriculum →</button>
        </div>
        <div class="course-stats" aria-label="Curriculum overview">
          <span><b>▣</b><strong>6</strong><small>volumes</small></span>
          <span><b>▱</b><strong>${phaseCount || '—'}</strong><small>phases</small></span>
          <span><b>▥</b><strong>${lessonCount || '—'}</strong><small>lessons</small></span>
        </div>
        <div class="course-scribble" aria-hidden="true">Learn<br />Build<br />Grow</div>
      </section>

      <div class="dashboard-row">
        <div class="card" style="flex: 1 1 55%;">
          <h3>Start with the AI Tutor</h3>
          <p class="helptext">Ask about machine learning, deep learning, computer vision, NLP, transformers, generative AI, LLM systems, agents, or the math and Python that support them.</p>
          <button class="primary" onClick=${() => (view.value = 'chat')}>Ask the Tutor →</button>
        </div>
        <div class="card" style="flex: 1 1 40%;">
          <h3>My latest roadmap</h3>
          ${latestPlan
            ? html`<p class="sub">${latestPlan.goal_text}</p><p class="helptext">${latestPlan.items.length} AI Engineering phases</p><button class="ghost" onClick=${() => (view.value = 'plans')}>Open my plans →</button>`
            : html`<p class="helptext">No saved roadmaps yet. Tell the Tutor what you want to learn or build, then save the suggested phases.</p><button class="ghost" onClick=${() => (view.value = 'chat')}>Create a roadmap →</button>`}
        </div>
      </div>
    </div>
  `;
}
