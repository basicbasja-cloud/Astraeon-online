# Original motion lab

A fresh engineering study for eight-direction modular animation. Every shape and pose is newly authored. No character image, atlas, rig output, or animation asset from Astraeon branches is loaded. The mannequin is diagnostic geometry, not a proposed final art style or approved production seed.

From the skill directory:

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory studies/motion-lab
```

Open `http://127.0.0.1:8765/`. Choose idle/walk/attack, normal/quarter speed, pause/scrub, and appearance changes. Camera yaw changes view selection; pitch demonstrates the fresh geometry's projection. All eight panels use one pose. Compare continuous, eight-pose diagnostic, and 30/60 FPS targets while ground travel remains continuous. The lower strip is a pose-design diagnostic, not an exported sprite sheet.

Checks:

```bash
node studies/motion-lab/motion.test.mjs
python studies/motion-lab/browser-check.py
node studies/motion-lab/export-study.mjs /tmp/sprite-export-study
```

The browser check requires Python Playwright, Chromium at `/usr/bin/chromium`, and the server above. Environment-specific paths can be adjusted. The direct Node invocation runs the `node:test` suite without spawning a test-runner child in restricted environments.

- [Browser measurement report](evidence/browser-report.json)
- [Native exported walk samples](evidence/exported-walk.png)
- [Independent part replacement/reconstruction](evidence/exported-swaps.png)
- [Export/reconstruction report](evidence/export-report.json)

The exporter writes freshly rasterized part PNGs, compressed depth maps, reference frames, timelines, contact metadata and a manifest to its explicit output directory. It requires Node built-ins only. The canonical walk/attack span all eight directions at a 60 FPS source-pose target. Other variants deliberately cover subsets. Empty equipment frames remain timeline entries. The generated package is an original diagnostic dataset, not a shippable character asset.

The browser check regenerates walk/attack/camera/held-pose/30 FPS/60 FPS screenshots under `evidence/`. The downloadable local research archive includes these captures; the research branch retains compact native export previews and reports.

See [motion findings](../../references/motion-study.md) for measured drift and limits. Original solver code uses a plane-constrained triangle construction; third-party implementation code was not imported. Research references remain credited in the package source catalog.

Limits: orthographic diagnostic projection, approximate browser-preview face sorting, flat-foot contacts, one body family, simple looped actions, no state-transition controller, no actual game integration, and no user-approved drawn animation. The offline exporter uses per-pixel depth for opaque geometry; it does not validate antialiased/translucent production composition. Correct clocks and bone lengths cannot establish artistic mastery.
