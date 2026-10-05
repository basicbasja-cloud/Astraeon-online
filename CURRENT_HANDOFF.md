# ASTRAEON continuation checkpoint — 2026-10-05 / source67

## Workspace and authority

Active branch: `codex/world-pipeline-v3-proof`.
Cloud checkout: `/workspace/Astraeon-online`.
Origin: `https://github.com/basicbasja-cloud/Astraeon-online.git`.
Parent checkpoint: `91565428a5fd91acb524cbc9e19e1c404f4af5ac`.
The commit containing this document is the new checkpoint; obtain its ID from Git
history. The user resumed development and asked to keep pursuing building
exterior detail, texture quality and lighting/shading against `RO3 Ref/`.
Development remains active. No deployment, merge or shutdown was requested.

**Town accepted=false. Locomotion accepted=false. Cosmetics implemented=false.**
Technical checks do not override the user's visual or painted-movement rejection.
This is a completed exterior/material/light iteration with review evidence.

Review: `docs/review/wayfarer-v67/README.md` and `summary.json`.
The preceding complete handoff is `docs/review/wayfarer-v67/previous-handoff.md`;
it links the full earlier reference research, character diagnosis, gait ZIP
manifests and held-study restrictions. No held character art was installed.

## Reference requirements

- Approved `concept art.png` owns original identity, layout, districts and Hall
  hierarchy above water. Preserve playable terraces and waterfalls.
- All ten local `RO3 Ref/` images were inspected this pass. Layered eaves/trim,
  tile courses, recessed openings, warm sun/cool shade and functional street
  density guide presentation. No proprietary assets or texture pixels were copied.
- Source67 advances exterior finish; silhouette variety, blank gable panels,
  broader civic composition and richer street life remain below acceptance.
- Native resolution is mandatory. Source66 removed the forced .5 software pixel
  ratio behind the sharp HUD. Revision67 keeps software at 1× CSS resolution and
  hardware at least 1×, following density up to 1.5×. Never lower resolution or
  loosen performance assertions solely to make a report pass.

## Exact saved state

Native: `authoring/wayfarer-spatial.blend`.
Export: `world/v3/wayfarer-spatial.json`.
Layout: `wayfarer-concept-terraced-town-v49`, 119 objects.
Architecture/exterior/material/corner-bake source pass: **67**.
Frontage opening/cross-gable source remains **65**; grounded flora remains **64**.
Boot, page and service-worker cache/precache versions: **67**, aligned.

- Corner bake67: 412,417 corners / 10,916 meshes / 24.2 seconds.
- Ground bake67: 1536², 1,386,159 land / 738,243 shadowed pixels / 179.0 seconds.
- Ground atlas retains historical `assets/wayfarer-ground-shadow-v54.png` name.
- Valid ground digest:
  `a1bc4697a60a3980e9c2346b70d287f1e2a9245e7305c5885cbef15e14df4b6e`.
- Original foliage alpha participates in casts; no stale bake was restored.
- Sun .68 / ambient .40 / unchanged cast (.62, -.40).
  Native optional ambientColor=(.80,.92,1.10), sun.color=(1.15,1.04,.84).
- Native AO authoring: 16 samples / .42 strength / 1.6-unit radius.
  The bake tools retain prior defaults for sources without those settings.

Save/export, corner and floor mutations must be sequential and must not overlap
browser review or isolated performance. Geometry edits invalidate both bakes.
Do not reconstruct the town by rerunning historical builders.

## Exterior/material work

`tools/author-exterior-craft-v67.py` works on the saved frontage65 town and replaces
only its own `exterior-v67-*` meshes. Twelve frontages gain layered eave beads,
rafter ends, ridge caps, side cornices/knee braces, sills/louvers and dressed-stone
entrances with arched wood leaves and ironwork. Twenty-two other existing lots
gain framing following the actual wall polygons. 316 roof faces now map tile
courses down their slopes; curved main roofs use continuous arc distance.

The new lower jamb/arch projection is <=.16 units, inside the existing .18-unit
collision margin. QA caught a deeper first draft; it was narrowed and both bakes
were rerun. Final `decor-clearance.json` checks all new low vertices under a
2.3-unit body-height assumption. New pieces preserve every existing floor,
solid geometry/visibility, navigation, spawn/route, service/presentation/light/
portal anchor, district and civilian patrol contract against source65.

Original material master/provenance:
`authoring/materials/wayfarer-exteriors-v67-source.png` and adjacent JSON.
Runtime: `assets/wayfarer-exteriors-v67.webp`, lossless pixel-identical encoding.
Actual 1254² atlas / four 627² tiles: clay, slate, oak and limestone. Better painting,
UV direction and retained contrast improve quality; no increased source pixel
count over v44 is claimed. Native materials carry measured meanLinearRGB and
paletteDetail. The shader applies texture variation relative to that linear mean
to the existing palette; older materials/foliage keep their previous behavior.
Tiles retain independent mip chains. Runtime floor shadows use the native bake's
actual 1536² size; the 2048² geometric approximation remains the fallback.

Visible triangles: 244,256 vs 231,062 (+5.71%). Visible parts: 15,588 vs 14,537.
61 visible materials remain (67 including hidden-mesh materials). No new
per-frame raycasting, dynamic shadow pass or PBR pipeline was added. Counts do
not establish physical-device performance.

## Verification and limitations

- All 95 individual Node checks, four public schemas and saved Blender/export
  parity passed. The parity test deliberately moves the Hall in RAM, confirms
  stale-ground invalidation and does not save; its stale-bake diagnostic is expected.
- Native preservation, low-trim clearance and lossless texture encoding passed.
- Six matched stills: residential, market, inn, plaza, civic approach and gate,
  zoom160/yaw25/pitch46 with explicit 1.5× capture ratio (1920×999). Same camera/
  ratio as source65 comparison stills. Review save-position fixtures, not traversal
  or FPS evidence. All errors[].
- Wider native Hall view: distance325/yaw−25/pitch≈64.88, ratio1; roofs/upper
  architecture inspected, lowest facade cropped. Distance65 initially produced a
  close-up; that attempt is not used as wider-Hall evidence.
- Ordinary-input Merchant, Artisan and Housing Keeper services all opened. Field
  departure and saved-character reload passed. Desktop/portrait/landscape/tablet
  snapshots; town 1280×666 / ratio1, runtime errors[] and resource errors[]. Other
  five services and every stair were not all replayed this pass. Native contracts
  and pure checks passed; source65's scoped wider replays remain in the prior review.
- Revision67 migration/offline reload passed: 93 precached requests, every source
  material present, ground PNG decoded offline at 1536². Fresh test-character
  name/class/zone/position/level/XP/inventory/equipment retained. No user browser
  state was changed.
- Isolated sound-on native SwiftShader performance **failed**: 1.62 FPS,
  p95=max 733.3 ms, 1280×666 / ratio1, errors[]. Thresholds remain >55 FPS /
  p95<25 ms / max<80 ms. Only 11 player samples / 10 moving pairs, zero held roots:
  insufficient to certify continuity or painted anatomy/contact. No hardware
  desktop/phone certification. Failed assertion and raw data are preserved.

Use Blender `--python-exit-code 1`. On this managed Node24 host the default runner
reports file wrappers; `python3 tools/run-node-checks.py` exposes all 95 registered
tests in six independent invocations. Browser helpers support Linux SwiftShader
and Windows D3D11. Run visual/service/cache replays serially; isolated timing must
have no concurrent browser or source-authoring work.

## Continue

Prioritize the user's next town feedback. Continue source-owned exterior forms,
blank gables/civic composition and person-relative functional detail using the
concept plus RO3 comparisons; keep the budget and native-resolution limitation
visible. Source67 is reviewable, not accepted. Full-body painted locomotion,
weapon/body registration, Mage/Ranger mode-specific art and cosmetics remain
unfinished. Do not install held gait studies or redirect this task into character
art before the user's town priority is satisfied.

The existing loopback static server on port8011 remains available. No npm/build
step is needed; Python, Blender, Chromium and Playwright are already installed.
