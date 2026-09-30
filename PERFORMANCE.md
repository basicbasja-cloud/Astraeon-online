# Performance record

Targets: desktop 60 FPS; modern phone 50–60 where possible; lower-tier phone 30+. Targets are not measured device guarantees.

Implemented: static town paving cached in one offscreen canvas; sprite atlases compressed to alpha WebP; DPR/ambient budgets selected by low/medium/high preferences; no per-character CSS hue filters for the new archetypes; presentation culling of offscreen city props; fixed camera smoothing independent of frame rate; capped simulation delta with uncapped frame-time measurement.

QA reports a rolling 180-frame FPS mean and p95 wall-clock frame duration in qa.html. Portrait/landscape resizing changes one iframe without reload. This simulates CSS viewport sizes, not iOS GPU, thermal limits, Safari behavior or touch hardware. Browser runtime measurements will be recorded after publishing this phase. Real Android/iOS device profiling remains necessary.

Known costs: Canvas2D particles and shadowBlur; full-screen ground at selected DPR; 17.7 MB raw town paving cache; UI status rebuild four times/second. No WebGL instancing, LOD, KTX2 or full chunk streaming is claimed. Reassess engine choice from measured renderer cost, not engine fashion.

## Directional pass validation — 2026-09-30

All JavaScript syntax checks, 29 pure movement/combat/dungeon tests and 40 Chromium browser checks passed. Browser checks reported no runtime or failed-resource errors. They cover keyboard directions, analog magnitude and arbitrary angles, dodge, 27 aimed class attacks, four viewport sizes, eight distinct rendered archetype views, field rewards, dungeon entry/exit and save reload. Full authored dungeon completion was not exercised by this suite.

In headless Chromium on this cloud machine, idle town samples after warmup measured 53–58 FPS at 1280×720 (p95 16.8–33.3 ms) and 60 FPS at 390×844 (p95 16.7 ms). These are desktop browser viewport measurements, not physical phone or combat-load guarantees. Six lossless directional atlases add approximately 12.5 MB of transfer/cache assets. Painted sprites retain the original art quality; there is no WebGL model dependency or runtime build step.

## Connected Shenzhou validation — 2026-09-30

The final source uses core-only precaching, asynchronous zone loading/retry, one current outdoor-road canvas (13.2 MB raw RGBA), viewport-culling painted props, source-silhouette Path2D reuse for walk extraction, and an authored minimap rather than hundreds of tile fills. Three compressed walk atlases add about 2.4 MB. Outdoor/ruin props and four ground materials add about 5.6 MB; these load with their zone rather than all at town boot. Script metadata is larger because frames include explicit source bounds and extraction silhouettes.

38 pure movement/combat/navigation/save/exploration tests passed. The fresh-Ranger UI journey passed five checks: level-one town/field route and contract rewards; one-time supply claim; forest/shrine entrance; all four rooms, both guardian phases and all three attacks, relic and safe return; crafting/equipment and persistent reload. There were no runtime or failed-resource errors. This verifies one Ranger route, not complete balance across every class.

Final Chromium smoke results and performance samples are recorded below. Phone-sized Chromium viewports use a desktop cloud browser; they do not measure actual phone GPUs, Safari, thermal limits or hardware touch. Production performance acceptance on physical Android/iOS devices remains open. No 60 FPS desktop guarantee is claimed.

43 Chromium smoke checks passed with no runtime/resource errors, including eight keyboard directions, analog magnitude/circular input, dodge, 27 aimed class attacks, four live viewport sizes, SW v24, distinct directional art, stride extraction, defeat/recovery persistence, failed zone-load retry and combat/reward/reload. An additional gallery coverage check rejects frames missing their upper body. The final muzzle-offset regression also prevents a projectile from starting beyond a thin adjacent wall.

Serial headless Chromium measurements on this cloud machine, DPR 1, default quality, eight-second windows with the last four rolling samples:

| Scene | Desktop 1280×720 FPS / p95 ms | Phone viewport 390×844 FPS / p95 ms |
|---|---|---|
| Town with walkers | 50–53 / 33.4–33.4 | 60–60 / 16.7–16.8 |
| Goldenfield with active enemies | 53–54 / 33.3–33.4 | 60–60 / 16.7–16.8 |
| Moonveil first room with hostile casts | 51–53 / 33.3–33.4 | 60–60 / 16.7–16.8 |

The desktop 60 FPS target is not yet met consistently in this software-rendered cloud browser. These encounter samples include hostile casts/reactions without a sustained player attack/VFX stress load; the town sample includes moving NPCs. Raw reports and viewport screenshots are in the task’s external master-performance artifact directory. Physical-device and sustained-load acceptance remain outstanding.

Guardian measurements were collected separately after reaching its court through normal UI input with a level-five equipment fixture (500 HP), then stopping player attacks during each sample. This profiles the guardian and phase-two adds, not fresh-character balance.

| Guardian case | Viewport | FPS | p95 ms |
|---|---|---|---|
| guardian-phase1 | 1280×720 | 53–54 | 33.3–33.4 |
| guardian-phase2 | 1280×720 | 50–52 | 33.4–33.4 |
| guardian-phase2 | 390×844 | 60–60 | 16.8–16.8 |

A separate completion/access browser check passed: first-clear guidance stays within Shenzhou (three destinations / one dungeon), while returning saves with later legacy progress retain five destinations and four chapter entries. All tested resource and runtime error lists were empty.
