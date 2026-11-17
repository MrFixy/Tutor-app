import { html, useState } from '../lib.js';
import { api, ApiError } from '../api.js';
import { userId, sessionId } from '../store.js';
import { ErrorBanner } from './ErrorBanner.js';
import { SkeletonQuiz } from './Skeleton.js';

const STATS_SUBTOPICS = [
  'descriptive_stats',
  'probability',
  'distributions',
  'hypothesis_testing',
  'p_values_significance',
  'confidence_intervals',
  'correlation_regression',
  'sampling',
  'other_stats',
];
const DIFFICULTIES = ['beginner', 'intermediate', 'advanced'];

function label(s) {
  return s.replaceAll('_', ' ');
}

export function QuizPanel({ prefill }) {
  const [subtopic, setSubtopic] = useState(
    prefill?.domain === 'stats' && STATS_SUBTOPICS.includes(prefill.subtopic) ? prefill.subtopic : STATS_SUBTOPICS[0]
  );
  const [difficulty, setDifficulty] = useState(prefill?.difficulty || 'beginner');
  const [count, setCount] = useState(3);
  const [questions, setQuestions] = useState(null); // [{question_id, stem, choices}]
  const [answers, setAnswers] = useState({}); // question_id -> {chosen_index, result}
  const [loading, setLoading] = useState(false);
  const [grading, setGrading] = useState(null); // question_id being submitted
  const [error, setError] = useState(null);
  const [lastFailedSubmit, setLastFailedSubmit] = useState(null); // question_id, or null if generate() failed

  const generate = async () => {
    setLoading(true);
    setError(null);
    setLastFailedSubmit(null);
    setQuestions(null);
    setAnswers({});
    try {
      const res = await api.quizGenerate({
        user_id: userId.value,
        session_id: sessionId.value,
        subtopic,
        difficulty,
        count,
      });
      setQuestions(res.questions);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not generate a quiz.');
    } finally {
      setLoading(false);
    }
  };

  const choose = (questionId, idx) => {
    if (answers[questionId]) return; // locked once answered
    setAnswers((a) => ({ ...a, [questionId]: { chosen_index: idx, result: null } }));
  };

  const submit = async (questionId) => {
    const chosen = answers[questionId]?.chosen_index;
    if (chosen === undefined) return;
    setGrading(questionId);
    setError(null);
    try {
      const res = await api.quizSubmit({ user_id: userId.value, question_id: questionId, chosen_index: chosen });
      setAnswers((a) => ({ ...a, [questionId]: { chosen_index: chosen, result: res } }));
      setLastFailedSubmit(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not grade that answer.');
      setLastFailedSubmit(questionId);
    } finally {
      setGrading(null);
    }
  };

  // The single error banner can follow either a failed generate() or a
  // failed submit() -- retry whichever one actually failed.
  const retry = () => (lastFailedSubmit !== null ? submit(lastFailedSubmit) : generate());

  return html`
    <div class="card">
      <h2>Quiz</h2>
      <div class="field-row" style="margin-top:12px;">
        <div class="field">
          <label>Subtopic</label>
          <select value=${subtopic} onChange=${(e) => setSubtopic(e.target.value)}>
            ${STATS_SUBTOPICS.map((s) => html`<option value=${s}>${label(s)}</option>`)}
          </select>
        </div>
        <div class="field">
          <label>Difficulty</label>
          <select value=${difficulty} onChange=${(e) => setDifficulty(e.target.value)}>
            ${DIFFICULTIES.map((d) => html`<option value=${d}>${d}</option>`)}
          </select>
        </div>
        <div class="field" style="max-width:100px;">
          <label>Questions</label>
          <input type="number" min="1" max="10" value=${count} onInput=${(e) => setCount(Number(e.target.value) || 1)} />
        </div>
      </div>
      <button class="primary" style="margin-top:10px;" onClick=${generate} disabled=${loading}>
        ${loading ? html`<span class="spinner" />` : questions ? 'Generate a new quiz' : 'Generate quiz'}
      </button>

      ${error &&
      html`<${ErrorBanner} message=${error} onRetry=${retry} retrying=${loading || grading !== null} style="margin-top:14px;" />`}

      ${loading && !questions && html`<div style="margin-top:14px;"><${SkeletonQuiz} count=${Math.min(count || 3, 5)} /></div>`}

      ${questions &&
      questions.map((q) => {
        const a = answers[q.question_id];
        const result = a?.result;
        return html`
          <div class="quiz-q">
            <div class="stem">${q.stem}</div>
            ${q.choices.map((choice, idx) => {
              let cls = 'choice';
              if (result) {
                if (idx === result.correct_index) cls += ' correct';
                else if (idx === a.chosen_index) cls += ' incorrect';
                cls += ' locked';
              } else if (a?.chosen_index === idx) {
                cls += ' selected';
              }
              return html`
                <label class=${cls} onClick=${() => !result && choose(q.question_id, idx)}>
                  <input type="radio" name="q${q.question_id}" checked=${a?.chosen_index === idx} readonly disabled=${!!result} />
                  ${choice}
                </label>
              `;
            })}
            ${!result &&
            html`
              <button
                class="primary"
                style="margin-top:6px;"
                disabled=${a?.chosen_index === undefined || grading === q.question_id}
                onClick=${() => submit(q.question_id)}
              >
                ${grading === q.question_id ? html`<span class="spinner" />` : 'Submit answer'}
              </button>
            `}
            ${result &&
            html`
              <div class="result-banner ${result.correct ? 'correct' : 'incorrect'}">
                <b>${result.correct ? 'Correct.' : 'Not quite.'}</b> ${result.feedback}
                <div style="margin-top:6px;">${result.explanation}</div>
              </div>
            `}
          </div>
        `;
      })}
    </div>
  `;
}
