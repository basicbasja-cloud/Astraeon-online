"""Refit existing foundation vegetation to the deliberately taller native curbs."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
def fit(scene):
 terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vertices=[];triangles=[]
 for o in terrain.objects:
  if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
  off=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();triangles.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
 floor=BVHTree.FromPolygons(vertices,triangles,all_triangles=True)
 def ground(p):
  q=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];assert q is not None;return q.z
 prior=json.loads(scene.get('ro3_grass_contact_v70_json','{}'));patches={r['id']:r for r in prior.get('patches',[])};clumps={r['id']:r for r in prior.get('clumps',[])}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  inv=o.matrix_world.inverted()
  if o.get('street_v69_patch'):
   original=[o.matrix_world@v.co for v in o.data.vertices]
   changed=0
   for v in o.data.vertices:
    p=o.matrix_world@v.co;z=ground(p)+.017
    if abs(z-p.z)>.002:p.z=z;v.co=inv@p;changed+=1
   current=[o.matrix_world@v.co for v in o.data.vertices];shrunk=False
   if max(p.z for p in current)-min(p.z for p in current)>.13:
    assert len(current)==4,o.name
    a,b,c,d=current
    spans=[(0,1),(0,.85),(.15,1),(0,.70),(.30,1),(.15,.85),(.25,.75),(0,.5),(.5,1),(0,.25),(.25,.5),(.5,.75),(.75,1)]
    candidates=sorted([(u,v) for u in spans for v in spans],key=lambda pair:(pair[0][1]-pair[0][0])*(pair[1][1]-pair[1][0]),reverse=True)
    for (u0,u1),(v0,v1) in candidates:
     def point(u,v):return a+(b-a)*u+(d-a)*v
     q=[point(u0,v0),point(u1,v0),point(u1,v1),point(u0,v1)]
     zs=[ground(q[0]+(q[1]-q[0])*i/4+(q[3]-q[0])*j/4) for i in range(5) for j in range(5)]
     if max(zs)-min(zs)>.035:continue
     for v,p in zip(o.data.vertices,q):p.z=ground(p)+.017;v.co=inv@p
     shrunk=True;break
    assert shrunk,('No smooth building-side grass span',o.name)
   if changed or shrunk or o.name in patches:
    rec=patches.get(o.name,{'id':o.name,'oldVertices':[list(p) for p in original]});rec.update(verticesChanged=changed,shrunkAtCurb=shrunk or rec.get('shrunkAtCurb',False),newVertices=[list(o.matrix_world@v.co) for v in o.data.vertices]);patches[o.name]=rec
  if o.get('street_v69_clump'):
   old=Vector(o['street_v69_root_world']);new=old.copy();new.z=ground(old)+.017;offset=new-old
   if abs(offset.z)>.002:
    for v in o.data.vertices:v.co=inv@(o.matrix_world@v.co+offset)
    o['street_v69_root_world']=list(new);first=clumps.get(o.name,{}).get('oldRoot',list(old));clumps[o.name]={'id':o.name,'oldRoot':first,'newRoot':list(new),'zOffset':new.z-first[2]}
 result={'patches':list(patches.values()),'clumps':list(clumps.values()),'reason':'629 curbs deliberately rise to .20; six grass strips retract within their original footprint to avoid spanning curb steps; clumps follow actual new floor; original structural geometry unchanged'}
 scene['ro3_grass_contact_v70_json']=json.dumps(result);bpy.context.view_layer.update();return result
if __name__=='__main__':
 result=fit(bpy.context.scene);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS native grass contact refit',len(result['patches']),'patches;',len(result['clumps']),'clumps')
