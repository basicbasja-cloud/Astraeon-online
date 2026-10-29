# Swordsman first — checkpoint 2026-10-29

The immediate goal is the preserved tall male Swordsman, with all 19 configured actions, before continuing the remaining characters. The overall 0.0.1 scope is unchanged. Its existing BasicAttack is a technical import with open visual and semantic defects; the other actions cannot be counted as finished merely because motion guides exist.

## NW BasicAttack frame 15

The prior underpaint proposal leaves a small detached blade-edge fragment in BodyCostume when Weapon is hidden. This single-frame candidate reassigns five identified edge pixels to Weapon. The original sword-on composition remains byte-identical; the no-weapon preview changes only those five pixels. Inputs and the original baseline remain unchanged. Two focused tests passed. The candidate, source hashes and preview are retained under `authoring/characters/factory-v3/patch-0.0.1/review/swordsman-nw15-detached-blade-cleanup-20261029/` and can be reproduced using `tools/character_factory_v3/propose_sword_nw15_detached_blade_cleanup.py --output <fresh-directory>`.

This is one small repair on one frame, not a completed cutout, interchangeability approval, animation or playable package. Other mask edges and hidden surfaces, foot contact and scale, other frames and actions, variants, trail, transitions and actual gameplay still need review and production. No runtime assets were replaced.
