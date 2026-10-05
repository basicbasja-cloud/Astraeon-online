# ASTRAEON continuation checkpoint — 2026-10-05 / source68

## Workspace and authority

Branch `codex/world-pipeline-v3-proof`; checkout `/workspace/Astraeon-online`;
origin `https://github.com/basicbasja-cloud/Astraeon-online.git`.
Parent complete checkpoint `79af03d6def470022defcdf828bd056401751656`/source67.
This document's commit is the source68 checkpoint. Development remains active;
no deployment, merge, PR or shutdown was requested. Leave loopback server8011 available.

User directive: **Hard reference RO3 exteriors, facade detail, texture quality,
lighting/shading and scale; include building density and water fountain; continue
until the gameplay visual test passes.** Supplied references control those visible
criteria. Original ASTRAEON identity/civic hierarchy remain; physical envelope,
infill and fountain floor changes are authorized to meet the target. Preserve
usable streets, services, portals and transitions. Do not resize actors or lower
native render resolution to disguise a mismatch or improve FPS.

**Town accepted=false; locomotion accepted=false; cosmetics implemented=false.**
Scoped agent visual review is separate from user Golden approval. Exact results,
limits and evidence: `docs/review/wayfarer-v68/README.md`, `summary.json`,
`visual-test.json`, `comparison.html`. Prior completed handoff and held-character
restrictions: `docs/review/wayfarer-v68/previous-handoff.md`.

## Saved source and implemented scope

Native `authoring/wayfarer-spatial.blend`; export `world/v3/wayfarer-spatial.json`.
Layout `wayfarer-concept-terraced-town-v49`,120 collections, bounds112×128.
Architecture/frontage/strict facade/density/fountain/contact fit/corner bake68;
original diffuse/exterior texture provenance67; flora64. Boot/page/cache68.

**37 ordinary building envelopes:** twelve primary frontages,24 other existing
house/inn/workshop lots (including the two lots without preceding placement roots)
and one new east-approach house. Strong timber posts/belts, genuine upper facade
openings, nine lights, small jetties, corbels/scalloped friezes and boarded wood
entrances replace old sparse facades and miniature-height secondary houses.
42° street-parallel clay roofs have paired cut dormers below their ridge;48°
front gables have shuttered attic windows/fan braces. Dormers have closed backs.
Windows at attached-wing junctions are omitted where the roof would block them.

Working dimensions: home/merchant/workshop wall top6.3/6.6/6.1, floor top
3.65/3.8/3.55, wood leaf2.8/3.0/2.75, jetty.42, ground trim≤.16. Constrained ground
fronts fit their actual traced front edge; one awning rises clear of a terrace.
The shipped registered moving body is70*(92/76)/35≈**2.42** world units; legacy
idle artwork bounds differ slightly. Earlier draft notes incorrectly omitted the
92/76 factor and claimed2 units. Registration/draw scale and actor artwork stay
unchanged; reference screenshot ratios include perspective/ground depth/pose.

Occupied house area grows**13.1%** (955.69→1080.81 square units at quarter-unit
sampling). This is a local before/after measure, not an RO3 proprietary map count.
New physical envelopes fit where roads allow them; constrained lots retain traced
occupied ground. Five complete rooted tree groups relocate outside lots. Main
roads/services/patrol legs remain open; public gate/civic/fountain squares keep
the reference's breathing space. Navigation/elevation are intentionally changed;
do **not** repeat the earlier primary-only claim that all ground is unchanged.

Fountain against04_08_20: four-lobed outer pool, raised circular inner water,
sculpted original celestial plinth/statue with cloth relief, four corner flowerbeds
and green benches, four broad water sheets. Two low steps(.12/.24) are native
walkable floor contacts. Basin, beds and benches have source colliders. Optional
material `texture.ripple` settings animate water through local authored UVs and a
shared clock; moving a placement keeps its ripple center. Existing surrounding
lamp/street stations remain. No RO3 texture pixels/models imported.

Original atlas `assets/wayfarer-exteriors-v67.webp` stays lossless1254²/four627²
tiles, with master/provenance under `authoring/materials/`. Roof repeat3.2→2.4;
slope/ridge UVs, palette-relative contrast and separate tile mip chains remain.
Software gameplay stays1×CSS; hardware stays1×–1.5×. Still1.5× is review-only.

Lighting: warm sun.68, cool fill.40, cast(.62,−.40), AO16 rays/.42 strength/1.6
radius. Corner bake484,592 corners/16,568 meshes/33.2s. Alpha-aware floor bake
1536²,1,386,159 land/806,702 shadowed pixels/214.7s. Ground filename stays
`assets/wayfarer-ground-shadow-v54.png`; current digest:
`eec4901a6e95394fcc64dfcd7dfbf663cc399e5c390d226be80df395694b6051`.
Geometry/light edits require sequential source save/export, corner and floor bakes.
Do not overlap source mutations with browser review or isolated performance.

Visible273,780 triangles vs244,256(+12.09%);21,018 visible parts vs15,588;
57 visible materials vs61. These costs are not an FPS result.

## Source tools and verified contracts

- `tools/ro3-facade-kit-v68.py`: shared facade/roof and traced-ground-front modules.
- `tools/author-ro3-facades-v68.py`: repeatable primary source migration, storing
  original structural vertices before height remapping.
- `tools/plan-ro3-density-v68.py` / `tools/author-ro3-density-v68.py`: reviewed
  envelopes/infill and complete tree relocation. The exact applied plan is in
  native scene metadata/`native-authoring.json`; do not recreate the current town
  with historical builders or re-plan already-remapped walls as an old baseline.
- `tools/author-ro3-fountain-v68.py`: native tiered public court and water metadata.
- `tools/check-ro3-apertures-v68.py`:4,095 rays/455 windows clear; courtyard remnants,
  old belts/signs and intersecting dormer braces were removed.
- `tools/check-ro3-ground-v68.cjs`:229,376 ground samples; all new low visible
  vertices contact occupied ground under2.3-unit body-height assumption.
  Changes:2,695 blocked samples; 1,340 floor-height samples change.
- `tools/check-ro3-traversal-v68.cjs`:17 reachable route/service destinations,
  ten clear patrol loops; no patrol reroute was needed.
- `tools/report-ro3-native-v68.py`: read-only exact saved source parameters.

All95 individual Node checks, four public schemas and saved Blender/export parity
pass. The parity check changes the Hall only in RAM and confirms floor-bake
invalidation; its stale-bake diagnostic is expected. Use Blender
`--python-exit-code 1`; default Blender can exit0 after a Python assertion.

Fixed stills share distance160/yaw25/pitch46; source67 comparison stills use the
same explicit1.5× buffer. Native views separately show1× buffers. Those fixtures
are disposable review positions, not traversal or performance proof. Ordinary
Merchant/Artisan/Housing Keeper service input, field departure, save reload,
cache migration/offline reload and isolated sound-on native timing are recorded
in the final review reports. Browser checks must be serial; isolated timing runs
without other browsers, authoring or bakes. Never loosen performance assertions
or reduce rendering resolution to pass.

Scoped visual criteria pass in ten reviewed views (seven matched stills and three native). Ordinary services, field departure, save reload and cache68 offline migration pass (93 precached requests). Isolated sound-on SwiftShader timing fails55FPS:1.7415FPS, p95/max700ms at1280×666/1×;11 samples/10 moving pairs/zero observed body holds are insufficient for continuity or gait certification. Physical-device timing remains unverified.

## Continue after this checkpoint

Scoped house/density/fountain visual result and exact timing are in the summary.
User Golden approval, broader civic carving/tracery, functional street goods,
painted full-body gait/anatomy and physical-device FPS acceptance remain open.
Cropped04_08_30 cannot establish the Hall's full height, so preserve the original
monumental hierarchy absent an observable comparison supporting a change.

Keep town work first. Held character strips remain excluded; no new character
art was installed. Previous handoff links prior gait/weapon/registration diagnosis,
Mage/Ranger mode-specific art and cosmetics restrictions. No npm/build/install
step is needed on this host; Blender/Python/Chromium/Playwright are available.
