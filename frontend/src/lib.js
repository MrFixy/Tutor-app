// No build step: Preact + htm loaded straight from esm.sh in the browser.
// Same component/hook model as React (useState, useEffect, ...), just
// without needing Node/npm on the machine running the pilot.
import { h, render } from 'https://esm.sh/preact@10.19.3';
import htm from 'https://esm.sh/htm@3.1.1';
import * as hooks from 'https://esm.sh/preact@10.19.3/hooks?deps=preact@10.19.3';

const html = htm.bind(h);

export { html, render, hooks };
export const { useState, useEffect, useRef, useMemo } = hooks;
