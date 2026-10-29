# Swordsman Pickup — 35-sample motion and floor study

An isolated Mesh2Motion candidate takes 35 actual source poses, adding samples during descent and recovery while retaining the bounded spine, arm, wrist, finger and right-thigh adjustments from this study. It uses eight real cameras, renders 280 guide images, and does not modify the source rig, canonical renderer, production ledger or runtime. The earlier 16-frame study remained too coarse and had a right knee/foot below the z=0 plane. The right-thigh correction ramps in and out; it does not freeze a leg or move the full painted frame.

[Eight directions near the current action duration](eight-directions-normal.gif) · [slow inspection](eight-directions-slow.gif). The first uses 20 ms for the first 34 samples and a 500 ms final pause, then repeats. Thus it is a diagnostic approximation of the game's 0.65 s action, not proof of actual event timing, transition or runtime playback. The slow GIF uses 60 ms. Both use the same fixed crop for all frames; no source alpha bounds crossed that crop.

## Actual diagnostics

- In SW the maximum consecutive displacement among the recorded guide landmarks decreased from **19.34 runtime px** in the earlier 16-sample arm study to **8.85 runtime px** in this 35-sample study. Different source sampling changes timing; this numerical comparison alone does not establish natural speed, acceleration, or a smooth animation.
- The lowest evaluated mannequin vertex across all 280 view-frames is **8.0 mm below z=0** (SW source frame 9, primarily weighted to right toe bones), corresponding to about 0.36 runtime px using the nominal orthographic scale. The z=0 plane is a guide assumption, not an actual map collision test. The prior 16-sample guide reached 36.1 mm below the plane.
- In SW the same lowest left-foot skin vertex (index 917) appears through output frames 2–14; its largest adjacent XY change is **3.43 mm**, an approximate orthographic upper bound of **0.155 runtime px**. This is one skin point, not a certified planted sole or all-frame contact.
- Torso positive controls hit in 280/280; the thin blade centerline reported zero mannequin surface hits at the sampled poses. The lowest blade proxy, including its 2.2 cm radius, was 11.02 cm above z=0. These do not certify the entire blade/hilt volume, cloth, floor sweep or in-between frames.
- The lowest sampled left distal-finger bone tail is 1.37 mm above z=0 and the largest left IK target clamp is 2.57 mm. A bone endpoint does not establish painted finger shape or contact with a game item.
- The separate SW capture and SW frames in the eight-view run were identical as decoded RGBA arrays. The complete factory suite passed **410 tests**, including existing Blender integration, on the current code. It does not approve this candidate's motion or art.

**Acceptance remains open:** verify the skin surface against the actual map, both feet and knee over time, 3D sword/hilt and wrist grip, fingertip/item contact, the source hold sampling and action-event timing, ready/idle transition, and the actual visual motion in all views. Then draw coherent full-frame masters, correct anatomy and temporal drift, cut same-frame BodyCostume/HeadHair/Weapon and masks, validate variants and test in the game. This guide does not count as a completed Swordsman action.

[Job](job.json), [guide manifest](manifest.json), [geometry records](geometry.json). Reproduce from repository root with Blender and a fresh destination:

```sh
blender -b -t 2 --python tools/character_factory_v3/render_kneel_arm_grip_study.py -- --job docs/character-factory/review/patch001-swordsman-pickup-35frame-20261029/job.json --output <fresh-output-directory>
python3 -m unittest discover -s tests/character_factory_v3 -q
```

Wrapper SHA-256: `458d5cd347c0392cbac7330e90df7710f569fcc64163c23428b13f56288202a8`; reach helper: `cb78832159ccf25f31327aa43a000d4eb3d18ca38f188832c829da438a66f245`. Use the exact commit for reproduction; source job pins the canonical renderer and motion hash.
