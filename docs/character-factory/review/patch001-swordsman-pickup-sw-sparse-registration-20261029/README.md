# Swordsman Pickup SW — sparse full-frame foot registration study

Frames 2, 4 and 6 were independently painted from the corresponding source guide; the generated images, exact prompts and guides are under patch `painted-candidates/swordsman-pickup-sw-inbetweens-20261029/`. Existing draft frames 8 and 16 are included for comparison. They remain **five sparse, unapproved stills**, not a 35-frame animation.

In the 35-sample SW guide the lowest selected left-foot skin vertex is index 917 in all five of these poses and its world XY is approximately stationary. In the painted drafts, the lowest brown pixel in a fixed boot ROI appears at tile Y 314, 298, 305, 318 and 318 for frames 2, 4, 6, 8 and 16 after the shared +17px placement. [Boot detail](boot-detail.png). These pixels are a heuristic that can include clothing or a different feature of the boot; they are not yet a manually verified corresponding sole landmark.

The proposal therefore moves the **entire** frame vertically by an additional +4, +20, +13, +0 and +0 tile pixels respectively, matching that proxy to frame 8. All use the same uniform 1254→384 resize; there is no per-part transform or per-frame scale. [Guide / proposal comparison](comparison.png) · [sparse-still toggle](sparse-stills-toggle.gif) · [measurements and hashes](../../../../authoring/characters/factory-v3/patch-0.0.1/review/swordsman-pickup-sw-sparse-foot-registration-20261029/receipt.json). The GIF is not continuous motion and uses one-second holds.

**This is not a pass.** The bottom-pixel proxy has not been matched to a real painted sole feature, and the mean X position in the same color ROI varies by roughly 10 tile pixels between frames 2 and 8; boot shape and angle may contribute, but horizontal instability must be checked rather than hidden. Head, hand, sword, anatomy, alpha and all missing frames remain unverified. No production data or source was overwritten. Three focused tests passed. Tool SHA-256: `43fff5336487c87b78ef1ec2f90d4eccfcf30dc6315783e165fdd96446d1a723`.

```sh
python3 tools/character_factory_v3/propose_pickup_sw_sparse_foot_registration.py --output <fresh-dir>
python3 -W error::ResourceWarning -m unittest discover -s tests/character_factory_v3 -p test_pickup_sw_sparse_foot_registration.py -v
```

Image-generation model and seeds were not exposed. These outputs do not establish a usable Swordsman action or game character.
