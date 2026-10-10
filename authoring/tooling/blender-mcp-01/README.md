# Verified local Blender toolset

10 October 2026. Branch `character/production-factory-v2`.

**LOCAL_MCP_CONNECTION_VERIFIED.** The owner authorized implementation after
the tooling research. This checkpoint installs and verifies the toolset; it is
not a new character, approved pose, motion library or completed factory.

Installed:

- `character-artist`, `rigging`, and `qa-review` in the user's Codex skills
  directory, pinned to arjun988/blender-skills commit
  `8f778d2405a214b508d4c7d80742be8e43acdd52`. All nine shared reference files
  and original MIT license are retained. Project-specific notes map the current
  MCP tool names and preserve ASTRAEON's reference and owner-approval rules.
- MCP for Blender 2.1.9 from ahujasid/mcp-for-blender commit
  `7a0373ec9199183cb460068c4f96aed9c579fb4f`, in an isolated Python 3.14 venv
  under `C:/Users/Lenovo/.codex/tools/astraeon-blender-mcp/`.
- The matching addon in Blender's user addon directory, enabled together with
  bundled Rigify. Existing user preferences were preserved; only these addons
  were enabled and the new addon's telemetry consent was set false.
- Global Codex STDIO entry `blender`, restricted to scene query, visual capture,
  Blender code execution and addon/telemetry status. Launch variables disable
  telemetry, enable safe mode and select localhost:9876. No uv installation
  was needed. Other existing MCP entries were preserved; the prior config has
  a private local backup in the tool directory.

`connection-validation.json` records actual MCP SDK round trips to Blender
5.2.2 LTS. Seven checks pass: protocol/tool discovery, telemetry-off state,
scene query, a cube moved and restored, returned viewport pixels, a blocked
non-Blender import, and Rigify generation with arm IK/finger controls (706 bones).
Paid generators and Premium are off. No paid jobs or provider keys were used.

`disposable-viewport.png` is inspected connection-test evidence, not character
art. `disposable-rigify.blend` is an editable generic Rigify test rig, not a
skeleton fitted to the approved character. The hidden Blender process is owned
by this task and keeps the local addon socket available. Its PID/logs are
ephemeral and excluded from the saved artifact manifest.

`rigify-skeleton-guide.png` shows the actual default metarig from front and
profile, captured through MCP with other scene objects temporarily hidden.
Visibility and selection were restored. This demonstrates available skeleton
guidance; its adult proportions are not an ASTRAEON proportion proposal.

## Compatibility fixes

The upstream addon installer copied successfully but its final Unicode arrow
failed on Windows cp1252 stdout. Installed addon bytes were verified against
the pinned bundled source; MCP launch uses UTF-8.

The pinned upstream release also lacks the config module imported by its
telemetry collector. Two local status-helper fixes are recorded in
`local-patch.json`: when launch variables disable collection, the off tool
returns after disabling addon consent; addon status reads live consent directly
from Blender. The upstream checkout is preserved unchanged; installed code
has a separate hash. Selected tools were re-tested after the fixes. The
dependency lock and source/archive hashes are retained here.

## Use and next gate

The installed skills become discoverable on the next turn. Restart Codex once
to load the newly registered MCP tools into chat; an enabled config entry alone
was not used as connection evidence. Keep Blender open when using its tools.
If starting Blender normally, the enabled addon auto-starts its local socket.
Use one Blender owner for port 9876; do not open two instances on that port.

To repeat the isolated proof, launch a dedicated Blender with
`tools/bootstrap-blender-mcp.py` and then run `tools/verify-blender-mcp.py`
using the installed venv Python. The verifier deliberately refuses any scene
except its named disposable scene. It removes earlier test rigs only inside
that owned scene. Do not run it against a character-authoring scene.

The next character work is a fresh proportion and pose blockout against the
unchanged approved candidate-01, followed by anatomical palm/thumb/finger grip
review at the reference angle and W/NW/N. The rejected free-master-01 is
preserved: all 50 manifest entries were checked unchanged. No detailed costumes
or motion expansion before owner acceptance of those gates.
