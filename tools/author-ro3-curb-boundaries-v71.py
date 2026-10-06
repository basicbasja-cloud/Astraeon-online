"""Clip native curbs and their verges to building-side public path boundaries."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_civic_trees_version')==70 and not scene.get('ro3_curb_boundaries_version')
exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));boundary=runpy.run_path(str(ROOT/'tools/ro3-public-boundaries-v71.py'));before=exporter['export'](scene);public=boundary['public_surfaces'](before);polys=[h['hull'](s['vertices']) for s in public]
review=json.loads(scene['ro3_road_curb_review_json']);changes=[];accepted=[]
def refresh_uv(o):
 scale=json.loads(o.data.materials[0].get('texture_json','{}')).get('worldSize',2.4)
 for f in o.data.polygons:
  for li in f.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;n=f.normal
   o.data.uv_layers.active.data[li].uv=(p.x/scale,p.y/scale) if abs(n.z)>.65 else (p.y/scale,p.z/scale) if abs(n.x)>abs(n.y) else (p.x/scale,p.z/scale)
def fit_span(o,a,t,length,lo,hi):
 inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co;u=(p-a).dot(t);p+=t*(lo+u*(hi-lo)/length-u);v.co=inv@p
 o.data.update();refresh_uv(o)
for rec in review['curbBlocks']:
 o=bpy.data.objects[rec['id']];points=[o.matrix_world@v.co for v in o.data.vertices];a,b=points[0],points[6];t=b-a;t.z=0;length=t.length;t.normalize();n=points[1]-a;n.z=0;width=n.length;n.normalize();intervals=boundary['outside_intervals'](a,b,n,width,polys)
 valid=[]
 for lo,hi in intervals:
  aa=a+t*lo;bb=a+t*hi
  for left,right in boundary['outside_intervals'](aa,bb,n,width,accepted,clearance=.002):
   if right-left>=.16:valid.append((lo+left,lo+right))
 span=max(valid,key=lambda s:s[1]-s[0]) if valid else None;fascia=bpy.data.objects['curb70-fascia-'+rec['id']]
 rec['active']=bool(span)
 if span is None:
  o['render_visible']=False;o['walkable']=False;fascia['render_visible']=False;changes.append({'id':o.name,'action':'suppressed','fascia':fascia.name,'reason':'public path footprint or junction overlap'});continue
 lo,hi=span
 if lo>.00001 or length-hi>.00001:
  fit_span(o,a,t,length,lo,hi);fit_span(fascia,a,t,length,lo,hi);rec['boundaryTrim']=[lo,hi];changes.append({'id':o.name,'action':'trimmed','fascia':fascia.name,'originalLength':length,'retainedLength':hi-lo})
 accepted.append(h['hull']([tuple(o.matrix_world@v.co) for v in o.data.vertices]))
scene['ro3_road_curb_review_json']=json.dumps(review);bpy.context.view_layer.update()
world=exporter['export'](scene);vs=[];fs=[]
for s in world['terrain']['surfaces']:
 if not s['walkable']:continue
 off=len(vs);vs.extend(s['vertices'])
 for f in s['faces']:
  for j in range(1,len(f)-1):fs.append((off+f[0],off+f[j],off+f[j+1]))
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];assert hit is not None;return hit.z
verges=json.loads(scene['ro3_curb_grass_review_json']);grass_changes=[];composition=json.loads(scene['ro3_town_composition_review_json'])
for rec in verges['strips']:
 o=bpy.data.objects[rec['id']];points=[o.matrix_world@v.co for v in o.data.vertices];a,b=points[0],points[1];t=b-a;t.z=0;length=t.length;t.normalize();n=points[3]-a;n.z=0;width=n.length;n.normalize();intervals=boundary['outside_intervals'](a,b,n,width,polys)
 valid=[p for p in intervals if p[1]-p[0]>=.35];span=max(valid,key=lambda p:p[1]-p[0]) if valid else None;rec['active']=bool(span)
 if not span:
  o['render_visible']=False;grass_changes.append({'id':o.name,'action':'suppressed','reason':'public path footprint'});continue
 lo,hi=span
 if lo>.00001 or length-hi>.00001:
  fit_span(o,a,t,length,lo,hi);inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;p.z=ground(p)+.017;v.co=inv@p
  refresh_uv(o);grass_changes.append({'id':o.name,'action':'trimmed','originalLength':length,'retainedLength':hi-lo})
 rec['vertices']=[list(o.matrix_world@v.co) for v in o.data.vertices]
scene['ro3_curb_grass_review_json']=json.dumps(verges)
for rec in composition.get('broadenedBuildingVergeStrips',[]):rec['active']=bpy.data.objects[rec['id']].get('render_visible',True)
scene['ro3_town_composition_review_json']=json.dumps(composition)
record={'sourcePass':71,'publicFootprints':len(public),'publicSurfaceIds':[s['id'] for s in public],'historicalCurbBlocks':len(review['curbBlocks']),'activeCurbBlocks':sum(r['active'] for r in review['curbBlocks']),'curbChanges':changes,'grassChanges':grass_changes,'activeRoadsideVergeStrips':sum(r['active'] for r in verges['strips']),'rule':'Native curb courses only on the building side of the full public path footprint; open square, cross paths and stair approaches stay clear; junction courses do not intersect','originalSolidsAndActorsUnchanged':True}
scene['ro3_curb_boundaries_version']=71;scene['ro3_curb_boundaries_review_json']=json.dumps(record);runpy.run_path(str(ROOT/'tools/fit-ro3-curb-verges-v71.py'))['fit'](scene);record=json.loads(scene['ro3_curb_boundaries_review_json']);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print(json.dumps(record))
