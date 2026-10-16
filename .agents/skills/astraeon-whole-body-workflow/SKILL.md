---
name: astraeon-whole-body-workflow
description: Use the audited Scenario, SPA and img2game2d adapters for Astraeon whole-body sprites, preserving source RGBA, explicit clocks, and user-reviewed anatomy.
---

Use the installed `.agents/skills/scenario-sprite-animation`, `spa`, and `img2game2d` skills only within the user's current requirements. These are project-local pinned installations. `UPSTREAM.json` records sources; img2game2d has a disclosed one-line alpha fix in LOCAL-PATCHES.json.

The user's body/head/weapon/trail split overrides default limb decomposition. Body includes all knees, thighs, hands, boots and costume. Never use the old segmented rig or procedural continuous shear as final art. Do not mirror this asymmetric character, quantize painted art to pixel art, center crouches by their bounding boxes, or shift individual frames to hide planted-foot motion. Source rigs are pose guides only.

Read CURRENT_HANDOFF.md and the latest non-production decisions. In particular v56's old appearance approval was superseded by the user's cut-body complaint; v58 still fails motion/contact and its manual head masks retain costume fragments. Do not approve head swaps from an exact technical recompose alone.

Scenario local helpers can build grid guides and draft requests. A guide does not establish registration; cycle_sheets.py's default mirroring/registering/palette/key pipeline is not approved here. Provider generation requires the actual Scenario connection and any spend authorization. Do not substitute credentials or assume installing skill files connects a cloud account.

For local pre-separated frame tooling:

- `python tools/whole-body-toolchain.py pack --clip <four-slot.json> --frames <ordered-full-PNG-directory> --out <fresh-output>` invokes patched img2game2d packing at scale1, verifies every RGBA cell, and carries exact per-frame durations from the source clip. It also reads img2game2d's local state gate; a stopped state is not bypassed. This diagnostic import does not mark the full production checklist complete.
- `python tools/whole-body-toolchain.py editable --clip <four-slot.json> --out <fresh-output> --spa <spa-executable> --aseprite <aseprite-executable>` uses supported SPA operations to build an editable RGBA file and export all frames. Frame Numbers are1based. Inspect the saved file and compare actual exported pixels and durations. Changing equipment depth per-frame requires explicit physical passes and is refused by this simpler exporter.

Both operations retain art as unapproved. They cannot generate missing poses or prove anatomy, hand grips, occluded joints, weapon trails or arbitrary-character head swaps. Continue actual image/motion review and preserve negative evidence.
