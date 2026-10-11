"""Render actual fitted right-hand/weapon contact from the critical headings."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
base=Path(__file__).resolve().parents[1];out=base/'authoring/characters/swordsman-production/fantasy-base-01/renders'
s=bpy.context.scene;rig=bpy.data.objects['ARM_FantasyCharacter01'];root=bpy.data.objects['ROOT_FantasyCharacter01']
contact=json.loads(s['swordContact']);p=rig.pose.bones['Hand.R'];local=Vector(contact['centerModel'])
s.render.resolution_x=768;s.render.resolution_y=768;s.camera.data.ortho_scale=.20
for d,yaw in [('SE',45),('W',-90),('NW',-135),('N',-180)]:
    root.rotation_euler.z=math.radians(yaw);bpy.context.view_layer.update()
    center=rig.matrix_world@(p.matrix@p.bone.matrix_local.inverted()@local)
    s.camera.rotation_euler=(math.radians(65),0,0)
    s.camera.location=center-(s.camera.rotation_euler.to_matrix()@Vector((0,0,-1)))*5
    s.render.filepath=str(out/(d+'-grip.png'));bpy.ops.render.render(write_still=True)
print('FANTASY_GRIP_CHECK_COMPLETE',flush=True)
