# Swordsman Pickup — Mesh2Motion kneeling candidate, 2026-10-29

Rendered the existing Mesh2Motion `Fixing_Kneeling` clip on its native human rig with the current Swordsman sword guide, SW camera, 16 source samples, and the existing orthographic camera settings. The retained job, 16 guide PNGs and manifest are in `authoring/characters/factory-v3/patch-0.0.1/research/swordsman-pickup-kneel-sword-sw-20261029/`. The guide was rendered at 768×768 for this isolated evaluation; no patch ledger or runtime binding was changed. [Candidate GIF](candidate.gif) and [contact sheet](contact.png) show the same fixed crop per frame. GIF timing is diagnostic and not the gameplay contract.

The candidate reaches lower: the lowest left wrist origin is 0.353 m, and the right 0.310 m. These are bone origins, not evidence of fingertip/floor contact. The captured sword guide intersects the hand/working area during the kneel. Full-clip sampling also spends many frames in a prolonged repair hold followed by a rapid rise. It therefore **does not pass as a Swordsman pickup** without checking and adapting grip, left-hand reach, timing, ground contact and recovery. It remains a source comparison; neither this clip nor the table-height clip is approved for a ground pickup.

Reproduction from repository root requires Blender and the source files pinned by `job.json`:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_patch001_guides.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/swordsman-pickup-kneel-sword-sw-20261029/job.json --output <fresh-output-directory>
```

The job pins the renderer and input source hashes; a changed renderer intentionally rejects the old job. This is one direction and no painted frames, cutouts, variant or gameplay result are implied.
