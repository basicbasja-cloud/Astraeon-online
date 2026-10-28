# Swordsman NW foot-chain projection

[Fixed-crop foot-chain comparison](foot-chains.png) overlays the original rig's projected `foot`, `ball` and `ball_leaf` heads/tails for frames 0, 14 and 15 and the whole-frame registration candidate. Cyan is the left chain and red the right chain. Native bone positions come from the retained Mesh2Motion source frames and are projected with the captured NW orthographic camera. Their `foot_l` and `foot_r` heads reproduce the recorded guide within **0.00005 authoring pixel**. The original painted bodies are verified against the technical import and the candidate is verified as the same −8-pixel whole-frame shift.

The projected chains extend beyond the visible shoe silhouettes in this view; notably the left chain does not clearly identify the illustrated rear shoe. Rig bone heads and tails (especially leaf-bone tails) are not shoe surfaces or ground-contact points, and their correspondence to the painting remains unverified. `contact_world` has no recorded contacts for these source frames. This view therefore cannot certify planted-foot error, the 1 px gate, or the candidate. The observed mismatch calls for checking rig geometry and painted anatomical landmarks before choosing a correction. Neither original art nor runtime bindings were changed.

Reproduce with a fresh output:

```sh
python3 tools/character_factory_v3/review_sword_nw_foot_skeleton.py --output /tmp/sword-nw-foot-chains
python3 -m unittest discover -s tests/character_factory_v3 -p test_review_sword_nw_foot_skeleton.py -q
```

Two projection unit tests passed; a fresh replay reproduced the image and receipt byte-for-byte. [Receipt](receipt.json) pins guide, native skeleton, artwork and code. This is a diagnostic only; 0/6 characters remain complete.
