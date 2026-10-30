# Swordsman BasicAttack NW 003: bounded sword-free master study

**Not approved.** The [16-frame NW review](nw16-weapon-hidden.png) compares each existing composite to the same frame with its Weapon role hidden. Several frames retain blade fragments or have missing costume pixels. At frame 03, the [source roles](source-roles.png) show blade fragments in other roles and a sword-shaped hole through the body.

A generated underpainting donor fills the removed sword area on the same full-master pose. The script replaces only a saved 2,859-pixel mask, including the removed Weapon footprint and a bounded band along the sword; all pixels outside the mask are byte-identical to the original no-weapon composite. [Compare on three backgrounds](comparison.png). A first white-background matte attempt darkened the generated bracer on dark backgrounds; the saved second study uses a different heuristic and looks more consistent at review size, but its edge alpha and seam are still unverified.

[Restoring the original Weapon role](restore-check.png) exposes a failure: the far tip and parts of the old blade were not in that role and therefore do not return. The generated full master is neither an exact reconstruction nor a swappable weapon assembly. Do not admit it until the complete visible original sword has correct ownership, the occluded costume and grip are authored, and both original and alternative sword passes are inspected across all frames and gameplay. Existing pale fringes also remain on dark backgrounds.

Source candidate inputs and raw generated donor are in `authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw003-underpaint-20261030/`; the mask, candidate and hashed receipt are in the corresponding `research/swordsman-nw003-underpaint-20261030/` directory. The image tool did not expose model or seed. Prompt:

> Repair this existing cropped fantasy character animation frame to provide the underlying body when its sword is hidden. The white diagonal strip is a missing region where a sword was cut out, and gray metal remnants remain along the strip. Remove all remaining metal sword, hilt and blade. Carefully paint the missing portions behind it: continue the dark navy sleeve, gold scarf, bracer and existing raised arm naturally in the SAME pose, maintaining the character's anatomy and original exact camera placement. Preserve every area outside the diagonal gap as closely as possible, including head, hair, both hands, costume and background. One consistent character only, no additional arms or hands, no new weapon, no text. Use the original painterly sprite style and white background.

Reproduce into a fresh path and run the bounded-pixel test:

```sh
python tools/character_factory_v3/propose_swordsman_nw003_underpaint.py --output /tmp/nw003-underpaint
python -m unittest discover -s tests/character_factory_v3 -p 'test_swordsman_nw003_underpaint.py' -v
```

One focused test passed. It checks source preservation and the overwrite guard; it does not approve the art, mask, alpha or animation. No production master or runtime data changed; no completed action is claimed.
