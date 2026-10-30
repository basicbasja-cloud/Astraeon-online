# Swordsman BasicAttack NW 008: blade tip and ownership

**Partial proposal; not admitted to production.** The existing painted annotation marks the tip at `(267,243)` in the 512px master, which falls on the yellow scarf. The visible blade tip is approximately `(280,227)`; [close-up](endpoint-close.png), [pixel grid](blade-grid.png). The hand/grip remains concealed and its annotation is not verified. The corresponding native motion guide also shows the blade partially hidden behind the figure; this supports the need to treat occlusion explicitly, but does not prove the whole painted blade is correct.

An isolated override places the estimated tip at `(280,227)` without modifying the original annotations. [Effect comparison](comparison.gif) and [frame 08](frame08.png): NW changes shape but still has a distorted ribbon. It is not a production-ready trail; SW/NE/SE still require their own visual and occlusion review. The curve derives from time-interpolated 2D registrations rather than a verified complete 3D blade sweep. The source finger-bone grip is a proxy.

We also found that the exposed tip pixel `(280,227)` belongs to BodyCostume and is transparent in Weapon. This would leave part of the old blade behind during a weapon swap. The [isolated ownership proposal](../../../../authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw008-blade-ownership-20261030/receipt.json) transfers 68 visible pixels into Weapon while preserving all pixels outside its mask and producing an identical RGBA composite. The lower blade/scarf intersection, fully hidden blade, and any newly exposed costume are not authored; the proposal is **not** a complete weapon swap. Exact recomposition alone does not establish correct semantics.

Reproduce into fresh output paths:

```sh
python tools/character_factory_v3/propose_swordsman_nw008_blade_ownership.py --output /tmp/nw008-blade-ownership
python tools/character_factory_v3/propose_swordsman_interpolated_sweep.py --overrides authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw008-tip-correction-20261030/overrides.json --output /tmp/nw008-trail-tip-study
python -m unittest discover -s tests/character_factory_v3 -p 'test_swordsman_nw008_blade_ownership.py' -v
python -m unittest discover -s tests/character_factory_v3 -p 'test_interpolated_sweep_study.py' -v
```

Four focused tests passed. The source art and production layer data are unchanged; no runtime/gameplay validation or finished action is claimed. Complete the semantic seam, hidden surfaces and grip before testing a genuine replacement sword, and review every frame and view.
