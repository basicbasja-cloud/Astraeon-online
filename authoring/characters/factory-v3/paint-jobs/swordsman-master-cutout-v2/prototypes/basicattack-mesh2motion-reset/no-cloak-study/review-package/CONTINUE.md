# Astraeon character factory — continuation checkpoint

Repository: https://github.com/basicbasja-cloud/Astraeon-online
Branch: character/production-factory-v3
Latest pushed implementation: fd7a9e9
GitHub progress reports: issue #2 (latest comment 6310503703).

## Owner direction

Use Mesh2Motion for a natural, weighted fantasy sword attack. Keep a fixed Blender camera and inspect blade orientation, wrist anatomy, foot contact, root movement and return timing. Show the back of the sword hand during the cut. Preserve the source motion; do not reinterpret it as a thrust. The long cape may be removed if it reduces quality; keep a short gold scarf. Art must be crisp illustrated fantasy quality matching the owner's references. Provide actual animated GIFs for motion review. Layer visible head/hair, body/outfit, weapon and effects from the same registered frame; do not describe a fused body/outfit as interchangeable clothing. Push work and put each progress report in GitHub issue #2.

## Authoritative motion

Path relative to repository: authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/
- eight-direction-guides/: 480 fixed-camera 1024px source captures, 60 frames per direction at 60fps, original Mesh2Motion rig, compressed eight-camera Blender scene, manifests with source joints and sword points.
- source-trail-guide/: source-blade-aligned independent FX guides across eight views. These are not validated painted character effects.
- Current candidate: Sword_Regular_B with matching recovery, terminal reset keys excluded, native root movement retained. One-shot, not an artificial forced loop.

## Actual art status

no-cloak-study/ contains three illustrated studies and exact prompts/provenance. Guard v2 improves the manually annotated grip error to about 14px at 1024px, but sword tip error remains about 39px; follow-through grip error is about 121px. All are rejected for production registration. The measurements are approximate manual annotations, not automated anatomy detection.

editable-cutouts/swordsman-no-cloak-study.ora has HeadHair, visible Weapon, and combined BodyOutfit. Its cutouts recompose with zero mismatched pixels; this proves registration of that still only. Body/outfit separation, hidden surfaces, animated continuity and game rendering are not complete.

## Next work

Solve source-registered illustrated geometry before expanding the animation. Independent per-frame image generation has repeatedly changed anatomy and canvas framing, including after cape removal. Do not generate another full sequence under the same assumption. Do not hide the mismatch with whole-body stretching, per-frame bbox fitting or dissolves. Inspect any limited new method at raised guard, contact, follow-through and recovery against the same camera and original guide. Only after geometry and continuity pass, expand real frames, cut same-frame semantic layers, align WeaponLight with the painted blade, and review in the correct game map.

Do not promote old Rokoko 480–511 or old low-frame painted pilots to production. Existing legacy selectors are historical; the latest master prompt and status describe the active Mesh2Motion direction. Preserve unrelated untracked experiments. Never claim final quality, complete modular equipment or runtime validation from a still-image reconstruction audit.
