"""Blender authoring + export. Run: blender -b --python tools/build-proof-blender.py
All runtime polygons are exported from world-space mesh vertices. Portal anchors
are Blender empties parented to their object; no hand-maintained collision file.
"""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
import runpy
helpers=runpy.run_path(str(ROOT/'tools/blender-v3-kit.py'));family=helpers['family'];box=helpers['box'];mesh=helpers['mesh'];empty=helpers['empty']
terrain=family('terrain','terrain')
box(terrain,'ground',(7,7,-.08),(14,14,.16),'grass','decorative',False)
# Roads are authored first. Deliberate arrival avenue and building forecourt.
roads=[{'id':'arrival-avenue','role':'primary','polygon':[[2.9,13.7],[5.1,13.7],[5.1,6],[2.9,6]]},
       {'id':'forecourt','role':'forecourt','polygon':[[3,6],[11.7,6],[11.7,8],[3,8]]},
       {'id':'rear-service','role':'service','polygon':[[11.3,2],[13,2],[13,8],[11.3,8]]}]
for r in roads:
 o=mesh(terrain,r['id'],[(x,y,.01) for x,y in r['polygon']],[[0,1,2,3]],'paving','decorative',False);o['surface_role']=r['role']
gate=family('west-gate','fortification')
for x,s in [(2.6,'west'),(5.4,'east')]:
 box(gate,s+'-pillar',(x,10,1.5),(.9,1.1,3),'stone')
 box(gate,s+'-cap',(x,10,3.12),(1.12,1.28,.24),'stoneLight','overhead')
 box(gate,s+'-banner',(x,10.57,1.9),(.42,.045,1.1),'blue','decorative',False)
 box(gate,s+'-gold',(x,10.60,1.9),(.04,.04,.9),'gold','decorative',False)
box(gate,'open-span',(4,10,2.86),(1.95,1.02,.32),'stoneLight','overhead')
empty(gate,'gate-passage',(4,10,0),'portal');empty(gate,'gate-approach',(4,11.1,0),'approach')
building=family('civic-proof','civic')
box(building,'foundation',(9,4,.12),(4.3,3.3,.24),'stoneLight')
box(building,'hall-body',(9,4,1.32),(4,3,2.4),'stone')
for x in [7.3,10.7]:
 box(building,'pilaster-'+str(x),(x,5.54,1.38),(.23,.22,2.5),'stoneLight')
box(building,'door',(9,5.51,.86),(.95,.03,1.5),'wood','decorative',False)
for x in [8,10]:
 box(building,'window-'+str(x),(x,5.53,1.64),(.46,.05,.7),'blue','decorative',False)
 box(building,'window-trim-'+str(x),(x,5.57,1.29),(.56,.08,.09),'gold','decorative',False)
mesh(building,'hall-roof',[(6.65,2.1,2.54),(11.35,2.1,2.54),(6.65,5.9,2.54),(11.35,5.9,2.54),(6.65,4,3.95),(11.35,4,3.95)],[[0,1,5,4],[2,4,5,3],[0,4,2],[1,3,5]],'blue','overhead')
box(building,'entrance-awning',(9,5.9,2.2),(1.3,1,.16),'blue','overhead')
empty(building,'hall-entrance',(9,5.68,0),'portal');empty(building,'hall-approach',(9,6.65,0),'approach')
lamp=empty(building,'entry-lamp',(9.75,5.62,1.7),'light');lamp['radius']=1.9;lamp['color']='#ffc77b'
box(building,'lamp-source',(9.75,5.65,1.7),(.12,.10,.2),'gold','decorative',False)
tree=family('garden-tree','vegetation')
box(tree,'trunk',(9.5,9.6,1),(.40,.40,2),'wood')
# Low-poly canopy, a distinct visibility layer with persistent cast shadow.
verts=[]
for z,r in [(1.8,1.05),(2.5,1.65),(3.35,1.1),(3.8,.1)]:
 for i in range(10):a=i*math.tau/10;verts.append((9.5+math.cos(a)*r,9.6+math.sin(a)*r,z))
faces=[]
for row in range(3):
 for i in range(10):faces.append([row*10+i,row*10+(i+1)%10,(row+1)*10+(i+1)%10,(row+1)*10+i])
faces+=[list(range(9,-1,-1)),list(range(30,40))]
mesh(tree,'canopy',verts,faces,'leaf','overhead')
# Authoring camera matches the runtime ground basis; z scale 35 px/unit.
basis_x=Vector((48,-32,0));basis_y=Vector((14,22,-35));direction=basis_x.cross(basis_y).normalized()
bpy.ops.object.camera_add(location=Vector((7,7,0))+direction*30);camera=bpy.context.object;camera.name='GameplayCamera';camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=19;scene.camera=camera
bpy.ops.object.light_add(type='SUN',location=(4,1,15));bpy.context.object.rotation_euler=(.5,-.3,-.6);bpy.context.object.data.energy=3
scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene['world_contract_version']=3;scene['purpose']='Golden proof: not approved full Wayfarer'
scene['world_id']='golden-proof';scene['navigation_radius']=.18;scene['navigation_cell_size']=.5;scene['sun_cast_x']=.65;scene['sun_cast_y']=.38;scene['sun_strength']=.24;scene['ambient']=.8
scene['spawn_json']=json.dumps([4,12.2,0]);scene['route_json']=json.dumps([{'name':'Outside gate','position':[4,12.2]},{'name':'Through passage','position':[4,8]},{'name':'Hall approach','position':[9,6.65]},{'name':'Rear service','position':[12.1,2.6]},{'name':'Canopy approach','position':[9.5,8.5]}])
bpy.data.objects['gate-passage']['approach_id']='gate-approach';bpy.data.objects['hall-entrance']['approach_id']='hall-approach'
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/golden-proof.blend'))
import runpy
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
