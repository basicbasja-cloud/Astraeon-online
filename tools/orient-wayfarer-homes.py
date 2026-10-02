"""Rotate existing saved homes around their massing centres toward local lanes.
Preserves meshes, artwork, IDs, roofs, child details, services and the town plan.
Creates short authored thresholds from the resulting entries to existing streets.
No town regeneration or manually maintained runtime placements.
"""
import bpy,json,math,runpy,subprocess
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
assert bpy.context.scene['world_id']=='wayfarer-spatial'
export=runpy.run_path(str(ROOT/'tools/export-world-v3.py'))['export']
changes={'residence':90,'willow-house':-90,'north-house':-18,'west-house':90,'north-garden-house':-90,'northwest-cottage':-30}
entries=[]
for id,degrees in changes.items():
 root=bpy.data.objects[id+'-placement'];body=bpy.data.objects[id+'-walls']
 centre=sum((v.co for v in body.data.vertices),Vector())/len(body.data.vertices)
 if not root.get('street_orientation_applied'):
  before=body.matrix_world@centre;root.rotation_euler.z+=math.radians(degrees);bpy.context.view_layer.update();root.location+=before-body.matrix_world@centre;bpy.context.view_layer.update()
  root['street_orientation_applied']=degrees
 door=bpy.data.objects[id+'-door'];point=door.matrix_world@(sum((v.co for v in door.data.vertices),Vector())/len(door.data.vertices));centre=body.matrix_world@centre
 direction=Vector((point.x-centre.x,point.y-centre.y,0)).normalized()
 entries.append({'id':id,'door':list(point),'direction':list(direction)})
source=export(bpy.context.scene)
# Navigation is queried against the very same edited Blender export. It guides
# authoring only: the final browser receives these saved meshes, not runtime paths.
query=r"""
global.window={};require('./world-view.js');require('./navigation.js');require('./world/v3/spatial.js');
let input='';process.stdin.on('data',s=>input+=s);process.stdin.on('end',()=>{const {source,entries}=JSON.parse(input),w=window.AstraeonSpatialV3.compile(source);
const roads=source.terrain.surfaces.filter(s=>s.centerline&&['primary','residential','service'].includes(s.role));
const result=entries.map(e=>{let start;for(const d of [.65,.85,1.05,1.25]){const p={x:e.door[0]+e.direction[0]*d,y:e.door[1]+e.direction[1]*d};if(!w.blocked(p.x,p.y)){start=p;break}}if(!start)throw Error('Entry blocked '+e.id);
const candidates=roads.map(s=>{const [a,b]=s.centerline,dx=b[0]-a[0],dy=b[1]-a[1],t=Math.max(0,Math.min(1,((start.x-a[0])*dx+(start.y-a[1])*dy)/(dx*dx+dy*dy)));return{road:s.id,point:{x:a[0]+t*dx,y:a[1]+t*dy}}}).filter(p=>!w.blocked(p.point.x,p.point.y)).sort((a,b)=>Math.hypot(a.point.x-start.x,a.point.y-start.y)-Math.hypot(b.point.x-start.x,b.point.y-start.y));
for(const c of candidates){const route=w.route(start,c.point);if(route)return{id:e.id,start,road:c.road,route}}throw Error('No street route '+e.id)});console.log(JSON.stringify(result));});
"""
result=subprocess.run(['node','-e',query],input=json.dumps({'source':source,'entries':entries}),cwd=ROOT,text=True,capture_output=True,check=True)
terrain=bpy.data.collections['court-terrain'];paths=json.loads(result.stdout)
for entry in paths:
 root=bpy.data.objects[entry['id']+'-placement'];inverse=root.matrix_world.inverted();points=[entry['start']]+entry['route']
 for i,(a,b) in enumerate(zip(points,points[1:])):
  delta=Vector((b['x']-a['x'],b['y']-a['y'],0))
  if delta.length<.08:continue
  n=Vector((-delta.y,delta.x,0)).normalized()*.48
  world=[Vector((a['x'],a['y'],.027))+n,Vector((b['x'],b['y'],.027))+n,Vector((b['x'],b['y'],.027))-n,Vector((a['x'],a['y'],.027))-n]
  name=entry['id']+f'-street-threshold-{i}'
  if bpy.data.objects.get(name):continue
  data=bpy.data.meshes.new(name);data.from_pydata([tuple(inverse@p) for p in world],[],[[0,3,2,1]]);data.materials.append(bpy.data.materials['paving']);data.uv_layers.new(name='Wayfarer-painterly')
  for loop in data.polygons[0].loop_indices:
   p=world[data.loops[loop].vertex_index];data.uv_layers.active.data[loop].uv=(p.x/4,p.y/4)
  obj=bpy.data.objects.new(name,data);terrain.objects.link(obj);obj.parent=root;obj['surface_role']='residential';obj['walkable']=True;obj['object_id']=entry['id'];obj['street_id']=entry['road']
  print('Authored',name,'to',entry['road'])
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Oriented',len(changes),'existing homes to their street/courtyard approaches')
