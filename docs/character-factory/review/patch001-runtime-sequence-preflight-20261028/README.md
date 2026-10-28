# Runtime packer: reject truncated source sequences

The runtime packer's preflight previously required only that all target `(direction, index)` pairs appear in the imported binding. A longer imported sequence could therefore satisfy a shorter action by silently taking its first frames. This is not sufficient evidence that a source pose sequence is reusable and conflicts with the patch's Mage action/alias requirements.

Preflight now requires **the exact index set for each requested direction**. It still allows additional real directions in the same import when each requested direction has the exact sequence length. This prevents a longer source from being silently truncated; equal frame counts alone still do not prove identical poses, camera, timing, semantic ownership or visual acceptance.

The regression test rejects a 3-frame source for a 2-frame action and accepts two exact frames in the requested direction alongside an additional complete direction. The targeted runtime packer suite passed 11 tests. The full character factory suite passed **369 tests**, including the real Blender checks; commands:

```sh
python -m unittest discover -s tests/character_factory_v3 -p test_patch001_runtime_pack.py -v
python -m unittest discover -s tests/character_factory_v3
```

No character package or artwork was produced or approved by this change. The existing Mage [own-frame diagnostic GIF](../patch001-mage-own-frame-head-recovery-20261028/own-frame-normal.gif) still has unresolved motion and cutout issues. Patch coverage remains **0/6 newly complete characters and 2/96 technical imports**.
