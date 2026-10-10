# Free connected source pilot

**OWNER_SOURCE_REVIEW_FAILED / ABANDONED_SOURCE_PILOT.**

The owner rejected this source on 10 October 2026 for incorrect body proportions
and size, a pose that does not match the approved photo, and an unacceptable
grip. See `OWNER_FEEDBACK.md` and `owner-review.json`. Preserve these files as
failure evidence; do not resume this model as the next production candidate.
The painted parent concept remains approved. Technical validation below is
historical and does not override this rejection.

The owner authorized the free Blender route on 10 October 2026: "Now let make it".
This is a fresh MPFB-based body and rig, not the rejected mannequin, turnaround,
or image-card assembly. The parent painted concept remains the design reference;
this source model has no owner approval.

The workspace-local MPFB 2.0.17 release loads and creates a weighted body in
Blender 5.2.2 LTS. `mpfb-baseline.blend` is compatibility evidence only.
`source-master.blend` contains the new compact shape, real finger topology,
clothing surfaces, full scalp/locks, armor, boots and cape. `grip-master.blend`
adds one shared sword grip, required sockets, alternate blade and locked camera.
Source files are editable native Blender data. MPFB is needed to rebuild from
the scripts; opening the modeled Blender files does not require a provider.

Review: [review.html](review.html), eight-direction contact sheet and grip contact
sheet. W, NW, N and SE also have large hand inspections. Right glove, right bracer
and sword are isolated in those details; other anatomy/outfit/cape are hidden.
Complete views retain real occlusion. Outfit removal
restores the concealed body and hands. Blade swapping uses the same skeleton,
body and grip pose. No animation coverage is claimed from this single pose.

Technical results are in `source-validation.json`, `render-validation.json`
and `review-ui-validation.json`; they cannot approve visual quality. One scale
is selected for all eight views, with 320 x 320 canvas, root (160,264), and
176-pixel reference height. Gameplay review displays the entire canvas at 160
x 160, corresponding to an 88-pixel reference height.

The refinement plan formerly attached to this pilot is superseded by rejection.
The next source needs proportions and a pose matched to the approved reference
before detailing, followed by an anatomical grip review. This is
not a finished painted character, accepted production candidate or completed
factory. No runtime code or gameplay assets are replaced.

No paid provider job or new image-generation call ran for this pilot.
The proposed Tripo job remains on hold. MPFB core assets are CC0; addon code is
GPL-3.0-or-later and stays in the ignored local tool cache. No third-party clothes,
hair or weapon assets were downloaded. See `provenance.json` and `licenses/`.
