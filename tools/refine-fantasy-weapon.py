"""Repair the fitted guard as a closed, hooked bronze source surface.

Runs after fitting/motion authoring. The holding hand, hilt, blade attachment,
poses and camera stay identical. Never draw a corrective overlay onto sprites.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
base=Path(__file__).resolve().parents[1];s=bpy.context.scene
rig=bpy.data.objects[s['rigObject']];root=bpy.data.objects[s['rootObject']]
center=Vector(json.loads(s['swordContact'])['centerModel']);guard=center+Vector((0,-.05,0))
obj=bpy.data.objects['F01_SwordGuard'];material=obj.data.materials[0]
# A non-self-intersecting quillon profile, hooked toward the blade at both ends.
profile=[(-.042,-.013),(-.029,-.010),(-.020,-.002),(-.008,-.004),(.008,-.004),(.020,-.002),(.029,-.010),(.042,-.013),
         (.038,.003),(.026,.008),(.014,.006),(.006,.005),(-.006,.005),(-.014,.006),(-.026,.008),(-.038,.003)]
verts=[tuple(guard+Vector((x,y,z))) for z in [-.005,.005] for x,y in profile];n=len(profile)
faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh=bpy.data.meshes.new('F01_HookedGuard');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(material)
obj.data=mesh;obj.vertex_groups.clear();g=obj.vertex_groups.new(name='Hand.R');g.add(list(range(2*n)),1,'REPLACE')
assert min(p.area for p in mesh.polygons)>1e-8,'Degenerate guard surface'
s['weaponRefinement']='Closed hooked guard; stable Hand.R attachment; no raster corrections.'
rig.animation_data.action=bpy.data.actions['F01_Idle'];s.frame_set(1);root.rotation_euler.z=math.radians(45)
s.render.resolution_x=320;s.render.resolution_y=320
bpy.ops.wm.save_as_mainfile(filepath=str(base/'.character-tools/checkpoints/fantasy-base-01-native.blend'))
for action,frame in [('Idle',1),('BasicAttack',9),('Death',12)]:
    rig.animation_data.action=bpy.data.actions['F01_'+action];s.frame_set(frame)
    for direction,yaw in [('SE',45),('W',-90),('NW',-135),('N',-180)]:
        root.rotation_euler.z=math.radians(yaw);s.render.resolution_x=640;s.render.resolution_y=640
        s.render.filepath=str(base/'authoring/characters/swordsman-production/fantasy-base-01/renders'/f'{action}-{direction}-{frame:02}.png')
        bpy.ops.render.render(write_still=True)
print('FANTASY_WEAPON_REPAIRED',flush=True)
