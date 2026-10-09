# True modular Swordsman v2 — baseline and reference contract

Verified 9 October 2026 through remote `git ls-remote`: baseline branch
`character/ro1-reference-engine-v1`, HEAD
`db2959b97a77b3f9b54c22d5e732fe2b2345a529`. It equals the supplied checkpoint.
Clean checkout; new branch `character/true-modular-ro1-swordsman-v2` begins at
that commit. No baseline rewrite, merge or force push.

## Good to preserve

Inspected CURRENT_HANDOFF, ARCHITECTURE, README, RAGNAROK_REFERENCE,
CHARACTER_ASSEMBLY_V1, animated-v1 REPORT, character-motion-template.js,
character-assembly.js, modular-sprites.js, build_painted_swordsman.py,
appearance sources, actual motion JSON and rendered-reference/research notes.

Keep MotionTemplate independent of AppearancePack; S/SW/W/NW/N/NE/E/SE;
320×320, root(160,264), reference height176; explicit timing, key identity,
anchors, direction/frame draw profiles, four independent sampling modes,
atomic swaps, validation, provenance and isolated browser/world review.
Preserve all baseline artwork and review evidence as historical v1 material.

Actual baseline data: Idle9 frames/2 standing-boundary keys/3000ms;
Walk16/8 keys/600ms; BasicAttack16/10 keys/450ms. Idle keys repeat the same
observed pose. Attack has9 attack keys plus Ready. Do not reinterpret these
counts as raw ACT extraction.

## Authoring method to replace

The v1 BodySpriteSet intentionally contains bald head, body, class clothes,
shoulders, waist and boots. Its own REPORT and source README confirm that
boundary. This is unsuitable as editable v2 BodyCore. The historical builder
also registers strips using detected scalp/bounds and uses glove search plus
calibration. Retain it to reproduce v1; do not feed it v2 sources or use it to
decompose the dressed raster. New sources are isolated parts from inception.

## Fresh Cloud Browser research

Cloud Chromium/Playwright loaded the site index and four resource pages with
HTTP200 and their full sheet images. A session-only verified HTTPS client
fulfilled browser requests using the environment's existing CA trust. No TLS
verification disablement or persistent trust-store change was used. Private
page captures stay in `/tmp/astraeon-ro-reference/`, outside Git and production.
Early web-service 403s did not become evidence of successful inspection.

| Resource / source URL | Inspected action/view | Observation and contract | Evidence |
| --- | --- | --- | --- |
| [RO index](https://www.spriters-resource.com/pc_computer/ragnarokonline/) | Male classes, heads, headgear and weapons categories | Resources are presented separately; categories alone do not prove an internal runtime implementation. | VISUAL_REFERENCE |
| [Male Swordsman](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141350/) | Standing directions, locomotion rows, committed action poses; hit/fall only to understand sheet structure | Headless costume/body poses expose a compact neck attachment region. Contact/passing silhouettes are legible with short rows. Side and rear views must read independently. The sheet does not show timing or identify every row's action. | VISUAL_REFERENCE |
| [Male Knight](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141301/) | Standing, locomotion and raised/committed action rows | A larger costume/cape silhouette preserves facing and the underlying neck connection. Rear cape can dominate the back silhouette; keep it independent in ASTRAEON. Sheet pixels do not prove RO cape source separation. | VISUAL_REFERENCE |
| [Male White Heads](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/126315/) | Front/diagonal/side/rear hairstyle rows | Skull/fringe mass, cheek exposure and nape distinguish facings; hair must be registered to a stable head volume. This sheet combines visible head and hair; it does not establish separate RO Face/HairBack layers. | VISUAL_REFERENCE |
| [Crowns & Circlets](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/127535/) | Circlet, tiara, coronet directional views | Very few bright shapes communicate equipment at small scale. Curvature and visible front/back arcs vary with orientation; one mirrored frontal accessory is insufficient. | VISUAL_REFERENCE |

Exact timing from these PNG sheets: UNKNOWN. No RO images enter authoring,
runtime, guides, generated-image references or committed review boards.

## Existing evidence reused

`authoring/characters/motion-templates/ro1-swordsman-male/rendered-reference.json`
binds35 sequences to renderer URLs, hashes, action/frame IDs and observed APNG
delays (RENDERED_REFERENCE). Source endpoint:
https://assets.latam-tools.com.br/image . Walk actions8–15 have8 rendered keys;
Attack80–87 has9; Ready32–39 supplies recovery. Raw ACT timing/offsets UNKNOWN.

Pinned roBrowser `e4b5b53aa1f8b7e429bfa987ab321c96502ba1da` mapping in the
reference manifest: WeaponType SWORD view2 → Swordman selector1 →
EntityAction ATTACK2/group10 →80+direction (SOURCE-DERIVED, reused repository
evidence, not newly fetched source). Baseline retargeted anchors, contact names,
breathing and450ms attack presentation budget are ASTRAEON_INTERPRETATION.

## Identity and authoring contract

Inspected unchanged approved-warrior-seed.png, SHA256
`750ffe25056760c6ab97c3e66a3488d15aec4c875e573d9a8cef65c8f0437e05`.
Its source README describes an unchanged shipped-atlas crop used as identity.
Use compact youthful proportions, silver/lavender hair, reserved face,
bronze/ivory/navy clothes, teal waist, mustard cape, narrow steel/bronze sword,
painted shading and elevated camera. This grants no approval to new images.

The South guide references exactly Idle/S/key0 and its anatomical-right
mainHand socket. It is technical annotation, not production art. Generate
BodyCore, HeadBase, Face, Outfit, HairBack, HairFront and Weapon separately on
the same1024 canvas, compiled with one shared transform to320. Preserve raw
source, exact prompts, hashes and pose ID. BodyCore has a neutral underlayer,
no skull, hairstyle, class outfit, armour, boots or weapons. Head and body
overlap at the neck rather than meeting along an exposed cut edge.

South proof remains authoring-only until its visual gate passes. Do not fake
missing directions to construct a valid all-direction runtime AppearancePack.
Optional OffHand/Headgear/Cape/FX may be absent. Runtime bakes may combine
sources but never replace editable sources. Cosmetic and gameplay loadouts
remain independent. Female production and additional actions remain gated.
