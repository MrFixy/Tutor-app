import { render, html } from './lib.js';
import { App } from './components/App.js';

render(html`<${App} />`, document.getElementById('root'));
