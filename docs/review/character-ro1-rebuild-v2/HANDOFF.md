# ASTRAEON character rebuild handoff — 2026-10-10

Continue the actual character rebuild, not just documentation or a one-off sprite.
The owner explicitly rejected previous artwork because anatomy, grip and other
details were wrong. Hard-reference Ragnarok Online 1 for proportions, camera,
animation, head/body separation, complete head-and-hair resources and equipment
assembly. The first approved Swordsman must become a reusable production master.

## Checkout and checkpoint

- Workspace: `C:\Users\Lenovo\Bas\Astra online` (PowerShell).
- Repository: https://github.com/basicbasja-cloud/Astraeon-online.git
- Branch: `character/ro1-reference-engine-v1`.
- Last verified local and remote-tracking checkpoint:
  `1fffc3091575d4e8fecbf0368cdf95e189e32a31`.
- Working tree was clean before this handoff was written. Fetch before continuing;
  do not assume the recorded remote checkpoint is still authoritative.
- Focused commits and normal pushes are authorized. No force push, rebase or
  history rewriting. Git author is already configured using the GitHub account.
- Original request: `C:\Users\Lenovo\.codex\attachments\1b888675-7236-4441-ab79-ed25c6367817\Pasted text.txt`.

## Required result and boundaries

Finish Idle, Walk and BasicAttack for the current Swordsman in canonical order
S, SW, W, NW, N, NE, E, SE. Do not add classes, gameplay actions or Combat changes.
Do not touch Backbone branches or redesign world/gameplay systems.

Reuse approved MotionTemplate + new BodyWithOutfit + new complete Head/Hair style
+ WeaponPoseSet + optional accessories. Future costume, hairstyle, weapon, offhand,
headgear and cape swaps must preserve action, direction, elapsed animation time and
cosmetic time. No appearance-specific engine branches or one-off anchor hacks.

Latest owner clarification favors RO1-style complete Head+Hair as one selectable
resource, separate from BodyWithOutfit. Earlier separate-Hair wording was superseded.
Keep MainHand, OffHand, Headgear, Garment/Cape and optional FX independently modular.
BodyWithOutfit includes dressed anatomy and hands. A weapon atlas must not own hands.

Canvas is 320×320; ground root is (160,264). Preserve the existing BasicAttack
16-frame/450 ms clock and 170 ms contact landmark. Do not fake eight views by
mirroring, auto-fit individual frames, warp old limbs, or rotate one sword image
as a substitute for a perspective-aware weapon set.

## Honest current status

The reusable code foundation exists. The production Swordsman does NOT.
No new master is approved. Current animation is combined artwork for review only.

Eight separately generated direction sheets supply 48 original attack key poses:
ready, anticipation, acceleration, contact, follow-through and recovery. Those six
poses are held on the existing 16-frame clock. This is not 128 newly painted frames.
It cannot demonstrate independent head or weapon swapping.

Known remaining visual problems include foot drift, inconsistent profile/diagonal
facing, variable proportions and recovery discontinuities. Rear sword trajectory
and grip still need stronger visual evidence. Clean source boundaries are not
anatomy approval. Do not relabel this study as completed production animation.

Fresh separated body/head assets exist only as an eight-direction, one-frame
neutral DEV_ONLY study. Full animated body/head/weapon separation, Walk, complete
Idle, alternate compatible appearance art and production swap checks remain.

## Open and inspect first

Start a server from the workspace if port 8022 is not already serving this repo:

```powershell
python -m http.server 8022 --bind 127.0.0.1
```

- `http://127.0.0.1:8022/character-pose-study.html`: new combined attack animation,
  normal and half speed, six pose stops, all eight directions, limitations visible.
- `character-baseline-review.html`: private RO1 reference comparison workbench.
- `character-production-review.html?motion=PATH&appearance=PATH`: generic modular
  renderer, part swaps, layer isolation and grip overlays. Supply explicit paths.
- `docs/review/character-ro1-rebuild-v2/attack-study/`: normal/half-speed GIF/APNG,
  six boards, export receipt and browser check results.
- `docs/review/character-ro1-rebuild-v2/neutral-layer-fit-board.png`: original
  separated neutral body/head fit study, not an animated master.

Read `REBUILD.md` here, then
`authoring/characters/baselines/humanoid-ro1-v1/CONTRACT.md` and `pipeline.json`.

## Reusable implementation

| File/tool | Purpose |
| --- | --- |
| `character-art-baseline.js` | Artwork-only families inherit baseline geometry/timing/occlusion; rejects unauthorized overrides and owner-rejected references |
| `tools/character_art_variant.cjs` | Scaffold and verify replacement manifests and actual PNG dimensions |
| `tools/create_character_master.cjs` | Create a candidate master only; requires full action/direction contract and complete Head+Hair topology; never approves it |
| `tools/normalize_character_art.py` | Explicit source maps, shared sheet scale, fixed direction origins, reject clipping/cross-cell art and private-reference sources |
| `character-production-validation.js` | Equipment socket, visible grip, independently authored hand contact and tip diagnostics; never certifies painted anatomy |
| `proof/character-production-review.js` | Generic review and time-preserving part swaps |
| `tools/export_character_production_review.py` | Any production pack, all eight directions, five review modes, normal/half-speed exports |
| `tools/export_character_pose_study.py` | Combined-study export only; records source hashes, transforms, timing and findings |
| `tools/compile_character_pose_study.cjs` | Compile neutral DEV_ONLY body/head fit; not a production animation compiler |
| `tools/build_humanoid_pose_guide.py` | Original 3D projection planning guide, fixed arm/leg lengths, all eight views; NOT decoded RO bones |
| `tools/build_ro1_rebuild_reference.py` | Decode private body/head evidence and publish numeric registration metadata |

Main art/config folder:
`authoring/characters/builds/swordsman-ro1-rebuild-v2/`.
`PROVENANCE.md` records original sources, rejected candidates and prompt specs.
`attack-study.json` chooses current sheets and fixed per-sheet registration/scales.
The study exporter removes explicitly declared alpha noise at <=16/255 and records
counts, preserving source bytes. No per-frame geometric fitting is performed.
Do not confuse source-sheet cleanup with validated production anatomy.

## RO1 evidence and limitations

Private source imagery/raw ACT/SPR are under
`authoring/characters/private-ro-reference/`, especially `rebuild-ro1/` and
`true8dir/`. These are ignored and may be absent on a different machine. NEVER
commit raw RO pixels or screenshots containing them. Original generated art and
numeric source measurements may be committed.

Public source references:

- https://ragnarokresearchlab.github.io/file-formats/act/
- https://ragnarokresearchlab.github.io/file-formats/spr/
- https://github.com/zhad3/zrenderer/blob/main/RESOLVER.md
- https://github.com/zhad3/zrenderer/blob/main/RESOURCES.md
- https://github.com/adsonpleal/ragassets

Pinned inspected ragassets revision:
`4de4fa747431979d35c747d7edd549a872efd9e1`.
Male Swordman body and male head 1 fixtures were decoded. The head includes hair.
`ro1-part-registration.json` here publishes 208 numeric body/head frame pairs.
Parent ACT anchor minus child ACT anchor plus child layer offset informs registration.
ACT does not supply named shoulder/elbow/wrist bones.

Raw Idle and Walk have distinct eight-direction records. Inspected ready/attack
families repeat adjacent pairs (S/SW, W/NW, N/NE, E/SE). Do not assert eight unique
source attacks merely because eight action IDs exist. Additional original views
are derived. The original 3D guide is VISUAL_DERIVED planning, not exact RO anatomy.

Raw weapon ACT/SPR has NOT been acquired. Rendered sword/slash captures are weaker
evidence for grip/perspective; slash obscures impact. Exact weapon pivots and view
counts are not established. Do not disguise inferred coordinates as decoded data.

## Rejected approaches to avoid repeating

- `swordsman-true8dir-v1` and prior limb-warps are owner-rejected historical material.
  Their appearance pack has `source.ownerRejected=true`.
- Full 48-pose image generation returned seven rows; missing coverage was rejected.
  Separate direction sheets were more inspectable, but still introduced errors.
- Northwest contact switched to the near left hand. The corrective pass placed
  the right sword arm on the occluded far side. Re-check it in motion.
- Northeast/Southeast swords crossed source cells. Padded replacements now export
  without boundary findings; that does not fix foot drift or pose inconsistencies.
- Equipment socket and grip contact have different semantics but can coincide
  numerically. Do not require unequal coordinates as proof of independent authorship.

## Verification already performed

- 312 Node tests passed with `node --test tests/*.test.cjs`.
- 34 Python tests passed before adding five pose-study exporter tests; those five
  also passed independently. The combined 39-test suite was not rerun as one command.
- Browser checks with Playwright/Edge: animation screenshots change, 900 ms half
  speed selected, all six pose stops load, mobile fits, no page errors.
- Exported APNG timing totals 450 ms normal/900 ms half speed. Encoders may merge
  identical held frames; six stored frames do not imply a changed shared clock.
- Source boundaries: zero findings for the selected padded study inputs.
- Historical tests also exercise rejected artwork. Test success is not visual acceptance.
- No full-game validation of a fresh production pack, because no complete pack exists.

Python/Pillow/Playwright and Node are installed; Edge runs with
`p.chromium.launch(channel='msedge', headless=True)`.

## Next production step

1. Inspect the current animation at normal/half speed beside RO1. Write concrete
   per-direction/frame findings for facing, planted feet, right-arm ownership,
   blade motion, body compression and recovery. Do not generate another large
   batch before understanding those failures.
2. Establish a stable attack body pose set and visible hand-contact landmarks for
   all eight views. Repair source art rather than hide drift with per-frame fitting.
   Check constant proportions, coherent camera and recovery into the initial pose.
3. Produce genuinely modular BodyWithOutfit, complete Head+Hair, WeaponPoseSet and
   necessary body-owned hand foreground passes. Validate body-only, weapon-only,
   body+weapon, full composite and grip debug. No hands embedded in sword art.
4. Complete Idle and Walk on the same baseline; verify all action/direction naming,
   frame timing, roots, attachments and occlusion. No new classes.
5. Demonstrate costume/head-style/weapon and accessory swaps without resetting
   the clock, using actual new artwork in the generic review and game integration.
6. Export new animated artifacts, run meaningful tests and browser/game checks,
   commit and normally push. Only after visual acceptance make the Swordsman the
   approved reusable master. Do not create fictitious owner approval.

The user permits relevant plugins, skills and localhost playtesting. Use the
built-in image generation tool for bitmap generation/edits; inspect references and
actual saved outputs. Do not silently switch to a paid API fallback. No subagents
unless newly authorized by the user or applicable skill instructions.

Keep the work focused: character #1 establishes contracts and production tools;
character #2+ should mostly be artwork replacement, retargeting and validation.
