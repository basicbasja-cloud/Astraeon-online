"""Exercise actual MCP/Blender round trips in an owned disposable scene."""
import asyncio
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OUTPUT = Path(__file__).resolve().parents[1] / "authoring/tooling/blender-mcp-01"
SERVER = Path.home() / ".codex/tools/astraeon-blender-mcp/venv/Scripts/mcp-for-blender.exe"


def result_text(result):
    return "\n".join(c.text for c in result.content if c.type == "text")


async def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(DISABLE_TELEMETRY="true", BLENDER_MCP_DISABLE_TELEMETRY="true",
               BLENDER_MCP_SAFE_MODE="1", BLENDER_HOST="127.0.0.1",
               BLENDER_PORT="9876", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    checks = []
    captures = []
    replies = {}
    stderr_log = (OUTPUT / "mcp-stderr.log").open("w", encoding="utf-8")
    async with stdio_client(StdioServerParameters(command=str(SERVER), env=env), errlog=stderr_log) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            names = [t.name for t in (await session.list_tools()).tools]
            for name in ("get_scene_info", "look", "execute_blender_code", "disable_telemetry"):
                assert name in names, name
            checks.append("MCP initialize and tool discovery")

            async def call(name, arguments):
                result = await asyncio.wait_for(session.call_tool(name, arguments), timeout=90)
                assert not result.isError, result_text(result)
                return result

            disabled = await call("disable_telemetry", {})
            replies["telemetry"] = result_text(disabled)
            assert "Data collection is OFF" in replies["telemetry"], replies["telemetry"]
            consent = await call("get_addon_status", {})
            addon_status = json.loads(result_text(consent))
            assert addon_status["telemetry_consent"] is False, addon_status
            assert not addon_status["premium_generators"], addon_status
            assert all(v.startswith("off") for v in addon_status["generators"].values()), addon_status
            replies["addonStatus"] = addon_status
            checks.append("Telemetry-off tool succeeds and live addon consent is false")
            initial = await call("get_scene_info", {})
            replies["initialScene"] = result_text(initial)
            assert "ASTRAEON_MCP_DISPOSABLE_CONNECTION_TEST" in replies["initialScene"]
            checks.append("Scene query reaches owned disposable Blender")

            code = '''import bpy
scene = bpy.context.scene
assert scene.name == "ASTRAEON_MCP_DISPOSABLE_CONNECTION_TEST"
cube = bpy.data.objects.get("Cube")
assert cube is not None
original = cube.location.copy()
cube.location.x += 0.75
bpy.context.view_layer.update()
assert abs(cube.location.x - original.x - 0.75) < 1e-6
cube.location = original
bpy.context.view_layer.update()
assert (cube.location - original).length < 1e-6
print("MCP_REVERSIBLE_EDIT_PASS: cube moved 0.75 and restored")
'''
            edited = await call("execute_blender_code", {"code": code})
            replies["reversibleEdit"] = result_text(edited)
            assert "MCP_REVERSIBLE_EDIT_PASS" in replies["reversibleEdit"]
            checks.append("Safe-mode Blender edit executes and restores original transform")

            capture = await call("look", {"mode": "angles", "target": ["Cube"],
                                        "views": ["front", "three_quarter"], "max_size": 768})
            for content in capture.content:
                if content.type == "image":
                    data = base64.b64decode(content.data)
                    f = OUTPUT / "disposable-viewport.png"
                    f.write_bytes(data)
                    captures.append({"path": f.name, "bytes": len(data),
                                     "sha256": hashlib.sha256(data).hexdigest()})
            assert captures, result_text(capture)
            replies["viewport"] = result_text(capture)
            checks.append("Actual Blender viewport capture returned through MCP")

            # This blocked script never executes. It verifies the configured guard.
            blocked = await session.call_tool("execute_blender_code", {"code": "import subprocess"})
            blocked_text = result_text(blocked)
            assert "blocked" in blocked_text.lower() or "not allowed" in blocked_text.lower(), blocked_text
            checks.append("Safe mode rejects a non-Blender import")

            rig_code = '''import bpy
import mathutils
assert bpy.context.scene.name == "ASTRAEON_MCP_DISPOSABLE_CONNECTION_TEST"
# Only repeat against this owned disposable scene; clear earlier test objects.
for obj in list(bpy.context.scene.objects):
    if obj.name != "Cube":
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.object.armature_human_metarig_add()
metarig = bpy.context.active_object
metarig.name = "MCP_Rigify_Guide"
assert "f_index.01.R" in metarig.data.bones
assert "thumb.01.R" in metarig.data.bones
bpy.ops.pose.rigify_generate()
rig = bpy.context.active_object
assert "hand_ik.R" in rig.pose.bones
assert "f_index.01_master.R" in rig.pose.bones
print("RIGIFY_GENERATION_PASS", len(rig.pose.bones), "bones; arm IK and finger controls present")
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath("//mcp-disposable.blend"))
'''
            # Use an explicit path; factory-startup has no production source path.
            rig_code = rig_code.replace('bpy.path.abspath("//mcp-disposable.blend")',
                                        repr(str(OUTPUT / "disposable-rigify.blend")))
            rig_result = await call("execute_blender_code", {"code": rig_code})
            replies["rigify"] = result_text(rig_result)
            assert "RIGIFY_GENERATION_PASS" in replies["rigify"]
            checks.append("Rigify generates an editable rig with arm IK and finger controls")

    stderr_log.close()
    receipt = {"status": "LOCAL_MCP_CONNECTION_VERIFIED", "checks": checks,
               "captures": captures, "replies": replies, "paidJobs": 0,
               "characterApproval": False, "productionCharacterChanged": False}
    (OUTPUT / "connection-validation.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "checks": checks, "captures": captures}, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main())
