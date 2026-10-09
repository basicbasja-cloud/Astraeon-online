# South source candidates — rejected visual gate

**REQUIRES_OWNER_VISUAL_REVIEW · VISUAL_FAIL · SOURCE COVERAGE INCOMPLETE**

`sources/` preserves untouched independently generated BodyCore, HeadBase,
Face and Outfit source PNGs. These are candidates, not accepted production art.
`attempts/` preserves superseded BodyCore and Outfit outputs; exact prompts and
input-image identities are in generation-jobs.json. No complete dressed
character was generated or cut apart for these sources.

`pose-contract.json` binds Idle/S/key0 to the unchanged baseline MotionTemplate,
root and camera convention. Its initial BodyCore calibration is explicit.
`source-manifest.json` binds every available source to that contract; no part
can own new anchors, timings or arbitrary offsets. Optional weapon hiding
changes appearance only. ClassId Swordsman and bodyVariant male remain distinct.

The Outfit and Face did not honor registration. BodyCore is too muscular;
HeadBase/neck are provisional. HairBack/HairFront were not generated after the
method failed. None are replaced by empty atlases or flattened v1 body pixels.
The sword reuses a correctly independent original v1 source sheet cell and
its documented grip normalization, attached by the shared South socket.

`generated/` holds early BodyCore/HeadBase guide inputs. These are not editable
authority. Final candidate normalization lives under
`assets/characters/swordsman-true-modular-v2/`, with a hash/transform receipt.
Composite guide images and previews are derived review material only.

Reproduce the diagnostic normalization and compact evidence:

```sh
python tools/build_modular_south_candidates.py
node tests/modular_source_authoring.test.cjs
python -m unittest discover -s tests -p 'test_modular_south_sources.py'
python -m http.server 8021 --bind 127.0.0.1
node tests/modular_south_browser.cjs
```

Do not rebuild while browser tests read the rasters. Open
`character-modular-source-review.html` for the static failed South assembly.
The explicit diagnostic-incomplete opt-in renders existing sources while
reporting incomplete coverage. Strict source compilation rejects missing Hair.
`assertSouthGatePassed` blocks later production. No runtime AppearancePack,
cosmetic A/B production, eight-direction Idle, Walk or BasicAttack v2 exists.

Resume with coordinate-constrained layer painting or an art-document workflow
that can preserve exact registration and export isolated layers without
flattening. Preserve the reference/motion work; replace the rejected candidates.
Do not repeat the same unconstrained full-canvas prompts, warp the large outfit
to conceal its failure, or crop facial skin away to invent a Face source.
