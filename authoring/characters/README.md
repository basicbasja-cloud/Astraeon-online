# Golden Warrior reaction source

`warrior-reactions-v3.png` is original generated ASTRAEON art, using the existing
original Warrior as the identity reference. The source contains sixteen poses:
hit and fallen death for S, SE, E, NE, N, NW, W and SW. No pose is mirrored.

`tools/register-warrior-reactions.py` registers connected source silhouettes,
source bounds and authored boot anchors into `world/v3/warrior-animation.json`.
It does not repaint, warp, mirror or erase source artwork. Bounds may overlap
because the source sheet is not a perfectly separated grid; contour clipping
excludes neighboring illustrations. `assets/warrior-reactions-v3.webp` is the
compressed runtime copy. Review the actual runtime gallery and combat states;
registration and schema validation are not visual acceptance.
