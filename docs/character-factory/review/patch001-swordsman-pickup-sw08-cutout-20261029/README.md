# Swordsman Pickup SW frame 08 — provisional same-frame cutouts

The single-frame paint study was keyed from its white background, resized once as a whole to a 384px tile, placed on a 768×768 canvas at `[192,257]`, and labeled into BodyCostume, HeadHair and Weapon from that same frame. The +17px vertical offset is an unapproved registration proposal, not a measured ground contact. The source image and guide were not modified.

The three disjoint visible layers [recompose exactly to the **keyed master**](../../../authoring/characters/factory-v3/patch-0.0.1/review/swordsman-pickup-sw08-visible-cutout-v2-20261029/receipt.json). This does not prove that the keyed master exactly preserves the white-background image or that the labels have correct semantic edges. [White/gray/dark edge review](edge-review.png) · [head detail](head-detail.png) · [weapon detail](weapon-detail.png) · [single-frame slot toggle](slot-toggle.gif). The GIF is an equipment visibility diagnostic, not motion or evidence that hidden surfaces exist.

## Rejected for production

- Background extraction uses an edge-connected near-white threshold; bright hair, sword highlights and halos require careful review. The edge preview shows visible light fringes on darker backgrounds.
- The head and weapon ownership polygons are rough. A color-based return of visibly brown pixels in the blade region fixes part of a boot overlap, but dark boot fragments remain in the Weapon layer. The head/collar boundary also requires pixel-level review.
- Hand-over-weapon occlusion and the underlying body behind removed parts are not authored; hiding a part is not a working head or weapon swap.
- This is a single view and one frame of 35. The +17px registration, pose, foot contact, motion continuity, variants and actual gameplay are not approved. No production store or runtime binding was changed.

[Source layers, labels, master and receipt](../../../authoring/characters/factory-v3/patch-0.0.1/review/swordsman-pickup-sw08-visible-cutout-v2-20261029/) are retained for correction. Tool SHA-256: `4312fde6d0ace4cf52460e2898b2cecbf3f31dc3353df1b1077892ec10fc62f9`. Two focused tests passed. Reproduce:

```sh
python3 tools/character_factory_v3/propose_pickup_sw08_visible_cutout.py --output <fresh-output-directory>
python3 -m unittest discover -s tests/character_factory_v3 -p test_pickup_sw08_visible_cutout.py -v
```
