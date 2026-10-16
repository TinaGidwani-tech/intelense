# Intelense site

Static multi-page site in the approved homepage style (Montserrat, `#f5f5f5` canvas, Intelense brand gradient).

## Pages
`index.html` (home), `platform.html`, `modules.html`, one page per Ken module (`kenvision.html`, `kensafety.html`, `kenhome.html`, `kenagri.html`, `keniot.html`, `kenrobotics.html`, `kenvoice.html`), `industries.html`, `about.html`, `contact.html`.

Every page shares the same header (with a Modules dropdown and mobile menu), breadcrumbs and footer, so all pages link to each other.

## Editing
Page content lives in `build.py` (module and industry copy is in the `MODULES` and `INDUSTRIES` lists). Shared styles are in `assets/site.css`, scripts in `assets/`.

```
python3 site/build.py                 # regenerate site/*.html
python3 -m http.server -d site 8000   # preview at http://localhost:8000
```

The home page reuses sections from `design/mockups/homepage-monad-style.html`.

## Assets
- `assets/site.js`: mobile menu, sensor diagram, console clock, contact form
- `assets/cctv.js`: simulated camera feeds (swap a tile's `<canvas>` for real footage or screenshots when available)
- `assets/cursor-grid.js`: cursor-reactive grid in each page hero (`initCursorGrid(container, options)`)

The contact form is not connected to email yet.
