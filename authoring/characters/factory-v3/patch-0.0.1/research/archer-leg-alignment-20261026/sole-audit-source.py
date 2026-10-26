import bpy,json,sys
from pathlib import Path
from mathutils import Matrix
base=Path("/workspace/Astraeon-online/authoring/characters/factory-v3/patch-0.0.1")
c=json.loads((base/"research/canonical-archer-nw-controls-20261026/pose-controls.json").read_text());bpy.ops.wm.open_mainfile(filepath=str(base/"rig-kits/sampled-native-action-library-v2-20261026/sampled-native-actions.blend"));rig=bpy.data.objects["ARM_FantasyCharacter01"];rig.animation_data_clear();body=bpy.data.objects["F01_BodyOutfit"];groups={side:{body.vertex_groups[n+"."+side].index for n in ["Foot","Toe"]}for side in ["L","R"]};rows=[]
for row in c["views"]["NW"]["frames"]:
 for bone in sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive)):
  if bone.name in row["world_matrices"]:bone.matrix=rig.matrix_world.inverted()@Matrix(row["world_matrices"][bone.name]);bpy.context.view_layer.update()
 graph=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(graph);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=graph);soles={}
 for side,ids in groups.items():
  vs=[ev.matrix_world@v.co for v in mesh.vertices if sum(g.weight for g in v.groups if g.group in ids)>.5];soles[side]=min(v.z for v in vs)
 ev.to_mesh_clear();rows.append({"index":row["index"],"sole_minimum_z_m":soles})
(base/"research/archer-leg-alignment-20261026/per-foot-sole-audit.json").write_text(json.dumps({"status":"MEASURED_WEIGHTED_FOOT_GEOMETRY_NOT_NATURALNESS_APPROVAL","frames":rows},indent=2));print("SOLE_AUDIT",json.dumps(rows))
