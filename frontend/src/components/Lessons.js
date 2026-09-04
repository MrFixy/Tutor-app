import { html, useState, useEffect } from '../lib.js';
import { api, ApiError } from '../api.js';
import { userId, lessonsBreadcrumb } from '../store.js';
import { StatusBadge } from './Badge.js';
import { ErrorBanner } from './ErrorBanner.js';

const TOP_LEVEL = [
  { domain: 'stats', label: 'Statistics', desc: 'Descriptive stats through sampling -- nine curated lessons.' },
  { domain: 'coding', label: 'Programming', desc: 'Pick a language, then a topic.' },
];

export function Lessons() {
  const bc = lessonsBreadcrumb.value;
  const [items, setItems] = useState(null);
  const [languages, setLanguages] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null); // { domain, subtopic, language } | null
  const [lesson, setLesson] = useState(null);

  useEffect(() => {
    setSelected(null);
    setLesson(null);
    if (!bc) {
      setItems(null);
      setLanguages(null);
      return;
    }
    setError(null);
    setLoading(true);
    (async () => {
      try {
        if (bc.domain === 'coding' && !bc.language) {
          const res = await api.getLessons({ domain: 'coding', user_id: userId.value });
          setLanguages(res.languages || []);
          setItems(null);
        } else {
          const res = await api.getLessons({ domain: bc.domain, user_id: userId.value, language: bc.language });
          setItems(res);
          setLanguages(null);
        }
      } catch (err) {
        setError(err instanceof ApiError ? err.message : 'Could not load lessons.');
      } finally {
        setLoading(false);
      }
    })();
  }, [bc?.domain, bc?.language]);

  useEffect(() => {
    if (!selected) {
      setLesson(null);
      return;
    }
    setError(null);
    setLoading(true);
    (async () => {
      try {
        const res = await api.getLesson(selected);
        setLesson(res);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : 'Could not load that lesson.');
      } finally {
        setLoading(false);
      }
    })();
  }, [selected?.domain, selected?.subtopic, selected?.language]);

  const crumbs = [];
  crumbs.push({ label: 'Lessons', onClick: () => (lessonsBreadcrumb.value = null) });
  if (bc?.domain === 'stats') crumbs.push({ label: 'Statistics' });
  if (bc?.domain === 'coding') {
    crumbs.push({ label: 'Programming', onClick: () => (lessonsBreadcrumb.value = { domain: 'coding', language: null }) });
    if (bc.language) crumbs.push({ label: bc.language });
  }
  if (selected) crumbs.push({ label: selected.subtopic.replaceAll('_', ' ') });

  return html`
    <div class="content">
      <div class="eyebrow"><span class="dot" />GET /lessons <b>Structured Theory</b></div>
      <h1>Lessons</h1>
      <div class="breadcrumbs">
        ${crumbs.map(
          (c, i) => html`
            ${i > 0 && html`<span class="crumb-sep">/</span>`}
            ${c.onClick ? html`<button class="crumb-link" onClick=${c.onClick}>${c.label}</button>` : html`<span class="crumb-current">${c.label}</span>`}
          `
        )}
      </div>

      ${error && html`<${ErrorBanner} message=${error} onRetry=${() => {}} retrying=${false} />`}

      ${!bc && html`
        <div class="lesson-grid">
          ${TOP_LEVEL.map(
            (t) => html`
              <div class="lesson-card" onClick=${() => (lessonsBreadcrumb.value = { domain: t.domain, language: null })}>
                <h3>${t.label}</h3>
                <p class="helptext">${t.desc}</p>
              </div>
            `
          )}
        </div>
      `}

      ${bc && !selected && loading && html`<p class="helptext">Loading&hellip;</p>`}

      ${bc && !selected && languages && html`
        <div class="lesson-grid">
          ${languages.map(
            (lang) => html`
              <div class="lesson-card" onClick=${() => (lessonsBreadcrumb.value = { domain: 'coding', language: lang })}>
                <h3>${lang}</h3>
                <p class="helptext">Browse ${lang} topics</p>
              </div>
            `
          )}
        </div>
      `}

      ${bc && !selected && items && html`
        <div class="lesson-grid">
          ${items.map(
            (item) => html`
              <div class="lesson-card" onClick=${() => (setSelected({ domain: item.domain, subtopic: item.subtopic, language: item.language }))}>
                <h3>${item.title}</h3>
                <${StatusBadge} status=${item.status} />
              </div>
            `
          )}
          ${items.length === 0 && html`<div class="helptext">No lessons here yet.</div>`}
        </div>
      `}

      ${selected && loading && html`<p class="helptext">Loading&hellip;</p>`}

      ${selected && lesson && html`
        <div class="card lesson-detail">
          <h2>${lesson.title}</h2>
          <div class="lesson-body">${lesson.body}</div>
        </div>
      `}
    </div>
  `;
}
