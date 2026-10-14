# RO-like logical equipment groups

Latest user corrects v34 part proportions and asks for body with outfit. Read [v35 comparison](../../../research/sprite-animation/body-outfit-v35/README.md) and [detailed know-how](../../../research/sprite-animation/body-outfit-v35/KNOW-HOW.md).

Default production unit: one coherent body+outfit per pose/view, plus compatible complete head/hair style, headgear, weapon/shield and only expressly needed independent accessories. Rig bones and limb cutouts are optional authoring/diagnostic machinery, not mandatory player equipment or runtime slots. Do not flatten a rejected limb assembly and claim its proportions were repaired. Internal rear/front hair may bake to a complete head-style cache while remaining editable.

Pinned roBrowser actually renders logical body/head/accessory/weapon/shield groups and aligns the head to the body ACT position. Community-client evidence does not prove proprietary-client implementation details or one primitive image per body frame; ACT may contain internal layers/transforms. Do not assume each armor inventory item changes body pixels.

Compare original art proportions before multiplying frames. Establish a same-view neutral character reference; inspect head, shoulders, armor, arms/hands, torso, hips, trouser volume and boot/cape/tabard scale. Different-pose/view equal-height boards are visual comparisons, not numerical anatomical accuracy. Whole-body continuity/contact tools remain required after redraw.

V35 supplies one genuine coherent generated outfit and reused complete head caches with one rest bind;10browserchecks prove actual two-draw rendering and unchanged body under head/size changes. User then flags head size: default.45→.40reduces the head11.1%around the same neck mount; retain same-canvas before/after. It is one neutral proportion candidate, no animated/outfit-swap/fullfactory/user-art approval. Keep v34's user criticism and exact older evidence. Actual alpha0 exterior RGB is invisible under correct blending; inspect RGBA before attempting cleanup.
