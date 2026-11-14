# BLACKTIDE — Operation Breakwater

A standalone, original browser-based first-person shooter set in a rain-soaked container port. Built with Three.js and vanilla JavaScript.

## Play locally

**Requirements:** a modern desktop browser and Python 3 (or another static file server). Internet is required to load the Three.js module and web fonts from their CDNs.

1. Download or clone this repository.
2. Run `run.bat` on Windows, or start a static server:
   ```bash
   python -m http.server 8000
   ```
3. Open [http://localhost:8000](http://localhost:8000).
4. Select Deploy, read the briefing, then enter the port.

Opening `index.html` directly with `file://` may block JavaScript modules. Use the local server.

## Controls

| Input | Action |
|---|---|
| WASD | Move |
| Mouse | Aim |
| Left click | Fire |
| R | Reload |
| E | Activate relay / extract |
| Shift | Sprint |
| Space | Jump |
| Esc | Pause |

## Mission

Restore all three uplink relays in the container yard, survive autonomous Hound and recon drone patrols, and reach the extraction vessel.

## Technology

- Three.js 0.160 (loaded from jsDelivr)
- Vanilla JavaScript ES modules
- Procedural geometry, lighting, fog, rain, weapon view model, enemy AI and HUD
- No account, backend, API key, build step or install dependencies

## Project structure

- `index.html` — game interface and screens
- `styles.css` — responsive cinematic HUD and menus
- `game.js` — 3D world, controls, weapons, enemies and mission logic
- `run.bat` — quick local launch on Windows

## Credits and originality

BLACKTIDE is an independent prototype. Saltline was used only as a high-level reference for rainy port atmosphere and objective-based FPS pacing. This repository does not include Saltline's source code, assets, or branding.
