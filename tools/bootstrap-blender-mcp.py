"""Enable the pinned local addon; optionally open an owned disposable test scene.

Run with Blender --python this-file -- --enable-only --output receipt.json,
or start a GUI Blender with --factory-startup --python this-file -- --output
receipt.json. The GUI test scene is not a production character.
"""
import argparse
import json
from pathlib import Path
import sys

import addon_utils
import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--enable-only", action="store_true")
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--port", type=int, default=9876)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

addon_utils.enable("blender_mcp", default_set=True, persistent=True)
addon_utils.enable("rigify", default_set=True, persistent=True)
prefs = bpy.context.preferences.addons["blender_mcp"].preferences
prefs.telemetry_consent = False
scene = bpy.context.scene
for name in ("polyhaven", "hyper3d", "hunyuan3d", "sketchfab", "tripo"):
    prop = "blendermcp_use_" + name
    if hasattr(scene, prop):
        setattr(scene, prop, False)

if args.enable_only:
    # Preserve the existing user preferences, enabling only these two addons.
    bpy.ops.wm.save_userpref()
else:
    # This GUI process was launched with factory startup, never an owner source.
    scene.name = "ASTRAEON_MCP_DISPOSABLE_CONNECTION_TEST"
    scene.blendermcp_auto_start_server = False
    import blender_mcp
    server = getattr(bpy.types, "blendermcp_server", None)
    if server is None:
        server = blender_mcp.BlenderMCPServer(host="127.0.0.1", port=args.port)
        bpy.types.blendermcp_server = server
        server.start()
    scene.blendermcp_server_running = server.running

receipt = {
    "blenderVersion": bpy.app.version_string,
    "addonEnabled": "blender_mcp" in bpy.context.preferences.addons,
    "rigifyEnabled": "rigify" in bpy.context.preferences.addons,
    "telemetryConsent": bool(prefs.telemetry_consent),
    "preferencesSaved": args.enable_only,
    "disposableScene": not args.enable_only,
    "serverRunning": bool(getattr(scene, "blendermcp_server_running", False)),
    "host": "127.0.0.1",
    "port": args.port,
    "paidJobs": 0,
}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print("ASTRAEON_MCP_BOOTSTRAP", json.dumps(receipt))
