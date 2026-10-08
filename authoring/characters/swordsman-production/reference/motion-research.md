# Auxiliary motion references

Reviewed 2026-10-08. These references are clarity/readability benchmarks only. The unchanged
owner-approved Warrior seed remains the character identity/style authority.
External sprite pixels are not used in ASTRAEON runtime artwork. Per the owner's
clarification, supplied references are **minimum quality/readability benchmarks**,
not templates for proportions, layout, exact poses or timing. ASTRAEON's measured
identity, 45-degree camera, 320×320 registration and independent motion/timing
remain authoritative.

- Owner-provided [eight-direction walking study](https://es.pinterest.com/pin/53058101855829875/):
  inspected in the browser. Compare distinct stride phases, alternating contact,
  body scale, grounding, eight-direction silhouette and gameplay-size cadence.
- Owner-provided [Ragnarok Online walking NPCs](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/127670/):
  page metadata accessible through its older `/sheet/127670/` URL; the direct
  browser page and image were blocked by the site's bot check. No claim of
  inspecting its actual frames is made.
- Owner-provided [Ragnarok asset 141222](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141222/):
  inaccessible through both browser and search fetch; identity/title unresolved.
- Supplementary Swordsman archive listings:
  [male](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141350/),
  [female](https://www.spriters-resource.com/pc_computer/ragnarokonline/asset/141255/).
  Listings distinguish rendered body variants under the same class name.
- [Monmouth University's walk-cycle instruction](https://animation.monmouth.edu/instruct/animation/walk-cycle/):
  reviewed contact, passing, down and push-off sequence, opposing limbs, and
  omission of the duplicate final loop pose. Shared source motion follows these
  general principles; no poses or timing are imported. ASTRAEON's gait was
  independently constructed before these references were supplied.

## Reinspection following owner rejection

The owner rejected Walk 14 and the subsequent west repaint. Re-read the actual
Pinterest image in the browser on 2026-10-08. Its side and diagonal views make
support versus swing unambiguous: the support leg extends under the pelvis;
the other knee flexes and its foot passes through; alternate contact reverses
the silhouette. Our attempts preserved a low, bent support leg and stiff torso,
then stretched standing trouser paint over it. Better boot painting retained
that faulty gait and cannot pass. Reject both motion and painting together.

The next authoring strategy computes pelvis height from the supporting leg's
near-straight arc and uses anatomical ankle/contact pivots, followed by a
separate untextured pose review before painted-frame acceptance. The existing
repository's `tools/author-warrior-gait-v51.py` documents the same crouch failure
and provides an original analytic heel/sole/toe construction to study. Its 3D
artwork is not an identity authority and will not ship. No external pixels,
coordinates, proportions, layouts or timings are transferred into ASTRAEON.

## Direct owner-uploaded sheets

The owner subsequently uploaded the actual `NPCs (Walking).png` (984×1034)
and `Classes (Female) - Novice.png` (679×778). Both were directly inspected,
including enlarged side-walk and NPC walk crops. This supersedes the earlier
inability to inspect the walking NPC frames through the blocked website.

The clearest benchmarks are an upright body, distinct support/passing/contact
silhouettes, heel-to-toe boot action, modest knee lift and weight transfer with
opposed arms. The owner explicitly requested ordinary walking, not running or
raised-knee marching. Accordingly the independent ASTRAEON candidate reduces
stride, swing clearance and arm travel, and uses a 1120 ms preview cycle. The
PNG sheets themselves do not establish playback durations; none are inferred
or copied. No external frame coordinates, layouts or pixels enter runtime art.

Paint inspection also found a separate compositor defect: static original
trousers remained over the reconstructed moving thighs, and the knee armour
was split/duplicated across two rotating patches. Repair these source masks;
motion formulas alone cannot correct that painted overlap.
- [CMU Graphics Lab motion database](https://mocap.cs.cmu.edu/): discovered as
  an optional motion source. No data imported; direct fetch timed out.

The malformed supplied Spriters Resource link was explicitly separated into
assets 141222 and 127670. No paid generation provider or new account was used.
