# Candidate art provenance

Built-in imagegen was used; no external paid-provider CLI. Original ASTRAEON six-cell inputs are saved beside generated results. RO raw attack board was supplied only as motion reference for NW/NE, with explicit no-copy instruction. No RO pixels are shipped.

Prompt set: surgical right sword-arm and shoulder-seam repair on six poses (frames 6,7,9,13,14,15), preserving original head, hair, face, torso, pelvis, costume and boots. SW/W require an open elbow and forward/downward contact; NW/NE require rear arm continuity outside shoulder/cape; middle recovery lowers the fist to shoulder level before returning overhead. Closed empty gauntlet, no sword/cape/effects, six-cell layout, transparent background. Each direction received its own image and prompt, never a mirrored neighboring direction.

Weapon prompt: original Sword A and Sword B design references; four physical views per design, upright broad face, narrow edge, foreshortened toward viewer and rear face. No hand or FX. Both designs retain their bronze/teal identity. Generated sheet normalized at common .21 scale; grip/equipment/tip landmarks are in weapon-samples.json.

Integration: generated arm keypoints manually annotated in generated-arm-landmarks.json. Uniform .43 scale and shoulder registration; authored old/new limb masks preserve outside pixels. Generated hair context removed only inside its head region. In-between frames 8,10,11,12 are explicitly deformed from reviewed key art with interpolated joint targets, not blind whole-frame reuse. These are ASTRAEON in-betweens, not raw RO frames. All 40 modified frames and review landmarks are in limb-receipt.json.

Combined head sets are raster assemblies of the existing original Head+Hair layers, not newly generated identities. Headgear sockets remain independent. Head masks are not body/neck anatomy proof.

All outputs remain candidates pending owner visual approval.
