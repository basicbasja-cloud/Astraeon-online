# Swordsman Pickup SW frame 08 — matte and SAM2 cutout studies

This is a single-frame draft derived from the same generated master as the previous cutout study. It is **not approved for production** and does not establish a 35-frame action or a working character factory.

## Changes and evidence

1. A bounded white-matte proposal treats the connected near-white exterior and four reviewed near-white gap seeds as transparent, then estimates alpha only on near-white pixels within three source pixels of that background. This clears the large white region between the arm and leg and three smaller gaps. It changes 3,829 source-edge pixels; 260 newly visible resampling pixels inherit the nearest prior slot label. [Old/new on gray and dark](matte-comparison.png) · [reviewed gap seeds](gap-seeds.png).
2. SAM2 tiny proposed head and weapon masks on the original 1254px source, with explicit positive/negative points and the pinned checkpoint. The selected head suggestion plus a limited fringe rule returns 27 prior HeadHair pixels to BodyCostume and assigns 50 BodyCostume pixels to HeadHair. [Head comparison](head-comparison.png).
3. The selected weapon suggestion assigns 35 earlier Weapon pixels to BodyCostume and 58 earlier BodyCostume pixels to Weapon. It visually excludes much of the boot overlap and retains the visible pommel, but small residual pixels around the hidden handle remain. [Weapon comparison](weapon-comparison.png).
4. The final visible BodyCostume, HeadHair and Weapon layers recompose byte-for-byte to the **new matte master**, not to the original white image. [Single-frame slot visibility GIF](slot-toggle.gif) is a diagnostic, not animation or a valid swap. Two focused tests passed, including exact RGBA recomposition.

The white-background recomposition of the source-sized matte differs from the original by at most 5 channel values; around 1.30 million pixels differ, largely from treating near-white background as transparent and recompositing on pure white. This is not pixel identity or proof of correct alpha on dark backgrounds. Bright hair, sword highlights and the matte near edges still require visual review. The 260 nearest-label assignments, SAM masks, scarf/neck boundary, hilt/hand occlusion and possible leftover enclosed gaps also require manual review. The source image, production store and runtime were not changed.

## Reproduction

Raw masks, prompt coordinates, model scores and checkpoint SHA are in `authoring/characters/factory-v3/patch-0.0.1/research/swordsman-pickup-sw08-sam-20261029/`. The SAM2 checkpoint is `sam2.1_hiera_tiny.pt` with SHA-256 `7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69`; the existing `astraeon-cutouts` environment was used on CPU. Outputs of each step are retained under `review/swordsman-pickup-sw08-unmatte-v3-20261029/`, `review/swordsman-pickup-sw08-sam-head-v3-20261029/`, and `review/swordsman-pickup-sw08-sam-weapon-20261029/` within the patch authoring directory. Use fresh destinations:

```sh
python3 tools/character_factory_v3/propose_pickup_sw08_unmatte.py --output <matte-dir>
python3 tools/character_factory_v3/refine_pickup_sw08_sam_head.py --mask authoring/characters/factory-v3/patch-0.0.1/research/swordsman-pickup-sw08-sam-20261029/head/masks/2.png --base <matte-dir> --output <head-dir>
python3 tools/character_factory_v3/refine_pickup_sw08_sam_weapon.py --mask authoring/characters/factory-v3/patch-0.0.1/research/swordsman-pickup-sw08-sam-20261029/weapon/masks/2.png --base <head-dir> --output <weapon-dir>
python3 -m unittest discover -s tests/character_factory_v3 -p test_pickup_sw08_matte_and_sam.py -v
```

To reproduce SAM proposals, use `propose_pickup_sw08_sam_head.py` and `propose_pickup_sw08_sam_weapon.py` in the existing SAM2 environment with `--checkpoint <checkpoint> --output <fresh-dir>`. Scores are model confidence, not semantic approval.

Hidden body/handle surfaces, an occluding hand, a different head or sword, all other frames and directions, character-scale stability, in-game transitions and gameplay remain open. This frame still does not count as a completed action or playable Swordsman.
