# Longer sword trail — 24 October 2026

The selected variant extends recent real blade-tip history from a .55 blade-length
cap to .80, using native source poses 11,12,13. It never extrapolates beyond the
recorded path or current tip. A pointed tail replaces the square-ended ribbon.
Emission stays at pose7/source13; pose8 fades to25%; all other poses are clear.
Timing remains1070ms. All256 body/head/weapon/grip asset bindings are unchanged.

SE/SW/NE history is1.45 times the previous length; NW is2.92 times because its
previous single interval is strongly foreshortened. Every view is capped at80%
of its painted blade length. View-dependent depth staging remains an artistic
approximation. This change is not blanket animation or cutout approval.

- [SE before/after GIF](SE-comparison.gif)
- [Four directions before/after GIF](four-direction-comparison.gif)
- [Full-color comparison APNG](SE-comparison.png)
- [Actual factory atlas runtime](runtime/index.html)

Separate768px front/back frames and3072px sprite sheets are under each view.
The isolated variant store is persisted in factory-store; original baseline
artwork and baseline factory remain unchanged. Import manifest reuses the same
masters and four non-FX parts. Actual browser compositor passes128 comparisons
across64poses with zero pixel differences and no page errors. Five focused
bounded-history tests pass.

Reproduce the FX from the repository root:

```bash
python tools/character_factory_v3/build_extended_sword_trail.py --output /tmp/astraeon-longer-trail-rebuild
python -m unittest discover -s tests/character_factory_v3 -p test_extended_sword_trail.py
```

The destination must be new. Review artifacts use one shared viewport; no body,
pose, frame fitting, motion retiming or weapon attachment changes are applied.
Patch0.0.1 still requires the remaining characters/actions and accepted art.
