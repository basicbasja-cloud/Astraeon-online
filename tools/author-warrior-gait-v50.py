"""Original articulated Warrior study, rendered as sprites without changing game art.

Uses an editable armature and fixed-length two-bone IK, rather than inventing
opposite poses from a repeated painted contact. All frames share the pelvis
origin; stance feet move backward in local space and cancel forward travel.
"""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/warrior-rig-v50';OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;rig=bpy.data.objects['Walk IK guide']
for o in list(bpy.data.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
rig.animation_data_clear()
def ik(a,b,l1,l2,bend_axis):
 a,b=Vector(a),Vector(b);delta=b-a;d=delta.length
 assert abs(l1-l2)<d<l1+l2,(d,l1,l2)
 along=(l1*l1-l2*l2+d*d)/(2*d);bend=Vector(bend_axis);bend=(bend-delta.normalized()*bend.dot(delta.normalized())).normalized()
 return a+delta.normalized()*along+bend*math.sqrt(max(0,l1*l1-along*along))
# Set fixed-length rest arms before binding costume geometry. Every sampled
# arm thereafter has unit bone scale, including all in-between source keys.
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for side,name in [(-1,'L'),(1,'R')]:
 sh=Vector((side*.30,0,1.605));hand=Vector((side*.36,-side*.12,1.095));el=ik(sh,hand,.32,.30,(0,1,0))
 rig.data.edit_bones[name+'-upper-arm'].head=sh;rig.data.edit_bones[name+'-upper-arm'].tail=el
 rig.data.edit_bones[name+'-forearm'].head=el;rig.data.edit_bones[name+'-forearm'].tail=hand
bpy.ops.object.mode_set(mode='OBJECT')
scene.render.resolution_x=scene.render.resolution_y=384
scene.cycles.samples=24
scene.render.fps=80
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
scene.camera.data.ortho_scale=3.05
scene.camera.location=(0,7,4.15)
scene.camera.rotation_euler=(Vector((0,0,1.12))-scene.camera.location).to_track_quat('-Z','Y').to_euler()

def material(name,color,rough=.8):
 m=bpy.data.materials.new('Warrior '+name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 p.inputs['Specular IOR Level'].default_value=.12
 return m
mats={k:material(k,c) for k,c in {
 'skin':(.68,.43,.28),'skin-light':(.83,.61,.43),'hair':(.29,.31,.39),'hair-light':(.49,.51,.60),
 'leather':(.065,.037,.024),'leather-light':(.12,.070,.035),'armor':(.17,.10,.054),'armor-light':(.28,.18,.083),
 'gold':(.56,.30,.075),'gold-light':(.77,.48,.12),'cloak':(.61,.32,.035),'cloak-edge':(.84,.54,.12),
 'cream':(.65,.54,.35),'cream-light':(.83,.72,.50),'green':(.034,.12,.095),'green-light':(.067,.23,.16),
 'eye-white':(.85,.81,.70),'iris':(.045,.077,.092),'pupil':(.006,.01,.013),'steel':(.38,.43,.46),'steel-dark':(.17,.22,.24),
 }.items()}
def bind(o,bone,mat):
 o.data.materials.append(mats[mat]);g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
 mod=o.modifiers.new('Articulated full-body source','ARMATURE');mod.object=rig
 return o
def mesh(name,vs,fs,bone,mat,smooth=True):
 d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
 if smooth:
  for p in d.polygons:p.use_smooth=True
 return bind(o,bone,mat)
def ellipsoid(name,c,size,bone,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=c);o=bpy.context.object;o.name=name;o.scale=size
 for p in o.data.polygons:p.use_smooth=True
 return bind(o,bone,mat)
def tube(name,a,b,r,bone,mat,n=12):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.01:u=Vector((1,0,0))
 u.normalize();v=axis.cross(u).normalized()
 vs=[tuple(p+r*(u*math.cos(k*math.tau/n)+v*math.sin(k*math.tau/n))) for p in (a,b) for k in range(n)]
 return mesh(name,vs,[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[k,(k+1)%n,(k+1)%n+n,k+n] for k in range(n)],bone,mat)
def rings(name,sections,bone,mat,n=24):
 # Elliptical horizontal sections with authored taper; not stacked cubes.
 vs=[(x+rx*math.cos(k*math.tau/n),y+ry*math.sin(k*math.tau/n),z) for x,y,z,rx,ry in sections for k in range(n)]
 fs=[list(range(n-1,-1,-1)),list(range((len(sections)-1)*n,len(sections)*n))]
 fs += [[j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k] for j in range(len(sections)-1) for k in range(n)]
 return mesh(name,vs,fs,bone,mat)
def tapered_limb(name,a,b,profile,bone,mat,n=16):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=Vector((1,0,0));u=(u-axis*u.dot(axis)).normalized();v=axis.cross(u).normalized()
 vs=[tuple(a.lerp(b,t)+u*rx*math.cos(k*math.tau/n)+v*ry*math.sin(k*math.tau/n)) for t,rx,ry in profile for k in range(n)]
 fs=[list(range(n-1,-1,-1)),list(range((len(profile)-1)*n,len(profile)*n))]+[[j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k] for j in range(len(profile)-1) for k in range(n)]
 return mesh(name,vs,fs,bone,mat)
def rest(name):return rig.data.bones[name].head_local,rig.data.bones[name].tail_local

rings('Fitted dark cuirass',[(0,0,1.10,.24,.14),(0,0,1.25,.27,.17),(0,0,1.47,.29,.19),(0,0,1.61,.25,.17),(0,0,1.65,.15,.12)],'spine','leather')
rings('Bronze breast plate',[(0,.09,1.25,.23,.15),(0,.08,1.47,.26,.17),(0,.055,1.58,.235,.16)],'spine','armor')
rings('Waist belt',[(0,0,1.095,.285,.19),(0,0,1.18,.285,.19)],'spine','leather-light')
# Chest and waist ornament stays broad enough to read at normal actor size.
ellipsoid('Belt central crest',(0,.204,1.135),(.064,.023,.061),'spine','gold-light')
for sign in (-1,1):
 tube('Chest gold seam '+str(sign),(sign*.04,.263,1.28),(sign*.23,.215,1.54),.018,'spine','gold')
 mesh('Chest raised plate '+str(sign),[(sign*.015,.271,1.27),(sign*.215,.235,1.39),(sign*.22,.225,1.53),(sign*.025,.259,1.48)],[[0,1,2,3]],'spine','armor-light',False)
 ellipsoid('Hip layered plate '+str(sign),(sign*.265,.01,1.02),(.115,.18,.19),'spine','armor')
 # Short, split tunic panels expose alternating knees in both contacts.
 vs=[(sign*.045,.215,1.12),(sign*.24,.17,1.12),(sign*.35,.20,.76),(sign*.07,.28,.72)]
 panel=mesh('Cream split tunic '+str(sign),vs,[[0,1,2,3]],'spine','cream-light')
 mod=panel.modifiers.new('Cloth thickness','SOLIDIFY');mod.thickness=.018
 for a,b in zip(vs,vs[1:]+vs[:1]):tube('Tunic hem '+str((sign,a)),a,b,.009,'spine','gold')

for sign,name in [(-1,'L'),(1,'R')]:
 for suffix,profile,mat in [
  ('thigh',[(0,.13,.14),(.25,.14,.145),(.8,.11,.11),(1,.105,.105)],'leather'),
  ('shin',[(0,.105,.105),(.3,.12,.115),(.75,.085,.09),(1,.07,.075)],'leather-light'),
  ('upper-arm',[(0,.115,.12),(.4,.105,.105),(1,.078,.080)],'leather'),
  ('forearm',[(0,.082,.085),(.28,.11,.10),(.85,.085,.075),(1,.07,.067)],'armor')]:
  a,b=rest(name+'-'+suffix);tapered_limb(name+' '+suffix,a,b,profile,name+'-'+suffix,mat)
 a,k=rest(name+'-thigh');_,ankle=rest(name+'-shin');sh,_=rest(name+'-upper-arm');_,hand=rest(name+'-forearm')
 ellipsoid(name+' bronze kneecap',k+Vector((0,.045,0)),(.13,.13,.125),name+'-thigh','armor-light')
 ellipsoid(name+' pauldron',sh+Vector((sign*.025,0,.025)),(.19,.20,.12),name+'-upper-arm','armor-light')
 ellipsoid(name+' pauldron gold trim',sh+Vector((sign*.025,.015,.01)),(.198,.204,.043),name+'-upper-arm','gold')
 ellipsoid(name+' bronze shin plate',ankle.lerp(k,.53)+Vector((0,.055,0)),(.08,.065,.18),name+'-shin','armor')
 for t in (.25,.64):
  p=ankle.lerp(k,t);tube(name+' greave band '+str(t),p+Vector((-.088,.04,0)),p+Vector((.088,.04,0)),.02,name+'-shin','gold')
 # Boot geometry is anchored to the ankle; the bottom is a true shared floor.
 rings(name+' boot',[(ankle.x,ankle.y+.04,.015,.105,.20),(ankle.x,ankle.y+.065,.065,.12,.235),(ankle.x,ankle.y+.035,.14,.105,.17),(ankle.x,ankle.y,.22,.082,.095)],name+'-boot','leather')
 rings(name+' boot sole',[(ankle.x,ankle.y+.045,.005,.109,.205),(ankle.x,ankle.y+.045,.035,.112,.21)],name+'-boot','leather-light')
 ellipsoid(name+' glove',hand,(.085,.073,.10),name+'-forearm','leather-light')

# Clean original face with a tapered chin and silver layered hair silhouette.
rings('Face',[(0,0,1.75,.09,.08),(0,.015,1.81,.17,.135),(0,0,1.96,.235,.19),(0,-.015,2.14,.22,.18),(0,-.025,2.22,.12,.115)],'head','skin-light',32)
ellipsoid('Hair crown',(0,-.035,2.16),(.25,.21,.18),'head','hair')
for sign in (-1,1):
 ellipsoid('Ear '+str(sign),(sign*.222,0,1.965),(.048,.047,.073),'head','skin')
 eye=ellipsoid('Eye white '+str(sign),(sign*.09,.182,2.015),(.061,.021,.049),'head','eye-white')
 ellipsoid('Iris '+str(sign),(sign*.085,.202,2.013),(.031,.010,.040),'head','iris')
 ellipsoid('Pupil '+str(sign),(sign*.085,.210,2.013),(.017,.006,.028),'head','pupil')
 ellipsoid('Eye highlight '+str(sign),(sign*.079,.214,2.030),(.009,.004,.011),'head','eye-white')
 tube('Brow '+str(sign),(sign*.040,.18,2.08),(sign*.148,.16,2.075),.010,'head','hair')
 tube('Upper lash '+str(sign),(sign*.035,.203,2.038),(sign*.145,.182,2.04),.008,'head','pupil')
ellipsoid('Small nose',(0,.186,1.946),(.027,.025,.034),'head','skin-light')
tube('Mouth',(-.033,.162,1.885),(.033,.162,1.885),.006,'head','skin')
random.seed(50)
for j in range(33):
 theta=j*math.tau/33;front=math.sin(theta)>0
 start=Vector((.13*math.cos(theta),-.02+.12*math.sin(theta),2.27))
 end=Vector((.27*math.cos(theta+.10),-.025+.225*math.sin(theta),(2.05+.11*math.sin(theta*3+1.1)) if front else (1.965+.045*math.sin(theta*4))))
 bend=start.lerp(end,.48)+Vector((.025*math.cos(theta),.025*math.sin(theta),.035));direction=(end-start).normalized();u=Vector((math.cos(theta),math.sin(theta),0));v=direction.cross(u).normalized();vs=[]
 for t,w in [(0,.025),(.40,.070),(.74,.042),(1,.002)]:
  center=(1-t)**2*start+2*(1-t)*t*bend+t*t*end
  for k in range(8):vs.append(tuple(center+w*(u*math.cos(k*math.tau/8)+v*.45*math.sin(k*math.tau/8))))
 fs=[list(range(7,-1,-1)),list(range(24,32))]+[[q*8+k,q*8+(k+1)%8,(q+1)*8+(k+1)%8,(q+1)*8+k] for q in range(3) for k in range(8)]
 mesh('Silver hair lock '+str(j),vs,fs,'head','hair-light' if j%3==0 else 'hair')
for j in range(13):
 theta=j*math.tau/13;start=Vector((.12*math.cos(theta),-.02+.11*math.sin(theta),2.245));tip=Vector((.29*math.cos(theta+.16),-.02+.26*math.sin(theta+.16),2.15+.10*math.sin(theta*2)))
 u=Vector((-math.sin(theta),math.cos(theta),0));mid=start.lerp(tip,.5)+Vector((0,0,.085))
 mesh('Tousled crown tuft '+str(j),[tuple(start-u*.06),tuple(start+u*.06),tuple(mid+Vector((0,0,.045))),tuple(tip)],[[0,1,2],[0,2,3],[2,1,3],[1,0,3]],'head','hair-light' if j%3==0 else 'hair',False)

# A joined, folded gold cape; only its trailing cloth flexes, never the boots.
cols,rows=17,12;vs=[]
for j in range(rows):
 t=j/(rows-1)
 for i in range(cols):
  u=i/(cols-1)*2-1
  vs.append((u*(.30+.40*t),-.18-.26*t-.06*math.cos(u*math.pi*4)*(t+.2),1.62-.85*t-.05*(1-u*u)*t))
cape=mesh('Golden folded cape',vs,[[j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i] for j in range(rows-1) for i in range(cols-1)],'spine','cloak')
mod=cape.modifiers.new('Joined cloth thickness','SOLIDIFY');mod.thickness=.017
cape.shape_key_add(name='Basis')
for sign in (-1,1):
 ellipsoid('Cape clasp '+str(sign),(sign*.225,.16,1.56),(.049,.025,.049),'spine','gold-light')
 tube('Cape neckline '+str(sign),(sign*.25,.105,1.61),(0,.15,1.535),.032,'spine','cloak-edge')
green=mesh('Emerald scarf',[(-.12,.25,1.59),(.12,.25,1.59),(.10,.27,1.43),(0,.27,1.36),(-.10,.27,1.43)],[[0,1,2,3,4]],'spine','green-light')
# Sword attached to the right hand, matching the shipped character's role.
_,hand=rest('R-forearm');h=hand+Vector((.025,.07,-.015));tip=h+Vector((.35,.10,-.68));axis=(tip-h).normalized();u=Vector((.92,0,.4)).normalized()
blade=mesh('Sword beveled blade',[tuple(h+u*.052),tuple(h-u*.052),tuple(h+Vector((0,.04,0))),tuple(tip)],[[0,1,2],[0,2,3],[2,1,3],[1,0,3]],'R-forearm','steel',False)
tube('Sword guard',h-u*.12,h+u*.12,.023,'R-forearm','gold');tube('Sword grip',h-axis*.16,h,.027,'R-forearm','leather')

stride,duty=.70,.62;distance=stride/duty;length=.57
def pose(phase):
 lift=.015*math.cos(phase*math.tau*2);hipz=1.03+lift
 result={'spine':((0,0,hipz),(0,0,1.66+lift)),'head':((0,0,1.66+lift),(0,0,2+lift))};feet={}
 for side,name in [(-1,'L'),(1,'R')]:
  q=(phase+(.5 if side==-1 else 0))%1;stance=q<duty;u=q/duty if stance else (q-duty)/(1-duty)
  y=stride/2-stride*u if stance else -stride/2+stride*(u*u*(3-2*u));z=.10+(0 if stance else .15*math.sin(u*math.pi))
  hip=Vector((side*.17,0,hipz));ankle=Vector((side*.17,y,z));knee=ik(hip,ankle,length,length,(0,1,0))
  result[name+'-thigh']=(hip,knee);result[name+'-shin']=(knee,ankle);result[name+'-boot']=(ankle,ankle+Vector((0,.23,0)))
  sh=Vector((side*.30,0,1.59+lift));swing=-side*.12*math.cos(phase*math.tau);hand=Vector((side*.36,swing,1.08+lift));el=ik(sh,hand,.32,.30,(0,1,0))
  result[name+'-upper-arm']=(sh,el);result[name+'-forearm']=(el,hand)
  feet[name]={'stance':stance,'ankle':list(ankle),'virtualRootY':phase*distance,'virtualAnkleY':phase*distance+y}
 return result,feet
# The evaluated endpoints, fixed limb lengths and planted-foot cancellation
# are checked before exporting a candidate. Mathematical checks do not approve
# the appearance or its match to the shipped illustration.
records=[];max_error=0
for frame in range(1,82):
 phase=(frame-1)/80;positions,feet=pose(phase%1)
 for foot in feet.values():
  foot['virtualRootY']=phase*distance;foot['virtualAnkleY']=phase*distance+foot['ankle'][1]
 for name,(a,b) in positions.items():
  bone=rig.pose.bones[name];a,b=Vector(a),Vector(b);q=Vector((0,1,0)).rotation_difference(b-a)
  scale=Matrix.Diagonal(Vector((1,(b-a).length/rig.data.bones[name].length,1,1)))
  bone.rotation_mode='QUATERNION';bone.matrix=Matrix.Translation(a)@q.to_matrix().to_4x4()@scale
  for prop in ('location','rotation_quaternion','scale'):bone.keyframe_insert(prop,frame=frame)
 bpy.context.view_layer.update()
 for name in ('L','R'):
  actual=rig.pose.bones[name+'-boot'].head
  error=(actual-Vector(feet[name]['ankle'])).length;max_error=max(max_error,error);assert error<1e-5
  feet[name]['evaluatedAnkle']=list(actual);feet[name]['virtualAnkleY']=phase*distance+actual.y
 key=cape.shape_key_add(name='Cape phase '+str(frame))
 for j in range(rows):
  t=j/(rows-1)
  for i in range(cols):
   u=i/(cols-1)*2-1;p=key.data[j*cols+i].co
   p.x+=.045*t*t*math.sin(phase*math.tau-u*.45);p.y-=.05*t*t*math.cos(phase*math.tau-t*1.4);p.z+=.04*t*t*math.sin(phase*math.tau-t)
 key.value=0;key.keyframe_insert('value',frame=frame-1);key.value=1;key.keyframe_insert('value',frame=frame);key.value=0;key.keyframe_insert('value',frame=frame+1)
 records.append({'frame':frame,'phase':phase,'feet':feet})
for action in bpy.data.actions:
 for f in action.fcurves:
  for key in f.keyframe_points:key.interpolation='LINEAR'
scene.frame_start=1;scene.frame_end=80;scene['purpose']='Original rigged sprite candidate, not approved or installed';scene['cycle_distance']=distance
scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'warrior-walk.blend'),compress=True)
# The 80-step stance displacement is measured from evaluated rig ankles. Each
# stance ankle cancels root travel; wrap boundaries are treated as new cycles.
stance_errors=[]
for a,b in zip(records,records[1:]):
 for name in ('L','R'):
  f,g=a['feet'][name],b['feet'][name]
  if f['stance'] and g['stance'] and abs(g['ankle'][1]-f['ankle'][1])<.1:stance_errors.append(abs(g['virtualAnkleY']-f['virtualAnkleY']))
assert max(stance_errors)<1e-6
(OUT/'rig-validation.json').write_text(json.dumps({'candidateOnly':True,'cycleDistance':distance,'legLength':length,'duty':duty,'maxEvaluatedAnkleError':max_error,'maxStanceTravelError':max(stance_errors),'fixedArmLengths':[.32,.30],'frames':records},indent=2)+'\n')
for frame in [1,11,21,31,41,51,61,71]:
 scene.frame_set(frame);scene.render.filepath=str(OUT/f'S-{frame:02d}.png');bpy.ops.render.render(write_still=True)
print('Saved original Warrior rig candidate; exact measured ankle error',max_error,'stance drift',max(stance_errors),flush=True)
