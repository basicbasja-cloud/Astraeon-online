"""Fit the Exchange between the market spine and circuit; do not narrow roads."""
import bpy,json,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_architecture_revision')==76
if not s.get('capital_exchange_street_clearance'):
 p=json.loads(s['capital_plan_json']);spec=next(a for a in p['landmarks'] if a['id']=='capital-trade-exchange');before={k:spec[k] for k in ('center','width','depth')}
 spec.update(center=[192.5,126],width=19,depth=13.5,front=[192.5,137])
 c=bpy.data.collections[spec['id']];data=[o.data for o in c.objects if o.type=='MESH'];bpy.data.batch_remove(ids=list(c.objects));bpy.data.batch_remove(ids=[d for d in data if not d.users]);c['capital_landmark_json']=json.dumps(spec)
 terrain=bpy.data.collections['court-terrain'];bpy.data.batch_remove(ids=[o for o in terrain.objects if o.get('object_id')==spec['id'] and '-entry-tread-' in o.name])
 r=bpy.data.objects.new(c.name+'-placement',None);c.objects.link(r);r.location=(*spec['center'],0)
 FacadeKit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];k=FacadeKit(c,r);k.prefix='capital-v76-'
 def floor(a):
  d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces']);d.materials.append(bpy.data.materials[a['material']]);d.uv_layers.new(name='WorldUV')
  for f in d.polygons:
   for li in f.loop_indices:
    v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/2.4,v.y/2.4)
  o=bpy.data.objects.new(a['id'],d);terrain.objects.link(o);o['surface_role']=a['role'];o['walkable']=True;o['object_id']=a['objectId'];o['render_visible']=False
 runpy.run_path(str(R/'tools/capital-architecture-kit-v76.py'))['build_civic'](spec,c,r,k,floor)
 p['architectureRevision']['exchangeBlockFit']={'before':before,'after':{k:spec[k] for k in ('center','width','depth')},'publicStreetWidthsUnchanged':True,'windowsAndDoorDimensionsAuthoredAtNativeSize':True}
 for folder in ('wayfarer-capital-v75','wayfarer-capital-v76'):
  for name in ('plan.json','native-plan.json'):(R/'docs/review'/folder/name).write_text(json.dumps(p,indent=2)+'\n')
 (R/'docs/review/wayfarer-capital-v76/architecture-plan.json').write_text(json.dumps(p['architectureRevision'],indent=2)+'\n')
 s['capital_plan_json']=json.dumps(p,separators=(',',':'));s['capital_exchange_street_clearance']=76
 runpy.run_path(str(R/'tools/consolidate-capital-components-v75.py'),run_name='__main__')
 print('Exchange rebuilt inside its real street block',json.dumps(p['architectureRevision']['exchangeBlockFit']),flush=True)
