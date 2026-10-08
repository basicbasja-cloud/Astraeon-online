# True modular character authoring: Swordsman Male

Status: `DEV_ONLY / REQUIRES_OWNER_VISUAL_REVIEW`

This package is an independent painted 2D authoring candidate for the existing
ASTRAEON Swordsman identity. The supplied eight-view Swordsman artwork is an
identity/style reference only. Every new authoring layer is drawn from the
shared pose and local geometry; no finished character is erased, segmented, or
used as a source layer.

Existing Swordsman masters, generated atlases, and gait studies remain intact.
The previous `tools/build-swordsman-production.py` route is preserved as
historical evidence; it is deprecated as an authoring source for this pipeline.
No old extracted layer pixels are inputs to this package.

## Rebuild

From the repository root:

```sh
python3 tools/build_true_modular_swordsman.py \
  --blueprint authoring/characters/true-modular/swordsman/male/blueprint.json \
  --out /tmp/astraeon-swordsman-male-dev \
  --clips Idle,Walk
python3 -m unittest discover -s tests -p "test_true_modular_character_engine.py"
```

The paint renderer is a replaceable style plug-in. The generic engine owns
blueprint validation, the canonical direction order, shared pose/frame/root/
socket registration, full-canvas raster baking, per-layer/per-clip atlas
packing, and per-frame composition. To extend it to another career, add a
career-specific blueprint and renderer with original per-layer geometry, then
run the same engine; no new runtime renderer is needed. A female variant needs
its own authored proportions and surfaces; it is not scaled from the male.

## Authoring parts and runtime compilation

| Authoring source | Runtime slot | Responsibility |
| --- | --- | --- |
| BodyCore | BaseBody | skin anatomy, limbs, hands and feet |
| HeadBase + Face | BaseBody | skull/jaw/neck registration and features |
| HairBack + HairFront | Hair | rear mass, cap/fringe and hairstyle swaps |
| Outfit | Outfit | fitted clothing and armor surfaces |
| Weapon | Weapon | cosmetic blade attached at anatomical right hand |
| Cape + BackAccessory | BackAccessory | separate cloth and optional rear cosmetic |
| Headgear | Headgear | optional cosmetic attachment |
| CosmeticFX | CosmeticFX | optional future cosmetic effect |

All layer frames are emitted from one `Clip / Direction / Frame` pose and one
full 320×320 canvas, with root (160,264) and the same socket map. Rear-facing
hair and weapon ordering can change by direction without re-registering parts.
Empty optional layers remain transparent.

The proof covers `Hair A → Hair B`, `Outfit A → Outfit B`,
`Weapon A → Weapon B`, and `Weapon → Hidden` in all eight directions from
shared direction poses. The validator checks that only intended layers change
and unaffected layers remain byte-identical in each direction. No per-direction
offsets are used.

## Current visual and runtime gates

- Built artwork: `Idle` (8 frames/direction) and `Walk` (16 frames/direction),
  across S, SW, W, NW, N, NE, E and SE.
- Baked authoring atlases: one 320px PNG per authoring layer and clip;
  direction rows follow the canonical order and frame columns follow each
  clip's timing. They require reviewed compilation into the runtime's 160px
  schema and remain `DEV_ONLY` until the owner reviews them.
- Swordsman release contract: 16 actions defined in the blueprint. `Sit` is
  supported but optional; `Blink` is Mage-only. The inspected Ragnarok sheet
  pages do not publish action labels or counts.
- Run, Sprint, BasicAttack, SkillAction, CastChannel, CastRelease, Guard, Dash,
  Hit, Death, Interact, Pickup, ItemUse and Respawn are specified but not yet
  painted by this checkpoint.
- Runtime integration is pending. Existing `modular-sprites.js` and the
  appearance/equipment separation are preserved. Existing `wardrobe.js`
  currently rejects any missing clip from its global 18-clip list; change that
  gate to use the class-specific release contract before loading this package.
- This output is a production-method proof. It is not owner-approved art and
  does not yet satisfy final gameplay visual review.

See `review/` for the eight-direction, layer, cosmetic-swap, gait, and
gameplay-size review images generated from this package.
