# Swordsman NW source foot-mesh study

This study evaluates the retained Mesh2Motion `Sword_Attack` action and skinned `Mannequin` in Blender 4.3.2 at the exact source frames used by NW poses 0, 14 and 15. The replayed head, pelvis and foot world coordinates match the frozen guide exactly; the locked-camera projection differs by at most **0.000030 authoring pixel**. The original painted BodyCostume pixels match the technically imported objects. The proposed frame-15 translation is checked against its recorded transform.

[Lowest source-foot mesh vertices on the original and candidate art](lowest-foot-surface.png) · [receipt with vertex IDs, projected coordinates and hashes](receipt.json). Cyan represents left and red right. Only vertices with at least 0.5 combined skin weight for the corresponding foot/ball/leaf groups and within 0.01 m of that foot's minimum world z are shown. The 3× crop is fixed; dots are diagnostic and are not painted pixels.

The same **26 low-band mesh vertex IDs per side** occur in both source frames 14 and 15. Their median screen displacement at the 240 canvas is approximately **(−0.0468, +0.0169) px for left** and **(−2.1971, +1.0101) px for right**. The source minima at these frames are close to world z=0, but that alone does not prove intentional planted contact. A whole-frame image translation affects both painted feet, even though these source surfaces move differently.

The colored points do not coincide cleanly with the painted shoe silhouettes, and no painted sole landmark has been identified for both feet. The existing candidate's 1.0102 px lower-component statistic uses an unverified painted component, so it is not a certified contact result. Do not admit or adjust the candidate solely to satisfy that statistic. Review the painted feet and source surface identity, the whole action and the actual recovery-to-ready transition before choosing an art or registration correction.

Reproduce using a fresh destination:

```sh
blender -b -t 2 --python-exit-code 1 --python tools/character_factory_v3/audit_sword_nw_source_foot_mesh.py -- --output /tmp/sword-nw-foot-mesh
```

A second Blender run reproduced the image and receipt byte-for-byte. The original baseline and game assets were not changed. This is source-geometry evidence, not visual or gameplay approval; coverage remains **2/96 technical imports, 0/6 complete characters**. [Earlier one-shot original/candidate GIF](../patch001-swordsman-nw-registration-proposal-20261028/comparison.gif).
