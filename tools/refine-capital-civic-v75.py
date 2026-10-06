"""Ground civic arcades, support roof lanterns and enlarge the inherited gates."""
import bpy,json,math,runpy
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_version')==75
p=json.loads((ROOT/'docs/review/wayfarer-capital-v75/plan.json').read_text());FacadeKit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
def kit(c,r):
 k=FacadeKit(c,r);k.prefix='capital-v75-';return k
def members(o,fragment):
 groups={g.index for g in o.vertex_groups if fragment in g.name}
 return {v.index for v in o.data.vertices if any(g.group in groups for g in v.groups)}
if not s.get('capital_civic_foundations'):
 # Leave a complete public cross avenue before the Exchange's colonnade.
 c=bpy.data.collections['capital-trade-exchange'];r=next(o for o in c.objects if o.type=='EMPTY' and not o.parent);dy=126-r.location.y;r.location.y=126
 for o in bpy.data.collections['court-terrain'].objects:
  if o.name.startswith('capital-trade-exchange-entry-tread-'):o.matrix_world=Matrix.Translation(Vector((0,dy,0)))@o.matrix_world
 for spec in p['landmarks']:
  c=bpy.data.collections[spec['id']];r=next(o for o in c.objects if o.type=='EMPTY' and not o.parent);k=kit(c,r);w,d,h=spec['width'],spec['depth'],spec['height'];exchange='exchange' in c.name
  for side in (-1,1):
   xx=side*((4.2 if exchange else 4.7)/2+.13);o=k.box(c.name+'-portal-pedestal-'+str(side),(xx,d/2+.22,.325),(.44,.86,.65),'civicShadow');o['role']='solid'
  if exchange:
   for j,x in enumerate((-10,-5,5,10)):
    for side in (-1,1):
     o=k.box(c.name+f'-arcade-pedestal-{j}-{side}',(x+side*2.03,d/2+1,.325),(.44,.86,.65),'civicShadow');o['role']='solid'
  if 'archive' in c.name:
   for o in c.objects:
    if o.type!='MESH':continue
    indices=members(o,'-archive-turret-');drums=members(o,'-archive-turret-') if o.data.materials[0].name=='civicIvory' else set()
    for i in indices:
     if not drums or o.data.vertices[i].co.z>17.19:o.data.vertices[i].co.z+=2.8
    o.data.update()
    if drums:
     for face in o.data.polygons:
      if not all(i in drums for i in face.vertices):continue
      for li in face.loop_indices:
       q=o.data.vertices[o.data.loops[li].vertex_index].co;n=face.normal;o.data.uv_layers.active.data[li].uv=(q.x/2.4,q.y/2.4) if abs(n.z)>.65 else (q.y/2.4,q.z/2.4) if abs(n.x)>abs(n.y) else (q.x/2.4,q.z/2.4)
  if 'council' in c.name:
   for o in c.objects:
    if o.type!='MESH':continue
    for i in members(o,'-council-lantern-')|members(o,'-lantern-rib-'):o.data.vertices[i].co.z+=1.35
   # A pierced octagonal drum physically joins the roof to its crowned lantern.
   radius=2;rp=spec['roofPeak'];upper=rp+.02;top=rp+1.20
   for i in range(8):
    a,b=(i+.5)*math.tau/8,(i+1.5)*math.tau/8;aa=(radius*math.cos(a),-2+radius*math.sin(a));bb=(radius*math.cos(b),-2+radius*math.sin(b));za=rp-abs(aa[0])/(w*.19)*(rp-h-.3)-.10;zb=rp-abs(bb[0])/(w*.19)*(rp-h-.3)-.10
    k.mesh(c.name+'-lantern-drum-base-'+str(i),[(*aa,za),(*bb,zb),(*bb,upper),(*aa,upper)],[[0,1,2,3]],'civicIvory')
    mid=((aa[0]+bb[0])/2,(aa[1]+bb[1])/2);angle=math.atan2(bb[1]-aa[1],bb[0]-aa[0])+math.pi
    k.upper_face(c.name+'-lantern-drum-window-'+str(i),math.dist(aa,bb),upper,top,[0],'civicIvory',mid,angle,wh=.70,ww=.68)
   for o in c.objects:
    if o.type!='MESH':continue
    mat=o.data.materials[0].name
    if mat=='timber':o.data.materials[0]=bpy.data.materials['civicShadow']
    elif mat=='stoneLight':o.data.materials[0]=bpy.data.materials['civicIvory']
    elif mat=='frontageGlazing':o.data.materials[0]=bpy.data.materials['civicGlass']
  c['capital_landmark_json']=json.dumps(spec)
 s['capital_civic_foundations']=75
# Original portal, service and arrival anchors remain in their collections.
# Old gate meshes are preserved as native references, outside gameplay export.
if not s.get('capital_transition_gates'):
 for owner,name,center,angle,width in [('caravan-gate','capital-west-gate',[18,144],math.pi/2,12),('north-gate','capital-north-gate',[128,20],0,9)]:
  c=bpy.data.collections[owner]
  for o in list(c.objects):
   if o.type=='MESH':o['export_reference_only']=True;o.hide_render=True
  r=bpy.data.objects.new(name+'-structure-placement',None);c.objects.link(r);r.location=(*center,0);r.rotation_euler.z=angle;k=kit(c,r)
  for side in (-1,1):
   x=side*(width/2+1.4);o=k.box(name+'-tower-'+str(side),(x,0,3.4),(2.8,3.5,6.8),'civicIvory');o['role']='solid'
   for zz in (.35,2.4,5.0,6.9):k.box(name+'-belt-'+str((side,zz)),(x,0,zz),(3.12,3.8,.25),'wallCap')
   for yy in (-1.9,1.9):k.box(name+'-lancet-'+str((side,yy)),(x,yy,4.65),(.48,.08,1.38),'civicShadow',False)
   o=k.mesh(name+'-crown-'+str(side),[(x-1.7,-2,7.15),(x+1.7,-2,7.15),(x+1.7,2,7.15),(x-1.7,2,7.15),(x,-2,9.45),(x,2,9.45)],[[0,3,5,4],[1,4,5,2],[0,4,1],[3,2,5]],'civicSlate');o['role']='overhead'
   k.box(name+'-banner-'+str(side),(x,1.82,2.0),(.85,.04,2.4),'clothBlue',False);k.beam(name+'-banner-pole-'+str(side),(x-.60,1.93,3.28),(x+.60,1.93,3.28),.075,'gold')
   k.beam(name+'-banner-star-a-'+str(side),(x-.25,1.89,2.08),(x+.25,1.89,2.08),.04,'gold');k.beam(name+'-banner-star-b-'+str(side),(x,1.89,1.7),(x,1.89,2.5),.04,'gold')
  for j in range(12):
   aa,bb=j*math.pi/12,(j+1)*math.pi/12;poly=[(-math.cos(q)*rad,3.65+math.sin(q)*rad*.28) for q,rad in [(aa,width/2),(bb,width/2),(bb,width/2+.36),(aa,width/2+.36)]];vs=[(xx,yy,zz) for yy in (-.7,.7) for xx,zz in poly]
   k.mesh(name+'-arch-'+str(j),vs,[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],'civicIvory')
  o=k.box(name+'-lintel',(0,0,5.4),(width+2.8,1.5,.55),'wallCap');o['role']='overhead'
 s['capital_transition_gates']=75
# Update hidden street metadata to the physically clear northern circuit.
for road in p['roads']:
 if road['id'] not in ('capital-circuit','north-civic-road'):continue
 for j,(a,b) in enumerate(zip(road['centerline'],road['centerline'][1:])):
  o=bpy.data.objects[road['id']+'-'+str(j)];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*road['width']/2,dx/length*road['width']/2;coords=[(a[0]+nx,a[1]+ny,.025),(b[0]+nx,b[1]+ny,.025),(b[0]-nx,b[1]-ny,.025),(a[0]-nx,a[1]-ny,.025)]
  for v,q in zip(o.data.vertices,coords):v.co=q
  o['centerline_json']=json.dumps([a,b]);o['road_width']=road['width']
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('Grounded civic profiles and royal transition gates saved',flush=True)
