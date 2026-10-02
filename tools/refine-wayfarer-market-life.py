"""Add two ambient market pedestrians to the existing saved Wayfarer scene.

This is a targeted Golden iteration. It preserves the existing town and route
definitions, then relies on the normal scene exporter for the runtime data.
"""
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get("world_id") == "wayfarer-spatial"

owner = "market-shop"
collection = bpy.data.collections[owner]
placement = bpy.data.objects[owner + "-placement"]

# The north edge of the market browsing area is a clear lane above the stall
# counters. Opposing routes keep both arrivals visible without crossing the
# food and spice counters or changing navigation geometry.
walkers = [
    (
        "market-buyer-2",
        [(27.2, 21.05), (29.5, 21.05), (32.1, 21.05), (34.8, 21.05), (36.15, 21.7)],
        0.43,
        28,
    ),
    (
        "market-courier-1",
        [(36.15, 21.7), (34.7, 21.45), (32.0, 21.45), (29.4, 21.45), (27.2, 21.05), (30.0, 21.05), (33.8, 21.05)],
        0.47,
        184,
    ),
]

for object_id, route, pace, tint in walkers:
    actor = bpy.data.objects.get(object_id)
    if actor is None:
        actor = bpy.data.objects.new(object_id, None)
        collection.objects.link(actor)
    actor.parent = placement
    # Walker routes are stored as offsets from the placement origin and then
    # transformed through this anchor by the scene exporter.
    actor.location = (0, 0, 0)
    actor.empty_display_type = "CIRCLE"
    actor.empty_display_size = 0.1
    actor["kind"] = "walker"
    actor["data_json"] = json.dumps({"pace": pace, "tint": tint}, separators=(",", ":"))
    actor["route_json"] = json.dumps(
        [[x - placement.location.x, y - placement.location.y, 0] for x, y in route],
        separators=(",", ":"),
    )

bpy.context.view_layer.update()
target = ROOT / "authoring/wayfarer-spatial.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print("Saved market pedestrians:", ", ".join(item[0] for item in walkers), "to", target)
