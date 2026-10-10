# Blender tooling after free-master-01 rejection

Researched 10 October 2026. Branch `character/production-factory-v2`.
Scope: answer the owner's request for installable Blender skills, skeleton
guidance and MCP. No new software was installed during this research. No new
character was generated, rendered or modified. The rejected source remains
abandoned; the original painted concept remains the target.

## Recommendation

Use one local Blender MCP connection, selected character/rigging guidance, and
Blender's bundled Rigify. These have complementary roles. MCP supplies live
scene inspection and editing; skills supply process instructions; Rigify
supplies fitted skeleton controls. None establishes ASTRAEON likeness or visual
approval by installation alone. The earlier failure was a generic proportion
transformation and insufficient reference-pose/grip matching, even though
binding and render checks passed.

### MCP for Blender

[Primary repository](https://github.com/ahujasid/mcp-for-blender), formerly
`ahujasid/blender-mcp`, MIT. Inspected current commit
`7a0373ec9199183cb460068c4f96aed9c579fb4f`; its pyproject version is 2.1.9.
Inspected README, addon.py, server.py, telemetry.py, rigging guide, pyproject
and Codex integration configuration. This is a community integration, not a
Blender Foundation product.

The server supports scene queries, visual inspection and Blender Python
execution. Its rigging guide specifically covers fitting a Rigify metarig,
generating controls, skinning to the generated rig and inspecting deformation.
This would improve the edit/capture/judge cycle over disconnected batch scripts.
It still executes Python and does not supply a trained character artist.

Use a pinned release/source matching the inspected version rather than the
unversioned one-line automatic installer. Keep the socket on localhost (default
port 9876; no socket authentication). Configure `DISABLE_TELEMETRY=true` and
`BLENDER_MCP_DISABLE_TELEMETRY=true`; leave addon telemetry consent false
(the inspected current addon defaults false). Set `BLENDER_MCP_SAFE_MODE=1`.
Do not enable optional paid generation integrations, premium, or asset imports
for the initial local proof. Local modeling and posing need no provider credits;
Codex usage still applies.

The plugin-directory search for Blender returned no entries on this date. The
repo contains a separately installable Codex marketplace integration, but it
uses an unpinned server command. Prefer the smaller pinned plain MCP setup for
the first connection check. No marketplace/plugin registration was performed.
Blender 5.2 is within the README's stated Blender 3.0+ prerequisite, but actual
local addon/MCP compatibility has not been tested.

### Character and rigging skills

[arjun988/blender-skills](https://github.com/arjun988/blender-skills), MIT.
Inspected commit `8f778d2405a214b508d4c7d80742be8e43acdd52`.
Reviewed the actual `character-artist`, `rigging`, `blender-director` and
`qa-review` SKILL.md files, body-proportions and humanoid-rig references. The
most directly useful initial skills are:

- `.claude/skills/character-artist`: proportion blockout before detailing,
  connected anatomy, deformation loops and separately modeled garments.
- `.claude/skills/rigging`: IK/FK, pole targets, constraints, weight cleanup
  and deformation review; includes a humanoid skeleton guide.
- `.claude/skills/qa-review`: actual screenshots and explicit visual verdicts.

These are short community guidance documents, not validated automatic organic
modeling algorithms. Their generic head-unit ratios must not replace measurements
of the approved character. Fingers are optional in the generic humanoid guide;
ASTRAEON sword gripping requires them. Generic FBX/GLB and engine bone-budget
rules are not this project's final 2D runtime contract.

Important install detail: skills reference sibling
`.claude/skills/references/`, including reference-image-match,
visual-match-checklist and asset-pipeline. Installing only three SKILL.md files
would leave these paths unresolved. Preserve the needed shared references and
license, inspect their contents before activation, and avoid installing all 94
unrelated skills. Use the system skill-installer with the pinned commit for
selected skill directories; references need separate placement/verification.

Also reviewed
[oh-ashen-one's concept-target-visual-gate](https://github.com/oh-ashen-one/blender-agent-skills/tree/e45ebb2b4ef29eace83572f083daff94c10215a1/concept-target-visual-gate).
Its useful principle is to keep the concept fixed and compare captured results
in the order silhouette/proportion before detail. It also contains generic
shipping/pushing instructions that must not override this owner's acceptance
gate or repository authorization. It is an optional process aid, not a skeleton
or character generator. No skill from these third-party repositories was activated.

### Skeleton, arm pose and grip

[Official Rigify manual](https://docs.blender.org/manual/en/5.2/addons/rigify/index.html)
and [bone positioning guide](https://docs.blender.org/manual/en/5.2/addons/rigify/bone_positioning.html).
Rigify is bundled with Blender; its local directory was confirmed at
`C:/Program Files/Blender Foundation/Blender 5.2/5.2/scripts/addons_core/rigify`.
Presence is verified; enablement and a new character rig are not.

The official guide places joints at anatomical landmarks and aligns finger
bend axes with knuckles. The
[limb documentation](https://docs.blender.org/manual/en/5.2/addons/rigify/rig_types/limbs.html)
describes arm IK/wrist pivots, finger curl controls, optional fingertip IK and a
held-object parent control. Finger IK adjusts an FK-authored finger shape to
touch a surface; the manual explicitly does not describe it as a complete
posing system. Therefore grip must be authored with palm placement, thumb
opposition, joint curl and real contact/clearance, then inspected. Endpoint
distance alone is insufficient.

Official pages were fetched successfully with Python requests after the web
reader returned 402 errors. No payment is needed to read these manuals.

## Local readiness and installation proof

- Blender 5.2.2 and bundled Rigify are present.
- Codex CLI is present; its local `mcp add --help` confirms STDIO command and
  `--env` configuration support. No config was changed.
- `uv` and `uvx` were not found on the current PATH. Their installation or an
  isolated alternative would be needed for the documented MCP route.
- The system curated-skill listing was queried; it contained no Blender skill.
  The reviewed community repositories are separate sources.
- Existing game asset production and sprite pipeline skills remain available.
  They cover pipeline operations but do not establish this character's anatomy.

After the owner selects installation: retain pinned source/license receipts,
install selected skills with complete references, add one local MCP entry with
telemetry disabled, then verify scene query, viewport capture and a reversible
object edit in a disposable scene. Merely listing an enabled MCP entry is not
a successful Blender connection. Do not touch the rejected character for this
connection test.

## Next character gate

Before any new detailed source, measure the approved image's projected head,
shoulder, torso, pelvis, knee, boot and wrist landmarks. These are image-space
targets, not guessed hidden 3D anatomy. Match framing, body/head proportion,
weight distribution, elbow/wrist pose and blade axis in a fresh low-detail
blockout at comparable view and common scale. List uncertain hidden anatomy
explicitly. Show side-by-side captures at authoring and game size, with body and
pose assessed independently from material polish.

Then author the grasp using actual finger-joint controls and inspect the full
character plus hand detail in the reference angle and W/NW/N. Model the complete
hilt for physical attachment; the eventual weapon-only sprite may omit pixels
covered by the owning hand, following the owner's Ragnarok example. This is a
layer/occlusion decision, not a substitute for a correct source grip.

Stop for owner visual judgment at those gates. Only accepted geometry/pose/grip
can expand into eight directions, reusable motion, costumes and layered 2D
exports. No reviewed tool demonstrated an automatic, reliable Ragnarok-style
factory matching this exact approved concept.
