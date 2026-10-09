# ASTRAEON true modular Swordsman v2 — blocked at South

**DEV_ONLY · DIAGNOSTIC ENGINE CHECKS PASS · SOURCE COVERAGE INCOMPLETE ·
SOUTH VISUAL FAIL · OWNER APPROVAL PENDING**

This task did **not** meet the character success criteria. Independent component
generation was attempted, but the shared registration contract failed visually.
The failed result is preserved transparently; no later production gate was
advanced and no rejected candidate was installed into ordinary gameplay.

## Git checkpoint

| Item | Result |
| --- | --- |
| Verified remote baseline | character/ro1-reference-engine-v1 |
| Verified baseline SHA | db2959b97a77b3f9b54c22d5e732fe2b2345a529 |
| Baseline inspection | Current remote HEAD equals the supplied checkpoint; no newer commits |
| New branch | character/true-modular-ro1-swordsman-v2 |
| First commit | bf73b40 — Define true modular South authoring contract and verify RO references |
| Final candidate/validation commit | Commit containing this report; exact SHA and verified push result are in the task response |
| Remote destination | [Working branch](https://github.com/basicbasja-cloud/Astraeon-online/tree/character/true-modular-ro1-swordsman-v2) |
| History | New branch from verified SHA; no merge, rewrite, reset or force push |

## Reference inspection and preserved work

Cloud Chromium visually inspected the RO index and these full sheets:
[Male Swordsman](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141350/),
[Male Knight](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141301/),
[Male White Heads](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/126315/),
[Crowns & Circlets](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/127535/).
Sheet structure, neck/head presentation, compact action silhouettes, directional
hair and equipment readability informed the contract. PNG timing stays UNKNOWN.
[Reference classifications and audit](REFERENCE_AND_AUDIT.md) separate
VISUAL_REFERENCE, SOURCE-DERIVED, RENDERED_REFERENCE and ASTRAEON_INTERPRETATION.

Reused unchanged: ragassets rendered-reference.json and35 sequence identities;
pinned roBrowser sword action80–87 mapping; canonical8 directions; MotionTemplate;
root(160,264),320×320, reference height176; timing/key classification, anchors,
draw profiles, four sampling modes, AppearancePack assembly, swap isolation,
validation and existing browser/world review. Baseline MotionTemplate remains
byte-identical. Walk is8 keys+8 transitions/600ms; attack9 keys+Ready+6
transitions/450ms. No raw ACT delay claim was added.

The approved-warrior-seed identity file is unchanged with SHA256
750ffe25056760c6ab97c3e66a3488d15aec4c875e573d9a8cef65c8f0437e05.
It was inspected and used as appearance reference only. No v1 dressed-body
pixels were copied, masked or decomposed into v2 editable sources.

Deprecated for new authoring: the v1 monolithic bald-head/body/class-outfit/
shoulder/waist/boots BodySpriteSet. Its builder, art and evidence remain intact
for historical reproduction. The separate Hair/Weapon/accessory engineering
and sources remain useful; this checkpoint reuses the original isolated sword.

## Source architecture and component status

Authoring-only source manifest → shared pose contract → independent raster
sources → normalized preview rasters → generic v1 raster drawing. Motion stays
separate. Preview composites and bakes never replace source PNGs. Source digests,
exact prompts, input guide identities and transforms are recorded. Gameplay
equipment never supplies an appearance fallback. ClassId remains Swordsman;
bodyVariant supports male/female structurally, with only male data authored.

| Source / gate | Result |
| --- | --- |
| BodyCore | Intentionally generated foundation with neutral underlayer, bare simplified feet, no permanent head/class outfit/armour/boots/weapon; too muscular, PROVISIONAL |
| HeadBase | Independently generated bald skull/jaw/ears/neck; neck overlap and identity PROVISIONAL |
| Face | Independently requested feature layer, but output contains skin shading and is misplaced; REJECTED |
| Outfit A | Independently generated garment-only forms; collar/shoulders/gloves/boots fail the established body pose after2 attempts; REJECTED |
| HairBack / HairFront | NOT AUTHORED; method stopped before further sources; no empty sprites substituted |
| Weapon | Original independently authored ASTRAEON v1 sword source cell reused; shared anatomical-right mainHand attachment, PROVISIONAL fit |
| OffHand / Headgear / Cape / FX | Not authored for v2; optional and absent |
| South Idle | VISUAL_FAIL, source set incomplete; one diagnostic neutral pose only |
| Cosmetic swap proof | NOT STARTED; diagnostic weapon hiding only, no new Hair/Outfit A/B proof |
| Eight-direction Idle | NOT STARTED, Gate3 blocked |
| Modular Walk | NOT STARTED, Gate3 blocked; baseline choreography preserved |
| Modular BasicAttack | NOT STARTED, Gate3 blocked; baseline attack/recovery preserved |

`character-source-authoring.js` adds validation for independent source identity,
pose binding, class/bodyVariant separation, canonical direction order, shared
root/canvas, declarative source order, source-only appearance selection and
missing-source coverage. Strict compilation rejects this incomplete draft.
The explicit incomplete diagnostic mode displays missing coverage; it cannot
create missing source paintings. Unauthored poses/actions fail instead of
being mirrored or duplicated. Ordinary boot does not load the module.

## Failure diagnosis and boundary

Six built-in ImageGen requests: BodyCore2, HeadBase1, Outfit2 and Face1.
Every request asked for an isolated source from inception. No full dressed
character was generated for subsequent deletion. The first BodyCore had a
short foot baseline and excess musculature. Its isolated repair improved the
baseline but retained excessive anatomy. One initial3px BodyCore root
calibration and measured shared grips were recorded before dependent authoring.

The method then changed from an abstract silhouette to painted registration
guides. The Outfit still chose new proportions after a second attempt: its
normalized opaque top is104 rather than the required neck/collar region around
132–142. HeadBase occupies y95–150; Face occupies y154–184. Generated square
sources are1254×1254 despite the requested1024, but whole-canvas resampling
preserves fractional placement and does not explain or fix the anatomy drift.

Large-scale, canonical1×/2×, approximately gameplay-scale(.54) and actual-world
review show detached Face, a collar across the head, doubled arms/gloves and
uncovered feet. The required coherent painted composite fails. BodyCore's
excess anatomy, provisional HeadBase identity/neck and missing Hair are also
unresolved. Canvas crop and hash passes do not approve any of these defects.

Per the failure policy, no third Outfit prompt or random generation campaign
was attempted. No large warps, per-layer fitting or pixel deletion conceal the
failure. The next method needs spatially constrained painting or a layered art
document with lossless isolated-layer export. The current ImageGen guide-only
workflow did not provide that control. This remains the production blocker.

## Evidence and validation

Repository-relative evidence:

- `character-modular-source-review.html` — static source toggles, honest failure state, optional isolated world review.
- `authoring/characters/true-modular/swordsman-male-v2/` — raw sources, attempts, exact prompts, generation-jobs, pose contract, source manifest and normalization receipt.
- `docs/review/character-true-modular-v2/south-candidate-decomposition.png` —5 actual layers and2 visibly missing source panels.
- `south-failed-composite.png` — transparent failed assembly.
- `south-game-size-failure.png`, `browser-game-size-failure.png`, `browser-authoring-failure.png` — large/canonical/game-scale evidence.
- `browser-weapon-hidden-diagnostic.png` — existing weapon hidden, not an A/B gate claim.
- `world-failed-candidate.png` — actual unchanged world, static South candidate, memory-only save.
- `visual-gate.json`, `browser-review.json`, `javascript-tests.log`, `world-streaming-tests.log`, `python-tests.log`.

Executed:261 individual CommonJS Node checks plus5 world-streaming checks =
**266 JavaScript PASS**, including9 new source checks; **20 Python PASS**,
including5 new source/raster checks. Existing tests are preserved. An initial
sandbox child-process restriction caused git-spawn EPERM in the Node suite;
the supported execution permissions resolved it, and the complete rerun passed.

Browser PASS_DIAGNOSTIC_ONLY:5 source/raster/prompt hashes verified;5 separately
rendered layer rasters unchanged across weapon hiding; combined output changes;
authoring and game-scale captures; actual-world rendering; owner localStorage
unchanged; memory-only save; no JavaScript errors or HTTP failures. Missing
Hair causes expected strict source validation failure. No all8-direction crop
or atlas coverage pass is claimed for v2. Current5 normalized candidates have
clear canvas crop margins and valid PNG/320×320 RGBA identity.

Normal gameplay, Combat, movement, world, map, NPC, networking, stats, equipment,
collision and boot files are unchanged. No full catalogue, female, other class
or extended action was produced. Physical-device performance was not tested.

## Precise handoff and owner boundary

Start from the new branch's published checkpoint. Keep the v1 motion/assembly
and approved identity bytes. Read pose-contract, source-manifest, generation-jobs
and visual-gate before authoring. Replace the rejected South parts using a
coordinate-constrained method; fit one shared neutral master without arbitrary
layer offsets. Finish independently authored HairBack/HairFront, then inspect
neck/head/face/hair fit, outfit joints/coverage, sword grip, light and identity
at actual game size. Only a passing South gate permits cosmetic variants;
only their proof permits8 directions and the preserved three-action sequence.

Owner review remains pending. The failed candidate is diagnostic evidence,
not a request to approve broken art. After repairs, owner review should judge
face/fringe identity, compact proportions, clothing fit, weapon grip and
painted coherence before approving the eventual three-action proof.

No branch was merged. No copied Ragnarok pixels were added to authoring,
production or tracked review evidence. Private browser reference captures
remain outside Git under `/tmp/astraeon-ro-reference/`.
