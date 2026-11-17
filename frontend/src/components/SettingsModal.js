import { html, useState } from '../lib.js';
import { apiBase } from '../store.js';

export function SettingsModal({ onClose }) {
  const [value, setValue] = useState(apiBase.value);

  const save = (e) => {
    e.preventDefault();
    apiBase.value = value.trim().replace(/\/+$/, '');
    onClose();
  };

  return html`
    <div class="modal-backdrop" onClick=${(e) => e.target === e.currentTarget && onClose()}>
      <div class="modal">
        <h3>API connection</h3>
        <p class="helptext" style="margin: 6px 0 14px;">
          Where the FastAPI backend is running. Change this if the frontend and backend are deployed on
          different machines or ports.
        </p>
        <form onSubmit=${save}>
          <input value=${value} onInput=${(e) => setValue(e.target.value)} placeholder="http://localhost:8000" />
          <div class="modal-actions">
            <button type="button" class="ghost" onClick=${onClose}>Cancel</button>
            <button type="submit" class="primary">Save</button>
          </div>
        </form>
      </div>
    </div>
  `;
}
