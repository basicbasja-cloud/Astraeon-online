# Concept proportion review — v37

Latest user asks whether size now matches the original concept. **Head height looks close, but overall proportions are not locked.** Connecting the neck correctly in v36 did not establish that hairstyle width, shoulder breadth or camera projection matches the concept.

- [Measured current neutral and motion-rest comparison](proportion-review.png).
- [Bound observations](observations.json), [measurements](proportion-report.json), [audit](audit-report.json).
- [Actual coordinate inspection](current-coordinate-review.png).
- [Reusable receiver/proportion practice](../../../skills/modular-eight-direction-sprites/references/painted-neck-receivers-and-coherent-motion.md).

The original user quality references include a four-pose pixel example and two detailed silver-haired character illustrations. They are visible in the conversation, but their original attachment bytes are not retained locally; this was already recorded in [v10 provenance](../quality-review-v10/evidence/prompts.json). Do not substitute a later generated character or accepted walking frame and label it the original concept. No concept source file hash, automatic concept landmark detection or exact percent error is invented here.

The current neutral is408px high at alpha≥128. A manually reviewed visible chin landmark gives a crown-to-jaw height of approximately105px, about26%of the full visible height (roughly3.9head-heights). This is visually near the original concept's roughly quarter-height head, so another global head shrink is not justified by height alone. The raw full head layer includes the neck; its116pxheight must not be called the head's crown-to-jaw height.

The current projected head is129pxwide, while the manually reviewed outer armor edges span101px. That1.28ratio is a real current-image measurement, **not a1.28ratio against the original concept**. The concept reads as less broad-haired relative to the shoulders. However, current art turns more toward profile than the concept, so narrower projected shoulders do not by themselves prove narrow anatomical shoulders or justify stretching the torso. Current/motion rest images also have different projected head spans from slightly different authored head angles. Do not fit a different head scale per pose to erase that.

Next production step is one physically authored neutral at the intended concept camera, with an actual retained full-body concept reference for precise landmark comparison. Keep uniform scale and camera; review crown/chin, outer armor, belt, knee ornament/boot top and sole. Compare full-character height first, then independent ratios. If head height is right but hair silhouette is too broad, redraw the silhouette at the correct angle rather than squashing it horizontally or shrinking the whole head. Correcting shoulder projection requires the matching view; it is not a hidden-bone inference from this image. Do not transfer a static same-height comparison transform into runtime animation registration.

No new art or motion was generated or approved. No character/pose pixels were changed. The existing v36far-forefoot6.703pxcontact failure remains unresolved. The comparison plate uses one uniform scale per complete static image solely for review. Original concept observations remain qualitative; candidate numeric observations are bound to actual PNGs and explicitly manual chin/armor features. No universal proportion pass threshold is introduced from two unmatched views.

Reproduce from repository root:

```bash
python research/sprite-animation/proportion-audit-v37/compare-proportions.py
python research/sprite-animation/proportion-audit-v37/audit-evidence.py
```

Both commands are local NumPy/Pillow diagnostics. Successful audit means evidence/measurement integrity, not concept match or production acceptance. All prior v30–v36evidence and protected W remain unchanged. Work stays on the existing sole research branch.
