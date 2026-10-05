"""Original celestial fountain with RO3 tiered pools and planted public court.

Native physical basin, raised walkable steps, rooted beds and green seating.
Uses owned water artwork; reference imagery is never imported as material.
"""
import json,math,runpy
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
owner=bpy.data.collections['astral-fountain']
for o in list(owner.objects):
 if o.name.startswith('ro3-v68-fountain-'):bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.data.objects):
 if o.name.startswith('ro3-v68-fountain-step-'):bpy.data.objects.remove(o,do_unlink=True)
root=bpy.data.objects.new('ro3-v68-fountain-model-frame',None);owner.objects.link(root)
root.parent=bpy.data.objects['astral-fountain-placement'];root.matrix_world=Matrix.Translation(Vector((54,51,0)))
bpy.context.view_layer.update();kit=Kit(owner,root)
for o in owner.objects:
 if o.type!='MESH' or o.name.startswith('ro3-v68-'):continue
 if o.name.startswith('landmark-v49-') and any(t in o.name for t in ('robe','neck','head','arm','feather','halo')):
  if 'ro3_v68_original_vertices' not in o:o['ro3_v68_original_vertices']=json.dumps([list(v.co) for v in o.data.vertices])
  mat=o.matrix_world;inv=mat.inverted()
  for v,p in zip(o.data.vertices,json.loads(o['ro3_v68_original_vertices'])):
   world=mat@Vector(p);world.z-=.60;v.co=inv@world
 else:o['render_visible']=False;o['shadow']=False;o['role']='decorative'
def material(name,color,source=None):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
 rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)];m.diffuse_color=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
 if source:m['texture_json']=bpy.data.materials[source]['texture_json']
 return m
material('gardenBenchGreen','#426b59','timber')
water=material('fountainWater','#4ba4b2','water');spec=json.loads(water['texture_json']);spec.update(worldSize=6.4,paletteDetail=.32,ripple={'frequency':11,'speed':1.2,'amplitude':.07});water['texture_json']=json.dumps(spec)
def lathe(name,profile,mat,n=64,lobes=0,role='decorative'):
 points=[(r*(1+lobes*math.cos(4*k*math.tau/n))*math.cos(k*math.tau/n),r*(1+lobes*math.cos(4*k*math.tau/n))*math.sin(k*math.tau/n),z) for z,r in profile for k in range(n)]
 obj=kit.mesh('fountain-'+name,points,[[j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k] for j in range(len(profile)-1) for k in range(n)],mat,mat!='fountainWater')
 obj['role']=role
 if mat=='fountainWater':
  for face in obj.data.polygons:
   for li in face.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;obj.data.uv_layers.active.data[li].uv=(.5+p.x/6.4,.5+p.y/6.4)
 return obj
# Two low steps are real native floor contact surfaces, including their risers.
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain')
for index,(radius,z,base) in enumerate(((5.15,.12,.05),(4.70,.24,.12))):
 obj=lathe('step-'+str(index),[(base,radius),(z,radius),(z,0)],'cream')
 owner.objects.unlink(obj);terrain.objects.link(obj);obj['surface_role']='forecourt';obj['walkable']=True
 obj['object_id']='astral-fountain'
lathe('basin-foot',[(.24,0),(.24,3.06),(.38,3.06),(.38,0)],'stoneLight',lobes=.075,role='solid')
lathe('basin-rim',[(.36,3.02),(.44,3.12),(.78,3.12),(.88,3.20),(.99,3.20),(.99,2.82),(.83,2.82),(.43,2.82)],'cream',lobes=.075)
lathe('outer-water',[(.73,0),(.73,2.83)],'fountainWater',lobes=.075)
lathe('inner-pool-support',[(.73,.93),(1.04,1.12),(1.16,1.48),(1.30,1.52),(1.30,1.27),(1.13,1.27)],'stoneLight',n=48)
lathe('inner-water',[(1.22,0),(1.22,1.28)],'fountainWater',n=48)
lathe('central-plinth',[(1.22,.68),(1.36,.72),(1.50,.49),(2.02,.43),(2.19,.63),(2.35,.63)],'cream',n=24)
lathe('plinth-gold-belt',[(2.12,.61),(2.19,.61)],'gold',n=24)
# Original cloth folds add relief to the retained winged statue.
for j in range(16):
 a=j*math.tau/16
 points=[]
 for z,r in ((2.36,.66),(2.78,.58),(3.22,.48),(3.65,.34),(4.02,.27)):
  for q in (-.055,.055):points.append(((r+.025)*math.cos(a+q),(r+.025)*math.sin(a+q),z))
 kit.mesh('fountain-robe-fold-'+str(j),points,[[i*2,i*2+1,i*2+3,i*2+2] for i in range(4)],'stoneLight' if j%3==0 else 'cream')
# Four short falling sheets, each broad enough to read as water at gameplay zoom.
for j in range(4):
 a=j*math.tau/4+.18;u=Vector((math.cos(a),math.sin(a),0));v=Vector((-math.sin(a),math.cos(a),0));points=[]
 for k in range(9):
  t=k/8;p=u*(1.35+.90*t)+Vector((0,0,1.22+.12*t-.61*t*t))
  points.extend(tuple(p+v*side*.18) for side in (-1,1))
 obj=kit.mesh('fountain-cascade-'+str(j),points,[[k*2,k*2+1,k*2+3,k*2+2] for k in range(8)],'riverCascade',False)
 for face in obj.data.polygons:
  for li in face.loop_indices:
   vi=obj.data.loops[li].vertex_index;obj.data.uv_layers.active.data[li].uv=(vi%2,(vi//2)/8)
 lathe('splash-ring-'+str(j),[(.748,.10),(.752,.34)],'riverFoam',n=24).location=u*2.25
# Raised corner planting with volume, rooted flowers and soil below the stems.
for sx in (-1,1):
 for sy in (-1,1):
  x,y=sx*3.28,sy*3.28;tag=str((sx,sy))
  obj=kit.box('fountain-bed-base-'+tag,(x,y,.43),(1.74,1.74,.38),'cream');obj['role']='solid'
  kit.box('fountain-bed-soil-'+tag,(x,y,.635),(1.42,1.42,.05),'soil',False)
  for dx,dy,size in ((0,-.79,(1.74,.18,.24)),(0,.79,(1.74,.18,.24)),(-.79,0,(.18,1.56,.24)),(.79,0,(.18,1.56,.24))):
   kit.box('fountain-bed-rim-'+tag+str((dx,dy)),(x+dx,y+dy,.70),size,'stoneLight')
  for j in range(25):
   xx=x+((j%5)-2)*.26;yy=y+((j//5)-2)*.26;h=.23+.07*math.sin(j*2.3)
   kit.beam('fountain-flower-stem-'+tag+str(j),(xx,yy,.65),(xx,yy,.65+h),.025,'leaf')
   kit.box('fountain-flower-leaves-'+tag+str(j),(xx,yy,.69+h*.25),(.20,.17,.11),'leafLight',False)
   z=.65+h;r=.105
   kit.mesh('fountain-flower-'+tag+str(j),[(xx,yy,z-.025)]+[(xx+r*math.cos(k*math.tau/10),yy+r*math.sin(k*math.tau/10),z+(.02 if k%2 else -.015)) for k in range(10)],[[0,k+1,(k+1)%10+1] for k in range(10)],'flowerRose' if j%3 else 'flowerIvory',False)
# Four benches face the basin. Seat/back boards remain visibly separate.
for j in range(4):
 a=j*math.tau/4;before=set(owner.objects)
 for k in range(4):kit.box('fountain-bench-seat-'+str((j,k)),((k-1.5)*.14,4.36,.80),(.12,2.45,.09),'gardenBenchGreen')
 for k in range(3):kit.box('fountain-bench-back-'+str((j,k)),(.37,4.36,1.00+k*.15),(.10,2.45,.11),'gardenBenchGreen')
 for side in (-1,1):
  kit.box('fountain-bench-leg-'+str((j,side)),(0,4.36+side*.9,.49),(.42,.09,.50),'iron')
  kit.box('fountain-bench-arm-'+str((j,side)),(.02,4.36+side*1.17,1.03),(.58,.08,.09),'iron')
 collider=kit.box('fountain-bench-contact-'+str(j),(.08,4.36,.72),(.70,2.50,.96),'iron',False);collider['role']='solid';collider['render_visible']=False
 # Tangential seat axis; transform the model around the court.
 for obj in set(owner.objects)-before:
  for v in obj.data.vertices:v.co=Matrix.Rotation(a,4,'Z')@Vector((v.co.y-4.36,v.co.x+4.36,v.co.z))
scene=bpy.context.scene;scene['ro3_fountain_version']=68
scene['ro3_fountain_review_json']=json.dumps({'reference':'04_08_20','originalStatue':'retained celestial figure with authored cloth folds','outerProfile':'four lobed rim','outerRadius':3.2,'innerRadius':1.52,'waterLevels':[.73,1.22],'raisedBeds':4,'benches':4,'cascades':4,'walkableSteps':[.12,.24],'ripples':'source-defined shader metadata'})
bpy.context.view_layer.update();bpy.data.batch_remove(ids=[d for d in bpy.data.meshes if not d.users])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved RO3 tiered celestial fountain and planted public court; rebake required',flush=True)
