# Open, verify and resume

Run from the research checkout root. Read the handoff first. Commands below never alter the frozen v61 snapshot; output goes to fresh `work/` directories. Python requires Pillow/numpy, and motion/contact helpers also scipy. Native checks require the installed SPA/Aseprite runtimes. No provider credentials or paid account are required for inspecting this transfer.

## Read-only integrity check

```bash
python research/sprite-animation/whole-body-handoff-v61/verify-handoff.py
```

Verifies every manifest payload, all30 raw/prompt digests, all48 non-production statuses,9 candidate clocks/available exposure hashes,48 real body/head recompositions, native headers and deliberate failed head contract. This is **not** a new native export, browser run or art approval. See `TRANSFER-VALIDATION.json` for the actual transfer check results.

Open the three offline, self-contained players directly in a browser:

- [S](snapshot/generation/S-candidate7/layer-player2/review.html)
- [W](snapshot/generation/W-candidate2/layer-player/review.html)
- [E](snapshot/generation/E-candidate1/layer-player/review.html)

Native files are under S `native-format2/sprite.aseprite` or `native-editable2/pickup-four-slots.aseprite`, W `native-editable2/pickup-four-slots.aseprite`, E `native-editable3/pickup-four-slots.aseprite`. Open them in Aseprite; these contain complete bodies but currently imperfect head ownership.

## Restore portable scratch

The snapshot preserves original JSON exactly, including absolute authoring paths and preliminary labels. Do not run old builders directly inside frozen research cases. `RELOCATION.json` maps each original generated output to its retained job PNG. Restore only when `work/all-actions-v61` and `work/v61-generated-images` are absent; existing scratch is deliberately refused.

```bash
python research/sprite-animation/whole-body-handoff-v61/restore-workspace.py --repo "$PWD"
```

This copies the curated snapshot, re-creates30 UUID-named raw files in scratch, rebases original checkout/generated-image paths **only in the copied scratch**, and recreates repeated ready/walk timeline PNGs by exact SHA matching to the8 keys. Original evidence files remain untouched. Restore does not rebuild omitted failed intermediate renders or native export PNGs. It does not run image generation or automatically execute historical builders.

## Supported tool commands after restore

Always choose new output directories; tools refuse overwriting evidence.

```bash
python tools/sprite-layer-player.py --help
python tools/sprite-native-package.py --help
python tools/sprite-head-ownership.py --help
python tools/sprite-head-mask.py --help
```

The actual parser flags shown by `--help` are authoritative. Examples:

```bash
python tools/sprite-layer-player.py \
  --clip work/all-actions-v61/generation/S-candidate7/four-slots2.json \
  --full work/all-actions-v61/generation/S-candidate7/clip.json \
  --out work/v61-player-fresh

python tools/sprite-native-package.py \
  --clip work/all-actions-v61/generation/S-candidate7/four-slots2.json \
  --full work/all-actions-v61/generation/S-candidate7/clip.json \
  --out work/v61-native-fresh \
  --spa work/tool-runtime/spa-env/bin/spa \
  --aseprite work/tool-runtime/aseprite-build/bin/aseprite
```

Re-run ownership with the current failed contract into a new scratch output; a failed quality result is expected, even though execution itself is valid:

```bash
python tools/sprite-head-ownership.py \
  work/all-actions-v61/generation/S-head-fields2.json \
  --out work/v61-ownership-fresh
```

If runtimes are absent, read `tools/setup-sprite-tools.py --help` and frozen v59 installation receipts before rebuilding. MobileSAM setup is separately pinned in `snapshot/model-provenance.json` and REFERENCES. Do not commit weights, virtualenvs, compiled Aseprite or the raw source clone. Source/model download costs are not provider generation jobs.

Archived `snapshot/generation/*.py` are authoring provenance, **not all one-command portable build targets**: some depend on deliberately omitted intermediate failures or old workspace runtimes. Use current keys/clip files as the exact handoff source; consult the ledger/raw/guide files when authoring a replacement. Never execute `ledger.py` blindly: it is the original23-job builder and would overwrite the newer30-job ledger in scratch. `checkpoint.md`, `checkpoint-live.md` and initial model counters are superseded.
