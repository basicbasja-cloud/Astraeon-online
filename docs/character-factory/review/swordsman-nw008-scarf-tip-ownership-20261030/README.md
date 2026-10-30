# Swordsman BasicAttack NW 008: scarf and visible blade ownership

**Isolated per-frame repair proposal; not a finished weapon swap.** The [original roles](roles-before.png) show that the existing Weapon layer contains an island of scarf, while the visibly exposed sword tip belongs to BodyCostume. With Weapon hidden, the missing scarf forms a conspicuous diagonal hole and the sword tip remains. This is a semantic cutout defect even though the original layers recompose exactly.

The proposal returns all 190 pixels of the scarf-colored Weapon island to BodyCostume and transfers 68 exposed blade pixels from BodyCostume to Weapon. [Compare the character without Weapon on three backgrounds](without-weapon-comparison.png). The obvious hole and exposed tip are gone in this one view; recomposition with the proposed Weapon is RGBA-identical to the original. Source pixels outside the two transfer masks do not change. The actual layers, masks, source hashes and result are stored in `authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw008-scarf-tip-ownership-20261030/`.

The blade/scarf intersection and concealed sword/grip remain ambiguous, and WeaponHandOccluder includes additional figure pixels. This is not evidence of a complete alternate-weapon swap, a clean production cutout, or an approved animation. Inspect mask boundaries, alpha halos and newly exposed surfaces, author the complete original and alternative sword as needed, and repeat for every frame/direction before runtime intake. Existing bright edge fringes also remain visible on dark backgrounds.

A separate image-edit donor was explored to remove the small blade and reconstruct the scarf boundary. The full generated donor and input are preserved in `authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw008-underpaint-20261030/`; it was **not used** in this pixel transfer. The donor was requested with: “Edit this same tightly cropped painted animation frame. Remove only the small upright steel sword blade protruding from behind the character's right shoulder. Restore the white background where the blade was visible and continue the existing gold scarf and shoulder contours naturally where the blade meets them. Preserve precisely the character's original head, hairstyle, scarf folds, armor, arm, back, crop and pose. No replacement sword, no added object, no text. This is a local underpainting for a modular sprite, not a new drawing.” The image tool did not expose a model or seed.

Reproduce to a fresh directory and check:

```sh
python tools/character_factory_v3/propose_swordsman_nw008_blade_ownership.py --output /tmp/nw008-scarf-tip-ownership
python -m unittest discover -s tests/character_factory_v3 -p 'test_swordsman_nw008_blade_ownership.py' -v
```

The focused test passed, including exact recomposition, counts, source preservation and refusing to overwrite output. No production data changed, no game run occurred and no action or character is complete. This supersedes the earlier proposal that only transferred 68 blade-tip pixels; both studies are retained.
