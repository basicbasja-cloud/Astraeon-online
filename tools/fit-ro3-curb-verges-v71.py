"""Keep roadside verge quads rooted on a continuous building-side floor span."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
def fit(scene):
 terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
 for o in terrain.objects:
  if o.type!='MESH' or not o.get('walkable',True) or o.get('surface_role')=='water':continue
  off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+k for k in t.vertices) for t in o.data.loop_triangles)
 floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
 def ground(p):
  hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];assert hit is not None;return hit.z
 review=json.loads(scene['ro3_curb_grass_review_json']);record=json.loads(scene['ro3_curb_boundaries_review_json']);fits=[]
 spans=[(0,1),(0,.95),(.05,1),(0,.85),(.15,1),(.05,.95),(0,.70),(.30,1),(.15,.85),(.25,.75),(0,.5),(.5,1),(0,.25),(.25,.5),(.5,.75),(.75,1)]
 candidates=sorted([(u,v) for u in spans for v in spans],key=lambda p:(p[0][1]-p[0][0])*(p[1][1]-p[1][0]),reverse=True)
 for rec in review['strips']:
  if not rec['active']:continue
  o=bpy.data.objects[rec['id']];points=[o.matrix_world@v.co for v in o.data.vertices];a,b,c,d=points;bad=False
  for i in range(5):
   for j in range(5):
    u,v=i/4,j/4;p=a+(b-a)*u+(c-b)*v if u>=v else a+(c-d)*u+(d-a)*v
    if abs(p.z-ground(p)-.017)>=.035:bad=True
  if not bad:continue
  inv=o.matrix_world.inverted();chosen=None
  for (u0,u1),(v0,v1) in candidates:
   def point(u,v):return a+(b-a)*u+(d-a)*v
   q=[point(u0,v0),point(u1,v0),point(u1,v1),point(u0,v1)]
   if (q[1]-q[0]).xy.length<.35 or (q[3]-q[0]).xy.length<.08:continue
   zs=[ground(q[0]+(q[1]-q[0])*i/8+(q[3]-q[0])*j/8) for i in range(9) for j in range(9)]
   if max(zs)-min(zs)>.025:continue
   for v,p in zip(o.data.vertices,q):p.z=ground(p)+.017;v.co=inv@p
   chosen=[u0,u1,v0,v1];break
  assert chosen is not None,('No continuous owned verge span',o.name)
  scale=json.loads(o.data.materials[0]['texture_json']).get('worldSize',1)
  for f in o.data.polygons:
   for li in f.loop_indices:
    p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(p.x/scale,p.y/scale)
  rec['vertices']=[list(o.matrix_world@v.co) for v in o.data.vertices];fits.append({'id':o.name,'action':'contact_fit','oldVertices':[list(p) for p in points],'retainedSpan':chosen,'newVertices':rec['vertices']})
 record['vergeContactFits']=list({r['id']:r for r in record.get('vergeContactFits',[])+fits}.values())
 for fit in fits:
  if not any(r['id']==fit['id'] for r in record['grassChanges']):record['grassChanges'].append(fit)
 scene['ro3_curb_boundaries_review_json']=json.dumps(record);scene['ro3_curb_grass_review_json']=json.dumps(review);bpy.context.view_layer.update();return fits
if __name__=='__main__':
 fits=fit(bpy.context.scene);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS rooted continuous roadside verges',len(fits))
