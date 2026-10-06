# RO3 town composition review — source70 / cache76

Branch `codex/world-pipeline-v3-proof`; source `authoring/wayfarer-spatial.blend`.
The curb/paving/lighting step was pushed as `a445c16`. The town composition source
and full native review continue in this checkpoint.

The ten supplied `RO3 Ref` images guide the whole town: public vs building-side
stone, curb height/profile, facade relief, roof palette, scale/density, planted
margins, evergreen form, fountain seating/flowers, sunlight and cast/contact shade.
Reference pixels are not imported into game textures. Original street/bough
artwork is packaged losslessly at its actual1254² dimensions, with editable masters.

- Public streets and court use medium irregular rounded stones in loose arcs;
  building walks, stairs and private aprons retain aged rectangular flagstones.
- 629 native curb blocks rise .20;618 widen .30→.40 outward into building zones.
  Dark vertical fascias improve legibility. Crossings and service gaps remain.
- Warm sun [1.18,1.05,.79], neutral warm fill [1.04,1,.90], strength .65/fill .44,
  down-left review-camera casts and eight rays at angular radius .018 replace
  the cool blue tint. Native eave/foundation contact shading remains.
- 54 rooted trees use eight tapered tiers of curved, textured boughs; two civic
  broadleaf accents remain. Original trunks/collision/placement frames stay. Original-alpha ray baking supplies self-shade between branch tiers, with no new per-frame rays. The first pale-tree native trial was rejected and retained in `tree-light-trial/`.
  Six safe owned grass beds and42 broader verge strips stay outside through-roads,
  solids and service approaches. Six inherited grass strips retract within their
  own footprint to avoid curb steps;38 clumps follow the taller native curb.
- Facades gain436 carved band/diamond parts and124 open shutters. Six houses use
  muted rose tile alongside terracotta/ochre, and fountain benches use sage green.
- The37 house envelopes and existing density layout remain. The tiered fountain
  keeps its celestial figure, water levels, four corner beds, four benches and
  four cascades, now in the distinct public stone court.
- The rejected stone-image wear pads remain absent.160 native tufts root in the
  actual paving joints, independently checked against UVs and image luminance.

Native evidence uses1280×666 world buffers, pixel ratio1 and camera160/yaw25/pitch46,
with ordinary camera controls. The parity test intentionally translates the Hall in RAM and expects a stale-bake diagnostic; it never saves that temporary edit. Fixed save positions are a screenshot fixture;
ordinary input is verified separately. The comparison page provides references,
matched before/after captures and final district views. NPC frames can differ.

Saved-source checks:666 windows/5994 clear pane rays,308 foundation strips/1237
rooted vertices and2464 clump contacts;1598 additional contact samples;
17 reachable routes and10 clear patrols;95 Node checks;four public schemas;
Blender/export parity.506 original solids remain exact, as do40,061 original
part geometries;44 vegetation parts receive the explicitly recorded contact fit.
Original services, portals, navigation, spawn, actors and house envelopes remain.
Curbs deliberately change visible walkable elevation/width: do not claim all
floors or all original decorative vertices unchanged.

Final native visual decisions and browser results are recorded in `visual-test.json`
and `summary.json` after capture. Agent scope review is separate from user Golden
acceptance. Software SwiftShader cannot establish physical-GPU performance or
painted gait acceptance. The development server8011 stays alive.
