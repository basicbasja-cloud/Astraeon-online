# Temporal visible cutout proposal

The manual mask boundary remains authoritative. SAM2 propagation proposes visible
pixel ownership across a fixed-canvas sequence; it does not paint missing surfaces,
correct anatomy, or approve art. The original RGBA pixel is assigned exactly once.
Tracked roles must all have frame0 seeds. Additional corrections may be supplied
for frames where hands, a string or arrows cross the head.

## Verified free local dependency

- Official source: https://github.com/facebookresearch/sam2
- Revision: `2b90b9f5ceec907a1c18123530e92e794ad901a4`
- Model: `sam2.1_hiera_tiny.pt`
- Download: https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt
- SHA256: `7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69`
- Official README License section explicitly licenses model checkpoints and code
  under Apache2.0. Optional third-party CUDA connected components are not used.
- CPU, postprocessing disabled; no provider account, fee, or credentials.

Code/checkpoint installed separately in the execution workspace, not committed.
The production CLI is `tools/character_factory_v3/track_visible_cutouts.py`.
`--seeds` is a JSON object with `roles` and `corrections`; each correction gives
an integer `index` and role-to-mask-path `masks`, relative to the seed JSON.
`--masters` must be contiguous000.png RGBA frames with one fixed canvas.
`--checkpoint`, `--model-revision` and a fresh `--output` are explicit inputs.

## Actual bounded pilot

Male Archer NW BasicAttack,16 existing canonical painted masters. HeadHair seeds
at0,5,8 use the retained manual edge-ownership proposal. BodyCostume is the
unclaimed remainder and **still includes the weapon**. Transparent and
antialiased source pixels retain their original alpha; neither body position nor
figure scale is altered. The result remains a partial proposal requiring visual
semantic review. Painted head/arm drift still prevents action acceptance.

The seed frame masks are retained exactly after tracking; highest positive model
score resolves overlaps between other proposed roles. Empty/invalid masks,
overlapping correction masks, mismatched canvases and nonfinite model scores are
rejected. Same-frame recomposition is checked against the actual master.
