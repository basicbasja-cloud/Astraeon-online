# Detailed continuation handoff — v61

Transfer date: 2026-10-17 UTC. Branch: `research/modular-sprites-full-body-2026-10-11`. Parent published commit: `4299c18d07b99ee64a21a5df5f27a5b0b85c9238`. The new commit containing this file is the transfer revision; use `git log -1` for its exact SHA.

## 1. Latest user intent and authorization

The user now needs to transfer this work: “เขียน handoff อย่างละเอียดพร้อม file map แล้ว push เลยครับ ต้องส่งต่อแล้ว”. Package, commit and push the current state. Do not keep generating art before transferring. Earlier instructions to wait until all actions pass are superseded **only for the transfer timing**. Work is unfinished and must be described honestly.

The underlying request remains: repair the original Astraeon character's animations, research external references especially RO, inspect every frame, loop through fixes and verification, embed GIFs in reports, and build reusable checks. The user found earlier segmented animation cut-looking with missing knees. Monthly ChatGPT built-in image generation is explicitly authorized; no further cost confirmation is needed. External paid providers, purchases and new credits are not authorized. No subagents. No main edits or force pushes.

## 2. Required architecture and art constraints

Runtime slots are (1) one complete posed body including outfit/cape/scarf, hands, thighs, knees, shins and boots, (2) one complete head with hair, (3) optional weapon, (4) optional weapon trail. Internal segmented rigs may supply pose guides, but their parts must not be the final runtime body. Equipment may eventually require front/back physical passes; the current exporters require one fixed order.

Original neutral art is `../core-family-v56/frames/idle/<view>/00.png` relative to the case. Eight native facing views are required for the asymmetric outfit: never mirror the final character. Never fit individual pose boxes, translate individual final frames to hide bob, clone/patch shoes, squash a torso or quantize painted art. Fixed equal-grid extraction, alpha matting without changing retained source RGBA, a uniform whole-plate resize from known grid aspect, and one neutral-only calibration shared by a bank are technical operations already used. A guide may be transformed/collaged only when clearly identified as a guide; final pixels must be native art.

The source canvas is 512×576. The 399px standing reference comes from the accepted historical original; different actions must still preserve head/body family. Numeric crown or sole passes are only bounded observations. They do not prove anatomy, gait phase, hidden joints, hand grip, cape secondary motion or complete head swapping.

## 3. Scope and status

Finite scope is 9 actions, 48 authored direction clips: idle8, walk8, sit8, pickup4, ready4, unarmed attack1×4, hurt4, dead4, skill4. Sit and dead currently mean terminal holds, not entry/exit transitions. Other weapon families/statuses are outside this finite core. RO body-direction pairing is S/SW, W/NW, N/NE, E/SE for the 4-facing actions; do not infer universal head aliasing from body aliasing.

`STATUS.json` records all48 clips and the old964 exposure inventory. This inventory is not an approval. Old v56 acceptance was superseded by the user's missing-knee/cut-body complaint. Baseline provenance: 19 segmented clips need replacing, 4 hurt rest-mesh reactions need replacing/review, and 25 whole-pose source clips remain eligible for fresh inspection (20 static, 4 skill, N pickup).

### Pickup: three technically verified candidates

- **S-candidate7:** 8 keys →16 forward/reverse exposures, 90ms×15+550ms =1900ms. Whole original neutral is first/last. Crown maxstep32px/excursion173px passes inherited motion profile. Visible screen-right sole X5/Y2 and screen-left X5/Y3, same6px budget. Full arms/knees are native whole poses. `head-extraction3` is the last technical mask. Actual browser is `layer-player2`, native SPA file `native-editable2`, fast native writer `native-format2`; each passed its actual comparison. New head fringe/family finding prevents production acceptance.
- **W-candidate2:** 8 keys →16 exposures, same clock and neutral lock. Crown maxstep32/excursion147. One visible overlapping sole X6/Y5 passes6px; hidden second sole is unproved. Final technical mask `head-extraction4` uses tight inference context for key6. Browser `layer-player`, native `native-editable2` pass. Earlier hair-only head/incorrect face prompts remain negatives.
- **E-candidate1:** 8 keys →16 exposures, crown maxstep31/excursion137. Correct visible E foot ROI[200,465,330,515] gives X2/Y3. Copied W ROI cropped the toe and remains UNKNOWN evidence; the6px limit was unchanged. Final technical mask `head-extraction3`, browser `layer-player`, native `native-editable3` pass. First native-editable2 hit a real SPA timeout during concurrent jobs; serial fresh3 succeeded.

All three browser players were actually tested: 48 rendered frames, exact composition over gray, authored frame boundaries, play/pause/quarter speed/seek, slot controls, no page errors/network. Native exports compared all16 frames each, visible RGBA+alpha and clocks. These facts do not certify full masks or art.

### Ready candidates

8 native drawings →24 authored exposures using 3 holds/key and old40/50ms clock. S-candidate1 too tall/floor too low: rejected. S-candidate2 soles pass, crown range1/maxstep1. W-candidate1 visible sole passes, crown6/3. N-candidate1 soles pass but crown10/6 **fails**6range/3step. E-candidate1 soles pass but crown8/6 **fails**. Do not loosen limits. Imagegen job30 is a new N redraw but has NOT been imported or measured; do not replace candidate1 status with a presumed pass.

### Walk candidates

S-walk-candidate1 and W-walk-candidate1 each have 8 real drawings →80×10ms exposures (100ms per drawing). Both crown range2/maxstep2, horizontal step<1.5px, within3step/6range/3horizontal. Full phase/visible leg ownership, family, masks and actual player/native review remain pending. Other six views only have guides; no new whole-body bank.

S uses job27 except keys5/6 from job29. Job27 repeated the screen-right leading leg; textual job28 failed to repair it. Job29 is a fresh native whole-body two-panel redraw from an explicit leg guide. **The guide alone** reflected symmetric lower-leg region[128,392,256,504]; final asymmetric costume was not mirrored. One neutral0-only bank calibration applies to all8.

W uses job21 keys0/2 and job22 keys1/3/4/5/6/7, one fixed guide inverse scale1.25, dx16.25, dy−100. Large arm arcs/near-far phase still need review. Jobs23/24 failed to create genuine halfway poses: do not count16 real walk drawings. Job26 has an entire second-row figure/floor shift around20px; reject rather than per-frame fit.

Attack4 and hurt4 have no new accepted whole-body replacement. N pickup, static20 and skill4 need fresh head/family/full-view QA. No clip currently has fresh complete production acceptance.

## 4. Most important current blocker: head ownership and family

Generated upright heads drift in width/style across actions. A promising RO-like approach is to reuse canonical original head pixels over each coherent body. A S-ready prototype looks naturally seated on the neck, without body warping or extra neck painting. It is **not production ready**.

MobileSAM masks inset painted hair fringe, leaving head pixels in BODY. On original upper-hair source ROI x100:390/y65:180, opaque wrongly owned pixels were S162, W175, N125, E188. Recomposition is exact because those pixels were not deleted; swapping heads would leave hair ghosts. Zero prompt violations and exact RGBA cannot prove semantic ownership. The earlier claim “complete visible head” in some JSON/title strings is superseded.

New `tools/sprite-head-ownership.py` takes explicit full-head fields, neck separator, SHA-bound source and protected head/body regions. Current contracts `S-head-fields.json` then `S-head-fields2.json` cover original S plus8 ready keys. First broad field appeared to pass limited ROIs but retains gold collar pieces. Adding lateral-hair protected regions correctly makes second contract FAIL:12–24 opaque left fringe pixels excluded on each ready pose. Original frame0 passes those limited regions but still includes gold; semantic FAIL remains. Inspect enlarged `S-head-field-detail.jpg`, plus S-ready source/original coordinate closeups.

Next refine the **neck boundary and protected evidence** against actual pixels: original chin around(255,206), neckskin~212, collar~215; gold left~(220,208), right~(285,201). Ready chin~(255,201), gold left~(219,198), right~(287,193); brown hair spikes near(210,193) must stay HEAD. These are inspection starting points, not automatically correct contours. Canonical W/N/E/diagonal fields are not authored. Do not reuse this S polygon universally.

## 5. New reusable root tools

- `tools/sprite-head-mask.py`: pinned free CPU MobileSAM, point/box/context prompts; inference crop only, returns full unchanged canvas, disjoint ownership/exact visible recomposition. Existing16 controls pass. Hair fringes remain a semantic limitation.
- `tools/sprite-head-ownership.py`: manual head-field/protected-region ownership check. Preserves source pixels, detects the current failed contract. No automatic head/factory approval.
- `tools/sprite-layer-player.py`: SHA-bound offline four-slot player; exact full-source comparison, clock and controls. Four genuine malformed input controls rejected before output.
- `tools/sprite-native-package.py`: lossless public .aseprite format writer with compressed and linked hold cels; independent supported live SPA inspect/validate/export comparison. Actual S16 roundtrip passes (16 compressed+16 linked cels). `plan run` cannot import images; do not bypass capability gates or introduce Lua fallback. Sequence exports are chunked to max40 frames for16M pixel limit.

Existing `sprite-review-pack.py`, `whole-body-toolchain.py`, contact/motion tools remain unchanged. img2game2d atlas S16cells is exactRGBA/clock. Old native-file writer experiment missing export destination is retained as negative; native-format2 fixes creation before export. Native .aseprite writing is asset packaging, not art generation.

## 6. What to do next after transfer

1. Verify this transfer read-only; restore only into disposable work paths using REPRODUCE.md. Read current STATUS before historical logs.
2. Solve S canonical-head fringe/collar ownership with stronger protected regions and enlarged visual review. Recompose both original identity and canonical-over-ready. Check neck hole/extra collar, complete hair, and head/body family. Then author the other7 canonical views. A native neck underpaint is needed only if an actual hole is observed.
3. Revisit all three pickup head banks with complete fringe checks and explicit pose/family inspection. Bending head pitch may require native pitched heads, not one upright asset blindly pasted everywhere.
4. Import/measure N-ready job30 using existing fixed-bank geometry; redraw N/E if still failing. Keep failed reports, do not relax bob limits. Complete ready masks/native/browser review.
5. Inspect S/W walk phase with external RO phase guides and anatomical ownership. Do not use failed midpoint art as new keys. Finish six other whole-body walk views and repeat full QA.
6. Author coherent unarmed attack4 and hurt4. Do not reinstate segmented old own attacks. Fresh-review eligible N pickup/static20/skill4, including head bank.
7. Re-run source-bound motion/contact/family/ownership checks, native exports, actual browser clocks/composition and GIF playback on final chosen pixels; update each of48 statuses truthfully. Only then discuss all-action completion.

Freeze all published <=v60 and W13. Root AGENTS.md/HANDOFF.md and the existing skill remain unchanged. This v61 case is a transfer snapshot: new art should go in a fresh v62 case or private mutable scratch, never overwrite its evidence. No work/, model caches, venvs or binaries in Git.

## 7. Reading hierarchy and stale receipts

Current entrypoint is root CURRENT_HANDOFF.md → this handoff → STATUS/FILE-MAP/REPRODUCE. Snapshot checkpoint.md and checkpoint-live.md are historical and explicitly superseded: earlier cost questions are resolved, first23-job counts are now30, mask completeness was disproved, and no longer wait to transfer. Original model-provenance.json describes the segmentation installation stage (0 imagegen jobs at that stage), not total v61 jobs. Generation ledger now records30. Never propagate these historical counters into new claims.
