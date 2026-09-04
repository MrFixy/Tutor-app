import { html } from './lib.js';

// Minimal stroke icons (18x18, currentColor) -- no external icon font so the
// pilot build stays dependency-free. One function per glyph, each returning
// an <svg> htm node ready to drop into a template.

const base = (children) => html`
  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    ${children}
  </svg>
`;

export const IconHome = () =>
  base(html`<path d="M3 11.5 12 4l9 7.5" /><path d="M5.5 10v9a1 1 0 0 0 1 1H9a1 1 0 0 0 1-1v-4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v4a1 1 0 0 0 1 1h2.5a1 1 0 0 0 1-1v-9" />`);

export const IconChat = () =>
  base(html`<path d="M4 5.5h16a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H9l-4.5 3.5V16.5H4a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1Z" />`);

export const IconTarget = () =>
  base(html`<circle cx="12" cy="12" r="7.5" /><circle cx="12" cy="12" r="3.5" /><path d="M12 2.5v2.5M12 19v2.5M21.5 12H19M5 12H2.5" />`);

export const IconBook = () =>
  base(html`<path d="M4 5a2 2 0 0 1 2-2h6v18H6a2 2 0 0 1-2-2Z" /><path d="M20 5a2 2 0 0 0-2-2h-6v18h6a2 2 0 0 0 2-2Z" />`);

export const IconChecklist = () =>
  base(html`<path d="M9 6h11M9 12h11M9 18h11" /><path d="m3.5 6 1.2 1.2L6.5 5" /><path d="m3.5 12 1.2 1.2 1.8-2.2" /><path d="m3.5 18 1.2 1.2 1.8-2.2" />`);

export const IconChart = () =>
  base(html`<path d="M4 20V10M11 20V4M18 20v-7" /><path d="M2.5 20.5h19" />`);

export const IconGear = () =>
  base(html`<circle cx="12" cy="12" r="3" /><path d="M12 3v2.2M12 18.8V21M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M3 12h2.2M18.8 12H21M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6" />`);

export const IconLogoMark = () =>
  base(html`<path d="M4 20V13M10 20V6M16 20v-9M22 20H2" stroke="var(--accent-strong)" />`);
