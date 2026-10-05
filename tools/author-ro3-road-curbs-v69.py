"""Native stone curb courses bound the union of through streets and building zones."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert not scene.get('ro3_road_curb_version')
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));w=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text());art=json.loads((ROOT/'authoring/materials/wayfarer-road-zone-v69.json').read_text())['materials']
for name,asset,color in [('roadCurbStone','wayfarer-curb-stone-v69',(.57,.535,.43,1)),('treeBark','wayfarer-tree-bark-v69',(.285,.17,.085,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=color;m['texture_json']=json.dumps(art[asset]['texture'])
bpy.data.materials['avenuePaving']['texture_json']=json.dumps(art['wayfarer-cobbles-v69']['texture']);bpy.data.materials['avenuePaving'].diffuse_color=(.405,.395,.325,1)
for name in ['paving','cityPaving','houseApronPaving','vergeGroundcover','vergeGroundcoverShade']:
 m=bpy.data.materials[name];s=json.loads(m['texture_json']);s['anisotropy']=4;m['texture_json']=json.dumps(s)
tree_parts=0
for c in bpy.data.collections:
 if c.get('family')=='vegetation':
  for o in c.objects:
   if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='timber':o.data.materials[0]=bpy.data.materials['treeBark'];tree_parts+=1
# Preserve the detailed existing foliage artwork while making its palette-relative
# leaf contrast and oblique sampling consistent with the new town materials.
m=bpy.data.materials['foliageCutout'];s=json.loads(m['texture_json']);im=np.asarray(Image.open(ROOT/s['file']).convert('RGBA'),dtype=float)/255;a=im[:,:,:3];linear=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);s.update(meanLinearRGB=np.average(linear.reshape(-1,3),axis=0,weights=im[:,:,3].reshape(-1)+1e-6).round(7).tolist(),paletteDetail=.84,anisotropy=4);m['texture_json']=json.dumps(s)
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];return hit.z if hit else None
roads=[s for s in w['terrain']['surfaces'] if s.get('centerline') and s.get('width',0)>=1.8 and s['material']=='avenuePaving' and s['role']=='primary' and max(v[2] for v in s['vertices'])<.2]
polys=[p['polygon'] for p in roads];solids=[h['hull'](p['vertices']) for o in w['objects'] for p in o['parts'] if p['role']=='solid'];services=[p['position'][:2] for o in w['objects'] for p in o.get('services',[])];doors=[p['anchor'][:2] for o in w['objects'] for p in o.get('portals',[])];kit=Kit(terrain,None);kit.prefix='roadrim69-';records=[];omissions=[]
for road in roads:
 poly=road['polygon'];area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]));sign=1 if area>0 else -1
 # Longitudinal edges only: crossings/open court ends stay open.
 for edge in [0,2]:
  a,b=Vector((*poly[edge],0)),Vector((*poly[(edge+1)%4],0));t=(b-a).normalized();n=Vector((t.y*sign,-t.x*sign,0));length=(b-a).length;steps=max(1,math.ceil(length/.7))
  for j in range(steps):
   l,r=length*j/steps,length*(j+1)/steps;mid=a+t*((l+r)/2)+n*.04
   if any(other is not poly and h['inside'](mid.xy,other) for other in polys):continue
   q=[tuple((a+t*u+n*d)[:2]) for u,d in [(l,.025),(r,.025),(r,.325),(l,.325)]]
   if any(not h['inside'](p,w['terrain']['walkablePolygon']) for p in q):continue
   if any(h['overlap'](q,p,.06) for p in solids):continue
   if any(h['inside'](p,q) or min(h['distance'](p,a,b) for a,b in zip(q,q[1:]+q[:1]))<.70 for p in services+doors):continue
   heights=[ground(Vector((*p,0))) for p in q]
   if any(z is None for z in heights) or max(heights)-min(heights)>.035:omissions.append({'road':road['id'],'segment':j,'reason':'step or slope'});continue
   z=max(heights);profile=[(.025,.012),(.325,.012),(.325,.095),(.300,.12),(.050,.12),(.025,.095)]
   points=[tuple(a+t*u+n*d+Vector((0,0,z+zz))) for u in (l+.006,r-.006) for d,zz in profile];ob=kit.mesh('stone-'+str(len(records)),points,[list(range(5,-1,-1)),list(range(6,12))]+[[k,(k+1)%6,(k+1)%6+6,k+6] for k in range(6)],'roadCurbStone',False)
   del ob['role'];ob['surface_role']='forecourt';ob['walkable']=True;ob['road_curb_v69']=True
   records.append({'id':ob.name,'road':road['id'],'ground':z,'rise':.12,'width':.30})
scene['ro3_road_curb_version']=69;scene['ro3_road_curb_review_json']=json.dumps({'curbBlocks':records,'omissions':omissions,'nativeWalkable':True,'treeBarkParts':tree_parts,'protected':'through-road union, open cross streets, services, portals, existing steps/solids','materials':art})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('Street separation:',len(records),'walkable bevelled curb blocks;',tree_parts,'native bark parts')
