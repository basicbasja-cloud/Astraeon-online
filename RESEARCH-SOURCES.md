# ASTRAEON Research Sources

This file lists the external repositories and documentation that should be used as architectural references for ASTRAEON ONLINE. These sources are for studying proven 2.5D MMORPG world, rendering, map, animation, and server-design patterns. Do not copy copyrighted Ragnarok Online assets, maps, textures, sprites, or proprietary content.

## 1. roBrowser

**Repository:** https://github.com/AesirWorld/client

**Role:** Browser-based Ragnarok Online client reimplementation using WebGL, JavaScript, and HTML5.

**Why it matters to ASTRAEON:**
- Demonstrates that an RO-like 2.5D MMORPG client can run in a browser.
- Useful for studying browser-side world rendering, sprite integration, resource loading, and client architecture.
- Relevant because ASTRAEON is also browser-first.

**Research focus:**
- World/rendering architecture
- Camera and world-space projection
- Sprite rendering
- Resource loading
- Map rendering
- Browser/WebGL constraints

**Do not use it as:**
- A source of art assets
- A source for copying maps or content
- A reason to reproduce old client limitations unchanged

---

## 2. NostalRO Client

**Repository:** https://github.com/nmeylan/nostalro-client

**Role:** Modern open-source Ragnarok Online client reimplementation written in Rust, focused on reproducing classic RO rendering and behavior while modernizing the runtime.

**Why it matters to ASTRAEON:**
- One of the best references for a modernized RO-style client architecture.
- Clean separation between game state, rendering, network, formats, UI, effects, and tools.
- Reads classic RO resources such as GAT, RSW, GND, SPR, ACT, STR, RSM, GR2, and textures.
- Includes standalone viewers and developer tools for maps, sprites, effects, UI, and integrated scenes.

**Important documentation:**
- Architecture:  
  https://github.com/nmeylan/nostalro-client/blob/master/docs/internal/architecture.md
- Rendering pipeline:  
  https://github.com/nmeylan/nostalro-client/blob/master/docs/internal/rendering.md

**Research focus:**
- Renderer/game separation
- Depth handling
- 2D sprites inside a 3D/polygonal world
- Scene passes
- Sprite projection
- Effects
- Resource graph
- Animation handling
- Debugging/viewer tooling
- High-DPI modernization without changing the original resource model

**Especially relevant lesson for ASTRAEON:**
Keep simulation, world data, rendering, and animation metadata separate enough that each can be tested and replaced independently.

---

## 3. Ragnarok Research Lab

**Documentation:** https://ragnarokresearchlab.github.io/

**Role:** Reverse-engineered technical documentation of Ragnarok Online file formats and rendering concepts.

**Why it matters to ASTRAEON:**
This is the best conceptual reference for understanding how RO separates terrain, navigation, world objects, models, sprites, and animation metadata.

**Key formats to study:**
- **GND** — terrain geometry, textures, UVs, vertex colors, lightmaps
- **GAT** — terrain height / walkability / navigation-related surface data
- **RSW** — map/world scene definition, object placement, lights, sounds, effects
- **SPR** — sprite image data
- **ACT** — animation actions, frame timing, offsets, anchors, events
- **RSM / GR2** — 3D world/model resources
- **STR** — effects

**Useful starting points:**
- GND:  
  https://ragnarokresearchlab.github.io/file-formats/gnd/
- ACT:  
  https://ragnarokresearchlab.github.io/file-formats/act/
- Rendering / coordinate-system documentation:  
  https://ragnarokresearchlab.github.io/rendering/

**Research focus:**
- Data separation
- Coordinate systems
- Terrain/world representation
- Sprite anchoring
- Animation metadata
- Elevation and walkability
- Scene composition

**ASTRAEON translation:**
Do not copy RO file formats directly. Recreate the same responsibilities using ASTRAEON-native data structures.

---

## 4. BrowEdit3

**Repository:** https://github.com/Borf/BrowEdit3

**Role:** Ragnarok map editor for working with RO world/map formats.

**Why it matters to ASTRAEON:**
Useful as a reference for level-authoring workflow rather than runtime rendering alone.

**Research focus:**
- Map authoring
- Object placement
- Terrain editing
- World composition
- Map inspection
- Separation between authored level data and runtime behavior

**ASTRAEON lesson:**
The game needs a proper authoring workflow. Blender can fill this role for ASTRAEON rather than trying to design towns directly inside runtime code.

---

## 5. rAthena

**Repository:** https://github.com/rathena/rathena

**Role:** Open-source Ragnarok Online MMORPG server package written primarily in C++.

**Important distinction:**
rAthena is **not the Ragnarok client renderer**.

It is useful for studying:
- Server-side map logic
- NPCs
- Warps
- Spawn systems
- Skills
- Combat
- Character/world state
- Map coordinates
- Map cache
- GAT/RSW usage for server-side map data

**Relevant directories:**
- `src/map`
- `src/char`
- `src/login`
- `npc`
- `db`
- `conf`
- `src/tool/mapcache.cpp`

**Why it matters to ASTRAEON:**
It reinforces the principle that gameplay/world logic should not depend directly on rendered images.

**ASTRAEON lesson:**
Keep navigation, collision, NPC logic, portal logic, and simulation data independent from visual presentation.

---

# How These Sources Map to ASTRAEON

| Ragnarok / Reference Concept | ASTRAEON Modern Equivalent |
|---|---|
| GND | Terrain / elevation / materials / roads / decals |
| GAT | Navigation grid or navmesh / blockers / surface types / elevation |
| RSW | Data-driven world definition / object placement / lights / audio / portals |
| RSM / GR2 | Modular 3D or structured pseudo-3D environment |
| SPR | High-resolution directional painterly sprites |
| ACT | Animation manifest with timing, anchors, contacts, events, attachments |
| BrowEdit | Blender-based level authoring workflow |
| rAthena map/server logic | ASTRAEON gameplay simulation and world logic |
| roBrowser | Browser-client architecture reference |
| NostalRO | Modern client/rendering/tooling architecture reference |

---

# Research Priority for ASTRAEON

Use the sources in this order for the current Wayfarer Square work:

1. **NostalRO**  
   Study rendering, scene separation, sprite/world depth, tooling, and modernization.

2. **Ragnarok Research Lab**  
   Study file-format responsibilities, coordinate systems, terrain, navigation, and ACT-style animation metadata.

3. **BrowEdit3**  
   Study map-authoring workflow and world construction.

4. **roBrowser**  
   Study browser-specific RO-like rendering/client patterns.

5. **rAthena**  
   Study server/map/NPC/warp/gameplay separation, not visual rendering.

---

# ASTRAEON Research Rules

When using these sources:

- Learn architecture, responsibilities, data flow, and production workflow.
- Do not copy official Ragnarok assets.
- Do not copy exact maps or layouts.
- Do not reproduce copyrighted visual content.
- Do not preserve old technical limitations merely because RO had them.
- Prefer modern browser rendering, scalable data contracts, high-resolution original art, and ASTRAEON-specific tooling.
- Use Wayfarer concept art as the artistic and spatial target.
- Use Blender as the preferred level-design/blockout authoring environment when spatial reasoning is needed.
- Use RO references to inform runtime structure, not visual imitation.

---

# Recommended Research Question

For every system studied, answer:

**How does RO separate this responsibility, how does ASTRAEON currently handle it, what should be preserved, what should be modernized, and which implementation approach is best for ASTRAEON: custom code, PixiJS, Three.js, Blender-authored data, or a hybrid?**
