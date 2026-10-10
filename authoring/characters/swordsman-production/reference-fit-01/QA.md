# QA verdict: reference-fit-01

**NO-SHIP. Owner review pending for proportions and standing pose only.**

The source is a new body volume study. The unchanged painted concept remains
the design authority. Hero comparison, overlay, authoring/game scale, W/NW/N and
body-only views were inspected in the local browser. No technical metric grants
art or owner acceptance.

## Technical evidence

- Body: one connected component, 34,030 vertices and 34,030 quad faces.
- Zero boundary edges, non-manifold edges or loose vertices.
- Fixed orthographic camera, 320-square RGBA render, root (160,264).
- SE alpha height is 177 pixels versus the 176-pixel normalized reference.
  This one-pixel raster difference does not establish a silhouette match.
- Manual landmarks project within 0.000077 pixels of their assigned guides.
  This checks the coordinate mapping; the landmarks are not independent ground truth.
- Reference SHA256 is unchanged. All 50 files in the rejected free-master-01
  evidence manifest remain byte-identical. No rejected source was imported.

## Open defects and limits

- Major: the head proxy lacks the approved face and tousled hair silhouette.
  It cannot establish identity or painted-style acceptance.
- Major: hands are coarse masses; fingers, thumb, palm/handle contact, wrist
  alignment and hand-owned hilt coverage are unfinished.
- Major: costume forms and materials lack the approved detail and finish.
  Garment fitting, separation and attachment require later review.
- Major: side/rear volume, camera elevation and hidden joints are inferred.
  W/NW/N reveal depth but have no independently approved reverse reference.
- Blocker for production: dense voxel blockout is unskinned and needs authored
  deformation loops. No motion, modular export or factory coverage exists.

The narrow next owner decision concerns overall body/head size and relaxed stance
before investing in detailed sculpting and a fitted rig. The complete coherent
source gate remains ahead: identity, grip, fixed-view stability, outfit removal
and alternate weapon, then motion and painted sprite finishing.
