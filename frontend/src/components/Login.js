import { html, useState } from '../lib.js';
import { logIn } from '../store.js';
import { IconLogoMark } from '../icons.js';

export function Login() {
  const [name, setName] = useState('');

  const submit = (event) => {
    event.preventDefault();
    if (name.trim().length < 2) return;
    logIn(name);
  };

  return html`
    <div class="login-wrap">
      <div class="login-card">
        <div class="login-mark"><${IconLogoMark} /></div>
        <h1>AI Engineering Tutor</h1>
        <p class="helptext">Enter a username to open your AI Engineering learning workspace. No password is required in this pilot.</p>
        <form onSubmit=${submit}>
          <input autofocus placeholder="e.g. alex" value=${name} onInput=${(event) => setName(event.target.value)} minlength="2" />
          <button class="primary" type="submit" disabled=${name.trim().length < 2}>Start learning</button>
        </form>
      </div>
    </div>
  `;
}
