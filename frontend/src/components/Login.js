import { html, useState } from '../lib.js';
import { logIn } from '../store.js';

export function Login() {
  const [name, setName] = useState('');

  const submit = (e) => {
    e.preventDefault();
    if (name.trim().length < 2) return;
    logIn(name);
  };

  return html`
    <div class="login-wrap">
      <div class="login-card">
        <h1>Stats/Coding Tutor</h1>
        <p class="helptext">Pilot build -- enter any username, no password. The same name always resumes the same progress.</p>
        <form onSubmit=${submit}>
          <input
            autofocus
            placeholder="e.g. jordan"
            value=${name}
            onInput=${(e) => setName(e.target.value)}
            minlength="2"
          />
          <button class="primary" type="submit" disabled=${name.trim().length < 2}>Start</button>
        </form>
      </div>
    </div>
  `;
}
