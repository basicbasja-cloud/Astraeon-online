# Silver Scarf — full-body attack candidate v3

**Rejected by the user:** frame-three hand continuity, effect quality, and missing replaceable character parts. This is failure evidence only.

This rebuild responds to the rejected stationary-body animation. It adds a loading stance, torso coil, forward drive, knee/hip movement, rear-leg extension and coordinated recovery. It uses fresh original artwork guided by a newly authored joint study; it does not use any rejected game-branch character art.

The 256² GIF has eight timeline entries over 800 ms, with seven distinct body images. Delays are 80, 100, 100, 60, 60, 120, 140 and 140 ms: approximately ten pose entries per second, with a brief strike and held recovery. This is an authored cadence inspired by studied examples, not a verified universal Ragnarok rate.

## Review files

- `attack-full-body.gif`: normal-speed loop, dark background.
- `attack-full-body-slow.gif`: quarter-speed inspection.
- `attack-body-only.gif`: inspect body participation without the effect.
- `attack-transparent.png`: animated PNG with transparency.
- `attack-contact-sheet.png`: eight entries in order.
- `preview.html`: interactive one-shot/loop, trail toggle and pose inspection.
- `body-frames/`, `trail-frames/`, and corresponding strips: aligned RGBA layers.
- `attack-manifest.json`: explicit durations, anchors, effect landmarks and limitations.
- `browser-report.json` and browser screenshots: actual preview evidence.
- `assemble.py`: reproducible extraction, shared-scale registration and export. Requires Python, Pillow, NumPy and SciPy; run beside the two source PNGs.

Serve this directory with `python -m http.server 8770`, then open `http://localhost:8770/preview.html`. Browser QA used a server rooted one directory above it; adjust the URL in `browser-check.py` if replaying from another layout.

## Evidence and limits

Decoded GIF timing/endpoints and export bounds passed. Chromium normal one-shot, quarter-speed loop, trail toggle and interruption checks passed without page errors. The ready image is exactly reused at completion; stopping clears the effect. Contact sheet, body-only strike and browser captures were visually inspected.

This candidate was rejected by the user and is not an animation base. It has only one southeast/front-right facing. The body, clothing, head and sword are flattened together; only the trail is separate. It is not yet a complete eight-direction replaceable-part asset. The painted rear foot departs from the diagnostic rig's contact policy. Marker alignment does not prove physical balance or zero visual jitter. Small painted details may vary between poses. Actual game-scale contact, combat interruptions and integration remain untested.

## Provenance

The character design follows the user's supplied silver-haired, gold-caped swordsman concept. New character art and the independent blue-white crescent effect were generated with the image-generation tool. The art pass used a fresh turnaround and an original kinematic guide. Whole-strip layout correction separated sprites and restored unclipped sword pixels. No individual body repainting, pose tweening, separate per-pose scaling or frozen-leg replacement was used in assembly.

The study consulted ACT/timing documentation, roBrowserLegacy, an external community-rendered RO attack, Flare's eight-direction separate layers, Saint11 and SLYNYRD attack tutorials, body-mechanics instruction and a full fencing-kinematics paper. See the accompanying `full-body-attack-repair.md` for links and qualified findings. External study artwork is excluded from this package.
