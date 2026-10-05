"""House-owned stone plinth courses, private aprons and low walkable brick rims."""
import bpy,json,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_grass_life_version')==69
assert not scene.get('ro3_house_apron_version')
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain')
def floor_tree():
 vs=[];fs=[]
 for o in terrain.objects:
  if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
  off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
 return BVHTree.FromPolygons(vs,fs,all_triangles=True)
floor=floor_tree();base_height=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())['terrain']['elevation']
def height(x,y,tree=None):
 hit=(tree or floor).ray_cast(Vector((x,y,100)),Vector((0,0,-1)),150)[0]
 return hit.z if hit else base_height

def hull(pts):
 p=sorted(set((round(v.x,5),round(v.y,5)) for v in pts))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 def chain(seq):
  out=[]
  for v in seq:
   while len(out)>1 and cross(out[-2],out[-1],v)<=0:out.pop()
   out.append(v)
  return out
 return chain(p)[:-1]+chain(reversed(p))[:-1]

private=bpy.data.materials.new('houseApronPaving');private.diffuse_color=(.51,.465,.365,1);private['texture_json']=bpy.data.materials['paving']['texture_json']
owners={};records=[]
for c in sorted(bpy.data.collections,key=lambda c:c.name):
 core=next((o for o in c.objects if o.type=='MESH' and (o.name.endswith('-ground-core') or o.name.startswith('side-v59-') and o.name.endswith('-lower-walls'))),None)
 if not core:continue
 root=core.parent;inv=root.matrix_world.inverted();kit=Kit(c,root);kit.prefix='lot69-'+c.name[:20]+'-';poly=hull([inv@core.matrix_world@v.co for v in core.data.vertices]);owners[c.name]=(c,root,kit)
 count=0
 for edge,(aa,bb) in enumerate(zip(poly,poly[1:]+poly[:1])):
  a,b=Vector((*aa,0)),Vector((*bb,0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));length=(b-a).length;steps=max(1,math.ceil(length/.75))
  p=root.matrix_world@((a+b)/2+n*.06);gz=height(p.x,p.y);assert gz is not None
  local_z=(inv@Vector((p.x,p.y,gz))).z
  # Two staggered, lightly bevelled courses. Keep their outer relief within
  # the existing body clearance of the solid house core.
  for row in range(2):
   stride=length/steps;cuts=sorted({0,length,*[max(0,min(length,j*stride+(stride*.5 if row else 0))) for j in range(steps+1)]})
   for j,(l,r) in enumerate(zip(cuts,cuts[1:])):
    if r-l<.10:continue
    z0=local_z+.07+row*.17;z1=z0+.145;front=.16 if row==0 else .12;back=-.08;bevel=.018
    profile=[(back,z0),(front-bevel,z0),(front,z0+bevel),(front,z1-bevel),(front-bevel,z1),(back,z1)]
    pts=[tuple(a+t*s+n*d+Vector((0,0,z))) for s in (l+.007,r-.007) for d,z in profile]
    kit.mesh(f'plinth-{edge}-{row}-{j}',pts,[list(range(5,-1,-1)),list(range(6,12))]+[[k,(k+1)%6,(k+1)%6+6,k+6] for k in range(6)],'stoneLight' if row else 'stone');count+=1
  # Narrow cap finishes the wall/platform datum instead of a raw box at floor.
  pts=[tuple(a+t*s+n*d+Vector((0,0,local_z+z))) for s in (0,length) for d,z in [(-.08,.385),(.12,.385),(.15,.405),(.12,.425),(-.08,.425)]]
  kit.mesh('plinth-cap-'+str(edge),pts,[list(range(4,-1,-1)),list(range(5,10))]+[[k,(k+1)%5,(k+1)%5+5,k+5] for k in range(5)],'stoneLight')
 records.append({'owner':c.name,'plinthCourses':2,'plinthBlocks':count})

def surface(name,polygon,z,owner,root,material):
 inv=root.matrix_world.inverted();kit=Kit(terrain,root);kit.prefix='lot69-'
 pts=[tuple(inv@Vector((x,y,z))) for x,y in polygon]
 # Plan polygons run clockwise; flip their triangles toward the daylight.
 ob=kit.mesh(name,pts,[[0,j+1,j] for j in range(1,len(pts)-1)],material,False)
 del ob['role'];ob['surface_role']='forecourt';ob['walkable']=True;ob['object_id']=owner
 for f in ob.data.polygons:
  for li in f.loop_indices:
   p=root.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co
   ob.data.uv_layers.active.data[li].uv=(p.x/8,p.y/8) if material=='houseApronPaving' else (p.x/4,p.y/4)
 return ob

plan=json.loads((ROOT/'authoring/ro3-house-aprons-v69.json').read_text());accepted=[];skipped=[]
for index,p in enumerate(plan['segments']):
 c,root,kit=owners[p['owner']];q=p['polygon'];heights=[height(*v) for v in q]
 if any(z is None for z in heights) or max(heights)-min(heights)>.025:skipped.append({'owner':p['owner'],'edge':p['edge'],'segment':p['segment'],'reason':'existing step or slope'});continue
 ground=max(heights);pad=surface('apron-'+str(index),q,ground+.055,c.name,root,'houseApronPaving')
 # Leave the visible entry lane through the rim; greenery also avoids doors.
 doors=[o for o in c.objects if o.type=='MESH' and o.name.startswith('ro3-v68-') and o.name.endswith('-door-leaf')]
 a,b=Vector((*q[3],0)),Vector((*q[2],0));t=(b-a).normalized();n=Vector((*p['normal'],0));length=(b-a).length
 gap=False
 for door in doors:
  dc=sum((door.matrix_world@v.co for v in door.data.vertices),Vector())/len(door.data.vertices)
  u=(dc-a).dot(t)
  if abs((dc-a).dot(n))<p['depth']+.25 and -.85<u<length+.85:gap=True
 curb=None
 if not gap:
  # This top face is the physical .10-high floor. Its bevel/fascia is owned
  # geometry, so boots step onto the same edge that the user sees.
  cp=[tuple((a+t*s+n*d)[:2]) for s,d in [(0,-.065),(length,-.065),(length,.025),(0,.025)]]
  curb=surface('rim-top-'+str(index),cp,ground+.105,c.name,root,'stoneLight')
  inv=root.matrix_world.inverted();points=[tuple(inv@(a+t*s+n*d+Vector((0,0,ground+z)))) for s in (0,length) for d,z in [(-.065,.055),(.025,.055),(.043,.078),(.025,.105),(-.065,.105)]]
  ob=kit.mesh('rim-fascia-'+str(index),points,[list(range(4,-1,-1)),list(range(5,10))]+[[k,(k+1)%5,(k+1)%5+5,k+5] for k in range(5)],'stoneLight')
  c.objects.unlink(ob);terrain.objects.link(ob);del ob['role'];ob['surface_role']='forecourt';ob['walkable']=True;ob['object_id']=c.name
  bpy.data.objects.remove(curb,do_unlink=True);curb=ob
 accepted.append({**p,'ground':ground,'surface':pad.name,'rimTop':curb.name if curb else None,'entranceGap':gap})
assert len(owners)==37
assert len({p['owner'] for p in accepted})==37
# Refit each complete goods station to its new authored lot floor.
bpy.context.view_layer.update()
new_floor=floor_tree();base_height=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())['terrain']['elevation'];life=json.loads(scene['ro3_house_life_review_json'])
for record in life['groundStations']:
 x,y=record['center'];new_ground=height(x,y,new_floor);dz=new_ground-record['ground']
 collider=bpy.data.objects[record['collider']];station=collider['house_life_v69_station']
 for o in bpy.data.collections[record['owner']].objects:
  if o.type=='MESH' and o.get('house_life_v69_station')==station:
   inv=o.matrix_world.inverted();delta=inv.to_3x3()@Vector((0,0,dz))
   for v in o.data.vertices:v.co+=delta
   o['house_life_v69_ground']=new_ground
 record['ground']=new_ground
scene['ro3_house_life_review_json']=json.dumps(life)
scene['ro3_house_apron_version']=69;scene['ro3_house_apron_review_json']=json.dumps({'buildings':records,'aprons':accepted,'skipped':skipped,'padRise':.055,'rimRise':.105,'protected':plan['protected']})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('House-owned space:',len(records),'bevelled plinths;',len(accepted),'private apron segments;',sum(bool(p['rimTop']) for p in accepted),'walkable rims; refitted 27 goods stations; rebake lights')
