"""Import the CURRENT town into Blender, not the future concept layout.
Existing coordinates, art and occupancy are preserved for a bounded migration.
Run: blender -b --python tools/build-court-blender.py
"""
import bpy,json,subprocess,math,runpy
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./world-view.js');require('./world-content.js');require('./town-structure.js');console.log(JSON.stringify({content:window.AstraeonContent,metadata:window.AstraeonTownStructure.metadata}))"],cwd=ROOT));C=source['content']
helpers=runpy.run_path(str(ROOT/'tools/blender-v3-kit.py'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
family=helpers['family'];box=helpers['box'];mesh=helpers['mesh'];empty=helpers['empty'];scene=bpy.context.scene
terrain=family('court-terrain','terrain');box(terrain,'court-ground',(22,20,-.08),(44,40,.16),'grass','decorative',False)
for index,road in enumerate(C['townRoads']):
 for j in range(1,len(road['points'])):
  a,b=road['points'][j-1],road['points'][j];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*road['width']/2,dx/length*road['width']/2
  points=[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]]
  o=mesh(terrain,'road-'+str(index)+'-'+str(j),[(x,y,.01) for x,y in points],[list(range(4))],'paving','decorative',False);o['surface_role']={'avenue':'primary','street':'residential'}.get(road['role'],road['role']);o['legacy_role']=road['role'];o['road_segment']=True
plaza=mesh(terrain,'court-plaza',[(x,y,.01) for x,y in C['goldenScene']['plaza']],[list(range(6))],'paving','decorative',False);plaza['surface_role']='plaza'
for court in C['forecourts']:
 o=mesh(terrain,'approach-'+court['id'],[(x,y,.01) for x,y in court['points']],[list(range(len(court['points'])))],'paving','decorative',False);o['surface_role']='forecourt';o['object_id']=court['id']
blocks={b['id']:b for b in C['townBlocks']}
for record in C['townObjects']:
 id=record['id'];art=record['art'];role='vegetation' if record.get('tree') else {'guild':'civic','gate':'fortification','shrine':'shrine','forge':'workshop','inn':'inn','shop':'market','stall':'market'}.get(art,'residential')
 collection=family(id,role);root=empty(collection,id+'-placement',(record['x'],record['y'],0),'presentation');root['data_json']=json.dumps({k:v for k,v in record.items() if k not in ['id','x','y']});root.empty_display_type='ARROWS'
 block=blocks.get(id)
 if block:
  height=3 if record.get('building') else .65;o=box(collection,id+'-volume',(block['x']+block['w']/2-record['x'],block['y']+block['h']/2-record['y'],height/2),(block['w'],block['h'],height),'stone');o.parent=root
  root['footprint_review']='inherited occupancy; visual registration review pending'
 else:
  o=box(collection,id+'-marker',(0,0,.01),(.08,.08,.02),'stone','decorative',False);o.parent=root;root['footprint_review']='visual-only; no new collision inferred'
bpy.context.view_layer.update()
for surface in terrain.objects:
 if surface.get('object_id'):
  root=bpy.data.objects[surface['object_id']+'-placement'];surface.parent=root;surface.matrix_parent_inverse=root.matrix_world.inverted()
scene['world_id']='wayfarer-court';scene['world_contract_version']=3;scene['purpose']='Placement-preserving current court import; Golden review pending'
scene['navigation_radius']=.18;scene['navigation_cell_size']=.5;scene['sun_cast_x']=.65;scene['sun_cast_y']=.38;scene['sun_strength']=.24;scene['ambient']=.8
scene['spawn_json']=json.dumps([14.5,18,0]);scene['route_json']=json.dumps([{'name':'Court','position':[14.5,18]},{'name':'Hall approach','position':[8.9,16.3]},{'name':'Market','position':[23.5,17.4]},{'name':'Gate','position':[40.7,16]}])
direction=Vector((48,-32,0)).cross(Vector((14,22,-35))).normalized()
bpy.ops.object.camera_add(location=Vector((22,20,0))+direction*70);camera=bpy.context.object;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=42;scene.camera=camera;camera.name='CourtReviewCamera'
scene.render.resolution_x=1280;scene.render.resolution_y=800;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-court.blend'))
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
