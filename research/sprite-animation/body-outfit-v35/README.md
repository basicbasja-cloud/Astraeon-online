# Body with outfit, not mandatory limb equipment slots — v35

The user identifies strange proportions in v34 and asks whether RO uses **body with outfit**. They are correct about the intended logical split. v32–v34 demonstrated a cutout rig with individual limb transforms; that technical proof drifted away from the intended production representation. Its numeric passes did not approve its proportions.

- [Original / v34 / new body-outfit comparison](proportion-comparison.png).
- [Head-size before/after, body unchanged](head-size-comparison.png): user identifies oversized head; default scale .45→.40,11.1% smaller around the same neck mount.
- [New neutral proportion candidate](preview/original.png), [complete body+outfit layer](preview/body-outfit.png).
- [Interactive head-style switch and body-only preview](outfit-preview.html).
- [Two-slot contract](slot-contract.json), [browser checks](browser-qa.json), [audit](audit-report.json).
- [Detailed know-how](KNOW-HOW.md), [source receipt](source/receipt.json), [exact user feedback](user-proportion-feedback.json).

The new example has **one coherent clothed body texture plus one complete head-style texture**. Its body includes torso, arms, gloves, legs, boots, armor, belt, tabards, scarf and cape. Every body feature receives one shared uniform transform; there is no per-arm/per-shin resizing. Changing hair selects a complete precomposited head style at the same neck mount. Independent front/rear hair may still be useful inside authoring, without becoming mandatory runtime layers.

The [pinned community roBrowser renderer](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/Entity/EntityRender.js) separately renders body, head, head accessories, weapon and shield. Body's ACT positional reference aligns the head. This supports logical equipment groups. It does **not** prove that every original-client body frame is one bitmap: ACT permits internal layers/transforms. In our pipeline a coherent full-body-with-outfit image per pose is the default export, with internal rig limbs retained only as optional authoring/diagnostic tools.

The old W art is the appearance comparison. v10 reinforces detailed materials only; no rejected walking/attack pose conditions this new neutral drawing. New body/head proportions and outfit details are **a review candidate, not user-approved or animated**. No new eight-frame motion is claimed, and existing accepted walking/smoothness evidence is untouched.

The equal-height board is a static visual comparison. Its source views/poses differ, so it is not a matched-camera shoulder-width measurement or an anatomy accuracy score. The next action must keep a coherent body/outfit per pose and one authoritative clock, with original art proportions checked before multiplying frames or directions.
