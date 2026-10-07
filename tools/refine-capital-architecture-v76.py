"""Apply the explicit architecture revision to native source; originals survive."""
import json,runpy,bpy
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76';s=bpy.context.scene
assert s.get('capital_version')==75
assert not s.get('capital_architecture_revision'), 'This native revision is already applied'
p=json.loads((O/'native-plan.json').read_text());old=json.loads(s['capital_plan_json']);terrain=bpy.data.collections['court-terrain']
FacadeKit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];builders=runpy.run_path(str(R/'tools/capital-architecture-kit-v76.py'))
changed={l['id'] for l in old['lots'] if not l['existing']}|{a['id'] for a in old['landmarks']}
# Keep all inherited models and gameplay anchors; replace only authored additions.
for name in changed:
 c=bpy.data.collections[name];data=[o.data for o in c.objects if o.type=='MESH'];bpy.data.batch_remove(ids=list(c.objects));bpy.data.collections.remove(c)
 bpy.data.batch_remove(ids=[d for d in data if not d.users])
contacts=[o for o in terrain.objects if o.get('object_id') in changed and ('-entry-contact-' in o.name or '-entry-tread-' in o.name)]
bpy.data.batch_remove(ids=contacts)
def collection(name,family):
 c=bpy.data.collections.new(name);s.collection.children.link(c);c['family']=family;return c
def root(c,position=(0,0,0),angle=0):
 o=bpy.data.objects.new(c.name+'-placement',None);c.objects.link(o);o.location=position;o.rotation_euler.z=angle;return o
def kit(c,r):
 k=FacadeKit(c,r);k.prefix='capital-v76-';return k
def floor(a):
 d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces']);d.materials.append(bpy.data.materials[a['material']]);d.uv_layers.new(name='WorldUV')
 scale=json.loads(bpy.data.materials[a['material']].get('texture_json','{}')).get('worldSize',2.4)
 for f in d.polygons:
  for li in f.loop_indices:
   v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/scale,v.y/scale)
 o=bpy.data.objects.new(a['id'],d);terrain.objects.link(o);o['surface_role']=a['role'];o['walkable']=True;o['object_id']=a['objectId'];o['render_visible']=False
for i,l in enumerate(l for l in p['lots'] if not l['existing']):
 c=builders['build_house'](l,i,collection,root,kit,floor);c['building_preset_json']=json.dumps(l);print('NEW FAMILY',l['id'],l['architectureType'],flush=True)
for a in p['landmarks']:
 c=collection(a['id'],'civic');r=root(c,(*a['center'],0));k=kit(c,r);builders['build_civic'](a,c,r,k,floor);c['capital_landmark_json']=json.dumps(a);print('CIVIC',a['id'],a['architectureType'],flush=True)
s['capital_architecture_revision']=76;s['capital_plan_json']=json.dumps(p,separators=(',',':'))
stats=json.loads(s['capital_stats_json']);stats.update(newHouses=p['newHouses'],totalHouses=len(p['lots']),architectureRevision=76);s['capital_stats_json']=json.dumps(stats)
# Existing runtime layout identity is retained: avenues, portals and save anchors
# are unchanged. The separately recorded architecture revision identifies meshes.
for name in ('plan.json','native-plan.json'):(R/'docs/review/wayfarer-capital-v75'/name).write_text(json.dumps(p,indent=2)+'\n')
runpy.run_path(str(R/'tools/consolidate-capital-components-v75.py'),run_name='__main__')
print('Distinct native capital architecture saved',flush=True)
