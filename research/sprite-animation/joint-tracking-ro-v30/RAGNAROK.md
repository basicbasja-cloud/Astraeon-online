# Ragnarok source inventory and bounded reverse-engineering findings

## Coverage actually acquired

Public community source: [ragassets renderer](https://assets.latam-tools.com.br). This is one client-content snapshot; renderer APNG is not an official game capture or every regional/version asset library. Full raw JSON/raster archives stay in ignored local cache. Published indexes, hashes and small study boards preserve reviewable evidence without admitting RO art into our game assets.

| Catalog | Actual retrieved records | Published receipt/index |
| --- | --- | --- |
| Job | 290 | ro-table-retrieval.json / ro-job-index.json |
| Class family | 85 renderID families | ro-extra-table-retrieval.json / ro-class-hair-index.json |
| Items | 17,319 | ro-table-retrieval.json / ro-equipment-index.json |
| Skills | 1,732 | ro-table-retrieval.json, raw cache only |
| Status | 704 | ro-extra-table-retrieval.json, raw cache only |
| Monsters | 2,732 | ro-extra-table-retrieval.json / ro-monster-index.json |
| Headgear view rows | 3,098 item rows | numeric view index, not 3,098 unique drawings |
| Garment view rows | 205 item rows | numeric view index, not all layer frames |
| Hair | human male/female42styles each, Doram male/female10 each;9swatches/group | ro-class-hair-index.json, not all hair rendered |

1,340 actual action requests:1,275 decoded /65 failed,5,927decoded images/exposures:5,642have native exposure durations and285are untimed single PNGs (clock unknown, not invented). Every indexed class renderID was requested as male SE across13provider blocks.80families rendered; renderIDs20,4021,4069,4264,4305 returned HTTP500 for all13blocks and remain gaps. Swordman additionally covers both genders/all8requested directions/all13blocks. Poring covers5monster blocks/all8directions. This is not all classes×gender×direction×weapon×hair×equipment×client versions. Do not describe indexed skill/item/monster names as captured motion.

Scripts retain native APNG presentation times, exposure durations, unique-pixel hashes, canvas, fixed origin, identical-direction groups and failures. Empty or repeated poses remain in sequence. The two all-exposure books have104exposures across selected walk/attack requests; they use one shared crop per action and a fixed2×nearest scale, not per-frame fitting. The 35overview boards select fewer exposures and are labelled as such.

## Action labels and directions

Provider directions are S,SW,W,NW,N,NE,E,SE. Convert explicitly to our direction order; do not treat index as a universal direction enum.

| Block | Provider description | Pinned player-action code interpretation |
| --- | --- | --- |
| 0 | stand | idle |
| 1 | walk | walk |
| 2 | sit | sit |
| 3 | pickup | pickup |
| 4 | combat ready | ready |
| 5 | attack | primary attack |
| 6 | hurt | HURT |
| 7 | frozen1 | FREEZE |
| 8 | dead | DIE |
| 9 | frozen2 | FREEZE2 |
| 10 | attack variant1 | ATTACK2 |
| 11 | attack variant2 | ATTACK3 |
| 12 | attack variant3 | **SKILL** |

Keep provider labels and client meanings separately. `WeaponAction.js` maps class/weapon and sometimes gender to attack blocks. One job's action5 cannot represent all weapon families. Monsters/pets/homunculi have different action mappings.

Swordman decoded sequence comparison: stand/walk/sit show8distinct sequences in both genders. Pickup/ready/hurt/death and most alternate blocks show4; freeze2 shows1. Male primary attack shows5distinct sequences while female shows4. That is a pixel-sequence observation, not proof that five independent viewing angles were authored. **The statement “only stand/walk have8, everything else4 diagonal” is too broad** for this source. Requested direction slots and unique visible drawings are different counts; hairstyle/head look/compositing can contribute differences.

Male SE stand:3×100ms exposures but1unique drawing. Walk:8×75ms,8unique drawings,600ms. Sit:3×100ms but1drawing. These timings are renderer output for this probe, not a universal RO FPS rule. In pinned client code ACT stored delay is multiplied by25ms; walk delay depends on walking speed, and action-specific speed/length can override timing. Preserve hold durations rather than blindly redrawing every exposure.

## Modular parts and weapon/trail know-how

Primary implementation read at pinned commit `56d0bf7c97989f034314391f92ab77858d66701c` in [roBrowserLegacy](https://github.com/MrAntares/roBrowserLegacy/tree/56d0bf7c97989f034314391f92ab77858d66701c). [Receipt](ro-code-retrieval.json) hashes15files. Selected sections were read, not every line or all clients.

- [ACT loader](https://github.com/MrAntares/roBrowserLegacy/blob/56d0bf7c97989f034314391f92ab77858d66701c/src/Loaders/Action.js): layers retain image IDs, positions, scale, mirror, color, rotation and attachment positions; timing is file data. Repeated exposures/transforms do exist. Our per-perspective weapon drawings requirement remains intact; do not falsely claim every RO exposure is freshly painted.
- [EntityRender](https://github.com/MrAntares/roBrowserLegacy/blob/56d0bf7c97989f034314391f92ab77858d66701c/src/Renderer/Entity/EntityRender.js): action selection includes action×8 plus camera/entity direction. Non-main parts use animation attachment-position offsets. Body/head/robe/shield/weapon/trail draw order changes with facing and behind/front flags. Head idle/sit selection can depend on head direction.
- [WeaponAction](https://github.com/MrAntares/roBrowserLegacy/blob/56d0bf7c97989f034314391f92ab77858d66701c/src/DB/Jobs/WeaponAction.js): different class/weapon types map to different action slots. Store compatibility as explicit data rather than assume one shared attack bank fits every weapon.
- [WeaponTrailTable](https://github.com/MrAntares/roBrowserLegacy/blob/56d0bf7c97989f034314391f92ab77858d66701c/src/DB/Items/WeaponTrailTable.js): separate trail lookup is concrete evidence of a part/effect system. Table presence does not prove its timing/shape for an unrendered combination.
- [RRL ACT](https://ragnarokresearchlab.github.io/file-formats/act/) documents sprite anchors for body/head/weapon/shield/headgear relative positioning. [RRL SPR](https://ragnarokresearchlab.github.io/file-formats/spr/) documents indexed BMP and truecolor TGA segments, transparency and RLE. An ACT attachment is not an anatomical skeleton.

Factory application: each frame/direction has fixed shared origin, anatomical owner names, source time/phase, part offsets, explicit z order, socket local frame and compatibility tags. Hair swaps must preserve head anchor/occlusion; weapon/trail swaps must preserve palm/grip/cut clock. Near/far pieces cannot be chosen by screen-left/right. At crossing poses split occluded fragments explicitly, or keep image review unknown. No new complete replacement part bank was made here.

## Visible lessons from the selected frame books

The male walk book keeps compact body motion and alternates visible boot silhouettes; heel/toe and passing stance differ without moving the whole actor arbitrarily. Attack shows clear raised-hand→lowered sweeping hand and compressed follow-through. The last rows repeat body pixels: holds contribute readable recovery without requiring many new drawings. Eight requested columns visibly reuse multiple poses. Head/hair partly obscure arm silhouette; do not place a “detected” elbow inside a hidden patch solely because a source point expects it.

These are body/head-only public probes, **not complete sword renders**. They cannot prove grip/blade angle/tail quality or recovered force/COM. For an actual weapon study request the complete weapon/trail combination, inspect its native clock, then draw our own matching perspective bank. Do not turn the RO body book into hidden bone ground truth.

Use classic RO as motion/compositing reference and our approved appearance target as art-quality standard. RO3/ToS and other games remain indexed in v29 with their actual acquisition/reading status; a URL lead is not a decoded frame bank. Comprehensive coverage here means all entries in this retrieved class table were attempted, not “all Ragnarok assets acquired.”
