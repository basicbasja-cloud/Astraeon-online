# Production Factory V3 status and handoff

**Branch:** `character/production-factory-v3`
**Target:** Male Swordsman
**Updated:** 19 October 2026
**Overall:** `TECHNICAL_PASS / PAINTED_VISUAL_CANDIDATE / OWNER_APPROVAL_PENDING`
**Runtime admission:** `DEV_ONLY / NOT_APPROVED`

The V3 pipeline now has two ImageGen-painted review iterations for Idle, Walk, and BasicAttack. Iteration 2 uses a sharper fantasy-art prompt and is packaged as its own DEV_ONLY candidate with eight-direction GIFs. It has been reviewed in the actual game on the default Wayfarer Capital map. The art remains a fused character image, motion status remains `CANDIDATE`, six other actions remain placeholders, and owner approval is pending. V3 is not production-complete.

## Progress

### Completed

- Built the 60-bone action-free V3 Swordsman rig with stable root, eight unmirrored directions, and the six required structural guide passes.
- Selected free Mesh2Motion `Idle_Sword`, `Walk`, and `Sword_Attack` sources from a pinned CC0 bundle. Recorded file hash, source skeleton, license evidence, retarget details, events, and frame timings. No login or credential was needed; no V2 motion fallback is used.
- Completed the forced Blender 5.2.2 pipeline run. Preflight, retargeting, 192 guide records, six structural passes, and the procedural DEV_ONLY runtime package passed. The motion gate correctly remains blocked because all three clips are owner-review candidates.
- Updated [the Swordsman identity lock](../../authoring/characters/factory-v3/identities/swordsman_identity_v1.json) and [master prompt](../../authoring/characters/factory-v3/identities/swordsman_master_prompt_v3.txt): illustrated fantasy style, human balance and weapon grip, a grounded low sword sweep, and no trailing cape by default. `BackAccessory` remains an optional slot.
- Generated two painted Idle, Walk, and BasicAttack sheets with eight directions and eight frames each. The first iteration is retained for comparison. The sharper-prompt iteration has exact prompts, raw inputs, pose guides, hashes, normalized sheets, GIFs, and an import report in [paint job `imagegen-swordsman-v2`](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-v2/selection.md).
- For iteration 2, removed alpha haze and disconnected cross-cell fragments, applied one shared scale (`0.724771`) across all 192 frames, aligned cells to the V3 guide contract, and trimmed pixels outside a guide silhouette dilated by 6px. The normalized character is about 79px tall in a 160×160 cell; root remains `(80,132)`.
- Added the separate `swordsman-male-v3-painted-v2` DEV_ONLY package and a review route. Browser playback used the app's default streamed `wayfarer-regional-capital-v75` map, loaded 17 nearby world chunks, showed Idle, Walk, and BasicAttack at the safe plaza spawn, and completed with no page errors or failed requests. The attack clip contact marker is at `983ms`.
- Set the procedural runtime default Back part to transparent. The cape remains an optional separate `BackAccessory` part in that package.

### Current review GIFs

- [Idle, eight directions](evidence/imagegen-swordsman-v2/v3-ai-painted-idle-8-directions.gif)
- [Walk, eight directions](evidence/imagegen-swordsman-v2/v3-ai-painted-walk-8-directions.gif)
- [BasicAttack, eight directions](evidence/imagegen-swordsman-v2/v3-ai-painted-basicattack-8-directions.gif)
- [BasicAttack with cape on/off, earlier procedural comparison](evidence/v3-basicattack-south-cape-compare.gif)

Iteration 2 improves contour definition and removes detached edge artifacts after guide-mask cleanup. Some painterly softness remains at the 160px cell size; this iteration is a review candidate, not a claim of final art quality. All three exact requests are retained. The images have not been approved by the owner.

## Still partial

- **Visual quality and motion:** iteration 2 is the sharper review candidate. Idle remains subtle; Walk is clearest from side views; BasicAttack reads as a grounded fantasy sweep. The owner has not approved the motion or painted art.
- **Layering:** the painted character is one fused Body/Hair/Outfit/Weapon composite. Independent equipment layers and hidden surfaces are not present. Its empty Hair, Outfit, Weapon, Headgear, and Back slots do not imply that the fused sprite can be customized.
- **Other actions:** Run, Hit, Death, Dash, Guard, and SkillAction are placeholders and still need free-source review and production art.
- **Production approval:** the painted pixels are provider-generated, so no CC0 claim is made for them. The runtime package remains `DEV_ONLY`, `PLACEHOLDER`, `NOT_FINAL_ART`, and `OWNER_APPROVAL_PENDING`.

## Review route

Use the rendered GIFs above to inspect silhouette and motion at runtime cell size. The actual game route uses the default streamed map, Wayfarer Capital:

`?qa=1&swordsman=v3-painted-v2`

The route shows the candidate in the character creator and actual player renderer. Browser screenshots and the QA report are in [the Wayfarer Capital evidence folder](evidence/imagegen-swordsman-v2/). It does not mark the candidate approved or production-admitted.

## Remaining acceptance gates

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Canonical rig | **PASS** | 60 bones, stable root, zero V2 actions. |
| Free motion sources | **PASS for candidate use** | Mesh2Motion CC0 source and evidence recorded. |
| Idle / Walk / BasicAttack | **CANDIDATE** | New source, retarget and painted direction set; owner visual review pending. |
| Eight directions and structural passes | **PASS** | 192 records, six passes, unmirrored directions. |
| Painted identity and fantasy readability | **INTERNAL VISUAL CANDIDATE** | GIFs and actual game route available; approval pending. |
| No-cape default | **PASS for review direction** | Transparent default Back part; optional cape remains separately available in procedural package. |
| Independent painted layers | **BLOCKED** | Current paint is fused; separate BaseBody, Hair, Outfit, Weapon, Headgear, and BackAccessory art is not supplied. |
| Remaining six actions | **PENDING** | Static placeholders only. |
| Runtime package | **PASS as DEV_ONLY** | Schema/atlas validation passes; no production admission. |
| Actual game preview | **PASS as development-only** | Creator, Idle, Walk, BasicAttack, contact timing, and recovery verified in browser. |
| Owner approval | **PENDING** | Review the three painted GIFs and accept or request changes. |

## Validation record

| Check | Result | Detail |
|---|---|---|
| Factory `--stage all --force` | **PASS** | Blender 5.2.2; rig, motion, guide, handoff, and procedural package stages completed. |
| Motion production gate | **PENDING by design** | Returns `passed=false` while clips remain `CANDIDATE`; no retarget/build error. |
| Painted importer | **PASS** | 192 cells, shared 0.752381 scale, cleanup and alignment report written to the paint job. |
| Runtime candidate validator | **PASS** | Iteration 2: 9 clip definitions, 20,763,712 decoded atlas bytes, no schema errors. |
| Procedural runtime validator | **PASS** | 9 clip definitions; no schema errors. |
| Painted-sheet normalization test | **PASS** | Shared scale, alpha cleanup, full frame count, and guide-mask containment. |
| Development browser preview | **PASS** | Default Wayfarer Capital map; no page errors or failed requests; actual player showed all three selected clips. BasicAttack contact marker is at 983ms. |

See [the implementation record](PRODUCTION_FACTORY_V3.md), [build evidence](evidence/production-factory-v3-motion.json), [iteration 2 paint job](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-v2/imported/job.json), and [Wayfarer Capital browser report](evidence/imagegen-swordsman-v2/wayfarer-capital-review.json) for the full progression and provenance.
