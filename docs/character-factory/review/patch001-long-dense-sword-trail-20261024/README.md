# Long dragging sword trail — 24 October 2026

The owner requested a substantially longer trail. A new guide captures33 native
subframes across Sword_Attack11..13 in Blender, in all four real cameras. The
end controls match the retained action exactly. The ribbon follows this dense
real path, with at most2.4 painted blade lengths of history and no extrapolation.
This avoids the angular shape produced by joining only three samples.

Emission begins only at pose7/source13. Pose8 fades to55%, pose9 to15%; other
poses are clear. Original1070ms timing and all256 non-FX male asset bindings
are unchanged. The selected long FX are now in the actual default male factory
import, and in the new female cosmetic action import. Original source artwork
is retained; previous bindings/receipt are archived with the new male intake.

- [Before/after SE GIF](SE-comparison.gif)
- [Actual runtime SE GIF](runtime-animation/SE-normal.gif)
- [Actual runtime four views](runtime-animation/four-views-normal.gif)
- [Full-color runtime APNG](runtime-animation/four-views-full-color.png)
- [Isolated factory/runtime proof](factory-variant/runtime/report.json)

The real compositor checks64poses /128 comparisons with zero differences and
page errors. Default bindings match the verified variant exactly. Reimporting
against a fresh Blender capture into an empty store reproduces384bindings and
269objects exactly. Source source-geometry and art approval remain separate.

The NW/NE front/back staging remains artist-selected, not a mesh-depth claim.
These proofs do not complete0.0.1 or certify every character's anatomy.

## Rebuild

From repository root, use a fresh output destination for each command:

```bash
blender -b -t 2 --python-exit-code 1 --python tools/character_factory_v3/render_explicit_patch001_guides.py -- --job authoring/characters/factory-v3/patch-0.0.1/research/long-dragging-sword-trail-20261024/dense-job.json --output /tmp/astraeon-dense-sweep-rebuild
python tools/character_factory_v3/build_long_sweep_sword_trail.py --dense-guide /tmp/astraeon-dense-sweep-rebuild --output docs/character-factory/review/long-sweep-rebuild
```

`verify_fresh_capture_factory.py --effects` selects this FX profile while checking
fresh-source replay of the current default factory. Historical source-only
imports remain available and should not silently replace the selected effects.
