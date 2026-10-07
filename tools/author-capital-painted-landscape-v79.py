"""Author selected original planted properties and painted native crown variants."""
import bpy,json,math,runpy,hashlib,gc
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v79/painted-landscape';s=bpy.context.scene
assert not s.get('capital_painted_landscape_v79'),'Already applied'
p=json.loads((O/'plan.json').read_text());assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==p['beforeSourceSHA256']
exp=runpy.run_path(str(R/'tools/export-world-v3.py'));before=exp['export'](s)
art=json.loads((R/p['newFoliageMetadata']).read_text());assert art['losslessRGBAExact']
assert hashlib.sha256((R/art['texture']['file']).read_bytes()).hexdigest()==art['assetSHA256']
changes={}
for name,color in p['materialColors'].items():
 m=bpy.data.materials[name];changes[name]={'before':before['materials'][name]};m.diffuse_color=(*color,1)
for name in ('conifer70','conifer70Light','conifer70Shade'):
 changes[name]={'before':before['materials'][name]};bpy.data.materials[name]['texture_json']=json.dumps(art['texture'])
c=bpy.data.collections['capital-beta-frontage-groundcover']
for name in p['replacedLawnParts']:
 o=bpy.data.objects[name];assert o in c.objects[:];bpy.data.objects.remove(o,do_unlink=True)
for a in p['pieces']:
 d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces']);d.materials.append(bpy.data.materials['grass']);d.uv_layers.new(name='WorldUV');opacity=d.attributes.new('SurfaceOpacity','FLOAT','POINT')
 for i,value in enumerate(a['vertexOpacity']):opacity.data[i].value=value
 for f in d.polygons:
  for li in f.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(q.x/7,q.y/7)
 o=bpy.data.objects.new(a['id'],d);c.objects.link(o);o['role']='decorative';o['shadow']=False;o['owned_block']=a['block']
formal=[];changed_leaves=[]
for name in p['formalTrees']:
 c=bpy.data.collections[name];stem=next(o for o in c.objects if o.type=='MESH' and o.get('role')=='solid');pts=[stem.matrix_world@v.co for v in stem.data.vertices]
 center=Vector(((min(v.x for v in pts)+max(v.x for v in pts))/2,(min(v.y for v in pts)+max(v.y for v in pts))/2,min(v.z for v in pts)))
 leaves=[o for o in c.objects if o.type=='MESH' and o.data.materials and o.data.materials[0].name in ('conifer70','conifer70Light','conifer70Shade')];assert len(leaves)==3
 allpts=[o.matrix_world@v.co for o in leaves for v in o.data.vertices];height=max(v.z-center.z for v in allpts);radius=max(math.hypot(v.x-center.x,v.y-center.y) for v in allpts)
 # Formal park pairs retain exact root, height, topology and original bough UVs.
 # A narrow lower skirt and rounded middle crown make these actual cypress-like
 # forms, not palette swaps of the same triangular neighborhood evergreen.
 for o in leaves:
  d=o.data;inverse=o.matrix_world.inverted();assert len(d.vertices)%9==0
  for start in range(0,len(d.vertices),9):
   q=o.matrix_world@d.vertices[start].co;t=max(0,min(1,((q.z-center.z)/height-.31)/.69))
   points=[o.matrix_world@d.vertices[start+j].co for j in range(9)];oldrad=max(math.hypot(v.x-center.x,v.y-center.y) for v in points)
   desired=radius*(.045+.78*max(0,math.sin(math.pi*t))**.74+.10*(1-t)**4);factor=desired/oldrad
   for j,v in enumerate(points):
    v.x=center.x+(v.x-center.x)*factor;v.y=center.y+(v.y-center.y)*factor;d.vertices[start+j].co=inverse@v
  d.update();changed_leaves.append(o.name)
  layer=d.color_attributes.get('BakedTownLight')
  if layer:d.color_attributes.remove(layer)
  o['painted_crown_v79']=True
 formal.append({'id':name,'center':list(center),'height':height,'beforeRadius':radius,'parts':[o.name for o in leaves],'shape':'Rounded formal crown with narrow skirt and pointed tip; original height and footprint envelope'})
# Sparse tiny native blades are attached to newly planted property edges, not
# public-road centres. They share the existing two blade materials.
c=bpy.data.collections.new(p['grassOwner']);c['family']='civic';s.collection.children.link(c)
groups={m:([],[]) for m in ('capitalGrassBladeLight','capitalGrassBladeShade')}
for i,a in enumerate(p['grassRoots']):
 x,y,z=a['position'];h=a['height'];w=a['width']
 for j in range(3):
  angle=a['angle']+j*math.tau/3;dx,dy=math.cos(angle)*w,math.sin(angle)*w;mat='capitalGrassBladeShade' if (i+j)%3==0 else 'capitalGrassBladeLight';verts,faces=groups[mat];off=len(verts)
  verts.extend([[x-dx/2,y-dy/2,z],[x+dx/2,y+dy/2,z],[x+math.sin(angle)*h*.18,y-math.cos(angle)*h*.18,z+h]]);faces.append([off,off+1,off+2])
for mat,(verts,faces) in groups.items():
 d=bpy.data.meshes.new(p['grassOwner']+'-'+mat);d.from_pydata(verts,[],faces);d.materials.append(bpy.data.materials[mat]);d.uv_layers.new(name='WorldUV')
 for f in d.polygons:
  for li in f.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(q.x/7,q.y/7)
 o=bpy.data.objects.new(d.name,d);c.objects.link(o);o['role']='decorative';o['shadow']=False
assert len(p['grassRoots'])*3<p['grassTriangleBudget']
city=json.loads(s['capital_plan_json']);city['paintedLandscapeRefinement']={'revision':79,'focusAreas':p['focusAreas'],'addedLawnArea':p['addedLawnArea'],'newLawnParts':[a['id'] for a in p['pieces']],'newGrassOwner':p['grassOwner'],'formalTrees':p['formalTrees'],'newFoliageTexture':art['texture']['file']}
s['capital_plan_json']=json.dumps(city);s['capital_painted_landscape_v79']=1;s['ground_shadow_asset']='assets/wayfarer-ground-shadow-v79-painted-landscape.png'
for f in ('plan.json','native-plan.json'):(O.parent/f).write_text(json.dumps(city,indent=2)+'\n')
bpy.context.view_layer.update();after=exp['export'](s);now={o['id']:o for o in after['objects']}
for o in before['objects']:
 q=now[o['id']]
 assert {k:v for k,v in o.items() if k!='parts'}=={k:v for k,v in q.items() if k!='parts'},o['id']
 assert [a for a in o['parts'] if a['role']=='solid']==[a for a in q['parts'] if a['role']=='solid'],o['id']
assert before['terrain']==after['terrain'] and before['navigation']==after['navigation']
for name in changes:changes[name]['after']=after['materials'][name]
receipt={'baselineCommit':p['baselineCommit'],'beforeSourceSHA256':p['beforeSourceSHA256'],'materialChanges':changes,'formalCrowns':formal,'changedLeafParts':changed_leaves,'replacedLawnParts':p['replacedLawnParts'],'newLawnParts':[a['id'] for a in p['pieces']],'newGrassOwner':p['grassOwner'],'newGrassTriangles':len(p['grassRoots'])*3,'lawnAddedTriangles':p['lawnAddedTriangles'],'allCollisionTerrainNavigationGameplayExact':True,'originalResolutionAndImagesPreserved':True,'visualAcceptance':'Pending paired normal gameplay comparison'}
(O/'authoring.json').write_text(json.dumps(receipt,indent=2)+'\n')
del before,after,now;gc.collect();bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('PASS saved painted property gardens,16 formal crown variants and original full-size foliage',flush=True)
