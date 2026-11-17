import { html } from '../lib.js';

// Phase 6 / Week 14: "no loading skeletons, only spinners + disabled
// buttons" was called out directly as a slow-perceived-latency risk
// (Week 13 brief) once /chat, quiz-generate, and code-generate are all
// waiting on a local Ollama cold model. These stand in the exact shape
// of what's about to render so the wait doesn't read as "did this hang?"

export function SkeletonQuiz({ count = 3 }) {
  return html`
    <div>
      ${Array.from({ length: count }).map(
        () => html`
          <div class="skeleton-quiz-q">
            <div class="skeleton skeleton-line mid" style="height:15px;"></div>
            <div class="skeleton skeleton-choice"></div>
            <div class="skeleton skeleton-choice"></div>
            <div class="skeleton skeleton-choice"></div>
            <div class="skeleton skeleton-choice"></div>
          </div>
        `
      )}
    </div>
  `;
}

export function SkeletonExercise() {
  return html`
    <div style="margin-top:18px;">
      <div class="skeleton skeleton-line" style="height:14px;"></div>
      <div class="skeleton skeleton-line" style="height:14px; width:90%;"></div>
      <div class="skeleton skeleton-line short" style="height:14px;"></div>
      <div class="skeleton" style="height:220px; border-radius: var(--radius); margin-top:10px;"></div>
    </div>
  `;
}

export function SkeletonTestRun() {
  return html`
    <div style="margin-top:14px;">
      <div class="skeleton skeleton-line" style="height:38px; border-radius: var(--radius); width:100%;"></div>
      <div class="skeleton" style="height:110px; margin-top:12px;"></div>
    </div>
  `;
}

export function SkeletonMastery({ count = 4 }) {
  return html`
    <div>
      ${Array.from({ length: count }).map(
        () => html`
          <div class="mastery-row">
            <div class="name">
              <div class="skeleton skeleton-line" style="height:13px; width:150px; margin-bottom:6px;"></div>
              <div class="skeleton skeleton-line" style="height:11px; width:80px;"></div>
            </div>
            <div class="bar-wrap"><div class="skeleton" style="width:100%; height:100%; border-radius:100px;"></div></div>
            <div class="pct"></div>
          </div>
        `
      )}
    </div>
  `;
}
