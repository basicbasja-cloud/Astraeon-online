# Swordsman Pickup SW: sparse head drift study

Status: **rejected draft; not admitted to runtime**. These are nonadjacent stills, not an animation. Source guide is the separately documented 35-sample Mesh2Motion kneeling study; pose and timing remain unapproved. Existing tall Swordsman baseline is unchanged.

The independently generated frame 06 had visible head-position drift relative to frames 04 and 08. The bounded repair combines an image-generated donor only within a feathered head/neck region; its receipt records no changed pixels outside that mask. It may also alter scarf or shoulder within that region.

As a warning signal, SAM2 proposals 0 and 2 compare movement of mask centroid against the guide head-bone movement after an unverified sole-based whole-frame vertical registration. For frames 04→06, residuals went from 7.46/7.18 to 3.62/3.42 runtime px; for 06→08, 7.74/8.13 to 4.35/4.68 px. These are two-frame gaps; masks include clothing or omit parts of the face and centroids are not anatomical landmarks. Lower numbers do not establish stability. The remaining difference, seam and altered anatomy require further correction, and the sole proxy itself is not certified.

Reproduce diagnostic: `python tools/character_factory_v3/audit_pickup_sparse_head_drift.py --output /tmp/pickup-head-diagnostic.json`. Mask proposals use SAM2 tiny checkpoint documented in the receipts; generator model/seed were unavailable. The still comparison is intentionally labeled to avoid implying smooth motion.

No accepted master, cutout, animation, gameplay binding, or completed character was produced by this study.
