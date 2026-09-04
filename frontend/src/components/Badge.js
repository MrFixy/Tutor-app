import { html } from '../lib.js';

const DOMAIN_LABEL = { stats: 'Stats', coding: 'Coding' };

export function DomainBadge({ domain }) {
  if (!domain) return null;
  const cls = domain === 'coding' ? 'coding' : 'stats';
  return html`<span class="tag ${cls}">${DOMAIN_LABEL[domain] || domain}</span>`;
}

export function SubtopicBadge({ subtopic }) {
  if (!subtopic) return null;
  return html`<span class="tag neutral">${subtopic.replaceAll('_', ' ')}</span>`;
}

export function DifficultyBadge({ difficulty }) {
  if (!difficulty) return null;
  return html`<span class="tag difficulty">${difficulty}</span>`;
}

const STATUS_LABEL = { not_started: 'Not started', in_progress: 'In progress', mastered: 'Mastered' };
const STATUS_CLASS = { not_started: 'neutral', in_progress: 'difficulty', mastered: 'success' };

export function StatusBadge({ status }) {
  if (!status) return null;
  return html`<span class="tag ${STATUS_CLASS[status] || 'neutral'}">${STATUS_LABEL[status] || status}</span>`;
}

export function IntentTags({ domain, subtopic, difficulty }) {
  if (!domain && !subtopic && !difficulty) return null;
  return html`
    <div class="tag-row">
      <${DomainBadge} domain=${domain} />
      <${SubtopicBadge} subtopic=${subtopic} />
      <${DifficultyBadge} difficulty=${difficulty} />
    </div>
  `;
}
