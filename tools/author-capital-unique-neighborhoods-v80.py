"""Original structural house variants and irregular owned garden tree groups.
Saved native work only; collision cores, entries, ground uses and old shelters
are retained. Four genuinely different roof/massing systems replace upper
assemblies on twelve selected new houses, rather than re-skinning duplicates.
"""
import bpy,bmesh,json,math,runpy,hashlib,gc
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v80/unique-neighborhoods';s=bpy.context.scene
assert not s.get('capital_unique_neighborhoods_v80'),'Already applied'
p=json.loads((O/'plan.json').read_text());assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==p['beforeSourceSHA256']
exp=runpy.run_path(str(R/'tools/export-world-v3.py'));before=exp['export'](s)
Kit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];basic=runpy.run_path(str(R/'tools/capital-architecture-kit-v76.py'))['roof']
def invariant(a):
 return {'terrain':a['terrain'],'navigation':a['navigation'],'spawn':a['spawn'],'route':a['route'],'owners':[{k:v for k,v in o.items() if k!='parts'} for o in a['objects']], 'solids':[(o['id'],q) for o in a['objects'] for q in o['parts'] if q['role']=='solid'], 'doors':[(o['id'],q) for o in a['objects'] for q in o['parts'] if q['id'].endswith('-door-leaf')]}
original=invariant(before);beforetri=sum(len(f)-2 for o in before['objects'] for a in o['parts'] if a.get('visible',True) for f in a['faces']);del before;gc.collect()
removed=[]
def erase_upper(c,r):
 for o in list(c.objects):
  if o.type!='MESH' or o.get('role')=='solid' or o.name.startswith('capital-v78-') or '-door-' in o.name:continue
  transform=r.matrix_world.inverted()@o.matrix_world
  if o.get('component_count'):
   chosen=[];sets=[]
   for g in o.vertex_groups:
    indices={v.index for v in o.data.vertices if any(a.group==g.index for a in v.groups)}
    if not indices or '-door-' in g.name:continue
    if min((transform@o.data.vertices[j].co).z for j in indices)>=2.985:
     chosen.append(g);sets.append(indices);removed.append({'owner':c.name,'component':g.name})
   if not chosen:continue
   doomed=[f.index for f in o.data.polygons if any(set(f.vertices).issubset(a) for a in sets)]
   bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in doomed],context='FACES_ONLY');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(o.data);bm.free()
   for g in chosen:o.vertex_groups.remove(g)
   o['component_count']=len(o.vertex_groups)
   if not o.data.polygons:bpy.data.objects.remove(o,do_unlink=True)
  elif min((transform@v.co).z for v in o.data.vertices)>=2.985:
   removed.append({'owner':c.name,'component':o.name});bpy.data.objects.remove(o,do_unlink=True)
def roof(k,n,x,y,w,d,eave,rise,mat,kind='gable',along=False):
 before=set(k.owner.objects);peak=basic(k,n,x,y,w,d,eave,rise,mat,kind,along)
 for o in set(k.owner.objects)-before:
  if o.get('role')=='overhead':
   for a in o.data.uv_layers.active.data:a.uv*=2.4/3.4
 return peak
def mass(k,n,x,y,w,d,top,mat):
 for face,width,origin,angle in [('front',w,(x,y+d/2+.10),0),('back',w,(x,y-d/2-.08),math.pi),('west',d,(x-w/2-.05,y),math.pi/2),('east',d,(x+w/2+.05,y),-math.pi/2)]:
  bays=max(1,min(4,int(width/1.9)));cs=[(j-(bays-1)/2)*width/(bays+.6) for j in range(bays)]
  k.upper_face(n+'-'+face,width,3.10,top,cs,mat,origin,angle,wh=min(1.48,(top-3.1)*.59),ww=min(1.15,width/(bays+.6)-.3))
 # Keep a solid visual ceiling under roof edges; the original low core remains.
 k.box(n+'-ceiling',(x,y,top-.03),(w,d,.10),mat)
def dormer(k,n,x,y,z,w,clay):
 # Pierced front opening plus actual side walls and a separate clay cap.
 k.upper_face(n+'-face',w,z,z+1.25,[0],'homeLimewash',(x,y),0,wh=.75,ww=min(.75,w-.45))
 for side in (-1,1):k.box(n+'-side-'+str(side),(x+side*w/2,y-.46,z+.6),(.16,.92,1.2),'homeLimewash')
 roof(k,n,x,y-.42,w+.24,1.2,z+1.28,.65,clay)
def gambrel(k,n,w,d,eave,clay):
 # Two slopes with a steep lower break and shallow crown: different from hips
 # or a single triangular extrusion. Ridge runs across the merchant frontage.
 a,b=w/2+.23,d/2+.28;inset=b*.45;mid=eave+1.8;peak=eave+2.65
 verts=[(-a,-b,eave),(a,-b,eave),(a,b,eave),(-a,b,eave),(-a,-inset,mid),(a,-inset,mid),(a,inset,mid),(-a,inset,mid),(-a,0,peak),(a,0,peak)]
 o=k.mesh(n+'-broken-roof',verts,[[0,1,5,4],[4,5,9,8],[8,9,6,7],[7,6,2,3]],clay);o['role']='overhead'
 for f in o.data.polygons:
  u=Vector((1,0,0));v=f.normal.cross(u).normalized()
  for li in f.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(q.dot(u)/3.4,q.dot(v)/3.4)
 for side in (-1,1):
  xx=side*a;pts=[(xx,-b,eave),(xx,b,eave),(xx,inset,mid),(xx,0,peak),(xx,-inset,mid)]
  k.mesh(n+'-end-'+str(side),pts,[[0,1,2,3,4]],'homeLimewash')
  for j in range(4):k.beam(n+'-rake-'+str((side,j)),pts[j],pts[(j+1)%5],.13)
 for yy in (-b,b):k.beam(n+'-eaves-'+str(yy),(-a,yy,eave),(a,yy,eave),.16)
 return peak
records=[]
for spec in p['houses']:
 c=bpy.data.collections[spec['id']];r=next(o for o in c.objects if o.type=='EMPTY' and not o.parent);erase_upper(c,r)
 k=Kit(c,r);k.prefix='capital-v80-';w,d=spec['width'],spec['depth'];v=spec['variation'];kind=spec['design'];clay=spec['clay'];mat={'residential':'homeLimewash','market':'merchantLimewash','workshop':'workshopLimewash'}[spec['family']]
 if kind=='stepped-gables':
  main=w*(.59+v*.15);side=w-main;left=-side/2;right=main/2;top=6.4+v
  mass(k,'main-wing',left,0,main,d,top,mat);mass(k,'lower-wing',right,0,side,d,4.25-v,mat)
  peak=roof(k,'main-wing',left,0,main+.32,d+.42,top+.14,main*.61,clay)
  roof(k,'lower-wing',right,0,side+.26,d+.4,4.4-v,min(side*1.1,1.9),clay,'hip',True)
  # Physical corbels and a single diagonal panel distinguish the tall wing.
  for xx in (left-main*.34,left+main*.34):k.beam('wing-corbel-'+str(xx),(xx,d/2-.05,2.8),(xx,d/2+.19,3.24),.14)
  k.beam('wing-diagonal',(left-main*.38,d/2+.25,5.65),(left-main*.12,d/2+.25,6.15),.10)
 elif kind=='garden-cottage':
  top=4.6+v;mass(k,'low-home',0,0,w,d,top,mat);peak=roof(k,'long-cottage',0,0,w+.4,d+.4,top+.14,2.05,clay,along=True)
  dormer(k,'single-dormer',-w*.18,d/2-.25,top+.42,min(1.8,w*.4),clay)
  k.box('cottage-shutter',(w*.27,d/2+.24,3.86),(.35,.12,.92),'oak')
 elif kind=='dormered-gambrel':
  top=5.2+v;mass(k,'trade-home',0,0,w,d,top,mat);peak=gambrel(k,'merchant-crown',w,d,top+.16,clay)
  number=3 if w>8 else 1
  for j in range(number):dormer(k,'dormer-'+str(j),(j-(number-1)/2)*w*.27,max(d/2-.25,(d/2+.28)*.8+.22),top+.55,min(1.65,w*.35),clay)
  k.box('trade-belt',(0,d/2+.23,3.18),(w,.20,.20),'stoneLight')
 else:
  top=5.8+v;mass(k,'corner-home',0,0,w,d,top,mat);peak=roof(k,'low-hip',0,-.04,w+.4,d+.4,top+.16,2.0,clay,'hip',True)
  # Glazed octagonal upper corner, physically supported above retained ground.
  rad=min(.84,w*.19);cx=w/2-rad*.95;cy=d/2-rad*.55;base=3.32;cap=6.65+v;ring=[(cx+rad*math.cos(math.tau*j/8+math.pi/8),cy+rad*math.sin(math.tau*j/8+math.pi/8)) for j in range(8)]
  for j,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
   width=math.dist(a,b);k.upper_face('oriel-face-'+str(j),width,base,cap,[0],mat,((a[0]+b[0])/2,(a[1]+b[1])/2),math.atan2(b[1]-a[1],b[0]-a[0]),wh=1.25,ww=width-.22)
  verts=[(x,y,cap+.08) for x,y in ring]+[(cx,cy,cap+1.75)];o=k.mesh('octagonal-oriel-roof',verts,[[j,(j+1)%8,8] for j in range(8)],clay);o['role']='overhead'
  k.box('oriel-soffit',(cx,cy,base-.03),(rad*1.75,rad*1.75,.18),'oak')
  for xx in (cx-rad*.55,cx+rad*.55):k.beam('oriel-brace-'+str(xx),(xx,d/2-.15,2.78),(xx,cy+.40,3.3),.13)
  peak=max(peak,cap+1.75)
 # Different chimney position and a broad light stone cap; no added atlas.
 xx=-w*.3;yy=-d*.26;bottom=3.14;end=peak+.36;k.box('chimney',(xx,yy,(bottom+end)/2),(.43,.49,end-bottom),'stoneLight');k.box('chimney-cap',(xx,yy,end+.08),(.62,.68,.16),'stoneLight');k.box('chimney-dark-mouth',(xx,yy,end+.165),(.31,.37,.012),'iron',False)
 c['unique_massing_v80']=kind;c['unique_massing_variation_v80']=v
 records.append({'id':c.name,'design':kind,'roofPeakLocal':peak,'doorCoreAndExistingShelterRetained':True})
print('Authored',len(records),'structural houses',flush=True)
# Clone original full-detail bough topology/UVs, with natural crown profiles and
# asymmetric groups at approved real planted contacts; no texture resolution cut.
source=bpy.data.collections['capital-tree-008'];visible=[o for o in source.objects if o.type=='MESH' and o.get('render_visible',True)];stem=next(o for o in visible if o.get('role')=='solid');pts=[stem.matrix_world@v.co for v in stem.data.vertices];center=Vector(((min(v.x for v in pts)+max(v.x for v in pts))/2,(min(v.y for v in pts)+max(v.y for v in pts))/2,min(v.z for v in pts)));height=max((o.matrix_world@v.co).z-center.z for o in visible for v in o.data.vertices)
for a in p['trees']:
 c=bpy.data.collections.new(a['id']);c['family']='vegetation';s.collection.children.link(c);c['natural_group_zone']=a['zone'];q=Vector(a['position']);q.z-=.015;scale=a['height']/height
 transform=Matrix.Translation(q)@Matrix.Rotation(a['rotation'],4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-center)
 for index,original_mesh in enumerate(visible):
  o=original_mesh.copy();o.data=original_mesh.data.copy();o.name=a['id']+'-'+str(index);o.parent=None;o.matrix_world=Matrix.Identity(4)
  for vert in o.data.vertices:vert.co=transform@(original_mesh.matrix_world@vert.co)
  if o.data.materials[0].name.startswith('conifer70'):
   points=list(o.data.vertices);assert len(points)%9==0
   for start in range(0,len(points),9):
    group=points[start:start+9];h=group[0].co.z-q.z;t=max(0,min(1,(h/a['height']-.31)/.69));oldrad=max(math.hypot(v.co.x-q.x,v.co.y-q.y) for v in group)
    shape=max(0,math.sin(math.pi*t))**(.65 if a['crown']=='rounded' else .85)
    desired=a['radiusBudget']*(.035+.91*shape+.08*(1-t)**4);factor=desired/oldrad
    for vert in group:vert.co.x=q.x+(vert.co.x-q.x)*factor;vert.co.y=q.y+(vert.co.y-q.y)*factor
   o['painted_crown_v80']=True
  layer=o.data.color_attributes.get('BakedTownLight')
  if layer:o.data.color_attributes.remove(layer)
  o.data.update();c.objects.link(o)
bpy.context.view_layer.update();after=exp['export'](s);newinv=invariant(after)
assert original['terrain']==newinv['terrain'] and original['navigation']==newinv['navigation'] and original['spawn']==newinv['spawn'] and original['route']==newinv['route']
oldids={a['id'] for a in original['owners']};assert [a for a in newinv['owners'] if a['id'] in oldids]==original['owners']
assert [a for a in newinv['solids'] if a[0] in oldids]==original['solids'] and newinv['doors']==original['doors']
tri=sum(len(f)-2 for o in after['objects'] for a in o['parts'] if a.get('visible',True) for f in a['faces']);treeids={a['id'] for a in p['trees']};treetri=sum(len(f)-2 for o in after['objects'] if o['id'] in treeids for a in o['parts'] for f in a['faces']);assert tri-beforetri<p['triangleBudget'] and treetri<p['treeTriangleBudget']
city=json.loads(s['capital_plan_json']);city['uniqueNeighborhoodRefinement']={'revision':80,'houses':records,'trees':p['trees'],'treeOwners':sorted(treeids),'placementPolicy':p['placementPolicy']};s['capital_plan_json']=json.dumps(city);s['capital_unique_neighborhoods_v80']=1;s['ground_shadow_asset']='assets/wayfarer-ground-shadow-v80-neighborhoods.png'
for f in ('plan.json','native-plan.json'):(O.parent/f).write_text(json.dumps(city,indent=2)+'\n')
(O/'authoring.json').write_text(json.dumps({'beforeSourceSHA256':p['beforeSourceSHA256'],'houses':records,'removedUpperComponents':removed,'newTreeOwners':sorted(treeids),'netAddedVisibleTriangles':tri-beforetri,'newTreeTriangles':treetri,'originalSolidDoorTerrainNavigationGameplayExact':True,'nativeResolutionAndOriginalImagesRetained':True,'visualAcceptance':'Pending normal paired gameplay comparison'},indent=2)+'\n')
del after,original,newinv;gc.collect();bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__');print('PASS saved12 distinct structural homes and',len(treeids),'natural garden trees; net triangles',tri-beforetri,flush=True)
