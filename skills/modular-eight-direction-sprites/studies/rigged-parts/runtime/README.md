# Original modular attack — review package

This is an unapproved technical study, not a production release. The model's appearance, palm/finger contact, acting and trail still require review. It has one rig family and one attack, without a finished walk/idle family. Exact color has six source-pixel discrepancies; visibility/alpha/depth are checked separately.

Unpack the review ZIP and serve this directory with `python -m http.server 8772`; open `http://localhost:8772/`. The preview allows actual hair, torso, cape, sword and helmet swaps on one clock, plus eight views or the explicitly paired diagonal attack study map. Use the quarter-speed control and turn off FX for anatomy review.

Inspect `pose-guide-review.png` for all 64 source-derived guides, or `guides/<direction>/<index>-skeleton.png` and `-overlay.png`. Blue is anatomical right, orange left, yellow weapon and green declared contacts. `pose-guides.json` holds the source-known joints and limitations; it does not validate finished finger drawings. These guides are not extracted from third-party character pixels.

`package-manifest.json` hashes the shipped ZIP subset. `pipeline-receipt.json` describes the larger local build, including intermediate/raw files excluded from the ZIP. `check` on an intact full build is an integrity check of recorded evidence; it does not rerun the renderer. Use a fresh build to reproduce Blender/Chromium evidence.

Source and commands: https://github.com/basicbasja-cloud/Astraeon-online/tree/research/modular-sprites-full-body-2026-10-11/skills/modular-eight-direction-sprites
