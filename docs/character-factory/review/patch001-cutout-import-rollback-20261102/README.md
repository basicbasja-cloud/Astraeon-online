# Complete-batch cutout intake with rollback

An invalid late frame previously left a new import directory and unindexed PNG
objects in the shared store. The next attempt then failed because that directory
already existed. This made a routine corrected-manifest retry require manual
cleanup, with a risk of confusing partial and complete imports.

The importer now validates/reconstructs every frame and stages generated labels,
bindings, receipts and new content-addressed objects in a private directory.
Shared assets are revalidated before reuse. Publication reserves a new job
directory exclusively, publishes objects without replacing existing files,
merges the latest index, and exposes the completion receipt last. Ordinary
validation/publication failures restore the previous index bytes and remove
only this intake's new objects/output. An input edited during the operation is
preserved and aborts the intake. Existing imports, symlinks, stale lock files
and the legacy`index.json.tmp` are never implicitly overwritten or removed.

## Evidence

[Before/after replay](replay-proof.json) executes the original importer from
commit`ad0bf2b` and the changed importer against disposable two-frame PNG
fixtures. No production artwork is imported in this replay.

| Final-frame failure | Original importer | Changed importer |
| --- | --- | --- |
| Recomposition validation |Rejected |Rejected |
| Partial job directory left |Yes |No |
| Unindexed shared objects left |3 |0 |
| Existing index bytes preserved |Yes |Yes |

Successful label-derived fixture imports produce the same bindings, asset IDs,
compatibility metadata and index bytes before/after the change. The successful
receipt still says`IMPORTED_REQUIRES_VISUAL_REVIEW`, with owner/runtime approval
false. This is a compatibility/preservation result, not art acceptance.

**34 selected tests pass**, including11 new transaction cases and23 existing
preservation, object-integrity, pose-recipe and review/occlusion cases. Failures
are injected during object publication, index writing and final receipt
publication after index replacement. Both an existing store and a first import
are covered. A rejected intake can be corrected and retried without deleting a
partial output. The complete historical factory suite and real64-pose intake
dataset were not rerun; the successful byte-identity comparison above is scoped
to the explicit synthetic fixtures.

[Verification and implementation hashes](verification.json). The regression
proof reproduces byte-for-byte.896/896 protected baseline hashes match. No
canonical renderer or original character painting was changed.

```sh
python tests/character_factory_v3/replay_cutout_import_transaction.py \
  --baseline-ref ad0bf2b --output /tmp/import-rollback-proof.json

python -m unittest discover -s tests/character_factory_v3 \
  -p test_cutout_import_transaction.py -v
python -m unittest discover -s tests/character_factory_v3 \
  -p test_cutout_import_preservation.py -v
python -m unittest discover -s tests/character_factory_v3 \
  -p test_cutout_store_integrity.py -v
python -m unittest discover -s tests/character_factory_v3 \
  -p test_import_pose_recipes.py -v
python -m unittest discover -s tests/character_factory_v3 \
  -p test_patch001_review_tools.py -v
```

The guarantee concerns handled validation/I/O exceptions with working rollback
writes. It is not a power-loss/disk-corruption guarantee across several files.
Object/receipt publication uses hard links on the same filesystem. The import
lock coordinates these batch imports; legacy direct index writers must run
separately. A hard-killed process may require inspection of a stale lock and
unfinished publication before retrying.

## Actual character status

The accompanying [bounded Walk edit and three-background PNGs](../swordsman-walk-local-weapon-20261102/README.md)
remain unapproved; two further image requests were rejected by the image service.
The earlier [16-pose GIF](../swordsman-walk-source-controls-20261102/full-normal.gif)
is still a guide/draft diagnostic. No new action, cutout set, variant or gameplay
result passed. Swordsman/Mage/Archer male and female remain **0/6 newly complete
characters**; the historical2/96 technical imports have not been increased or
recertified by these fixture tests.
