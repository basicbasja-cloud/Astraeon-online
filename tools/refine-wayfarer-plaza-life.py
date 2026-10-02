"""Place two authored pedestrians on the clear paving around Wayfarer's fountain."""
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
assert bpy.context.scene.get("world_id") == "wayfarer-spatial"

# Preserve each existing walker's intended character look explicitly before
# adding new actors to the fountain collection.
walker_kinds = {
    "guard-1": "guild",
    "guard-2": "guild",
    "customer-1": "market",
    "market-buyer-2": "market",
    "market-courier-1": "craft",
}
for actor in bpy.data.objects:
    if actor.get("kind") != "walker" or actor.name not in walker_kinds:
        continue
    data = json.loads(actor["data_json"])
    data["kind"] = walker_kinds[actor.name]
    actor["data_json"] = json.dumps(data, separators=(",", ":"))

owner = "astral-fountain"
collection = bpy.data.collections[owner]
placement = bpy.data.objects[owner + "-placement"]

# Both loops stay on the walkable paving around the fountain basin and the Hall
# stair landing. Segments were checked against the live authored navigation.
walkers = [
    (
        "plaza-pedestrian-1",
        [(19.3, 19.0), (20.2, 21.2), (22.5, 21.7), (24.2, 19.7), (22.8, 17.4), (20.1, 17.3)],
        0.38,
        64,
        "travel",
    ),
    (
        "plaza-pedestrian-2",
        [(24.5, 20.7), (23.3, 22.7), (20.6, 22.7), (18.5, 20.6), (19.4, 18.0), (21.8, 17.0), (24.0, 18.0)],
        0.42,
        176,
        "market",
    ),
]

for object_id, route, pace, tint, kind in walkers:
    actor = bpy.data.objects.get(object_id)
    if actor is None:
        actor = bpy.data.objects.new(object_id, None)
        collection.objects.link(actor)
    actor.parent = placement
    # The exporter transforms route offsets through this placement anchor.
    actor.location = (0, 0, 0)
    actor.empty_display_type = "CIRCLE"
    actor.empty_display_size = 0.1
    actor["kind"] = "walker"
    actor["data_json"] = json.dumps(
        {"pace": pace, "tint": tint, "kind": kind}, separators=(",", ":")
    )
    actor["route_json"] = json.dumps(
        [[x - placement.location.x, y - placement.location.y, 0] for x, y in route],
        separators=(",", ":"),
    )

bpy.context.view_layer.update()
target = ROOT / "authoring/wayfarer-spatial.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(target))
print("Saved fountain pedestrians:", ", ".join(item[0] for item in walkers), "to", target)
