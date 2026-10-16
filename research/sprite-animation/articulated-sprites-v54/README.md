# Static-art articulated walking research

This case evaluates original painted parts with one authored rest binding and motion deltas projected from the saved source rig. It does not detect painted joints automatically. Hidden limb art is authored by native image generation; reference geometry is a guide, not proof of painted anatomy.

## Current checkpoint

All eight views have six fixed RGBA parts and257 source-time samples. The source gait covers0.8m in800ms, with60% stance and opposing arm swing. Each view exports80 evaluated PNGs at10ms, **not80 new native drawings**; its GIF has40 samples at20ms. Output is512×576 with64 transparent pixels of added floor clearance; source art/UV scale remains512×512. Earlier512-high S output clipped a shoe and remains rejected.

`verify-walk-artifacts.py` rechecks640 production-candidate PNGs,13,920 actual world-foot diagnostic PNGs, current source/part/renderer dependencies, geometry and player reports. Continuous and held80 world-foot checks pass within2px; wrong-root and held16 controls fail. Held40 is measured separately and is not a universal negative. World displacement is applied before GPU rasterization. Isolated diagnostic boot masks are never inserted into character output.

Every exposure in all eight view contact sheets was inspected in the combined v56 review. SW's narrow far arm was checked again at full512px and is connected. Actual separate GPU buffers establish covered neck overlap at all80 phases in all8 views. Static source ownership excludes3 neighboring SE boot pixels that previously caused8px raster jitter; the real failed source is preserved. This is bounded appearance/attachment review, not hidden anatomy or user acceptance.

`test-articulated-reuse.py`, foot-binding controls and the standalone8-view player cover invalid ownership, missing/collapsed inputs, variable logical canvas/output size, actual PNG comparisons, quarter-speed, pause/seek/resume, repeated view switches and world one-shot playback. See the individual SHA-bound reports. The managed browser blocked file:// navigation; identical self-contained HTML was tested offline through document content.

The original full spatial-contract snapshots are retained in `world-proof-contracts`. Current `sprite-foot-binding.py` hashes only leg/source/world data actually consumed by the foot proof; head-only underlap changes do not invalidate the foot proof. The one-time migration script must not be rerun against newer full contracts.

## Authorship and limitations

Exact generation prompts, ordered reference hashes, raw original results and selections are in `generation-ledger.json`. Host billing is unknown; no external paid provider calls were made. Source artwork remains original project artwork. RO artwork elsewhere in the research tree is credited reference only.

Native atlases do not reliably retain cell-local part sizes. W retains its reviewed static bank scales; E has explicit per-piece uniform packing scales. These are constant across the entire animation, recorded in the rest contract, and require a visual rest comparison. No per-frame shoe relocation, image registration or image fitting is used.

This is an authoring prototype. Combined core coverage is tracked in v56. Runtime integration, modular swaps and action transitions are not established here. `production_pass: false` remains intentional until combined review.
