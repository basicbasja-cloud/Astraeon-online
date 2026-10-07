"""Give low lodges full-height entries and a lower loft, retaining editable parts."""
import json,bpy,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_architecture_revision')==76
if not s.get('capital_lodge_entries'):
 for c in bpy.data.collections:
  if not c.get('building_preset_json'):continue
  l=json.loads(c['building_preset_json'])
  if l.get('architectureType')!='craft-lodge':continue
  core_groups=[(o,g) for o in c.objects if o.type=='MESH' for g in o.vertex_groups if g.name.endswith('-ground-core')]
  core_height=max(o.data.vertices[v.index].co.z for o,g in core_groups for v in o.data.vertices if any(a.group==g.index for a in v.groups))
  if core_height>3.0:continue
  for o in c.objects:
   if o.type!='MESH':continue
   categories={key:set() for key in ('loft','core','post')}
   for g in o.vertex_groups:
    key='loft' if '-story-0-' in g.name else 'core' if g.name.endswith('-ground-core') else 'post' if '-ground-post-' in g.name else None
    if key:categories[key].update(v.index for v in o.data.vertices if any(a.group==g.index for a in v.groups))
   for key,indices in categories.items():
    for vi in indices:
     v=o.data.vertices[vi]
     if key=='loft':v.co.z=4.75-(4.75-v.co.z)*(4.75-3.12)/(4.75-2.65)
     elif key=='core':v.co.z=.2+(v.co.z-.2)*(3.12-.2)/(2.65-.2)
     else:v.co.z*=3.12/2.65
   o.data.update()
   if categories['loft'] or categories['core'] or categories['post']:
    scale=json.loads(o.data.materials[0].get('texture_json','{}')).get('worldSize',2.4)
    for face in o.data.polygons:
     if not any(v in (categories['loft']|categories['core']|categories['post']) for v in face.vertices):continue
     for li in face.loop_indices:
      v=o.data.vertices[o.data.loops[li].vertex_index].co;n=face.normal;o.data.uv_layers.active.data[li].uv=(v.x/scale,v.y/scale) if abs(n.z)>.65 else (v.y/scale,v.z/scale) if abs(n.x)>abs(n.y) else (v.x/scale,v.z/scale)
  print('LOW LODGE ENTRY',c.name,flush=True)
 p=json.loads(s['capital_plan_json'])
 for l in p['lots']:
  if l.get('architectureType')=='courtyard-villa':
   l['architectureType']='gallery-villa';bpy.data.collections[l['id']]['building_preset_json']=json.dumps(l)
 a=p['architectureRevision']
 if 'courtyard-villa' in a['families']:a['families']['gallery-villa']=a['families'].pop('courtyard-villa')
 for m in a['pairedPlotConsolidations']:
  if m['type']=='courtyard-villa':m['type']='gallery-villa'
 for landmark in p['landmarks']:
  landmark['height'],landmark['roofPeak']={'capital-council-chambers':(12,24.9),'capital-grand-archive':(13.1,28.8),'capital-trade-exchange':(7.8,22.3)}[landmark['id']]
  bpy.data.collections[landmark['id']]['capital_landmark_json']=json.dumps(landmark)
 for folder in ('wayfarer-capital-v75','wayfarer-capital-v76'):
  for name in ('plan.json','native-plan.json'):(R/'docs/review'/folder/name).write_text(json.dumps(p,indent=2)+'\n')
 (R/'docs/review/wayfarer-capital-v76/architecture-plan.json').write_text(json.dumps(a,indent=2)+'\n')
 s['capital_plan_json']=json.dumps(p,separators=(',',':'));s['architecture_revision']=76;s['capital_lodge_entries']=76
runpy.run_path(str(R/'tools/refine-capital-architecture-contacts-v76.py'),run_name='__main__')
