# Shared-scale Mage contact study

One global scale (0.7387753851) and whole-master translations align the six new
keypose paintings against the corresponding source raster boot contacts. No
per-frame scale, limb warp, frozen legs or independently generated body pieces.

Maximum paired fit residual is 3.8899 authoring pixels, approximately 1.216
runtime pixels at the configured 0.3125 scale. This exceeds the proposed 1px
contact threshold. Screen-ordered raster sole points are not manually approved
anatomical landmarks. The fit is a diagnostic and is NOT a paintover acceptance.

![Contact review](contact-review.jpg)

![Keypose inspection only, not full animation](keypose-inspection.gif)

The transformed artwork remains unadmitted. Other landmarks (head, pelvis,
hands, knees, staff) require actual guide comparison and coherent master paint
correction. The six samples do not establish full 24-frame smoothness.

Reusable fit helper has three passing regression tests: one common scale with
translations, preservation of nonrigid residuals, rejection of coincident feet.
Frozen recipe and helper are retained beside authoring review outputs. Current
coverage remains 2/96, zero complete new characters; goal remains active.
