# Patch 0.0.1 production checkpoint

In production; not release complete. Six characters: male/female Swordsman, Mage and Archer.

## Direction policy

Physical attacks and casting use four real diagonal views, without mirroring. Casting includes CastChannel, CastRelease and Mage basic attack/SkillAction, per latest owner instruction. Other actions retain eight. See research/action-direction-decision.md.

## Actual coverage

47 source guide jobs captured locally (5,472 source positions after reuse). Generated captures are reproducible and excluded from Git due to size. Run `python tools/character_factory_v3/patch001_factory.py guides` to regenerate from pinned CC0 sources.

Six eight-view identity studies exist. They are not final animation coverage. There are 94 unique paint jobs, zero complete imported cutout jobs. The new SE basic-attack paint study has 16 uniformly sliced cells; no alpha/cutout/FX or acceptance is claimed.

## Outstanding quality work

- Inspect source joins and terminal keys, especially KayKit bow entry and retargeted hand/foot contact. Source capture success is not motion acceptance.
- Complete coherent action painting with fixed cameras and source landmark review.
- Author same-frame HeadHair, BodyCostume, Weapon cutouts and hand overlap; FX independent.
- Validate trajectory-based trail after actual cutting motion; short recent history and correct foreground occlusion.
- Package six complete character sets and inspect normal/slow GIFs before runtime admission.

Existing accepted-review work under the previous Swordsman prototype remains separate because camera/timeline fitting differs. Do not blindly import it as matching these guide jobs. Mesh2Motion remains preferred; KayKit CC0 supplies actual bow clips absent from the free Quaternius Standard download.

No unit tests added or run. Current counts describe source generation and production bookkeeping, not owner approval.
