# Hit SW 000: transparent donor and source blade-mask patch

**Draft, not approved.** A close-up donor with transparent background was generated from the 125×125 authoring crop and the same source mannequin guide. A SAM2 suggestion for the original visible blade was downsampled to the crop and dilated one authoring pixel, creating a 921-pixel replacement mask. Donor RGBA is placed only inside that mask on the original 768px full master. The [white/gray/dark comparison](comparison.png) no longer shows the obvious white wedge of the earlier bounding-box patch. Pixels outside the mask are exactly unchanged. [Source blade-mask proposals](mask-proposals.png).

The manually estimated donor tip `(806,404)` is **0.79 runtime px** from the projected finger-derived guide point, with ±0.12 runtime-pixel uncertainty for a ±4-pixel donor annotation. This is a visual landmark diagnostic only: the actual sword socket and grip have not been verified, and a small tip error does not approve anatomy, foot contact, animation or gameplay.

Crucially, **53 pixels** that had alpha ≥240 in the source have alpha <10 in the candidate. These may be old blade, but can also include body or arm: inspect the saved `removed-opaque-mask.png` against source and guide before accepting. The segmentation may contain garment, and the donor can introduce seams or changed colors inside the mask. The same figure is still a single unapproved draft pose, with no semantic BodyCostume/HeadHair/Weapon cutouts or runtime admission.

[Draft master, mask, removed-pixel mask and receipt](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-sw000-transparent-mask-patch-20261102/receipt.json). The original 768px draft and generated input/donor are retained in `painted-candidates/swordsman-hit-sw000-bounded-repair-20261102` and `painted-candidates/swordsman-hit-sw000-close-transparent-20261102`. The saved source mask is SAM2 tiny checkpoint SHA-256 `7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69`; positive points in the 1000px crop: `(520,440),(440,540),(660,290),(300,700)`; negatives `(810,280),(630,550),(430,250)`. Proposal index 1 is used. SAM confidence is not semantic approval.

Image editing prompt: “Edit ONLY the sword in the first close-up image to match the guide in the second. Both show the same crop. Keep the same gripping hand; the second image's red dot marks the hand and cyan dot marks the required shorter blade tip. The old blade beyond the cyan dot must disappear and the underlying sleeve/costume be restored coherently. Preserve all parts outside the old and new sword, including both arms, hand, waist, clothing and camera. Return the same square close-up with a transparent background outside the character, no colored dots or labels.” Generator model/seed were not exposed.

```sh
python tools/character_factory_v3/propose_hit_sw000_transparent_mask_patch.py --output /tmp/hit-sw000-transparent-mask
python -m unittest discover -s tests/character_factory_v3 -p 'test_hit_sw000_transparent_mask_patch.py' -v
```

The focused outside-mask, recorded-alpha-change and overwrite tests passed. No source, production or runtime asset was overwritten. No action or character is complete.
