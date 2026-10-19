# Mesh2Motion motion source evidence

Reviewed 2026-10-19. The selected library file is `static/animations/human-base-animations.glb` from the official `Mesh2Motion/mesh2motion-app` repository at commit `653a9698f5f315523072f1c3ff3496100401317b`.

The repository's [CC0 asset statement](https://github.com/Mesh2Motion/mesh2motion-app/blob/653a9698f5f315523072f1c3ff3496100401317b/LICENSE-CC0.MD) says the 3D models, Blender files, rigs, and animations are dedicated under CC0 1.0 Universal and may be remixed and used commercially. The separate [source art repository](https://github.com/Mesh2Motion/mesh2motion-assets/blob/main/LICENSE) also carries a CC0 1.0 license. The [project README](https://github.com/Mesh2Motion/mesh2motion-app/blob/653a9698f5f315523072f1c3ff3496100401317b/README.md) states that human assets are provided as bundled GLB/GLTF animations and identifies CC0 as the animation license.

## Selected bundle and actions

- Exact source URL: <https://github.com/Mesh2Motion/mesh2motion-app/blob/653a9698f5f315523072f1c3ff3496100401317b/static/animations/human-base-animations.glb>
- Downloaded source SHA-256: `406eb0a8dc4ab366e623b79b6e3005a4951392e1bda78ae39c1099d31147733c`
- Git blob SHA: `3c5b3258af3b982fb922bbc4008296ec4efa8814`
- Blender-imported human skeleton: 66 bones; 24 FPS; actions are separate named animation clips.
- Selected actions: `Idle_Sword` (0–50 frames, loop), `Walk` (0–40 frames, loop), and `Sword_Attack` (0–46 frames, non-looping).
- Each action is retargeted from the same immutable GLB into a new V3 action. The source GLB is local and ignored by Git.

The Mesh2Motion app README notes that some human animations are from Quaternius. The selected bundle remains covered by the repository's CC0 statement; existing Quaternius candidate clips remain documented separately and are no longer selected for this V3 build.
