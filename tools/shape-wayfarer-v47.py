"""Sculpt street boundaries, roofs, facades and planted courts in the saved scene.
The concept supplies hierarchy and atmosphere; exact geometry serves traversal.
Run once after the v46 source pass. No complete building is duplicated.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('architectural_quality_version')==46 and not scene.get('organic_town_version')
owner=None;root=None
def mesh(name,vs,fs,mat,role='decorative',shadow=True):
 data=bpy.data.meshes.new('organic-v47-'+name);data.from_pydata(vs,[],fs)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='PhysicalUV')
 o=bpy.data.objects.new('organic-v47-'+name,data);owner.objects.link(o);o['role']=role;o['shadow']=shadow
 if root:o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4)
 world=root.matrix_world.copy() if root else Matrix.Identity(4);size=json.loads(bpy.data.materials[mat].get('texture_json','{}')).get('worldSize',3)
 for f in data.polygons:
  n=(world.to_3x3()@f.normal).normalized()
  for li in f.loop_indices:
   p=world@data.vertices[data.loops[li].vertex_index].co
   uv=(p.y/size,p.x/size) if any(t in mat.lower() for t in ['slate','roof','terracotta']) else (p.x/size,p.y/size) if abs(n.z)>.65 else (p.x/size,p.z/size) if abs(n.y)>abs(n.x) else (p.y/size,p.z/size)
   data.uv_layers.active.data[li].uv=uv
 return o
def box(name,c,size,mat,role='decorative',shadow=True):
 x,y,z=c;a,b,h=[v/2 for v in size]
 return mesh(name,[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role,shadow)
def beam(name,a,b,width,mat):
 a,b=Vector(a),Vector(b);direction=(b-a).normalized();cross=direction.cross(Vector((0,1,0))).normalized()*width/2;other=direction.cross(cross).normalized()*width/2
 return mesh(name,[tuple(p+u*cross+v*other) for p in (a,b) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat)
def arch(name,c,width,spring,rise,depth,mat,axis='y'):
 x,y,z=c;steps=12;thick=.16
 for k in range(steps):
  a,b=k*math.pi/steps,(k+1)*math.pi/steps
  points=[(-math.cos(t)*r,spring+math.sin(t)*(rise+rr)) for r,rr,t in [(width/2,0,a),(width/2,0,b),(width/2+thick,thick,b),(width/2+thick,thick,a)]]
  vs=[(x+px,y+off,z+pz) if axis=='y' else (x+off,y+px,z+pz) for off in (-depth/2,depth/2) for px,pz in points]
  mesh(name+'-'+str(k),vs,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat)

# Irregular civic court, with narrow crossings and neighbourhood streets that
# bend gently between their existing usable frontages.
terrain=bpy.data.collections['court-terrain'];owner=terrain
old=bpy.data.objects['plan-v44-central-square'];bpy.data.objects.remove(old,do_unlink=True)
outline=[(43.4,47.8),(44.8,44.4),(49.1,42.2),(56.4,42.5),(61.4,44.0),(64.7,48.2),(64.1,54.6),(61.4,58.9),(56.9,60.5),(50.2,60.1),(45.3,57.6),(42.9,53.6)]
o=mesh('civic-court',[(x,y,.049) for x,y in outline],[list(range(len(outline)))],'paving',shadow=False);o['surface_role']='plaza';o['walkable']=True
roads=[o for o in terrain.objects if o.get('road_segment') and o.name.startswith('plan-')]
for index,o in enumerate(roads):
 # Each prior straight corridor is replaced by several individually authored
 # strips. Their bounded bend remains inside the established building setbacks.
 vs=[o.matrix_world@v.co for v in o.data.vertices];a=(vs[0]+vs[3])/2;b=(vs[1]+vs[2])/2;delta=b-a;length=delta.length;n=Vector((-delta.y,delta.x,0)).normalized();width=(vs[0]-vs[3]).length
 if length<9:continue
 amplitude=.56 if width>=7 else .30
 steps=max(4,math.ceil(length/3));left=[];right=[]
 for i in range(steps+1):
  t=i/steps;center=a+delta*t+n*(amplitude*math.sin(math.pi*t)*math.sin(math.pi*t+.55+index*.3));half=width/2*(1+.022*math.sin(t*math.tau+index))
  left.append(center+n*half);right.append(center-n*half)
 name=o.name;role=o['surface_role'];legacy=o['legacy_role'];bpy.data.objects.remove(o,do_unlink=True)
 for j in range(steps):
  strip=mesh(name+'-'+str(j),[tuple(left[j]),tuple(left[j+1]),tuple(right[j+1]),tuple(right[j])],[[0,1,2,3]],'paving',shadow=False)
  strip['surface_role']=role;strip['walkable']=True;strip['road_segment']=True;strip['legacy_role']=legacy

# Individual roof profiles and projecting upper storeys break the identical
# rectangular shells. Existing door approaches and ground solids stay intact.
for index,c in enumerate(sorted([c for c in bpy.data.collections if c.name.startswith('frontage-')],key=lambda c:c.name)):
 owner=c;root=bpy.data.objects[c.name+'-placement'];walls=next(o for o in c.objects if o.name.endswith('-walls'));inv=root.matrix_world.inverted();vs=[inv@walls.matrix_world@v.co for v in walls.data.vertices]
 x0,x1=min(v.x for v in vs),max(v.x for v in vs);y0,y1=min(v.y for v in vs),max(v.y for v in vs);w,d=x1-x0,y1-y0;h=max(v.z for v in vs);x,y=(x0+x1)/2,(y0+y1)/2
 original=[o for o in c.objects if o.name.startswith('plan-v44-') and ('-roof-' in o.name or o.name.endswith('-gable'))]
 peak=max((inv@o.matrix_world@v.co).z for o in original for v in o.data.vertices)+(.25 if index%3==0 else .05)
 for o in original:o['render_visible']=False;o['shadow']=False
 mat='slate' if index%3==0 else 'terracotta';ridge=x+(.10*w if index%4==1 else -.07*w if index%4==3 else 0);eave=h+.28
 front=[]
 for side in (-1,1):
  xx=x+side*(w/2+.5);profile=[]
  for j in range(5):
   t=j/4;px=xx+(ridge-xx)*t;pz=eave+(peak-eave)*(t**(1.1 if index%2 else .93))-.09*math.sin(math.pi*t)
   profile.append((px,pz))
  for j,((a,za),(b,zb)) in enumerate(zip(profile,profile[1:])):
   mesh(c.name+'-curved-roof-'+str(side)+'-'+str(j),[(a,y0-.5,za),(a,y1+.61,za),(b,y1+.61,zb),(b,y0-.5,zb)],[[0,1,2,3]],mat,'overhead')
   beam(c.name+'-verge-'+str(side)+'-'+str(j),(a,y1+.66,za),(b,y1+.66,zb),.15,'timber')
  front.extend(profile if side==-1 else list(reversed(profile[:-1])))
  box(c.name+'-deep-eave'+str(side),(xx,y,eave-.08),(.2,d+1.1,.23),'timber')
 mesh(c.name+'-shaped-gable',[(px,y1+.54,pz) for px,pz in front],[list(range(len(front)))],'plaster',shadow=False)
 beam(c.name+'-gable-kingpost',(ridge,y1+.69,eave),(ridge,y1+.69,peak-.1),.15,'timber')
 for side in (-1,1):beam(c.name+'-gable-brace'+str(side),(x+side*w*.34,y1+.68,eave+.10),(ridge,y1+.68,peak-.7),.11,'timber')
 box(c.name+'-upper-jetty',(x,y+.045,h*.76),(w+.23,d+.24,h*.47),'plaster','overhead')
 box(c.name+'-jetty-belt',(x,y1+.22,h*.53),(w+.33,.20,.20),'timber')
 for side in (-1,1):box(c.name+'-jetty-corner'+str(side),(x+side*(w/2+.12),y1+.2,h*.76),(.16,.17,h*.5),'timber')
 # Bring upper glazing to the new facade, preserving source registration.
 for o in list(c.objects):
  if not o.name.startswith('plan-v44-') or not any(k in o.name for k in ('window','shutter','sill')):continue
  p=sum((inv@o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
  if p.z>h*.52:
   o.matrix_basis.translation+=Vector((0,.19,0))
 # Curved entrance lintels and deep outer jambs vary by shop/home family.
 arch(c.name+'-door-arch',(x,y1+.18,0),1.12,1.95,.44,.22,'stoneLight' if index%3==0 else 'timber')
 for side in (-1,1):box(c.name+'-door-jamb'+str(side),(x+side*.64,y1+.18,1.0),(.15,.22,1.95),'stoneLight' if index%3==0 else 'timber')

# Real stone arches give the public loggias a civic identity instead of sheds.
owner=bpy.data.collections['consortium-forecourt-arcades'];root=None
for side in (-1,1):
 x=54+side*7.6
 arch('loggia-front'+str(side),(x,38.7,0),2.42,1.95,1.18,.25,'stoneLight')
 for y in (32.5,35.0,37.5):arch('loggia-side'+str(side)+'-'+str(y),(x-side*1.3,y,0),2.15,2.0,1.08,.20,'stoneLight','x')

# Replace checkerboard flower cubes with low, irregular planted beds.
owner=bpy.data.collections['wayfarer-civic-gardens'];root=None
for i in range(5):
 bed=bpy.data.objects.get('garden-v4-flowerbed-'+str(i))
 if not bed:continue
 vs=[bed.matrix_world@v.co for v in bed.data.vertices];cx=(min(v.x for v in vs)+max(v.x for v in vs))/2;cy=(min(v.y for v in vs)+max(v.y for v in vs))/2;w=max(v.x for v in vs)-min(v.x for v in vs);d=max(v.y for v in vs)-min(v.y for v in vs)
 for o in owner.objects:
  if o.name.startswith('garden-v4-flowerbed-'+str(i)):o['render_visible']=False;o['shadow']=False;o['role']='decorative'
 points=[]
 for k in range(20):
  a=k*math.tau/20;cs,sn=math.cos(a),math.sin(a);r=1+.055*math.sin(k*2.17+i)
  points.append((cx+math.copysign(abs(cs)**.65,cs)*w*.47*r,cy+math.copysign(abs(sn)**.65,sn)*d*.46*r,.16))
 mesh('bed-'+str(i),points,[list(range(20))],'soil',shadow=False)
 # Loose layered foliage mounds carry clusters, rather than a grid of cubes.
 for j in range(7):
  a=j*2.399;xx=cx+math.cos(a)*w*.30*(.5+j/14);yy=cy+math.sin(a)*d*.30*(.5+j/14);r=.33+.07*(j%3)
  vv=[(xx,yy,.68)]+[(xx+math.cos(k*math.tau/9)*r,yy+math.sin(k*math.tau/9)*r,.23+.05*math.sin(k+j)) for k in range(9)]
  mesh('bed-shrub-'+str(i)+'-'+str(j),vv,[[0,k+1,(k+1)%9+1] for k in range(9)],'leaf' if j%2 else 'leafLight',shadow=False)
  for f in range(3):
   fx=xx+.14*math.cos(f*2.7+j);fy=yy+.14*math.sin(f*2.7+j);z=.69+.07*(f%2)
   vv=[(fx,fy,z+.025)]+[(fx+.12*(1 if k%2==0 else .56)*math.cos(k*math.tau/10),fy+.12*(1 if k%2==0 else .56)*math.sin(k*math.tau/10),z) for k in range(10)]
   mesh('bed-petal-'+str(i)+'-'+str(j)+'-'+str(f),vv,[[0,k+1,(k+1)%10+1] for k in range(10)],'flowerRose' if (i+j)%3 else 'flowerIvory',shadow=False)

scene['organic_town_version']=47;scene['layout_id']='wayfarer-painterly-civic-town-v47'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved sculpted roofs, projecting facades, civic arches, irregular court, gently bent lanes and planted beds')
