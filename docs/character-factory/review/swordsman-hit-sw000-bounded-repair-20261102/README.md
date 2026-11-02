# Swordsman Hit SW 000: bounded donor patch

**Rejected.** The v3 target-guided donor was downsampled into the fixed 320px authoring crop and its RGB was applied to 2,281 source-master pixels within a fixed rectangle and alpha threshold, keeping original alpha and every pixel outside the mask unchanged. [Before/after close comparison](comparison.png). The result has a white wedge beside the forearm and broken sword continuity. The donor's apparent white background, silhouette, color and registration cannot be substituted safely using this simple threshold; outside-mask equality does not make the inside correct.

[Rejected candidate, mask and hashed receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-sw000-bounded-repair-20261102/receipt.json). The original 768px draft and unbounded v3 donor remain preserved. No canonical or runtime asset was overwritten, and no animation or gameplay was accepted.

Reproduce in a fresh directory: `python tools/character_factory_v3/review_hit_sw000_bounded_repair.py --output /tmp/hit-sw000-bounded`. The script verifies outside-mask pixels and output overwrite refusal; it does not establish visual correctness. The next repair needs verified donor registration and matte/occlusion with coherent sword and costume, followed by a full pose and continuity review.
