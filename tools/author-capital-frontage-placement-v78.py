"""Add guarded original low-roof thresholds to selected existing native owners.
No existing vertex or gameplay record moves. New roof tiles use full images at
a deliberately larger authored frequency; no renderer-only quality override.
"""
import bpy,json,math,runpy,hashlib,gc
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v78/frontage-placement';s=bpy.context.scene
assert not s.get('capital_frontage_placement_v78'),'Already applied'
p=json.loads((O/'plan.json').read_text());assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==p['beforeSourceSHA256']
exp=runpy.run_path(str(R/'tools/export-world-v3.py'));before=exp['export'](s)
Kit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];roof=runpy.run_path(str(R/'tools/capital-architecture-kit-v76.py'))['roof']
# Roof texture frequency is changed through the native material and every native
# corner of the matching materials, including inherited editable components.
uv_ids=[];materials={}
for name in p['materialNames']:
 m=bpy.data.materials[name];materials[name]={'before':before['materials'][name]}
 spec=json.loads(m['texture_json']);assert spec['worldSize']==2.4;spec['worldSize']=3.4;m['texture_json']=json.dumps(spec)
for o in bpy.data.objects:
 if o.type!='MESH' or not o.data.materials or o.data.materials[0].name not in p['materialNames']:continue
 for q in o.data.uv_layers.active.data:q.uv*=p['roofUVFactor']
 uv_ids.append(o.name)
newparts={}
for a in p['frontages']:
 c=bpy.data.collections[a['id']];oldnames={o.name for o in c.objects}
 root=bpy.data.objects.new('capital-v78-'+a['id']+'-threshold-frame',None);c.objects.link(root)
 root.location=a['position'];root.rotation_euler.z=a['angle'];k=Kit(c,root);k.prefix='capital-v78-'
 name=a['id'];w=a['width'];d=a['depth'];eave=max(3.46,a['doorTop']+.19);style=a['style'];mat=a['roofMaterial']
 if style in ('garden-hip','entry-gable'):
  roof(k,name+'-threshold',0,(d-.20)/2,w,d+.20,eave,.56 if style=='garden-hip' else .82,mat,'hip' if style=='garden-hip' else 'gable')
 else:
  # Two shallow slopes create a readable lower eave instead of another large
  # triangle wall. Native normals and corner UVs remain ordinary mesh data.
  ys=[-.20,.24,d];zs=[eave+.66,eave+.42,eave]
  for j in range(2):
   o=k.mesh(name+'-threshold-slope-'+str(j),[(-w/2,ys[j],zs[j]),(w/2,ys[j],zs[j]),(w/2,ys[j+1],zs[j+1]),(-w/2,ys[j+1],zs[j+1])],[[0,1,2,3]],mat);o['role']='overhead'
  for x in (-w/2,w/2):
   for j in range(2):k.beam(name+'-threshold-verge-'+str((x,j)),(x,ys[j],zs[j]),(x,ys[j+1],zs[j+1]),.12)
  k.beam(name+'-threshold-front-fascia',(-w/2,d,eave),(w/2,d,eave),.14)
 k.box(name+'-threshold-bressummer',(0,d-.12,eave-.13),(w,.16,.20),'timber')
 for side in (-1,1):
  x=side*(w/2-.14);y=d-.17
  post=k.box(name+'-threshold-post-'+str(side),(x,y,(eave-.15)/2),(.13,.13,eave-.15),'timber');post['role']='solid'
  k.box(name+'-threshold-plinth-'+str(side),(x,y,.17),(.13,.13,.34),'stoneLight')
  k.beam(name+'-threshold-brace-'+str(side),(x,y,eave-.72),(x-side*.43,y,eave-.19),.09)
  k.beam(name+'-threshold-wall-brace-'+str(side),(x,-.06,eave-.55),(x,y,eave-.19),.09)
 # An original blue/gold hanging lantern identifies a sheltered entry. Place
 # it above shoulder height outside the2.2m route; it has no ground footprint.
 x=w/2-.14;y=d-.10
 k.beam(name+'-entry-lantern-hook',(x,y,eave-.20),(x,y+.05,2.76),.035,'iron')
 k.box(name+'-entry-lantern-cage',(x,y+.05,2.61),(.16,.16,.25),'gold')
 k.box(name+'-entry-lantern-glass',(x,y+.143,2.61),(.115,.018,.18),'clothBlue',False)
 k.mesh(name+'-entry-lantern-cap',[(x-.12,y-.07,2.75),(x+.12,y-.07,2.75),(x+.12,y+.17,2.75),(x-.12,y+.17,2.75),(x,y+.05,2.84)],[[0,1,4],[1,2,4],[2,3,4],[3,0,4]],'iron')
 # Small terracotta wall pots stay elevated inside the plot and frame the
 # sheltered front; they are not extra obstacles or scattered street props.
 x=-w/2+.14;y=d-.13;z=.79;rad=.11
 pts=[(x+r*math.cos(j*math.tau/8),y+r*math.sin(j*math.tau/8),h) for r,h in [(rad*.7,z),(rad,z+.20)] for j in range(8)]
 k.mesh(name+'-threshold-herb-pot',pts,[[j,(j+1)%8,8+(j+1)%8,8+j] for j in range(8)],'roofClayOchre')
 for j in range(3):
  theta=j*math.tau/3
  k.mesh(name+'-threshold-herb-'+str(j),[(x,y,z+.20),(x+.16*math.cos(theta),y+.16*math.sin(theta),z+.33),(x+.06*math.cos(theta+.7),y+.06*math.sin(theta+.7),z+.49)],[[0,1,2]],'leaf',False)
 newparts[name]=[o.name for o in c.objects if o.type=='MESH' and o.name not in oldnames]
 print('SHELTER',name,style,flush=True)
# New helper roofs authored by the older kit use2.4 slope coordinates; correct
# only those new roof corners to the explicit3.4 material frequency.
for names in newparts.values():
 for name in names:
  o=bpy.data.objects[name]
  if o.data.materials[0].name in p['materialNames'] and o.get('role')=='overhead' and ('threshold-roof' in name):
   for q in o.data.uv_layers.active.data:q.uv*=p['roofUVFactor']
pnative=json.loads(s['capital_plan_json']);pnative['frontagePlacementRefinement']={'revision':78,'frontages':p['frontages'],'roofUVFactor':p['roofUVFactor'],'roofMaterialWorldSize':3.4,'roofUVMeshes':uv_ids}
s['capital_plan_json']=json.dumps(pnative);s['capital_frontage_placement_v78']=1;s['ground_shadow_asset']='assets/wayfarer-ground-shadow-v78-frontages.png'
for f in ('plan.json','native-plan.json'):(O.parent/f).write_text(json.dumps(pnative,indent=2)+'\n')
bpy.context.view_layer.update();after=exp['export'](s);afterowners={o['id']:o for o in after['objects']}
for o in before['objects']:
 n=afterowners[o['id']]
 for key in o.keys()-{'parts'}:assert o[key]==n[key],(o['id'],key)
 oldids={a['id'] for a in o['parts']}
 assert [a for a in o['parts'] if a['role']=='solid']==[a for a in n['parts'] if a['role']=='solid' and a['id'] in oldids]
 for a in o['parts']:
  b=next(b for b in n['parts'] if b['id']==a['id'])
  assert {k:v for k,v in a.items() if k!='uvs'}=={k:v for k,v in b.items() if k!='uvs'},a['id']
assert before['terrain']==after['terrain'] and before['navigation']==after['navigation']
for name in materials:materials[name]['after']=after['materials'][name]
added=sum(len(f)-2 for n,names in newparts.items() for a in afterowners[n]['parts'] if a['id'] in names and a.get('visible',True) for f in a['faces']);assert added<p['triangleBudget']
receipt={'baselineCommit':p['baselineCommit'],'beforeSourceSHA256':p['beforeSourceSHA256'],'newParts':newparts,'roofUVMeshes':uv_ids,'materialChanges':materials,'addedVisibleTriangles':added,'oldGeometryGameplayTerrainNavigationExact':True,'newSolidPosts':len(p['frontages'])*2,'additionalImageAssets':0,'visualAcceptance':'Pending paired normal gameplay review'}
(O/'authoring.json').write_text(json.dumps(receipt,indent=2)+'\n')
del before,after,afterowners;gc.collect()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
assert (R/'world/v3/wayfarer-spatial.json').stat().st_size<100*1024*1024
print('PASS saved19 guarded threshold shelters',added,'triangles',flush=True)
