# Logical equipment slots versus authoring limbs

## The user's correction changes the production default

The user observes strange part proportions in the latest pilot and asks for RO-like body-with-outfit. Bind the exact feedback to v34 bank/bind/render hashes. Keep v34's mechanical/pixel findings, but mark its appearance as correction-required and do not use its proportions as a new character template.

We had16–18 articulated render pieces in v32–v34, including separate upper arms, forearms, thighs and shins. That is an authoring method, not a requirement from the user or evidence that RO exposes those equipment slots. Individual width scales, source-adapted limb lengths and oversized decorative pieces can each look acceptable in isolation while producing the wrong complete character. Passing a planted-toe, matrix or hair-swap test cannot establish artistic proportion fidelity.

## What was actually verified in the RO reference

The existing pinned community `vthibault/roBrowser` source at commit `e4b5b53aa1f8b7e429bfa987ab321c96502ba1da` was reopened. `renderEntity` calls body, head, head accessories, weapon and shield separately; shield order changes with facing. `renderElement` selects the action/direction, reads ACT layers and uses the main element's positional reference to align the head. The source path/hash, permalink and short research excerpt are recorded.

This is community-client evidence, not recovered proprietary original-client code. Its body file is a logical character/clothing appearance group. It does not establish universal individual armor-item visibility, a separate base-skin layer below every outfit, or one bitmap per ACT frame. ACT internal layers and equipment slots are different concepts.

Our default slots now are:

| Logical slot | Contents / replacement unit |
| --- | --- |
| body_outfit | Complete clothed body with arms, hands, legs, boots and intended outfit accessories, for the required pose/view matrix |
| head_style | Complete compatible head/hair appearance; can be authored from base head/rear/front hair and baked into a head cache |
| headgear | Separate compatible head accessory, if actually produced |
| weapon / shield | Separate perspective/action-specific art and mounts, if actually produced |
| optional back accessory | Only when the game requires it independently replaceable, with full coverage/occlusion work |

v35 actually implements only body_outfit and head_style. Other slots are proposed contracts, not supplied assets. One outfit is not proof of clothing swapping; four head choices are not four views. Replacing an outfit later selects a complete compatible pose/view bank. Do not silently borrow another facing or attach a new sleeve to an old body without an explicitly reviewed alternative architecture.

## Establish proportions before multiplying poses

The user's accepted W appearance and v10 quality image supply costume/material identity. W's motion acceptance is scoped; v10's failed leg poses are not motion seeds. The generated body is a fresh neutral, headless, coherent drawing with both arms, boots, scarf and cape already integrated. Only the neck is an attachment seam. All body anatomy is drawn together before runtime composition.

The selected body uses one uniform rest transform: its neck receiver [434,225] maps to [250,180] on a512-square canvas and source near sole1430maps to480. This is a single authored neutral bind, not per-frame centering. Every head cache shares source mount[202,326] and target[250,180]. The first v35candidate uses scale.45; the user then specifically finds the head oversized. Default scale is now.40, an11.1%linear reduction, with the complete body texture/matrix and neck mount unchanged. Before/after uses identical canvases and body placement, without whole-character normalization. The old v34head scale was.52, but comparing those settings is not a measured anatomical percentage correction: body drawings and views also differ.

The new full character better preserves a continuous torso/shoulder/arm/hip structure by construction. That alone does not certify anatomy or make the new design user-approved. Inspect original versus candidate at native size and at one common whole-character height. Compare head mass, shoulder breadth, pauldron-to-upper-arm size, elbow/wrist placement, torso/waist relation, trouser volume, boot height/foot size, cape and tabard lengths. Where pose/camera differ, call the comparison visual only. Do not score screen shoulder width across different projections as an anatomical error.

For a new character, bind a same-view neutral reference and visible landmarks with declared uncertainty before numerical proportion scoring. Keep hidden shoulders/hips unknown. Record intended stylization in the character brief; do not hardcode this hero's head count, color thresholds or scale as a universal factory rule.

## Check actual alpha, not a misleading preview

The first generation appears to have a brown halo in the provider preview. Actual RGBA shows the sampled exterior pixels have alpha0, even when their RGB contains color. That RGB does not contribute under ordinary RGBA blending. No pixel cleanup is required or applied to the selected first image.

A second native cleanup request was made before inspecting RGBA. It redraws/rescales the body and is unselected. Retain it and the reason. Never describe it as a successful exact-pixel repair. White/slate/dark browser backgrounds review the actual composite; the selected raw file remains unchanged. This is a lesson to inspect the real alpha channel before spending another generation or trimming a valid asset.

## Scope the prototype honestly

The Canvas preview draws exactly one body texture and one head texture. Original/silver/auburn/bald head caches come from the preserved v33 bank; all share the same mount and selected scale. Ten actual browser checks include instrumented two-draw execution, unchanged body pixels/neck mount under size changes, uniform transforms, missing-head rejection and background review. There is no bone animation in this neutral prototype, no extra frame generation and no new outfit bank. It is a **proportion/representation candidate**, not a replacement animation or a completed factory.

The old image-joint/continuity tools remain useful for guiding/reviewing whole-body redraws. A source rig can have many bones internally; that does not dictate shipping those limb images. After the body proportions are established, create coherent body-with-outfit poses on one source clock, then align the head/accessories and recheck limbs, contacts, placement and exact frame continuity. Flattening the already-wrong v34 limbs is not a proportion fix.

## Reproduce

From repository root, using Python/Pillow/NumPy and Node/Playwright/Chromium:

```bash
python research/sprite-animation/body-outfit-v35/build-preview.py
node research/sprite-animation/body-outfit-v35/export-preview.cjs
python research/sprite-animation/body-outfit-v35/build-comparison.py
python research/sprite-animation/body-outfit-v35/audit-evidence.py
python research/sprite-animation/body-outfit-v35/freeze-evidence.py
```

The browser launcher must be allowed by the current sandbox. No rebuild invokes MiniMax or any image provider. New art requires explicit new generation; this package retains both actual raw outputs and prompts. Keep all v30–v34/protected-W evidence unchanged and work/push only on the existing research branch.
