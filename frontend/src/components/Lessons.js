import { html, marked, useState, useEffect } from '../lib.js';
import { lessonsBreadcrumb } from '../store.js';
import { ErrorBanner } from './ErrorBanner.js';

function humanizePhaseSlug(slug) {
  const [, name = slug] = slug.match(/^\d+-([\s\S]+)$/) || [];
  return name.replaceAll('-', ' ');
}

const VOLUMES = [
  { id: 1, title: 'Foundations', subtitle: 'Math, tooling, and classical machine learning', from: 0, to: 2 },
  { id: 2, title: 'Deep Learning', subtitle: 'Networks, vision, and speech', phases: [3, 4, 6] },
  { id: 3, title: 'Language', subtitle: 'NLP foundations and the transformer', phases: [5, 7] },
  { id: 4, title: 'Large Language Models', subtitle: 'Generation, reinforcement, pretraining, and engineering', from: 8, to: 11 },
  { id: 5, title: 'Agents', subtitle: 'Multimodality, protocols, autonomy, and swarms', from: 12, to: 16 },
  { id: 6, title: 'Production', subtitle: 'Infrastructure, safety, and capstones', from: 17, to: 19 },
];

function phasesForVolume(volume, curriculum) {
  return (curriculum || []).filter((phase) => {
    return volume.phases?.includes(phase.number) || (phase.number >= volume.from && phase.number <= volume.to);
  });
}

function volumeRange(volume) {
  if (volume.phases) return volume.phases.map((phase) => String(phase).padStart(2, '0')).join('  ');
  return `${String(volume.from).padStart(2, '0')}—${String(volume.to).padStart(2, '0')}`;
}

export function Lessons() {
  const bc = lessonsBreadcrumb.value;
  const [curriculum, setCurriculum] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);
  const [lesson, setLesson] = useState(null);

  useEffect(() => {
    setError(null);
    setLoading(true);
    fetch('./content/curriculum.json')
      .then((response) => {
        if (!response.ok) throw new Error('Could not load the curriculum.');
        return response.json();
      })
      .then(setCurriculum)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    setSelected(null);
    setLesson(null);
  }, [bc?.volumeId, bc?.phaseSlug]);

  useEffect(() => {
    if (!selected) {
      setLesson(null);
      return;
    }
    setError(null);
    setLoading(true);
    fetch(`./content/phases/${selected.phaseSlug}/${selected.slug}.md`)
      .then((response) => {
        if (!response.ok) throw new Error('Could not load that lesson.');
        return response.text();
      })
      .then((text) => {
        const [, frontmatter, body] = text.split('---', 3);
        const title = frontmatter?.match(/^title:\s*(.+)$/m)?.[1] || selected.title;
        setLesson({ title: title.replace(/^['"]|['"]$/g, ''), body: body?.trim() || text });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [selected?.phaseSlug, selected?.slug]);

  const crumbs = [];
  crumbs.push({ label: 'Guides', onClick: () => (lessonsBreadcrumb.value = null) });
  if (bc?.volumeId) {
    const volume = VOLUMES.find((item) => item.id === bc.volumeId);
    crumbs.push({ label: 'AI Engineering', onClick: () => (lessonsBreadcrumb.value = null) });
    crumbs.push({ label: volume?.title, onClick: () => (lessonsBreadcrumb.value = { volumeId: bc.volumeId }) });
  }
  if (bc?.phaseSlug) {
    crumbs.push({ label: humanizePhaseSlug(bc.phaseSlug) });
  }
  if (selected) crumbs.push({ label: selected.title });

  return html`
    <div class="content">
      <div class="eyebrow"><span class="dot" />AI ENGINEERING <b>Self-paced curriculum</b></div>
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
        <section class="course-intro">
          <div class="course-intro-copy">
            <span class="course-kicker">THE CURRICULUM</span>
            <h1>Course <em>Volumes</em></h1>
            <p>A structured journey from fundamentals to real-world systems.</p>
          </div>
          <div class="course-stats" aria-label="Course statistics">
            <span><b>▣</b><strong>6</strong><small>volumes</small></span>
            <span><b>▱</b><strong>20</strong><small>phases</small></span>
            <span><b>▥</b><strong>1</strong><small>journey</small></span>
          </div>
          <div class="course-scribble" aria-hidden="true">Learn<br />Build<br />Grow</div>
        </section>

        <div class="volume-board">
          ${VOLUMES.map(
            (volume) => html`
              <div class="volume-card volume-card-${volume.id}" onClick=${() => (lessonsBreadcrumb.value = { volumeId: volume.id })} role="button" tabIndex="0">
                <div class="volume-card-top"><span class="volume-card-number">${String(volume.id).padStart(2, '0')}</span><span class="volume-card-label">VOLUME ${String(volume.id).padStart(2, '0')}</span><span class="volume-card-open">→</span></div>
                <h3>${volume.title}</h3>
                <p>${volume.subtitle}</p>
                <span class="volume-card-range">${volumeRange(volume)}</span>
                <span class="volume-card-mark" aria-hidden="true">${['∑', '◉', '•••', '✦', '⊙', '↑'][volume.id - 1]}</span>
              </div>
            `
          )}
        </div>
      `}

      ${bc?.volumeId && !bc?.phaseSlug && curriculum && html`
        <div class="chapter-header">
          <span class="section-kicker">VOLUME ${String(bc.volumeId).padStart(2, '0')}</span>
          <h1>${VOLUMES.find((volume) => volume.id === bc.volumeId)?.title}</h1>
          <p class="helptext">${VOLUMES.find((volume) => volume.id === bc.volumeId)?.subtitle}</p>
        </div>
        <div class="chapter-list">
          ${phasesForVolume(VOLUMES.find((volume) => volume.id === bc.volumeId), curriculum).map(
            (phase) => html`
              <div class="chapter-row" onClick=${() => (lessonsBreadcrumb.value = { volumeId: bc.volumeId, phaseSlug: phase.slug })} role="button" tabIndex="0">
                <span class="chapter-number">${String(phase.number).padStart(2, '0')}</span>
                <span class="chapter-main"><strong>${phase.title}</strong><span>Open phase topics</span></span>
                <span class="chapter-lessons">${phase.lessons.length} lessons</span>
                <span class="chapter-arrow">→</span>
              </div>
            `
          )}
        </div>
      `}

      ${bc?.phaseSlug && !selected && curriculum && html`
        <div class="chapter-header">
          <span class="section-kicker">CHAPTER ${String(curriculum.find((phase) => phase.slug === bc.phaseSlug)?.number || '').padStart(2, '0')}</span>
          <h1>${curriculum.find((phase) => phase.slug === bc.phaseSlug)?.title}</h1>
          <p class="helptext">Choose a topic to open its lessons.</p>
        </div>
        <div class="lesson-grid topic-grid">
          ${(curriculum.find((phase) => phase.slug === bc.phaseSlug)?.lessons || []).map(
            (item) => html`
              <div class="lesson-card" onClick=${() => setSelected({ ...item, phaseSlug: bc.phaseSlug })}>
                <h3>${item.title}</h3>
                <p class="helptext">Lesson ${String(item.order).padStart(2, '0')}</p>
              </div>
            `
          )}
        </div>
      `}

      ${selected && loading && html`<p class="helptext">Loading&hellip;</p>`}

      ${selected && lesson && html`
        <div class="card lesson-detail">
          <h2>${lesson.title}</h2>
          <div class="lesson-body" dangerouslySetInnerHTML=${{ __html: marked.parse(lesson.body) }} />
        </div>
      `}
    </div>
  `;
}
