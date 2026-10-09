# BasicAttack painted-arm repair checkpoint

**OWNER VISUAL APPROVAL PENDING.** This package repairs 55 of 128 attack arm paintings and preserves the other 73 body cells. It is an owner-review candidate, not an approved production animation. The normal game and in-world review still use their previous appearance configuration; the new candidate is selected by `character-review.html`.

Branch: `character/ro1-reference-engine-v1`

Starting HEAD: `e0886e419212586161cd778d53e665a170a8f181`

Scope: BasicAttack only; eight authored directions, no mirroring, 16 frames, 450ms, presentation contact at frame7 / 170ms. All frame numbers below are zero-based. Final checkpoint identity is the commit containing this report; the final delivery records its SHA.

## Watch and inspect

| Evidence | Contents |
| --- | --- |
| [Focused owner GIF](swordsman-basicattack-anatomy-repair-owner-preview.gif) | 14.4 seconds; S, SW, W, NW, N, NE, E, SE; two normal attacks and one half-speed close-up per direction |
| [Normal-speed eight-direction GIF](BasicAttack-fixed-eight-directions.gif) | 450ms loop, all directions together |
| [Half-speed arm close-up](BasicAttack-slow-closeup-eight-directions.gif) | 900ms loop with a fixed crop, no hand-following camera |
| [Exact-timing APNG](BasicAttack-fixed-eight-directions.apng) | Original millisecond frame durations; GIF durations necessarily use 10ms quantization while preserving total loop time |
| [Body-only sheet](BasicAttack-body-only-eight-directions.png) | All 128 cells without Head/Hair/weapon/Cape; independent-head extraction gaps are intentional |
| [Joint overlay](BasicAttack-arm-joint-overlay-eight-directions.png) | Shoulder, elbow, wrist, grip; projected review estimates, including inferred occluded joints |
| [Priority before/after](BasicAttack-contact-priority-before-after.png) | Identical direction, frame, 320px canvas and scale; BodyWithOutfit plus independent Head |
| [Grip before/after](BasicAttack-grip-relation-before-after.png) | Identical fixed 160px crops enlarged 2× |
| [Contact grip debug](BasicAttack-contact-grip-debug.png) | Painted-arm landmarks and owned weapon pivot |
| [Loop boundary](BasicAttack-loop-boundary.png) | Frame15 beside the next frame0; retained stance changes are explicit |
| [Costume swap proof](BasicAttack-costume-swap-proof.png) | Same repaired anatomy and independent attachments in costumes A/B |
| [Alternate equipment](BasicAttack-alternate-equipped-eight-directions.gif) | Hair B, Sword B, shield and circlet |
| [Interactive review](../../../character-review.html) | Clean BasicAttack autoplay; play/pause, previous/next frame, eight directions, body/head/hair/sword/cape visibility, optional joints and anchors |

The folder also contains a body-only and composite strip for each direction, 128 individual assembled PNGs in `frames/`, desktop/mobile screenshots, and [artifact hashes](artifact-receipt.json). Use `character-review.html?registration=1` for the unchanged previous appearance pack. Previous review artifacts have not been overwritten.

## Diagnosis and actual changes

The main fault was painted retargeting: compressed or obscured upper arms and elbows, inconsistent sleeve/forearm volume, weak wrist-to-palm continuity and a low-hand recovery that jumped into a raised ready pose. The earlier five neighbour-pose substitutions also removed distinct contact/follow-through/return arm poses. A socket adjustment alone could not fix this chain. Torso and stance variation in the retained source contributes to the remaining loop discontinuity.

Worst directions were **SW, W and NW**. Highest-priority regions were SW4–9, W3/6–12 and NW6–9, plus recovery14–15 in every direction. NE6 also had a detached-looking fist; an intermediate generated NE6 with an extra arm was rejected and corrected. The real-motion review caught a further SW6 skull/arm overlap in the first repair. Its final isolated-arm painting restores a visible ivory upper arm and bent elbow outside the original Head.

ImageGen supplied localized arm paintings with the existing character as context. Authored limb masks integrate those paintings into the original body cells. No generated face, whole replacement character or RO pixels enter the appearance pack. Source paintings, prompts, rejected trials, selected cells, masks and normalization receipts are retained under `authoring/characters/builds/swordsman-basicattack-anatomy-v1/`. The active SW6 source is `SW-frame6-isolated-arm-sheet.png`; the full-body SW6 trial is retained only as rejected provenance. Its 1280px isolated element was normalized to 154px before the common 0.45 integration scale, as recorded in `arm-art-edits.json`.

| Direction | Re-authored frames | Result for owner review |
| --- | --- | --- |
| S | 6, 7, 9, 14, 15 | Clearer contact elbow and forearm; raised return arm |
| SW | 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15 | Connected loading arm outside the skull; distinct contact, follow-through and return paintings |
| W | 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15 | More readable loaded elbow; separate contact/follow-through and raised recovery |
| NW | 6, 7, 8, 9, 10, 11, 14, 15 | Rear attacking arm remains attached; distinct contact and return poses |
| N | 6, 7, 9, 14, 15 | Rear shoulder/forearm connection clarified; raised recovery |
| NE | 6, 7, 9, 14, 15 | Floating/extra-arm defect removed; connected rear contact and recovery |
| E | 6, 7, 9, 14, 15 | Elbow/bracer chain clarified; painted hand returns upward |
| SE | 6, 7, 9, 14, 15 | Contact sleeve/elbow clarified; raised return |

**Frames still reused:** the previous SW7←8, NW7←8, W10←11 and W14/15←13 retain their inherited non-arm torso/head/stance context. All five now have distinct new arm painting. No new neighbouring-frame substitution was added. Existing frame4/frame5 loading holds remain pixel-identical in S/NW/N/NE/E/SE; SW4/5 are similar but distinct, and W4/5 are distinct. These preserved loading holds were not an excuse to copy a broken contact pose. The 73 unchanged body cells retain the original source because surgical repair was the requested scope.

## Motion references and layer boundaries

See [the anatomy and motion comparison](MOTION-REFERENCE-REVIEW.md), [initial audit](AUDIT.md), and [RO reference reinspection](ro1-reinspection.json). Reacquired RO frames match the retained hashes. The renderer supplies four distinct projected attack sequences repeated across adjacent directions, not eight independent anatomical measurements. Actual one-handed sword-cut footage supports the preparation → acceleration → impact travel → deceleration sequence; its real-time durations were not imposed on this game. Raw RO ACT timing remains unverified.

**MotionTemplate changed: NO.** Original bytes, landmarks, root, canonical direction identities and durations remain intact. No new action or engine change was made.

| Layer | Change |
| --- | --- |
| BodyWithOutfit | 55 arm cells replaced within authored masks; royal costume uses the same corrected silhouettes; 73 cells and all pixels outside the masks remain unchanged |
| Head | No artwork or attachment change; original independent Head pixels protected during integration |
| Hair | No artwork or registration change |
| MainHand | Downstream grip follows repaired palms; E13's old cloth-point socket moves to its actual palm; frame14/15 sword presentation returns toward the ready angle/view |
| Owned swords A/B | BasicAttack-only transparent hand opening at the existing hilt pivot; original blade, guard and pommel preserved; body-owned fingers draw over the grip |
| OffHand / Headgear / Cape | No artwork or registration change |
| FX | Independent optional slot preserved; no RO slash artwork imported and no effect used to cover the repaired arms |

The owner's Ragnarok Alchemist Swords PNG was inspected before the weapon work. It contains grip openings and separate effect sprites; the PNG alone does not specify attachment coordinates or ACT timing. The implementation modifies our own sword pixels only. Idle/Walk still use the original sword atlases.

The requested [sprite-gen skill](https://github.com/aldegad/sprite-gen) is installed in the local project workspace at pinned revision `9935d674128e512ea9727168252bb544e68c8f69` (2.43.0): [installation receipt](sprite-gen-installation.json). It was used for independent `inspect-motion` checks with exact source durations, without mirroring or resampling. This is not an account-wide desktop installation. Reports in `sprite-gen-motion/` remain `needs-review`: planted-foot contact/stride was not established. Their duplicate warnings describe retained loading holds, not removed timing. All frame bounds are inside the canonical canvas.

## Validation

- **303 JavaScript tests passed:** [298 CJS checks](node-checks/report.json) plus [5 streaming checks](world-streaming-tests.log).
- **29 Python tests passed:** [log](python-tests.log), including 8 new mask, palette, palm, protected-layer and source-reuse checks.
- [Browser verification](browser-review.json): 128 attack composites; 328 same-clock costume swaps with identical independent-layer rasters; 200 unchanged Idle/Walk composites; controls, frame wrap, desktop/mobile and clean default debug state; no browser errors or unexpected HTTP responses.
- [Timing receipt](animation-timing.json): focused owner GIF 14,400ms, normal 450ms, half speed 900ms; exact-duration APNG included.
- [Protected-source verification](protected-source-check.json): original MotionTemplate, assembly engine, original appearance/assets and previous evidence unchanged. The existing protected-world/gameplay test also passes.
- JavaScript syntax, Python compilation and `git diff --check` passed. The first restricted Node run could not spawn `git`; the rerun in the permitted execution context passed without changing the test.

Reproduction from the repository root: `python tools/build_attack_anatomy.py`, then `python tools/package_attack_anatomy.py`; serve the repository on port8022 and run `python tools/export_attack_anatomy.py --sprite-gen /workspace/skills/sprite-gen/.venv/bin/sprite-gen`. The inspector option is optional and requires the locally installed CLI. Export uses Chromium through Playwright. Python authoring requires Pillow, NumPy and SciPy. Running these commands rebuilds only the new candidate/evidence paths.

## Remaining visual issues and acceptance

Frame13→14 recovery is still brisk at the protected timing, and the original torso/head/stance changes across frame15→0 remain visible. Painted limb volume and integration seams deserve scrutiny in the slow close-up, especially the rear projections and SW6. Joint overlays are 2D estimates, with interpolation on untouched/occluded joints; they are neither measured 3D bones nor gameplay authority. Source artwork still varies in projection. No automated result certifies anatomical realism or owner acceptance.

The candidate repairs the visibly missing/confused arm chains identified in this pass, but it is not claimed perfect or fully smooth. Review the focused GIF and frame-steppable page before accepting it. No Run, Hit, Death, Guard, Dash, Cast, SkillAction or other class was started.

**OWNER VISUAL APPROVAL PENDING.**
