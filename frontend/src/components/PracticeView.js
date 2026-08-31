import { html, useState, useEffect } from '../lib.js';
import { practicePrefill } from '../store.js';
import { QuizPanel } from './QuizPanel.js';
import { CodePanel } from './CodePanel.js';

export function PracticeView() {
  const prefill = practicePrefill.value;
  const [tab, setTab] = useState(prefill?.domain === 'coding' ? 'code' : 'quiz');

  // Only honor the incoming prefill once per handoff, then clear it so
  // switching subtabs later doesn't keep resetting the form.
  useEffect(() => {
    if (prefill) practicePrefill.value = null;
  }, []);

  return html`
    <div class="content">
      <h1>Practice</h1>
      <p class="helptext" style="margin-bottom:18px;">
        Stats questions come as multiple choice. Coding exercises run against real test cases.
      </p>
      <div class="subtabs">
        <button class=${tab === 'quiz' ? 'active' : ''} onClick=${() => setTab('quiz')}>Quiz (stats)</button>
        <button class=${tab === 'code' ? 'active' : ''} onClick=${() => setTab('code')}>Code (coding)</button>
      </div>
      ${tab === 'quiz' ? html`<${QuizPanel} prefill=${prefill} />` : html`<${CodePanel} prefill=${prefill} />`}
    </div>
  `;
}
