"""Free/local original character blockout; not painted production art.
All visible character geometry is bone-weighted, including rigid accessories.
Source v43 is read-only. No provider/API/network, imported art, or external model.
"""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent; PRIOR=P.parent/'continuous-arm-v43'; OUT=P/'renders'; OUT.mkdir(exist_ok=True)
S=json.loads((PRIOR/'source/source.json').read_text()); V=Vector
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=False;sc.render.fps=30
sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.view_settings.view_transform='Standard'
sc.world=bpy.data.worlds.new('World');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
COLORS=dict(skin=(.73,.43,.28),skinlight=(.94,.65,.43),hair=(.53,.45,.59),hairlight=(.82,.73,.82),hairshine=(.96,.88,.77),navy=(.035,.045,.080),navylight=(.065,.080,.12),gold=(.70,.34,.025),goldlight=(.95,.60,.12),bronze=(.40,.22,.09),bronzebright=(.77,.48,.19),brown=(.13,.055,.025),leather=(.21,.10,.045),olive=(.12,.13,.075),cream=(.86,.76,.57),teal=(.026,.19,.21),white=(.99,.95,.86),ink=(.021,.015,.027),iris=(.18,.12,.23),gem=(.02,.57,.71))
M={}
for k,c in COLORS.items():
 m=bpy.data.materials.new(k);m.diffuse_color=(*c,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.65;bs.inputs['Metallic'].default_value=.5 if 'bronze' in k else 0;M[k]=m
# Same explicit source targets; monotone cubic interpolation, then fixed-length IK.
D=[0,.18,.72,1,.82,.38,.06,0];B=[0,12,50,65,54,26,4,0];G=[f['points']['right.grip']['world_xyz'] for f in S['frames']]
def cubic(vals,t):
 n=len(vals);x=max(0,min(n-1,t*(n-1)));j=min(n-2,int(x));u=x-j;ds=[vals[k+1]-vals[k] for k in range(n-1)];sl=[0.]*n
 for k in range(1,n-1):sl[k]=2*ds[k-1]*ds[k]/(ds[k-1]+ds[k]) if ds[k-1]*ds[k]>0 else 0
 # Zero endpoint velocity makes rest and final hold continuous.
 return (2*u**3-3*u*u+1)*vals[j]+(u**3-2*u*u+u)*sl[j]+(-2*u**3+3*u*u)*vals[j+1]+(u**3-u*u)*sl[j+1]
def ik(a,b,l1,l2,pole):
 delta=b-a;dist=delta.length
 if not abs(l1-l2)+1e-7<dist<l1+l2-1e-7:raise ValueError(('unreachable',dist,l1+l2))
 n=delta/dist;v=pole-a;v-=n*v.dot(n);v.normalize();u=(l1*l1-l2*l2+dist*dist)/(2*dist);return a+n*u+v*math.sqrt(max(0,l1*l1-u*u))
def pose(t):
 d=cubic(D,t);bend=cubic(B,t);a=math.radians(bend);axis=V((0,-math.sin(a),math.cos(a)));hip=V((0,.14*d,.95-.47*d));p=dict(pelvis=hip,chest=hip+axis*.55,neck=hip+axis*.72);ht=math.radians(5+45*d);p['head']=p['neck']+V((0,-math.sin(ht)*.25,math.cos(ht)*.25))
 for side,sgn in [('left',1),('right',-1)]:
  h=hip+V((sgn*.14,0,0));ankle=V((sgn*.18,.02,.14));knee=ik(h,ankle,.42,.40,V((sgn*.17,-1,.45)));shoulder=p['chest']+V((sgn*.22,0,0));grip=V([cubic([g[k] for g in G],t) for k in range(3)]) if side=='right' else V((.32,.015+.205*d,.85-.25*d));elbow=ik(shoulder,grip,.29,.39,shoulder+V((sgn*.45,0,-.30)) if side=='left' else shoulder+V((sgn*.25,.05,-.30)));distal=(grip-elbow).normalized();wrist=elbow+distal*.27;palm=wrist+distal*.07
  for label,v in dict(hip=h,knee=knee,ankle=ankle,toe=ankle+V((0,-.20,-.05)),shoulder=shoulder,elbow=elbow,wrist=wrist,palm=palm,grip=grip).items():p[side+'.'+label]=v
 return p,d,bend
REST=pose(0)[0]
def frame(y,n):
 y=y.normalized();n=n.normalized();x=y.cross(n).normalized();z=x.cross(y).normalized();return Matrix((x,y,z)).transposed().to_quaternion()
def matrices(p,d):
 axis=(p['neck']-p['pelvis']).normalized();q=Matrix.Rotation(math.atan2(-axis.y,axis.z),4,'X').to_quaternion();hq=Matrix.Rotation(math.radians(5+45*d),4,'X').to_quaternion();m={'root':Matrix.Translation(p['pelvis']),'torso':Matrix.LocRotScale(p['pelvis'],q,V((1,1,1))),'head':Matrix.LocRotScale(p['head'],hq,V((1,1,1)))}
 for side in ['left','right']:
  for labels,keys in [(('upperarm','forearm','hand'),('shoulder','elbow','wrist','palm')),(('thigh','shin'),('hip','knee','ankle'))]:
   vs=[p[side+'.'+k] for k in keys];u=(vs[1]-vs[0]).normalized();f=(vs[2]-vs[1]).normalized();n=u.cross(f)
   if n.length<1e-6:raise ValueError('hinge plane undefined: explicit transport required')
   for j,label in enumerate(labels):m[side+'.'+label]=Matrix.LocRotScale(vs[j],frame(u if j==0 else f,n),V((1,1,1)))
  m[side+'.foot']=Matrix.Translation(p[side+'.ankle'])
 return m
BM=matrices(REST,0)
AD=bpy.data.armatures.new('Astraeon_Free_Local');rig=bpy.data.objects.new('Astraeon_Free_Local',AD);sc.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
ends={'root':REST['pelvis']+V((0,.06,0)),'torso':REST['neck'],'head':REST['head']+BM['head'].to_quaternion()@V((0,.10,0))}
parents={'torso':'root','head':'torso'}
for side in ['left','right']:
 for label,key,parent in [('upperarm','elbow','torso'),('forearm','wrist',side+'.upperarm'),('hand','palm',side+'.forearm'),('thigh','knee','root'),('shin','ankle',side+'.thigh'),('foot','toe',side+'.shin')]:ends[side+'.'+label]=REST[side+'.'+key];parents[side+'.'+label]=parent
for name,mat in BM.items():
 b=AD.edit_bones.new(name);length=max(.06,(ends[name]-mat.translation).length);b.head=mat.translation;b.tail=mat.translation+mat.to_3x3().col[1]*length;b.matrix=mat;b.length=length
 if name in parents:b.parent=AD.edit_bones[parents[name]]
bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
for name,expected in BM.items():
 error=max(abs(a-b) for ra,rb in zip(AD.bones[name].matrix_local,expected) for a,b in zip(ra,rb))
 assert error<1e-5,('actual bind basis mismatch',name,error)
ALL=[]
def bind(o,weights,slot='body_outfit'):
 o['runtime_slot']=slot;groups={}
 for i,ws in enumerate(weights):
  for bone,w in ws.items():
   if w>0:
    if bone not in groups:groups[bone]=o.vertex_groups.new(name=bone)
    groups[bone].add([i],float(w),'REPLACE')
 mod=o.modifiers.new('Weighted original mesh','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;ALL.append(o);return o
def mesh(name,vs,fs,mat,weights,slot='body_outfit',smooth=False):
 data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update();o=bpy.data.objects.new(name,data);sc.collection.objects.link(o);o.data.materials.append(M[mat]);bind(o,weights,slot)
 for f in data.polygons:f.use_smooth=smooth
 return o
def rigid(o,bone,mat,slot='body_outfit'):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.data.materials.append(M[mat]);return bind(o,[{bone:1} for v in o.data.vertices],slot)
def ell(name,pos,scale,mat,bone,slot='body_outfit',q=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1);o=bpy.context.object;o.name=name;o.location=pos;o.scale=scale
 if q:o.rotation_mode='QUATERNION';o.rotation_quaternion=q
 for f in o.data.polygons:f.use_smooth=True
 return rigid(o,bone,mat,slot)
def box(name,pos,scale,mat,bone,bevel=.02):
 bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;o.location=pos;o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Beveled craft','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return rigid(o,bone,mat)
def line(name,points,r,mat,bone,slot='body_outfit'):
 # Mesh converted locally; bind actual rendered curve surface, not a diagnostic overlay.
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=8;cu.bevel_depth=r;cu.bevel_resolution=2;s=cu.splines.new('POLY');s.points.add(len(points)-1)
 for a,b in zip(s.points,points):a.co=(*b,1)
 o=bpy.data.objects.new(name,cu);sc.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');return rigid(bpy.context.object,bone,mat,slot)
def surface_rings(side,kind):
 arm=kind=='arm';a,b,c=[REST[side+'.'+x] for x in (('shoulder','elbow','wrist') if arm else ('hip','knee','ankle'))];l1=(b-a).length;l2=(c-b).length;u=(b-a).normalized();v=(c-b).normalized();n=u.cross(v).normalized();vs=[];ws=[];fs=[];nr=29;ns=24;total=l1+l2
 knots=[(0,.053),(.15,.050),(.29,.043),(.34,.049),(.45,.042),(.56,.033)] if arm else [(0,.086),(.18,.092),(.35,.080),(.42,.079),(.48,.078),(.68,.064),(.82,.058)]
 for j in range(nr):
  t=total*j/(nr-1);center=a+u*t if t<=l1 else b+v*(t-l1);w=max(0,min(1,(t-l1+.055)/.11));w=w*w*(3-2*w);tangent=(u*(1-w)+v*w).normalized();normal=tangent.cross(n).normalized();radius=knots[-1][1]
  for (t0,r0),(t1,r1) in zip(knots,knots[1:]):
   if t0<=t<=t1:radius=r0+(r1-r0)*(t-t0)/(t1-t0);break
  for k in range(ns):
   ang=2*math.pi*k/ns;vs.append(center+normal*(math.cos(ang)*radius)+n*(math.sin(ang)*radius*.90));ws.append({side+('.upperarm' if arm else '.thigh'):1-w,side+('.forearm' if arm else '.shin'):w})
 for j in range(nr-1):
  for k in range(ns):fs.append((j*ns+k,j*ns+(k+1)%ns,(j+1)*ns+(k+1)%ns,(j+1)*ns+k))
 fs.extend([tuple(range(ns-1,-1,-1)),tuple((nr-1)*ns+k for k in range(ns))]);o=mesh(side+'.continuous_'+kind,vs,fs,'navy' if arm else 'olive',ws,smooth=True);o.data.materials.append(M['bronze' if arm else 'leather'])
 for poly in o.data.polygons:poly.material_index=1 if sum(v//ns for v in poly.vertices)/len(poly.vertices)*total/(nr-1)>(.32 if arm else .44) else 0
 return o
for side in ['left','right']:
 surface_rings(side,'arm');surface_rings(side,'leg');p=REST[side+'.ankle'];foot=side+'.foot';shin=side+'.shin';hand=side+'.hand';arm=side+'.upperarm';fore=side+'.forearm'
 box(side+'.sole',p+V((0,-.072,-.111)),(.183,.325,.057),'brown',foot,.022);ell(side+'.boot',p+V((0,-.065,-.047)),(.094,.166,.076),'leather',foot)
 # Leather vamp seam and ankle gold band follow their actual foot bone.
 line(side+'.boot_seam',[p+V((-.078,-.14,-.028)),p+V((0,-.19,-.011)),p+V((.078,-.14,-.028))],.004,'bronze',foot)
 for z in [.042,.257]:ell(side+'.boot_band'+str(z),p+V((0,0,z)),(.074,.074,.018),'bronzebright',shin)
 knee=REST[side+'.knee'];ell(side+'.knee_guard',knee+V((0,-.052,-.014)),(.075,.049,.078),'bronze',shin);ell(side+'.kneepad_highlight',knee+V((0,-.093,-.012)),(.031,.015,.044),'bronzebright',shin)
 shoulder=REST[side+'.shoulder'];ell(side+'.shoulder_plate',shoulder+V((0,0,.004)),(.106,.105,.085),'bronze',arm)
 ell(side+'.shoulder_rim',shoulder+V((0,-.006,-.035)),(.110,.110,.022),'bronzebright',arm)
 w=REST[side+'.wrist'];palm=REST[side+'.palm'];q=(palm-w).to_track_quat('Z','Y');ell(side+'.glove',w+(palm-w)*.6,(.039,.038,.076),'brown',hand,q=q);ell(side+'.knuckles',REST[side+'.grip']-V((0,0,-.014)),(.038,.037,.034),'leather',hand,q=q)
 # Authored thumb position tied to the hand frame, not screen-near inference.
 thumb=BM[hand].to_quaternion()@V((.031,0,.018));ell(side+'.thumb',palm+thumb,(.018,.021,.032),'brown',hand,q=q)
 for f in [.10,.80]:
  loc=REST[side+'.elbow'].lerp(w,f);ell(side+'.bracer_band'+str(f),loc,(.051,.050,.014),'bronzebright',fore,q=(w-REST[side+'.elbow']).to_track_quat('Z','Y'))
# Coherent tunic: weighted rings, root/torso overlap at the hidden waist.
vs=[];ws=[];fs=[];hip=REST['pelvis'];RINGS=[(-.09,.20,.145,0),(0,.19,.140,.35),(.12,.165,.125,1),(.33,.18,.13,1),(.55,.215,.135,1),(.62,.14,.10,1)]
for z,rx,ry,w in RINGS:
 for k in range(32):
  a=2*math.pi*k/32;vs.append(hip+V((rx*math.cos(a),ry*math.sin(a),z)));ws.append({'root':1-w,'torso':w})
for j in range(len(RINGS)-1):
 for k in range(32):fs.append((j*32+k,j*32+(k+1)%32,(j+1)*32+(k+1)%32,(j+1)*32+k))
mesh('coherent_tunic',vs,fs,'navy',ws,smooth=True)
# Ivory chest panel follows torso. Gold edge is real geometry.
def torso_pos(x,y,z):return BM['torso']@V((x,y,z))
for x,w,mat in [(0,.14,'cream'),(-.078,.009,'bronzebright'),(.078,.009,'bronzebright')]:
 vv=[torso_pos(x-w/2,-.142,.09),torso_pos(x+w/2,-.142,.09),torso_pos(x+w/2,-.143,.51),torso_pos(x-w/2,-.143,.51)];mesh('tunic_front_'+str(x),vv,[(0,1,2,3)],mat,[{'torso':1}]*4)
ell('waist_belt',hip+V((0,0,.022)),(.208,.155,.043),'brown','root');box('belt_buckle',hip+V((0,-.158,.023)),(.078,.025,.066),'bronzebright','root',.008);box('buckle_inset',hip+V((0,-.174,.023)),(.044,.008,.038),'brown','root',.002)
for x in [-.20,.20]:box('belt_pouch'+str(x),hip+V((x,.022,-.02)),(.095,.095,.11),'leather','root',.016)
# Two original waist tabs, closed shells authored with full body outfit.
for x,mat,w,depth in [(-.075,'cream',.15,.155),(.14,'teal',.14,.14)]:
 vv=[hip+V((x-w/2,-depth,-.01)),hip+V((x+w/2,-depth,-.01)),hip+V((x+w*.58,-depth-.025,-.30)),hip+V((x,-depth-.03,-.36)),hip+V((x-w*.58,-depth-.025,-.30))];mesh('waist_tab_'+mat,vv,[(0,1,2,3,4)],mat,[{'root':1}]*5)
 line('waist_trim_'+mat,[v+V((0,-.003,0)) for v in vv+[vv[0]]],.006,'bronzebright','root')
 vv2=[hip+V((x,-depth-.036,-.17)),hip+V((x+.027,-depth-.036,-.22)),hip+V((x,-depth-.036,-.26)),hip+V((x-.027,-depth-.036,-.22))];mesh('tab_rune_'+mat,vv2,[(0,1,2,3)],'goldlight',[{'root':1}]*4)
# Scarf: chest-owned collar covers the neck receiver.
neck=REST['neck'];ell('scarf',neck+V((0,.016,-.083)),(.19,.135,.078),'gold','torso');ell('scarf_fold',neck+V((0,-.045,-.105)),(.192,.13,.034),'goldlight','torso')
ell('neck_skin',neck+V((0,0,.025)),(.068,.067,.13),'skinlight','torso')
# Cape's local surface follows torso with its hem above the shins; no independent frame fitting.
cv=[];cw=[];cf=[]
for j in range(9):
 t=j/8;z=.66-.91*t;y=.18+.32*t;w=.17+.20*t
 for k in range(9):
  u=k/8*2-1;cv.append(torso_pos(u*w,y+.022*math.cos(u*math.pi*4)*t,z+.022*math.cos(u*math.pi*2)*t));cw.append({'torso':1})
for j in range(8):
 for k in range(8):a=j*9+k;cf.append((a,a+1,a+10,a+9))
cape=mesh('original_cape',cv,cf,'gold',cw,smooth=True);sol=cape.modifiers.new('Cloth shell','SOLIDIFY');sol.thickness=.008
for k in [0,8]:line('cape_trim'+str(k),[cv[j*9+k]+V((0,.008,0)) for j in range(9)],.007,'goldlight','torso')
# Ivory angular original emblem on the back, not a borrowed game texture.
line('cape_rune',[torso_pos(x,y,z) for x,y,z in [(-.15,.435,-.02),(-.07,.44,-.08),(0,.455,-.02),(.07,.46,-.11),(.14,.47,-.05),(.04,.49,-.18),(-.02,.48,-.12),(-.09,.475,-.17)]],.013,'cream','torso')
# Complete original head-style slot: face, ears, eyes, brows, and authored volumetric hair locks.
h=REST['head'];hq=BM['head'].to_quaternion();HP=lambda x:h+hq@V(x)
ell('face',h,(.202,.187,.218),'skinlight','head','complete_head',hq)
for sgn in [-1,1]:
 ell('ear'+str(sgn),HP((sgn*.194,.005,-.015)),(.035,.036,.058),'skinlight','head','complete_head',hq)
 ell('ear_inner'+str(sgn),HP((sgn*.212,-.016,-.015)),(.012,.024,.033),'skin','head','complete_head',hq)
 # Flush curved eye patches, not protruding spherical eyeballs.
 def eye_surface(x,z,off=.003):return HP((x,-.187*math.sqrt(max(.02,1-(x/.202)**2-(z/.218)**2))-off,z))
 for mat,rx,rz,off in [('ink',.058,.037,.002),('white',.050,.029,.003),('iris',.022,.028,.004),('ink',.010,.025,.005)]:
  vv=[eye_surface(sgn*.081,.006,off)]+[eye_surface(sgn*.081+rx*math.cos(2*math.pi*k/32),.006+rz*math.sin(2*math.pi*k/32),off) for k in range(32)];mesh('eye_'+mat+str(sgn),vv,[(0,1+k,1+(k+1)%32) for k in range(32)],mat,[{'head':1}]*len(vv),'complete_head',True)
 ell('eye_glint'+str(sgn),eye_surface(sgn*.081-.008,.015,.008),(.005,.002,.007),'white','head','complete_head',hq)
 line('eyebrow'+str(sgn),[HP((sgn*.045,-.184,.066)),HP((sgn*.088,-.185,.075)),HP((sgn*.123,-.165,.066))],.009,'hair','head','complete_head')
ell('nose',HP((0,-.181,-.040)),(.018,.027,.022),'skinlight','head','complete_head',hq);line('mouth',[HP((-.028,-.171,-.091)),HP((0,-.179,-.097)),HP((.024,-.174,-.091))],.003,'skin','head','complete_head')
# Hair cap sits behind the face; front fringe gets distinct curled tapered locks.
ell('hair_cap',HP((0,.030,.071)),(.219,.189,.215),'hair','head','complete_head',hq)
def lock(name,centers,widths,mat):
 centers=[HP(c) for c in centers];vs=[];fs=[]
 for j,(c,w) in enumerate(zip(centers,widths)):
  tangent=(centers[min(j+1,len(centers)-1)]-centers[max(0,j-1)]).normalized();n=tangent.cross(V((0,-1,0)))
  if n.length<.01:n=tangent.cross(V((1,0,0)))
  n.normalize();b=tangent.cross(n).normalized()
  for k in range(8):a=2*math.pi*k/8;vs.append(c+n*math.cos(a)*w+b*math.sin(a)*w*.35)
 for j in range(len(centers)-1):
  for k in range(8):fs.append((j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k))
 fs.extend([tuple(range(7,-1,-1)),tuple((len(centers)-1)*8+k for k in range(8))]);mesh(name,vs,fs,mat,[{'head':1}]*len(vs),'complete_head',True)
for j in range(22):
 a=2*math.pi*j/22;xx=math.sin(a);yy=math.cos(a);z=.11+.045*math.sin(j*2.3);lock('hair_crown_'+str(j),[(xx*.075,yy*.075,z+.10),(xx*.165,yy*.16,z+.095),(xx*.23,yy*.20,z+.01),(xx*.265+ .024,yy*.22,z+.025)],[.043,.058,.045,.001],'hairlight' if j%3 else 'hairshine')
for j in range(15):
 a=2*math.pi*j/15;xx=math.sin(a);yy=math.cos(a)
 if yy>-.4:lock('hair_lower_'+str(j),[(xx*.17,yy*.15,.14),(xx*.205,yy*.18,.055),(xx*.225,yy*.20,-.04),(xx*.25,yy*.205,-.065)],[.042,.053,.043,.001],'hairlight' if j%3 else 'hair')
for j in range(9):
 x=(j-4)*.043;lock('fringe_'+str(j),[(x*.4,-.10,.22),(x-.02,-.17,.15),(x-.036,-.197,.09),(x-.075,-.184,.035+ .035*abs(j-4)/4)],[.036,.044,.030,.001],'hairlight' if j%3 else 'hairshine')
lock('cowlick',[(0,.01,.24),(-.035,.015,.29),(-.10,.025,.32),(-.14,.02,.30)],[.04,.033,.020,.001],'hairlight')
# Held collectible has one canonical RIGHT owner, no owner change at lift.
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1);gem=bpy.context.object;gem.name='collectible';gem.scale=(.055,.055,.075);gem.data.materials.append(M['gem'])
for loc,energy,size in [((3,-5,8),700,4),((-4,2,5),450,4)]:
 ld=bpy.data.lights.new('Studio','AREA');ld.energy=energy;ld.size=size;o=bpy.data.objects.new('Studio',ld);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(V((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
CAMS={}
for view,c in S['cameras'].items():
 cd=bpy.data.cameras.new(view);o=bpy.data.objects.new(view,cd);sc.collection.objects.link(o);o.matrix_world=Matrix(c['world_matrix']);cd.type='ORTHO';cd.ortho_scale=c['ortho_scale'];CAMS[view]=o
# Pose and key every real bone densely; rigid detail surfaces remain genuinely weighted.
def apply(t,key=False):
 p,d,b=pose(t);m=matrices(p,d)
 for name,mat in m.items():
  pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=mat;bpy.context.view_layer.update()
  if key:
   for path in ['location','rotation_quaternion','scale']:pb.keyframe_insert(path,frame=1+39*t)
 gem.hide_render=t>=1-1e-8;gem.location=V((0,-.62,.075)) if t<=3/7 else p['right.grip']-V((0,0,.075))
 if key:
  gem.keyframe_insert('location',frame=1+39*t);gem.keyframe_insert('hide_render',frame=1+39*t)
 bpy.context.view_layer.update();return p,d,b
for t in sorted(set([j/156 for j in range(157)]+[i/7 for i in range(8)])):apply(t,True)
for fc in gem.animation_data.action.fcurves:
 for kp in fc.keyframe_points:kp.interpolation='CONSTANT' if fc.data_path=='hide_render' else 'LINEAR'
for fc in rig.animation_data.action.fcurves:
 for kp in fc.keyframe_points:kp.interpolation='LINEAR'
apply(0)
# Actual evaluated bind vertices must equal original rest vertices.
bind_errors={}
for obj in ALL:
 ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 if len(me.vertices)==len(obj.data.vertices):
  error=max(((ev.matrix_world@v.co)-(obj.matrix_world@w.co)).length for v,w in zip(me.vertices,obj.data.vertices));bind_errors[obj.name]=error;assert error<1e-5,('bind deformation',obj.name,error)
 ev.to_mesh_clear()
sc.camera=CAMS['SW'];bpy.ops.wm.save_as_mainfile(filepath=str(P/'original-character.blend'))
# Each file is a direct physical-camera capture, not an image mirror or fitted pose.
mode='all' if '--all' in sys.argv else 'preview';jobs=[('key',i,i/7) for i in range(8)] if mode=='all' else [('preview',i,i/7) for i in [0,3]]
if mode=='all':jobs += [('dense',i,i/26) for i in range(27)]
rec=[]
for bank,i,t in jobs:
 p,d,b=apply(t);measure={};deps=bpy.context.evaluated_depsgraph_get()
 for o in ALL:
  ev=o.evaluated_get(deps);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];measure[o.name]=dict(vertices=len(pts),min_z=min(v.z for v in pts),max_z=max(v.z for v in pts));ev.to_mesh_clear()
 imgs={}
 for view,cam in CAMS.items():
  sc.camera=cam;folder=OUT/bank/view;folder.mkdir(parents=True,exist_ok=True);path=folder/f'{i:02}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);imgs[view]=dict(path=str(path.relative_to(P)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 rec.append(dict(bank=bank,index=i,t=t,depth=d,bend_degrees=b,world_points={k:list(v) for k,v in p.items()},object_center=list(gem.location),object_visible=not gem.hide_render,bone_matrices={k:[list(row) for row in rig.pose.bones[k].matrix] for k in BM},mesh_measurements=measure,views=imgs))
receipt=dict(method='LOCAL PROCEDURAL ORIGINAL CHARACTER / full bone-weighted geometry / physically rendered eight views',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256=hashlib.sha256((PRIOR/'source/source.json').read_bytes()).hexdigest(),bind_vertex_errors=bind_errors,provider_calls=0,credits=0,slots=['body_outfit','complete_head'],objects=[dict(name=o.name,slot=o['runtime_slot'],vertices=len(o.data.vertices),groups=[v.name for v in o.vertex_groups],armature=next(m.object.name for m in o.modifiers if m.type=='ARMATURE')) for o in ALL],frames=rec,production_pass=False)
(P/('receipt.json' if mode=='all' else 'preview-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');print('FREE_LOCAL_CHARACTER_RENDERED',mode,len(rec)*8)
