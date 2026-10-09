# RO1 assembly evidence and ASTRAEON decisions

## Pinned evidence

Raw male Swordsman body ACT/SPR acquired from public ragassets test fixtures, revision `4de4fa747431979d35c747d7edd549a872efd9e1`. Exact paths, hashes, action IDs and direction record hashes are in reference-coverage.json. Pixels and raw binaries remain in ignored `authoring/characters/private-ro-reference/true8dir/`. No copied RO pixels enter runtime or committed boards.

- [ACT format](https://ragnarokresearchlab.github.io/file-formats/act/): CONFIRMED_FORMAT. ACT stores action frames, ordered sprite layers, offsets, scale, rotation, image selection, tint, events, anchors and intervals. Anchor coordinates are attachment registration, not painted hand contact. A named action or anatomical joint is not stored in this format.
- [SPR format](https://ragnarokresearchlab.github.io/file-formats/spr/): CONFIRMED_FORMAT. Indexed images use palette entries with index zero transparent; truecolor images carry alpha. Multiple images are selectable per ACT frame. PAL replacement recolors indexed art.
- [Resolver](https://github.com/zhad3/zrenderer/blob/main/RESOLVER.md): CLIENT_TABLE_MAPPING. Job/gender/outfit select a body pair; head/gender select another pair; headgear resolves independently. Weapon names resolve through ReqWeaponName / GetRealWeaponId and job-weapon tables. Shield paths depend on job, gender and shield table. Weapon slash uses a distinct suffixed resource. Garments have job/gender-specific paths and a generic fallback. Alternate outfits replace the body resource, not a naked core under interchangeable clothing.
- [Sprite assembly source](https://github.com/adsonpleal/ragassets/blob/4de4fa747431979d35c747d7edd549a872efd9e1/gateway/internal/render/sprite/sprite.go): CONFIRMED_RENDERER_BEHAVIOR. Child placement adds body attach point zero and subtracts the child's attach point zero, then applies layer transforms. Head/accessory stand/sit views can slice a third of their frame sequence. This describes this renderer, not every historical official client.
- [Frame selection source](https://github.com/adsonpleal/ragassets/blob/4de4fa747431979d35c747d7edd549a872efd9e1/gateway/internal/render/engine/render.go): CONFIRMED_RENDERER_BEHAVIOR. The longest component establishes output frame count. Short sequences wrap, with three-frame and head-direction special cases. It is not universally normalized-time interpolation. Weapon resources use the same selected action and frame resolution path as other components.
- [Draw-order source](https://github.com/adsonpleal/ragassets/blob/4de4fa747431979d35c747d7edd549a872efd9e1/gateway/internal/render/sprite/zindex.go): CONFIRMED_RENDERER_BEHAVIOR. Directions 2..5 change body/shield ordering. IMF head priority can change ordering by action/frame. Garment ordering is handled separately by the engine and client tables; do not reduce it to one fixed cape z-index.
- [Required client resources](https://github.com/zhad3/zrenderer/blob/main/RESOURCES.md): CLIENT_TABLE_MAPPING. Layer-direction, robe, weapon, item-offset and IMF resources supplement ACT/SPR. Raw format alone cannot prove equipment resolution or ordering.

## Direction result

CONFIRMED_FORMAT: raw actions 0..7 and 8..15 contain eight distinct Idle and Walk records. Ready 32..39 and sword attack 80..87 duplicate adjacent action records: S=SW, W=NW, N=NE, E=SE. Other inspected attack groups likewise pair directions. Thus the previous four-projection observation is corroborated by raw data, not merely a renderer-cache hypothesis. It is not eight unique attack references.

VISUAL_DERIVED: all eight ASTRAEON attack projections combine the raw attack phase sequence with raw Idle/Walk direction evidence and original pose reconstruction. Confidence is medium, especially hidden elbows and depth. No diagonal is certified as exact original RO attack art. RO-derived phase order is retained; the ASTRAEON 450ms clock and 170ms contact remain unchanged. Raw format interval units and gameplay attack-speed rules are separate.

## Part separation

CONFIRMED_RENDERER_BEHAVIOR / CLIENT_TABLE_MAPPING: the head resource is independent of body, and its head style includes hair rather than requiring ASTRAEON's former separate Hair slot. Headgear remains a distinct resource. Owner subsequently requested this RO-style combined Head+Hair appearance model. Existing original face/hair art will be assembled into complete head variants. Costume swaps replace BodyWithOutfit only. Hair-style swaps select a complete head variant without resetting action or time.

INFERENCE / ASTRAEON design: explicit WeaponPoseSet with equipment anchor, visible grip contact, tip, perspective sample and draw profile makes the distinction inspectable. ACT image selection supports many weapon views, but this audit has not acquired a raw weapon ACT/SPR pair; exact sword perspective count is not claimed as a format fact. Slash remains optional separate presentation; Combat retains hit authority.

No community authoring assertion is promoted to CONFIRMED_FORMAT. No raw reference is shipped.
