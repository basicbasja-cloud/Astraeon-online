# Performance record

Targets: desktop 60 FPS; modern phone 50–60 where possible; lower-tier phone 30+. Targets are not measured device guarantees.

Implemented: static town paving cached in one offscreen canvas; sprite atlases compressed to alpha WebP; DPR/ambient budgets selected by low/medium/high preferences; no per-character CSS hue filters for the new archetypes; presentation culling of offscreen city props; fixed camera smoothing independent of frame rate; capped simulation delta with uncapped frame-time measurement.

QA reports a rolling 180-frame FPS mean and p95 wall-clock frame duration in qa.html. Portrait/landscape resizing changes one iframe without reload. This simulates CSS viewport sizes, not iOS GPU, thermal limits, Safari behavior or touch hardware. Browser runtime measurements will be recorded after publishing this phase. Real Android/iOS device profiling remains necessary.

Known costs: Canvas2D particles and shadowBlur; full-screen ground at selected DPR; 17.7 MB raw town paving cache; UI status rebuild four times/second. No WebGL instancing, LOD, KTX2 or full chunk streaming is claimed. Reassess engine choice from measured renderer cost, not engine fashion.
