# New anatomy source study

11 October 2026. `character/production-factory-v2`. **NO-SHIP.**

Owner feedback: "anatomy not correct right now please check, the hand is not correct".
Owner authorization: "you can download asset for based and polish until we have our."

The new source uses pixiv's CC0 VRoid Base Male beta body and native face. The
original palm and phalanx lengths are preserved. Native rotational finger curl
and thumb opposition are evaluated first; each whole hand receives one rigid
placement. Major body fitting remains an inference from the approved painting.
It is not an accepted anatomy or animation bind.

The previous compressed palm/circular finger paths are not reused. Existing
ASTRAEON costume design surfaces are refitted around the new body. No Ragnarok
pixels, proprietary sprite sheet or paid provider asset is used.

Source fitting includes sleeve-surface bracers, connected hilt/pommel, boot room,
native iris UV recoloring, a coherent cape grid, and a whole-head pose study.
A bounded 8.71-degree sword-frame adjustment rotates the palm and hilt together;
its tip changes 1.18 pixels in the reference projection. Actual rear visibility
and contact are checked in the rendered source, not certified by the search.
The older source04 sword-depth experiment failed and was rolled back.

`review.html` compares the unchanged approved painting and the new source on a
shared canvas/root, with game size, anatomy-only views and grip diagnostics.
Body/outfit, head/hair, weapon and cape are rendered from the same source frame.
Headgear is unequipped. These visible-only static modules are combination-specific.
Hidden handle pixels are covered by the real hand. They do not prove arbitrary
costume/weapon swapping or motion coverage.

The anatomy/head donor, Fumiriya inspection, unused Shibu download and inactive
HairSample_Male comparison are recorded separately in `FREE_ASSET_PROVENANCE.json`.
The hair alternative was not selected because it misses the approved design.
Publisher license evidence and exact download hashes are retained. Raw downloads
remain in the ignored local cache; the native project is a local working copy.

## Reproduce this study

Use the connected Blender MCP in safe mode. Start from the preserved source03/04
working checkpoint and separate imported donor inspection scenes. Scripts are
source-native Blender Python, sent as code through MCP, not external execution
inside Blender. Run once for builders; correction/bake scripts are repeatable.

1. `build-anatomical-hand-study.py`, `refine-anatomical-hand-study.py`.
2. `build-vroid-anatomy-source-study.py`, `polish-vroid-anatomy-source-study.py`.
3. `correct-anatomy-source-contact.py`, `refine-anatomy-source-face-pose.py`.
4. Optional read-only `probe-anatomy-weapon-clearance.py`, then the selected
   `refine-anatomy-weapon-clearance.py` shared fit.
5. `polish-anatomy-source-clothing.py`, then `bake-new-anatomy-source-checks.py`
   and `bake-anatomy-source-modules.py`.
6. Save Copy to `.character-tools/checkpoints/anatomy-base-05-native.blend`,
   export scene receipts, then host `record-anatomy-source-study.py`.

The current recipe depends on existing authoring/inspection scenes. It is not a
self-contained clean-room factory build yet. Do not reapply step 3 after step 4
without resetting the sword frame; step 3 is an earlier fitting stage.

## Remaining work

Approved facial/hair likeness, costume silhouette and painted finish remain
unresolved. The native body has 156 boundary edges and requires joint topology
and deformation review before a production rig. The active source has zero
armatures/actions. Imported donor rigs exist only in inspection scenes.
No approved animation, complete action matrix or admitted runtime package exists.
The accepted concept is unchanged; this study has no owner approval.
