# Walk SW — projected source-skeleton controls

**Control input, not painted or accepted art.** Blender 4.3.2 replayed the original Mesh2Motion Walk SW guide and exported 66 evaluated bones across 16 poses. The replay checks source guide hashes, source action/frame, known bone rotations and world landmarks. `build_walk_openpose_controls.py` projects joint heads through the recorded orthographic camera, checks head/hands/feet against recorded projected landmarks within 0.002 source px, and renders 16 control images using one fixed guide crop and scale. The head joint is a head-center proxy, not an anatomically detected nose. Face, fingers and sword are not represented.

[16 projected controls](controls.png) · [control preview](controls.gif). The GIF only shows source controls, not character artwork. Rebuild with:

```sh
blender -b -t 2 --python tools/character_factory_v3/export_evaluated_guide_skeleton.py -- --source-guide authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2 --direction SW --output /tmp/walk-skeleton.json
python3 tools/character_factory_v3/build_walk_openpose_controls.py --output /tmp/walk-openpose-controls
```

The Python control builder reads the saved skeleton at `research/swordsman-walk-sw-source-skeleton-20261104/skeleton.json`; compare the fresh export hash or inspect numerical tolerances before substituting it. A fresh local build reproduced all 16 control PNGs byte-for-byte. Inputs and hashes are recorded in `control-receipt.json`. These controls are OpenPose-like, not a standard full OpenPose detector output; they do not establish painted landmarks, shoe contact, sword grip, pose adherence, visual quality or temporal stability. ControlNet and game use are not approved. No original or runtime asset changed; coverage remains 2/96 technical imports and 0/6 complete characters.
