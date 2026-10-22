# Isolated modular contract metadata

These historical JSON definitions are unit-test fixtures only. No proof artwork
or rejected playable assets are restored. Tests mock atlas images and network
requests; the files cannot establish character artwork or gameplay readiness.

Source: `origin/codex/modular-sprite-pipeline-v0.1`.

- Swordsman metadata blob: `784e28e0f34b8e4e5fa098cf81477197c5ccffac`.
- Mage metadata blob: `43d84e854abf156c1080da33272c020fdc088337`.

The runtime-contract suite previously depended on deleted files under
`assets/characters/*-proof/`, causing an import failure before its assertions ran.
