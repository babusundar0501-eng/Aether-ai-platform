# BLACKTIDE

**Operation Dead Current** — a standalone, browser-based first-person shooter set in a storm-battered container port.

## Play

Open the GitHub Pages site after Pages is enabled, or run a local static server:

```bash
python -m http.server 8000
```

Then visit http://localhost:8000.

The game loads Three.js from jsDelivr and its display fonts from Google Fonts, so an internet connection is required.

## Controls

- **W A S D** — move
- **Mouse** — aim
- **Left click** — fire
- **Shift** — sprint
- **R** — reload
- **E** — activate a relay / extraction
- **Esc** — release mouse / pause

## Mission

Restore the three uplink terminals, neutralize hostile autonomous patrol units, and reach the extraction beacon.

## Project

BLACKTIDE is an original implementation. It is inspired by the broad atmosphere and mission structure of rainy tactical extraction shooters, not a copy of Saltline's source code or assets. All gameplay code and visuals in this repository were created for BLACKTIDE.

## GitHub Pages

The included workflow publishes the root directory to GitHub Pages whenever changes are pushed to the default branch. In repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions** if it is not already configured.
