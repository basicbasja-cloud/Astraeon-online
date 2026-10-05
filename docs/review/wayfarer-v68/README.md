# Wayfarer RO3 exterior, density and fountain review — source68

Continue `79af03d`/source67 on `codex/world-pipeline-v3-proof`. The user requires
RO3 as the hard reference for exterior construction, scale, textures, shading,
building density and the fountain, with gameplay visual checks before completion.
The supplied screenshots guide observable forms; the models, textures and
celestial statue remain original ASTRAEON work. No RO3 pixels/models are imported.

**Town accepted=false; locomotion accepted=false; cosmetics implemented=false.**
The scoped visual result is recorded in `visual-test.json`. This is an agent
review of these exterior/density/fountain criteria, separate from user Golden
approval, the rest of the art backlog and physical-device performance.

## Buildings and street enclosure

All 36 preceding ordinary house/inn/workshop envelopes now use the strict facade
kit, plus one new street house: **37 envelopes**. Twelve primary frontages have
three/four upper bays; narrow traced lots have two bays and ground modules fitted
to their actual front edge. Genuine upper openings, nine lights, timber reveals,
small jetties, corbels, scalloped friezes and boarded/iron-bound wood entrances
replace the earlier sparse facade and low miniature-house forms.

RO3 `04_08_00` / `04_08_45` guide street-parallel 42° clay roofs with two dormers
cut through the roof below its ridge. `04_08_34` guides 48° front gables with attic
shutters. Upper walls are warm ivory and most ordinary roofs use original clay
materials; civic blue roofs keep the original town hierarchy. Attached wings
remain joined volumes; side openings that would face a wing are omitted.

Occupied house ground area increases **13.1%**, from955.69 to1080.81 square world
units, measured at quarter-unit resolution. This is a local before/after measure,
not a proprietary RO3 map-density number. Houses gain physical ground envelopes
where roads allow it; constrained lots retain their traced footprint. One house
closes the eastern edge of the approach, and five complete rooted tree groups
move clear of occupied lots. Main roads, services and ten patrol loops remain
usable. Gate, civic and fountain courts stay open, following the references'
distinction between enclosed streets and broad public squares.

The registered moving human height is `70*(92/76)/35 ≈ 2.42` world units under the
shipped draw scale; legacy idle artwork has slightly different visible bounds.
Earlier draft notes incorrectly used2 units without the92/76 draw factor.
Actors and their registration are unchanged. Door leaves2.8/3.0/2.75, floor
tops3.65/3.8/3.55 and wall tops6.3/6.6/6.1 are working native dimensions, with
entrance frames/steps checked against the visible character. Screenshot ratios
also include perspective, ground depth and pose; they do not establish RO3 meters.

## Fountain and public court

RO3 `04_08_20` guides the four-lobed outer basin, raised circular inner pool,
central sculpted plinth, four raised flowerbeds and four green benches. Two
walkable steps (.12/.24) are actual native terrain contacts. The original winged
celestial statue gains cloth folds and a lower, tiered support. Four broad falling
sheets replace thin wire-like jets. Two blue water levels have quiet animated
ripples defined by native material metadata and local authored UVs, so moving a
placement preserves their center. Existing lamp and street furniture stations
remain around the court.

The basin, beds and benches have source colliders. Water/flowers sit inside those
occupied regions. Fountain steps change gameplay floor height intentionally;
no decoration is used as an invisible replacement for navigation geometry.

## Texture, shading and review checks

Reuse the original lossless1254² exterior atlas (four627² tiles), its master and
provenance. Roof repeat changes3.2→2.4 world units with slope/ridge UVs. Palette
normalization and separate tile mip chains retain detail without adjacent-tile
bleed. Runtime software resolution stays1× CSS pixels; hardware uses1×–1.5×.
Warm sun.68 / cool ambient.40 continue. Both native lighting bakes are refreshed:
AO16 rays/.42 strength/1.6 radius and alpha-aware1536² floor casts. Exact current
parameters/digest are in `native-authoring.json` and `summary.json`.

- `aperture-clearance.json`:4,095 outward pane-center rays through455 windows;
  old courtyard walls/gables, belts and signs crossing glass are removed.
- `decor-clearance.json`:229,376 quarter-unit ground samples and low-detail
  contact checks. Intentional occupied-ground/floor changes are recorded;
  this expanded pass does **not** claim identical collision/elevation to67.
- `traversal.json`:17 route/service destinations reachable and ten clear patrol
  loops. Ordinary-input services, field departure, save reload and offline cache
  migration are checked separately in their reports.
- `geometry-budget.json`, Node report, schema log and saved Blender/export parity
  describe source coherence and cost. They do not establish artistic fidelity.

`comparison.html` places the reference beside matched source67/source68 stills
(distance160/yaw25/pitch46, explicit1.5× still buffer). `native/` separately shows
ordinary1× buffers. Disposable save-position fixtures provide review views;
service/field tests use real input. Visual owner fading near the player is the
existing gameplay visibility behavior.

Scoped agent visual criteria pass across ten final views. All95 Node checks, four schemas, source/export parity, ordinary services/field/save and offline cache68 reload pass. Isolated sound-on SwiftShader timing fails the55FPS gate:1.74FPS, p95/max700ms at native1280×666. Eleven samples do not certify movement continuity or physical-device performance.

## Native sources and continuation

Native source `authoring/wayfarer-spatial.blend`; matching export
`world/v3/wayfarer-spatial.json`. Authoring is split into primary facade,
secondary/density and fountain scripts sharing `ro3-facade-kit-v68.py`. The density
planner respects roads, patrol legs, service access and existing solids. Scripts
are recorded source migrations; do not run old town builders to reconstruct the
current scene. Any geometry/light edit requires sequential corner/floor bakes.

Original civic detail, richer street goods and wider art direction can continue;
full user Golden approval, painted gait/anatomy and physical-device profiling
remain open. The cropped civic reference does not establish the Hall's full height.
`previous-handoff.md` preserves the completed67 checkpoint and held-art restrictions.
