import { html, useState } from '../lib.js';
import { api, ApiError } from '../api.js';
import { userId, sessionId } from '../store.js';
import { ErrorBanner } from './ErrorBanner.js';
import { SkeletonExercise, SkeletonTestRun } from './Skeleton.js';

const CODING_SUBTOPICS = [
  'syntax_basics',
  'data_structures',
  'control_flow',
  'functions',
  'recursion',
  'algorithms',
  'debugging',
  'oop',
  'other_coding',
];
const DIFFICULTIES = ['beginner', 'intermediate', 'advanced'];

function label(s) {
  return s.replaceAll('_', ' ');
}

// Preserve tabs in the plain <textarea> code editor instead of losing focus
// to the browser's default tab-to-next-field behaviour.
function handleTab(e, value, setValue) {
  if (e.key !== 'Tab') return;
  e.preventDefault();
  const { selectionStart: s, selectionEnd: en } = e.target;
  const next = `${value.slice(0, s)}    ${value.slice(en)}`;
  setValue(next);
  requestAnimationFrame(() => {
    e.target.selectionStart = e.target.selectionEnd = s + 4;
  });
}

export function CodePanel({ prefill }) {
  const [subtopic, setSubtopic] = useState(
    prefill?.domain === 'coding' && CODING_SUBTOPICS.includes(prefill.subtopic) ? prefill.subtopic : CODING_SUBTOPICS[0]
  );
  const [difficulty, setDifficulty] = useState(prefill?.difficulty || 'beginner');
  const [exercise, setExercise] = useState(null); // {question_id, prompt, starter_code}
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null); // CodeSubmitResponse
  const [error, setError] = useState(null);
  const [lastFailed, setLastFailed] = useState(null); // 'generate' | 'run' | null

  const generate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setExercise(null);
    try {
      const res = await api.codeGenerate({ user_id: userId.value, session_id: sessionId.value, subtopic, difficulty });
      setExercise(res.exercise);
      setCode(res.exercise.starter_code);
      setLastFailed(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not generate an exercise.');
      setLastFailed('generate');
    } finally {
      setLoading(false);
    }
  };

  const run = async () => {
    if (!exercise) return;
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.codeSubmit({ user_id: userId.value, question_id: exercise.question_id, source_code: code });
      setResult(res);
      setLastFailed(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not run that submission.');
      setLastFailed('run');
    } finally {
      setRunning(false);
    }
  };

  const retry = () => (lastFailed === 'run' ? run() : generate());

  return html`
    <div class="card">
      <h2>Coding exercise</h2>
      <div class="field-row" style="margin-top:12px;">
        <div class="field">
          <label>Subtopic</label>
          <select value=${subtopic} onChange=${(e) => setSubtopic(e.target.value)}>
            ${CODING_SUBTOPICS.map((s) => html`<option value=${s}>${label(s)}</option>`)}
          </select>
        </div>
        <div class="field">
          <label>Difficulty</label>
          <select value=${difficulty} onChange=${(e) => setDifficulty(e.target.value)}>
            ${DIFFICULTIES.map((d) => html`<option value=${d}>${d}</option>`)}
          </select>
        </div>
      </div>
      <button class="primary" style="margin-top:10px;" onClick=${generate} disabled=${loading}>
        ${loading ? html`<span class="spinner" />` : exercise ? 'Generate a new exercise' : 'Generate exercise'}
      </button>

      ${error &&
      html`<${ErrorBanner} message=${error} onRetry=${retry} retrying=${loading || running} style="margin-top:14px;" />`}

      ${loading && !exercise && html`<${SkeletonExercise} />`}

      ${exercise &&
      html`
        <div style="margin-top:18px;">
          <p style="white-space:pre-wrap;">${exercise.prompt}</p>
          <textarea
            class="code-editor"
            spellcheck="false"
            value=${code}
            onInput=${(e) => setCode(e.target.value)}
            onKeyDown=${(e) => handleTab(e, code, setCode)}
          />
          <button class="primary" style="margin-top:10px;" onClick=${run} disabled=${running || !code.trim()}>
            ${running ? html`<span class="spinner" />` : 'Run'}
          </button>

          ${running && !result && html`<${SkeletonTestRun} />`}

          ${result &&
          html`
            <div class="result-banner ${result.passed ? 'correct' : 'incorrect'}" style="margin-top:14px;">
              <b>${result.passed ? 'All tests passed.' : `${Math.round(result.score * 100)}% of tests passed.`}</b>
              ${result.feedback}
            </div>
            <table class="test-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Input</th>
                  <th>Expected</th>
                  <th>Actual</th>
                </tr>
              </thead>
              <tbody>
                ${result.results.map(
                  (r) => html`
                    <tr>
                      <td class="status ${r.passed ? 'status-pass' : 'status-fail'}">${r.passed ? 'Pass' : 'Fail'}</td>
                      <td>${r.stdin || html`<span class="helptext">(none)</span>`}</td>
                      <td>${r.expected_output}</td>
                      <td>${r.actual_output}${r.stderr ? html`<br /><span style="color:var(--danger)">${r.stderr}</span>` : ''}</td>
                    </tr>
                  `
                )}
              </tbody>
            </table>
          `}
        </div>
      `}
    </div>
  `;
}
