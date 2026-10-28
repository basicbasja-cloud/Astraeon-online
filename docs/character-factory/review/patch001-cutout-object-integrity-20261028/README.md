# Bound cutout object integrity

The existing two technical Swordsman imports have 128 binding frames referencing 406 distinct RGBA objects. All 406 files were readable and their decoded RGBA pixel hashes and canvas dimensions matched their indexed objects. There were no integrity errors in these referenced objects.

This check does **not** approve pixel ownership, clean edges, hidden anatomy, interchangeable parts, motion or game rendering. Mage and Archer remain unimported, Mage master continuity remains unresolved, and 0/6 characters are complete.

Reproduce with a fresh output path:

```sh
python3 tools/character_factory_v3/audit_bound_cutout_objects.py --output /tmp/patch001-bound-object-audit.json
python3 -m unittest discover -s tests/character_factory_v3 -p test_audit_bound_cutout_objects.py -q
```

The three new tests cover intact pixels, altered pixels and a path outside the repository. See [receipt](receipt.json).
