# Frontend Toolchain

This frontend now uses a real Node build pipeline (`Vite + Tailwind + PostCSS`) and outputs static assets for Flask templates.

## Directory Layout

- `frontend/src/styles/app.css`
  - Tailwind entry + project custom styles
- `frontend/src/js/*.js`
  - Page entry modules (`portal`, `admin_list`, `admin_edit`, `print`, `core`)
- `frontend/vite.config.js`
  - Multi-entry build config
  - Output target: `../static/dist`
- `static/dist/*`
  - Build artifacts consumed by Flask templates

## Commands

Run inside `frontend/`:

- Install dependencies:
  - `npm install`
- Development mode:
  - `npm run dev`
- Production build:
  - `npm run build`
- Preview built assets:
  - `npm run preview`
- Lint JavaScript:
  - `npm run lint`
- Format source files:
  - `npm run format`

## Flask Template Integration

`templates/base.html` loads:

- `static/dist/app.css`
- `static/dist/core.js`

Each page template loads its own entry:

- `portal.html` -> `static/dist/portal.js`
- `admin_list.html` -> `static/dist/admin_list.js`
- `admin_edit.html` -> `static/dist/admin_edit.js`
- `print.html` -> `static/dist/print.js`

## Notes

- DingTalk JSAPI is still loaded from CDN in template because it is runtime platform-specific.
- PDF preview uses `pdfjs-dist` bundled by Vite.
- Vite is configured to disable sourcemaps in production build output.

