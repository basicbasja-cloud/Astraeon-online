# Identity references are not a six-character fit proof

The retained six-character lineup is a generated design concept. Its provenance says the generated male Swordsman is only a comparison and the earlier tall Swordsman is the visual reference. The five non-male-Swordsman identity seed PNGs are 512×512 RGBA images whose nontransparent bounds all extend from y=25 to y=495; this shared outer bound includes hair, staff, bow, quiver or costumes and cannot establish anatomical height, ground contact or a fixed character fit. The male Swordsman seed is RGB, so its image-wide opacity cannot be compared to those alpha bounds at all.

Consequently, neither seed image dimensions nor those alpha bounds establish a consistent six-character size, and the lineup is not an approved eight-direction board. Do not calculate per-frame body scale from these bounds or mark the six fits approved. A valid fit review still needs same-camera complete painted characters, recorded body/foot landmarks and common transforms against the original tall Swordsman, followed by in-game scale checks. The Mage same-frame guide studies remain unapproved.

Reproduce the file observations:

```sh
python3 - <<'PY'
from PIL import Image
from pathlib import Path
for p in sorted(Path('authoring/characters/factory-v3/patch-0.0.1/identities').glob('*-seed.png')):
 im=Image.open(p)
 print(p.name, im.size, im.mode, im.getchannel('A').getbbox() if 'A' in im.getbands() else 'no alpha')
PY
```

This observation does not change coverage: 2/96 technical imports and 0/6 complete characters. No image was altered or approved by this check.
