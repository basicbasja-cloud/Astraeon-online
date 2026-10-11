# Ragnarok as hard reference

2026-10-11. Binding user steering: study **rig, sprite production and Ragnarok**, with Ragnarok as the hard reference. Other rigs and generic sprite tutorials supply techniques; they do not replace the required RO sprite appeal. No rejected Astraeon character art is a reference.

## Reference hierarchy

| Reference | Use | Limit |
|---|---|---|
| [Official Gravity Swordsman gallery](https://ro.gnjoy.asia/gallery/detail.php?id=3) and [class introduction](https://renewal.playragnarok.com/gameguide/classes_introduction.aspx?c=2) | Actual RO class/source context | Opened pages are not frame-by-frame combat captures |
| Ragnarok Research Lab [ACT](https://ragnarokresearchlab.github.io/file-formats/act/), [SPR](https://ragnarokresearchlab.github.io/file-formats/spr/), [animation](https://ragnarokresearchlab.github.io/rendering/animation-systems/), [camera](https://ragnarokresearchlab.github.io/rendering/camera-controls/) | Attachment, image, timing and camera behavior | Reverse-engineered, version-dependent observations; experiments were not reproduced |
| Pinned [roBrowserLegacy renderer](https://github.com/MrAntares/roBrowserLegacy/blob/1370afa878ba296a6ea35f5b76eb904a2611537b/src/Renderer/Entity/EntityRender.js) | Body/head/equipment/trail composition | Community implementation, not official source |
| [ragassets](https://github.com/adsonpleal/ragassets) | Actual externally rendered sprite poses with exact request parameters | Merged client asset tree and conversion timing, not original-client recording |
| Final game's native-scale scene | Judge original art under real camera/combat behavior | Not executed in this study yet |

## Fresh visual study executed

Eight public requests used `job=1`, `gender=male`, `head=1`, `weapon=2`, `action=80..87`, `enableShadow=false`. Each returned a nine-frame APNG with nine 100 ms delays. View canvases were 104×121, 84×134 or 82×134. Preparation, load, drive and strike poses were inspected together. [Request/hash/frame audit](ro-hard-reference-audit.json) records the responses. External RO images remain outside this repository and the original-character package.

This block supplies **four unique animation hashes**, reused by adjacent indices: 80/81, 82/83, 84/85, 86/87. Eight valid directional indices do not prove eight distinct drawings. Direction labels follow the provider convention; actual reused views remain evidence. This does not establish a universal rule for historical RO or excuse missing directions in our own contract.

The inspected preparation lifts a leg and loads the body. Later poses widen/settle the stance, displace the hips and lean the torso into the cut. The strike uses a broad blade smear. Low pose cadence still communicates force because body and weapon change together. These observations concern this particular attack, not every RO class or slash.

The provider uses `(animation_type × 8) + direction`, ordered `S,SW,W,NW,N,NE,E,SE`. Our prototype uses `S,SE,E,NE,N,NW,W,SW`. Translate with an explicit mapping and verify visible face/chest/weapon orientation. The provider README also contains an inconsistent monster arithmetic example; actual sprite/action data takes precedence over that prose.

## Eight selectable directions versus four drawings

The user observed that standing/walking use eight directions while other actions use four diagonals. A follow-up made **64 bounded sequential requests** for eight selected action blocks of the same male Swordman. `headdir=straight` fixes the head option and excludes the provider's optional idle/sitting head-look cycle. [Action-direction audit](ro-action-direction-audit.json) records exact URLs, file/decoded hashes, frame counts and delays. Sitting, standard-attack and death contact sheets were visually inspected outside the repository.

| Selected action | Block / indices | Distinct decoded sequences | Observed reuse |
|---|---|---:|---|
| Stand | 0 / 0–7 | 8 | All separate |
| Walk | 1 / 8–15 | 8 | All separate |
| **Sit** | 2 / 16–23 | **8** | All separate; direct exception to “only stand/walk” |
| Pick up | 3 / 24–31 | 4 | Adjacent pairs |
| Combat ready | 4 / 32–39 | 4 | Adjacent pairs |
| Standard attack block | 5 / 40–47 | 5 | Three identical pairs; N/NE differ in one head-region sample |
| Hurt | 6 / 48–55 | 4 | Adjacent pairs |
| Death | 8 / 64–71 | 4 | Adjacent pairs |
| Earlier weapon attack variant | 10 / 80–87 | 4 | Adjacent pairs; earlier request parameters omit fixed `headdir` |

For block 5, N/NE have equal 53×81 canvases and five 100 ms frames. Only frame 1 differs: 70 pixels in source box `[13,18,27,24]`, at the head/upper-neck region. The other four frames are identical. Five distinct decoded sequences therefore do **not** establish five intended attack camera angles. Preserve this anomaly pending attachment/source-ACT investigation. Whole-animation hashes are equality evidence, not an automatic artistic-view classifier.

The practical finding is: **standing, walking and sitting can use eight distinct views; many tested combat/interaction actions reuse four diagonals.** Declare the map per action. These requests do not audit every class, gender, head/body combination, freeze/cast action or weapon variant, and do not substitute for an original-client recording or a source-ACT audit.

The archived [ActOR2 manual](https://raw.githubusercontent.com/CairoLee/Ragnarok.Tools/master/ClientTools/ActOR2/help/how_to_use_it.html), English `Dir.4→8` section lines 160–169, explicitly describes copying diagonal actions to adjacent cardinal directions. The [rAthena Acts guide](https://github.com/rathena/rathena/wiki/Acts) also documents that operation and notes differing view counts for monsters/NPCs. These technical sources support explicit action-view reuse; they do not establish every class's actual unique-image matrix.

The prototype now offers an optional paired attack policy: `S/SW→SW`, `W/NW→NW`, `N/NE→NE`, `E/SE→SE`. It selects a complete existing diagonal view for every equipped piece; no image flip is used. This is a research option, not a silent change to the game's direction contract. The original eight independently rendered views remain available. Current Chromium verification passed all eight requested-to-source mappings while retaining the same attack subframe; see the 31-check browser report in the review package.

For future production, declare **selectable facing coverage**, **authored view coverage** and **action-specific facing map** separately. Keep body, head, hair, weapon and FX on the same resolved action view. A coverage validator should accept intentional declared reuse, reject an undeclared missing direction, and preserve anatomical ownership. A mapped attack still targets the requested world direction; picture selection must not rotate gameplay aim to match its diagonal art.

## Production rules

- Use RO's readable oblique sprite presentation and compact silhouette as visual reference. The user's silver-haired, gold-scarf illustration supplies identity; no RO artwork is copied into its source.
- Judge head/face, wrist/grip, boots and equipment at native gameplay scale. A polished large illustration alone does not establish sprite quality.
- Author anticipation, whole-body commitment, fast strike and recovery. Our provisional 800 ms delays `[80,100,100,60,60,120,140,140]` are a new design, not a universal measured RO rate. Attack-speed integration remains untested.
- Preserve the user's anatomical right-hand sword even when references reuse or mirror views.
- Distinguish pose-authoring bones from exported runtime attachments. Complete body/head/hair/equipment still need one authoritative pose and anchors.
- Classic head-style replacement and independent hair replacement differ. Our complete bald-head/hair split is a deliberate extension.
- Register a separate trail to the blade sweep and clear it after the cut/interruption. The current ribbon remains unapproved and does not yet reproduce the inspected RO smear's appeal.
- Preserve fixed capture scale and root. The provider's different view canvas sizes do not justify independently scaling or recentering our frames.

## Remaining limits

The proof's 30° orthographic capture and 128 px display canvas are provisional research choices, not exact RO camera settings or final Astraeon contracts. Astraeon's earlier technical snapshot uses another world-camera pitch; captured sprite elevation and world projection need joint review. The simplified head, rigid cloth and segmented limbs remain prototype art. An approved turnaround, final attack/effect acting and actual game checks are still required before adopting a production base.
