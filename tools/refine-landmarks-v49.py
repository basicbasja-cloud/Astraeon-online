"""Concept-led fountain sculpture and genuinely recessed Hall side bays.

Repeatable source pass after terrace/bank/falls. Keeps placement roots and
service entrances; all added geometry is authored in Blender.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('terrace_version')==49 or scene.get('concept_architecture_version')==49
PREFIX='landmark-v49-'
for o in list(bpy.data.objects):
 if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
for d in list(bpy.data.meshes):
 if d.name.startswith(PREFIX) and not d.users:bpy.data.meshes.remove(d)
owner=None;root=None
def mesh(name,vs,fs,mat,role='decorative',shadow=True):
 inv=root.matrix_world.inverted();d=bpy.data.meshes.new(PREFIX+name)
 d.from_pydata([inv@Vector(v) for v in vs],[],fs)
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 d.materials.append(bpy.data.materials[mat]);d.uv_layers.new(name='PhysicalUV')
 for f in d.polygons:
  for li in f.loop_indices:
   p=Vector(vs[d.loops[li].vertex_index]);n=f.normal
   d.uv_layers.active.data[li].uv=(p.x/3,p.y/3) if abs(n.z)>.65 else (p.y/3,p.z/3) if abs(n.x)>.65 else (p.x/3,p.z/3)
 o=bpy.data.objects.new(PREFIX+name,d);owner.objects.link(o);o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o['role']=role;o['shadow']=shadow
 return o
def box(name,c,size,mat,role='decorative'):
 x,y,z=c;a,b,h=[v/2 for v in size]
 return mesh(name,[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role)
def tube(name,a,b,r,mat,sides=10):
 a,b=Vector(a),Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,0,1)))
 if u.length<.01:u=Vector((1,0,0))
 u.normalize();w=v.cross(u).normalized()
 vs=[tuple(p+r*(math.cos(k*math.tau/sides)*u+math.sin(k*math.tau/sides)*w)) for p in (a,b) for k in range(sides)]
 return mesh(name,vs,[list(range(sides-1,-1,-1)),list(range(sides,2*sides))]+[[k,(k+1)%sides,(k+1)%sides+sides,k+sides] for k in range(sides)],mat)
def lathe(name,profile,mat,n=48,role='decorative',center=(54,51)):
 vs=[(center[0]+r*math.cos(k*math.tau/n),center[1]+r*math.sin(k*math.tau/n),z) for z,r in profile for k in range(n)]
 fs=[[j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k] for j in range(len(profile)-1) for k in range(n)]
 return mesh(name,vs,fs,mat,role)
owner=bpy.data.collections['astral-fountain'];root=bpy.data.objects['astral-fountain-placement'];owner['family']='civic'
for o in owner.objects:
 if o.type=='MESH' and not o.name.startswith(PREFIX):o['render_visible']=False;o['shadow']=False;o['role']='decorative'
# A substantial basin, with real rim thickness and an unobstructed paved apron.
lathe('basin-foot',[(0,0),(0,3.35),(.18,3.35),(.18,3.13),(.32,3.13),(.32,0)],'stoneLight',role='solid')
lathe('basin-rim',[(.32,3.03),(.42,3.18),(.85,3.18),(.94,3.28),(1.04,3.28),(1.04,2.87),(.90,2.87),(.42,2.87)],'cream')
lathe('basin-water',[(.69,0),(.69,2.88)],'water',role='decorative')
lathe('pedestal',[(.65,.80),(.86,.84),(1.05,.62),(2.20,.50),(2.35,.86),(2.59,.94),(2.72,.65),(3.10,.42)],'stoneLight',n=24)
lathe('upper-water',[(2.64,0),(2.64,.82)],'waterLight')
# Draped, volumetric celestial figure. Wings use overlapping tapered feathers,
# rather than the old paper triangles and disconnected sticks.
lathe('draped-robe',[(2.95,.68),(3.28,.61),(3.65,.52),(4.10,.38),(4.62,.28),(5.07,.39),(5.27,.34)],'cream',n=24)
lathe('neck',[(5.24,.15),(5.52,.15)],'stoneLight',n=16)
lathe('head',[(5.44,.08),(5.55,.24),(5.83,.29),(6.07,.20),(6.17,.05)],'cream',n=24)
for sign in (-1,1):
 tube('arm-upper-'+str(sign),(54+sign*.32,51,5.06),(54+sign*.73,51.08,5.31),.16,'cream')
 tube('arm-raised-'+str(sign),(54+sign*.73,51.08,5.31),(54+sign*.94,51.16,5.83),.13,'cream')
 for j in range(9):
  t=j/8;a=(54+sign*(.35+.16*t),50.81,4.86-.70*t);b=(54+sign*(1.06+1.22*t),50.81-.10*math.sin(t*math.pi),6.69-.85*t)
  axis=(Vector(b)-Vector(a)).normalized();normal=Vector((axis.z,0,-axis.x));vs=[]
  for t,width in [(0,.11),(.3,.18),(.75,.14),(1,.018)]:
   center=Vector(a).lerp(Vector(b),t)+normal*(.10*math.sin(t*math.pi))
   for k in range(8):vs.append(tuple(center+normal*(width*math.cos(k*math.tau/8))+Vector((0,.065*math.sin(k*math.tau/8),0))))
  fs=[list(range(7,-1,-1)),list(range(24,32))]+[[q*8+k,q*8+(k+1)%8,(q+1)*8+(k+1)%8,(q+1)*8+k] for q in range(3) for k in range(8)]
  mesh('feather-'+str((sign,j)),vs,fs,'cream' if j%3 else 'stoneLight')
for k in range(48):
 a,b=k*math.tau/48,(k+1)*math.tau/48
 tube('halo-'+str(k),(54+1.05*math.cos(a),50.78,6.14+1.05*math.sin(a)),(54+1.05*math.cos(b),50.78,6.14+1.05*math.sin(b)),.047,'gold',6)
for k in range(8):
 a=k*math.tau/8
 for j in range(12):
  u,v=j/12,(j+1)/12
  def jet(t):return (54+math.cos(a)*(.65+1.75*t),51+math.sin(a)*(.65+1.75*t),2.62+.44*t-2.35*t*t)
  tube('jet-'+str((k,j)),jet(u),jet(v),.034,'waterLight',6)
# Replace the Hall's filled side slabs with pierced walls; upper clerestory and
# lower aisle bays read from orbit as well as the ordinary gameplay camera.
owner=bpy.data.collections['guild-hall'];root=bpy.data.objects['guild-hall-placement']
def hall(p):
 x,y,z=p;return (54+(x-54)*1.8,21.35+(y-21.35)*1.12,.6075+(z-.6075)*2.0+1.4)
def side_mesh(name,vs,fs,mat,role='decorative'):return mesh(name,[hall(v) for v in vs],fs,mat,role)
def side_box(name,c,size,mat,role='decorative'):
 x,y,z=c;a,b,h=[v/2 for v in size]
 return side_mesh(name,[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role)
# Buttresses must flank window bays, not occupy their centers. Shift their
# saved meshes (and each matching flying arch) to the pier axes, repeatably.
import ast
for o in owner.objects:
 if not o.name.startswith(('concept-v49-side-buttress-','concept-v49-flying-arch-')):continue
 suffix=o.name[o.name.index('('):];index=ast.literal_eval(suffix)[1]
 target=hall((54,[12.65,15.75,18.85][index],0))[1]
 center=sum((o.matrix_world@v.co).y for v in o.data.vertices)/len(o.data.vertices)
 o.location+=root.matrix_world.inverted().to_3x3()@Vector((0,target-center,0))
bpy.context.view_layer.update()
for sign in (-1,1):
 for family,x,z0,z1,w0,w1,bottom,h,width in [('nave',54+sign*4.2,.60,9.3,10.6,21.4,6.35,2.30,1.10),('aisle',54+sign*8.025,.60,5.9,12.8,22.4,1.6,3.25,1.32)]:
  old=bpy.data.objects.get('concept-v49-'+('nave-side-' if family=='nave' else 'aisle-outer-')+str(sign))
  if old:old['render_visible']=False;old['shadow']=False;old['role']='decorative'
  centers=[14.2,17.3,20.4];last=w0
  for j,cy in enumerate(centers):
   lo,hi=cy-width/2,cy+width/2;stem=h*.60;rise=h*.40;tag=family+'-'+str((sign,j));xf=x+sign*.25
   side_box(tag+'-pier',(x,(last+lo)/2,(z0+z1)/2),(.40,lo-last,z1-z0),'civicIvory','solid');last=hi
   side_box(tag+'-base',(x,cy,(z0+bottom)/2),(.40,width,bottom-z0),'civicIvory','solid')
   side_box(tag+'-top',(x,cy,(bottom+h+z1)/2),(.40,width,z1-bottom-h),'civicIvory','solid')
   poly=[(xf-sign*.36,lo,bottom),(xf-sign*.36,hi,bottom)]+[(xf-sign*.36,cy+math.cos(k*math.pi/16)*width/2,bottom+stem+math.sin(k*math.pi/16)*rise) for k in range(17)]
   side_mesh(tag+'-glass',poly,[list(range(len(poly)))],'civicGlass')
   for k in range(16):
    a,b=k*math.pi/16,(k+1)*math.pi/16
    arc=[(cy+math.cos(t)*r,bottom+stem+math.sin(t)*hh) for t,r,hh in [(a,width/2,rise),(b,width/2,rise),(b,width/2+.17,rise+.17),(a,width/2+.17,rise+.17)]]
    vs=[(xx,yy,zz) for xx in (xf-sign*.05,xf+sign*.22) for yy,zz in arc]
    side_mesh(tag+'-arch-'+str(k),vs,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'civicIvory')
    sp=[(x,cy+math.cos(a)*width/2,bottom+stem+math.sin(a)*rise),(x,cy+math.cos(b)*width/2,bottom+stem+math.sin(b)*rise),(x,cy+math.cos(b)*width/2,bottom+h),(x,cy+math.cos(a)*width/2,bottom+h)]
    side_mesh(tag+'-spandrel-'+str(k),sp,[[0,1,2,3]],'civicIvory')
   for s in (-1,1):side_box(tag+'-jamb-'+str(s),(xf,cy+s*(width/2+.085),bottom+stem/2),(.52,.17,stem),'civicIvory')
   side_box(tag+'-mullion',(xf-sign*.12,cy,bottom+h/2),(.08,.07,h-.08),'civicGold')
   side_box(tag+'-sill',(xf,cy,bottom-.10),(.65,width+.5,.20),'civicShadow')
  side_box(family+'-last-pier-'+str(sign),(x,(last+w1)/2,(z0+z1)/2),(.40,w1-last,z1-z0),'civicIvory','solid')
scene['landmark_refinement_version']=49
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
print('Saved monumental celestial basin and pierced Hall clerestory/aisle side bays')
