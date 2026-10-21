# Handoff: replace simulated camera feeds with real footage

Goal: swap the procedural canvas CCTV scenes for photorealistic, free-licence footage (Pexels / Unsplash) with subtle, enterprise-grade analytics overlays.

## How the site uses footage
- Put a still (.jpg/.webp, ~1600x900, 16:9) or a short loop (.mp4) in `site/assets/footage/`.
- Add an entry to `site/assets/footage/feeds.json` keyed by scene name. See `_example` there for the format. Coordinates are fractions of the frame (0 to 1).
- `build.py` (`swap_feeds`) then replaces every `<canvas class="cctv" data-scene="NAME">` with the real frame plus overlays (corner-bracket boxes, dashed zones, count lines, small label chips, camera name and live clock).
- Build: `python3 site/build.py`, then the inline copy for the artifact: `python3 site/build.py --inline <scratchpad>/site-art`. The inline copy also copies `assets/footage`, so pass the footage files in the Artifact `files` map.
- Artifact URL: https://claude.ai/artifact/JoNDvG6KNuVXyhJiPEXkU8 (publish the inline `index.html` with `root` set to the inline folder).

## Scenes to source, in priority order
1. `store`: fixed high-angle view of a bright retail store or supermarket with shoppers (KenVision hero and dashboard, home page).
2. `dock`: warehouse loading dock with workers in hi-vis and a forklift (KenSafety).
3. `porch`: front door or porch of a house, ideally with a person or package (KenHome).
4. Optional: `whse` (warehouse aisle), `living` (living room), `drive` (driveway at night).

## Rules
- Use free-licence sources only: Pexels or Unsplash. Record the photographer and source URL in `feeds.json` (add `credit` and `source` fields).
- Choose images that look like a fixed ceiling or corner camera, not POV, close-up or blurred-background shots. Avoid images with baked-in UI overlays.
- Place the overlay boxes by looking at each image. Keep them sparse (3 to 5 boxes per frame).
- Once a scene is real, change its "Simulated camera feed" captions (`demo-note`) to "Example footage and data".
- Then run the crawl checks, publish the artifact and commit to `claude/website-design-inspiration-kp9nd6`.
