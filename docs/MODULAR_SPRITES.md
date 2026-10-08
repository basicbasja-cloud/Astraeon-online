# Modular painted character sprites 0.1

This is a production contract and a development proof. Final characters remain
painted/stylized **2D**. `sprite-preview.html` shows geometric markers only:
`DEV_ONLY`, `PLACEHOLDER`, `NOT_FINAL_ART`. They are never selected by normal
player calls. The existing Warrior/Mage/Ranger visuals and gameplay remain.

## Registration and shared pose

Direction order is **S, SW, W, NW, N, NE, E, SE** everywhere in this pipeline.
Legacy directional and v4 locomotion tables use a different order; do not index
those tables with these row numbers. The adapter projects a heading and resolves
a direction by name, without mirroring or changing weapon hands.

`canvas` stores `frameWidth`, `frameHeight`, `rootAnchorX`, `rootAnchorY`, and
`referenceHeight`. The proof inherits 320×320, root (160,264), reference height 176
from `world/v3/warrior-painted-locomotion.json`. These are the existing painted
registration, not an arbitrary replacement size. An approved character can declare
its own reviewed registration; every one of its parts must use that same canvas.
The root is a fixed ground reference, not a per-frame lowest alpha pixel.

A clip owns its `durations` in milliseconds, loop policy, and eight directional
pose sequences. Each pose owns `frameIndex`, sockets, and optional draw order.
Parts reference that pose by frame ID; they have **no separate clock, canvas,
root, sockets or timing overrides**. `sample()` returns animation, direction,
frame index, duration, canvas, sockets and all selected part atlas references.
Clips have different counts/timing. Non-looping actions hold their last frame.

Every pose declares `root`, `head`, `hand_R`, `hand_L`, `back`, `waist` in frame
pixels. `hand_R` means anatomical right in every view. Extra named sockets are
allowed. Every modular image is already rendered into the complete shared canvas;
do not translate a weapon again by its socket during composition. Sockets guide
source rendering and expose registered locations for debug/VFX attachments.

## Layers, appearances and sorting

Required logical layers: `BaseBody`, `Hair`, `Outfit`, `Weapon`, `Headgear`,
`BackAccessory`. Supported optional layers: `Face`, `Offhand`, `Cape`, `CosmeticFX`,
`Aura`, `ShoulderAccessory`. A no-hat/no-back variant supplies transparent frames.

`slots` map render slots to logical layers, `defaultParts` select part IDs, and
`parts` contain each part's slot and frame references. Swap an appearance with
`{Weapon: 'weapon-alt'}`; incompatible part/slot pairs fail. Optional slots can be
hidden with `null`; required logical layers stay present. Appearance IDs are
presentation data. This foundation does not change equipment stats or save data.

`drawOrder` lists each slot once, back to front. It can be overridden for a
whole directional sequence or an individual pose. To split an occluded weapon,
add a `WeaponBack` slot mapped to logical `Weapon`, keep `Weapon` for its front
section, and author both into the same coordinate contract. This needs no
skeletal runtime renderer. The tests exercise split weapon slots and extra sockets.

Shared clips: `Idle`, `Walk`, `Run`, `BasicAttack`, `SkillAction`, `Hit`, `Death`.
Swordsman adds `Guard`, `Dash`; Mage adds `CastChannel`, `Blink`. Fire and ice
skills can both use `SkillAction`; projectiles/skill VFX remain in their existing
separate systems. There is no new body sheet per skill/node.

## Authoring and packing

1. Record the owner-approved reference, camera, handedness, palette, proportions,
   hair, costume and weapon locks in the canonical definition. Keep its source
   artwork in `authoring/characters/modular/<characterId>/approved-reference.png`.
2. Author the base body and shared poses, then all **eight directional masters**
   with that identity and camera. Review asymmetry/directional identity before
   making whole animation sequences. Individual regenerated frames are repairs.
3. Render whole modular strips to
   `authoring/characters/modular/<characterId>/parts/<partId>/<AnimationId>/strip.png`.
   Frames run left to right; canonical directions run top to bottom. Keep an
   unnormalized original beside it when normalization is required.
4. Normalize using the single `source.normalization` transform in the definition:

   ```sh
   python3 tools/normalize-modular-strip.py \
     --definition authoring/characters/modular/<characterId>/definition.json \
     --animation Walk --input <raw-whole-strip.png> --output <normalized-strip.png>
   ```

   `--input-order S,SE,E,NE,N,NW,W,SW` explicitly imports legacy row order. It
   reorders authored views, never mirrors them. All parts/clips share source cell
   size, source root and scale; no alpha-bound fitting or per-frame resizing.
   Cropped-off painted pixels, non-RGBA strips and opaque backgrounds fail.
5. Pack all parts and clips:

   ```sh
   python3 tools/pack-modular-sprites.py \
     --definition authoring/characters/modular/<characterId>/definition.json \
     --sources authoring/characters/modular/<characterId>
   python3 tools/validate-sprites.py
   ```

The packer uses one lossless PNG atlas per part/clip, eight direction rows,
untrimmed canonical cells and two transparent pixels of padding. It checks all
inputs before writing output, refuses atlases over 4096 pixels, and deterministically
writes `assets/characters/<characterId>/atlases/<partId>-<animation-lowercase>.png`
and `sprite.json`. Longer clips exceeding that bound need page-packing work before
production. Modular source strips and shared pose metadata remain authoritative;
any flattened preview/bake is derived output.

Frame IDs are `<characterId>_<partId>_<AnimationId>_<Direction>_<index:02>`:
`swordsman-proof_weapon_Walk_SW_04`. Atlas IDs use lowercase hyphenated slugs.
The JSON Schema is `assets/characters/schemas/sprite-definition.schema.json`.
Timing/coordinates are stored once per pose; part refs contain only `atlasId/rect`.

## Add a cosmetic, weapon skin or animation

For a cosmetic/weapon skin, add a part ID with the existing compatible slot.
Render the new part against **all existing canonical poses**, using their sockets,
canvas, timing and identity locks. Pack and validate, then select its part ID in
`appearance`. Unchanged/empty frames may reuse an identical atlas rect. A new
logical optional layer needs a slot, default part and placement in every draw-order
override. Cosmetic ownership/payment rules belong to a later backend task.

For a new animation, add one clip with its own durations/loop policy, eight
ordered pose sequences and sockets. Render a whole strip for every compatible
part. Pack/validate and review normal/quarter-speed playback. Keep cosmetic/VFX
changes separate from body motion wherever the action permits it.

## Runtime and preview

```js
const visual = await AstraeonModularSprites.load(
  './assets/characters/<characterId>/sprite.json',
  {animationIds: ['Idle', 'Walk', 'Run', 'BasicAttack', 'SkillAction', 'Hit', 'Death']}
);
await visual.ensure('Guard'); // preload a later clip before selecting it
const frame = visual.compiled.sample('Walk', 'SW', 130,
  {appearance: {Weapon: '<weapon-part-id>'}});
AstraeonModularSprites.draw(ctx, frame, visual.images, {x: groundX, y: groundY, scale: 0.5});
// Existing equipment is passed through unchanged; visual is an optional 8th arg.
AstraeonAnimation.player(ctx, cls, anim, transform, iso, time, equipment, visual);
```

`load()` defaults to Idle only; `ensure()` loads/caches the atlases for a clip,
including compatible variants. Prewarm required action clips before use. Failed
image requests can be retried. `allowDev: true` is required for placeholder loading
and drawing. The preview enables that flag explicitly. No placeholder is registered
as a default player appearance.

The adapter maps the existing `warrior` renderer archetype to the **visual** class
`Swordsman`, and `mage` to `Mage`; gameplay class IDs are unchanged. It uses the
existing distance-driven `gait` for Walk/Run and action progress for non-looping
clips. `animationId`, `direction`, `elapsedMs` and `appearance` can be supplied on
the visual object for an authoritative simulation clock or debug selection.
Canvas composition fits the existing WebGL actor's 2D billboard assembly path.
No realtime 3D character is introduced. Existing world socket aliases remain;
`spriteSockets` expose the canonical pose sockets in rendered pixels.

Serve the repository and open `sprite-preview.html`. Choose class, clip,
direction/frame; inspect layers, registered sockets, normal/quarter playback and
an alternate sword/staff marker. Hidden preview layers do not remove required
layers from the runtime definition. Development-page navigation is cached under
its own URL and cannot overwrite the offline game entry point.

## Checks and approval boundaries

```sh
python3 tools/validate-sprites.py
python3 tools/run-node-checks.py
node --test --test-isolation=none tests/world_streaming.test.mjs
python3 tests/modular_sprite_tools.py
python3 tests/modular_sprite_browser.py --url http://127.0.0.1:8011
python3 tests/modular_runtime_browser.py --url http://127.0.0.1:8011
python3 tests/cache_resume.py --url http://127.0.0.1:8011
```

The validator uses the project's existing Pillow/jsonschema/Node tooling. It
rejects duplicate JSON keys, schema/naming violations, missing directions/layers/
frames, timing overrides, invalid roots/sockets/orders, missing atlas refs/files,
canvas/image-size mismatches, non-RGBA or opaque PNGs, overlapping cells and gutter
bleed. The browser tests cover every proof pose and actual composited pixels.

Reproduce the temporary sources and outputs with
`python3 tools/build-modular-proof.py --sources /tmp/astraeon-modular-sources`.
This only generates original geometric test markers. It is not a production art
command. Source strips are reproducible from that checked-in generator.

The unchanged approved Warrior identity seed exists at
`authoring/characters/gait-rig-v50/approved-warrior-seed.png`; its neighboring
pose/rig studies are rejected/unapproved and must not be installed. Owner review
must confirm its intended Swordsman identity mapping and approve the canonical
modular masters. No approved Mage modular reference was found. Insert it at the
source path above. Proof faces/hair/outfit/weapon/palette are not final designs.
Only the owner can record a real `source.approvedBy`, reference and `APPROVED`
status after visual review; passing schema/kinematic tests cannot grant approval.
Actual artwork, anatomical gait/sole travel, camera consistency and gameplay
acceptance remain the next production work, not claims made by this foundation.
