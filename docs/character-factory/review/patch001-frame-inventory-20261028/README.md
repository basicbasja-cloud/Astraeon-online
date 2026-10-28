# Patch 0.0.1 frame inventory

The inventory enumerates each configured character × action × authored direction × frame. The CSV deliberately repeats shared source views for each logical action; the totals are **not unique source frames**.

- 12,992 logical frame/views; all 12,992 expected guide PNG paths exist.
- 128 logical frame/views have imported bindings, belonging to the two existing Swordsman BasicAttack technical imports.
- Those 128 bindings report no missing core asset record or pose/camera/role mismatch in the indexed metadata.
- The audit does not verify RGBA content hashes, semantic masks, hidden surfaces, motion quality, foot contact, cutout edges or game rendering. No frame is marked visually or runtime approved. **0/6 complete characters** remains the status.
- [Frame-level CSV](frames.csv.gz) and [machine-readable summary](summary.json).

Reproduce from repository root, choosing a fresh output directory:

```sh
python3 tools/character_factory_v3/audit_frame_coverage.py --output /tmp/patch001-frame-inventory
python3 -m unittest discover -s tests/character_factory_v3 -p test_audit_frame_coverage.py -q
```

Next inspect the Mage master against same-frame guides and resolve the known neck, anatomy and continuity defects before admitting cutouts or expanding the artwork.
