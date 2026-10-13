# Dataset contract: references, observations, source motion and original production

This contract is our proposed engineering practice. Current data is a **research reference corpus**, not a training-ready licensed dataset or an accepted character animation package.

## Dataset layers

| Layer | Contents | Authority |
| --- | --- | --- |
| Discovery | sources.json, search-log.json | A lead exists; no pose/capture claim |
| Retrieval | retrieval.json, trees.json, pinned-details.json | Exact fetched page/file bytes and commit; not automatically read or approved |
| Acquired sample | downloads.json, open-data/, clip-inventory.json | Specific archive and actual serialized clip records |
| Native raster capture | captures/*/capture.json + lossless frames | Actual GIF presentation times/order/pixels |
| Source evaluation | preset-samples.json.gz | Actual Blender-evaluated world joints at explicitly selected source key times |
| Observations | image-review.json, annotations/ | Only marked visual observations; hidden properties remain unknown |
| Proposed adaptation | motions.json, MOTION-RECIPES.md | Suggested RPG families, phase semantics, contacts and event names |
| Original production | future character/action/parts package | Separate authored bytes, runtime, QA and user approval |

Do not sum records from different layers into one “number of correct frames”. Multiple facings, repeated GIF holds and nine samples from one clip remain correlated examples.

## Identity of a sample

Use source_id + pinned commit or archive SHA + asset path + clip/action + direction + source time/frame ordinal. Keep these distinct from the character/item identity we will author.

Video/GIF record:
- source URL and source container SHA;
- decoder/version, source ordinal, PTS, exposure duration, fixed crop;
- source canvas and output canvas;
- frame file SHA and decoded RGBA SHA;
- declared/observed camera status;
- shot boundaries and transition/title cards;
- any storage conversion, original frame SHA and exact pixel check;
- original actor ID and visible facing, both unknown until reviewed.

Rig record:
- GLB/archive SHA, bundled license SHA, importer version and fps set BEFORE import;
- named animation, exact native input times, interpolation type;
- bone/node names, hierarchy, local/rest basis, world/root/object transforms;
- explicit times at which the rig was evaluated;
- root-motion mode measured from tracks, not assumed from “RM” name;
- source meshes/sole/palm/prop surfaces if evaluated;
- contacts unknown until surface data and interval evidence exist.

Sprite atlas record:
- image SHA, grid/cell rect, source frame/row ID;
- descriptor/code clock only if bound to the same asset/version;
- repeated frame IDs retained;
- one-shot/loop/back-forth/terminal-hold semantics;
- per-frame offsets/anchors/layers if actual source provides them;
- gameplay event clock separate from display duration.

Current isometric atlas boards preserve cell IDs but have UNKNOWN playback time for that archived PNG. The current Flare text descriptors are a separately pinned source. Similar column layout is not sufficient to transfer its timing to the archive.

## Observation schema

Each visible landmark includes coordinates, visibility, anatomical owner, uncertainty, evidence_kind and reviewer. Use one of:
- observed_pixel: directly visible contour/surface;
- source_evaluated: actual source rig value;
- estimated: a proposed hidden location with uncertainty;
- unknown: absent or ambiguous.

A source_evaluated joint in a source rig is not an observed_pixel joint in a redraw. Screen-right foot is not anatomical right. An inferred hip covered by a tabard is not known because a tool has filled in coordinates.

Keep clip semantic labels multi-valued and interval-aware. A character may walk while carrying and looking. A block impact may coincide with a torso recoil. BABEL motivates temporal multi-label annotation; we are not importing its restricted data.

Contacts need owner, surface, target, interval, evidence and contact_type. Proposed phases from motions.json are **requirements**, not observed contact annotations.

## Usage buckets

Record licenses per actual item, not per website or repository:
- creator CC0: the exact acquired Quaternius and legacy KayKit GLBs/licenses are retained as reusable external source study data;
- attribution/open art: source credits and item conditions follow derivative reference boards;
- provider terms: account/download/use conditions; no paid pack is counted as acquired;
- restricted research datasets: papers/license pages only unless the intended use is actually authorized;
- commercial game footage: observational reference; never incorporated into original shipping sprite parts;
- original art: independently authored appearance and motion with a separate receipt.

We have not bought content, logged into Mixamo/Rokoko/ActorCore, executed downloaded skills, trained a model, agreed to restricted dataset enrollment, or run paper inference. Reading an external SKILL.md does not authorize its instructions to install tools, submit paid jobs, or message others.

Source pages are locally cached in local-cache/ and excluded from Git. Published records are bounded receipts, original analysis, openly licensed selected source assets and attributed diagnostic study boards.

## Counts and exclusions

The authoritative count comes from clip-inventory.json, not provider marketing:
- serialized animation records include rest poses;
- dash clips stay in acquisition inventory so provenance is complete;
- dash clips are now included for optional research after explicit user steering; no gameplay mechanic is committed;
- rest poses are calibration data, not motions;
- non-dash candidates may still be irrelevant, unsuitable, stylized or missing body chains;
- a bone/node count establishes available structure, not animation quality.

The legacy KayKit GLB has only six skin joints: head, body, left/right arm and hand slots. It is not suitable evidence for anatomical walking leg-chain validation. The updated provider pack is a separate version and has not been acquired in this round.

Dataset ingestion must never whitelist a clip merely because its name says sword/walk. Manual semantics and actual visible review remain required.

## Train/dev/test strategy when model training is actually proposed

Current corpus is not ready for training. Before any model use:
1. resolve training, commercial adaptation and redistribution rights for every source;
2. separate restricted/observational material from trainable content;
3. assign split by original actor/subject/game/pack/clip family, not random frames;
4. keep duplicates, alternate encodings, mirrored copies, neighboring time windows and overlapping crops in the same split;
5. hold out some actors/costumes/items AND some views/actions;
6. maintain a dedicated negative bank for anatomy swap, contact drift, event mismatch and silhouette collapse;
7. measure quality on independent annotations and native-speed review;
8. document biases: humanoid-only sources, sparse casts, preview montage cuts, limited camera/weapon diversity.

Nine pose samples from one GLB clip are not nine independent human performances. 745 montage frames are not 745 independent examples of RPG attacks. More bytes do not establish diversity or error-free generation.

## Capture policy

Preserve native presentation times. Do not convert every clip to a common FPS before analysis. Select bounded windows by exposure onset and keep full selected exposure duration. Title cards/camera cuts remain in the full capture but are excluded from motion intervals.

For animated PNG/GIF/WebP, verify timing is actually present. A still atlas has no animation clock. For video, use decoded frame ordinal and source PTS, with the actual final exposure if available. Missing timing is unknown/refused, never silently guessed.

A fixed rectangular crop is one recorded transform for the shot. No per-frame trim, scale, align, mirror, optical-flow warp or registration used to make a bad motion appear correct. Model-required resampling is a separately generated adaptation with explicit mapping back to source times.

Storage in this corpus converts PNG frames to lossless WebP; all original decoded RGBA bytes were compared before the PNG moved into ignored local cache. This is not interpolation, alpha removal or pose modification. Both old PNG file SHA and new storage file SHA are retained.

## Annotation and agreement

Begin with an empty observation template. Use actual imagery/source values, record ambiguous overlap and retain disagreements. For future accuracy claims create an independent double-reviewed test set; measure agreement per side, visibility and action family.

Do not score unknown joints as correct. Do not estimate a source-derived contact and later test the artwork against the same estimate as an independent truth. Keep calibration landmarks separate from held-out validation landmarks.

Current annotations remain mostly unknown. image-review.json records only the boards actually inspected. Other boards are generated and available, not silently fully reviewed.

## Packaging and reproducibility

Open-data/ has two exact creator-licensed GLBs plus bundled licenses. clip-inventory.json includes native input times and hash bindings. preset-samples.json.gz binds actual source evaluation. preset-board-manifest.json binds diagnostic projections. Captures contain source PTS, storage image hash and exact RGBA hash.

fetch-evidence.py/acquire-open-samples.py resolve public sources; rerunning live web retrieval creates new receipts, so freeze a corpus version before analysis. Do not overwrite old evidence with a moving branch and keep the same dataset ID.

To reproduce captured GIFs, fetch the exact public URL into a local file, verify downloads.json SHA, then run capture-reference.py into a NEW folder. Run compact-captures.py only after successful native capture. There are no credentials or signed private download URLs in the committed receipts.

## Release boundary

Reference corpus validation PASS means provenance/timing/pixel/structure checks passed within their declared scope. It is not art/anatomy/acting approval. No production asset index is updated by these scripts.

Required before a production motion: approved original appearance; action/facing/event contract; independently reviewed body/prop mechanics; actual painted owner/contact/continuity checks; complete interchangeable parts; wardrobe extremes; runtime transitions; exact-byte user acceptance or authorized artistic review scope.
