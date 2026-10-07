"""Partition the new tiny blade geometry by32m cell, preserving every face/UV.
The transport already partitions each triangle. This keeps editable native
blade components local too; it does not claim a new transport optimization.
"""
import bpy,json,math,runpy,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v79/painted-landscape';s=bpy.context.scene
assert s.get('capital_painted_landscape_v79') and not s.get('capital_painted_blade_batches_v79')
p=json.loads((O/'plan.json').read_text());c=bpy.data.collections[p['grassOwner']];old=list(c.objects);groups={}
def fingerprint(objects):
 result=[]
 for o in objects:
  if o.type!='MESH':continue
  for f in o.data.polygons:
   result.append((o.data.materials[0].name,tuple(tuple(o.matrix_world@o.data.vertices[i].co) for i in f.vertices),tuple(tuple(o.data.uv_layers.active.data[li].uv) for li in f.loop_indices)))
 return sorted(result)
before=fingerprint(old)
for o in old:
 assert o.type=='MESH' and o.get('role')=='decorative' and not o.get('shadow') and not o.parent
 for f in o.data.polygons:
  verts=[tuple(o.data.vertices[i].co) for i in f.vertices];cx=sum(v[0] for v in verts)/len(verts);cy=sum(v[1] for v in verts)/len(verts);cell=(math.floor(cx/32),math.floor(cy/32),o.data.materials[0].name)
  groups.setdefault(cell,[]).append((verts,[tuple(o.data.uv_layers.active.data[li].uv) for li in f.loop_indices]))
new=[]
for (x,y,mat),source in sorted(groups.items()):
 name=f'{p["grassOwner"]}-cell-{x}-{y}-{mat}';verts=[];faces=[];uvs=[]
 for points,uv in source:
  off=len(verts);verts.extend(points);faces.append(list(range(off,off+len(points))));uvs.append(uv)
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.materials.append(bpy.data.materials[mat]);d.uv_layers.new(name='WorldUV')
 for f,uv in zip(d.polygons,uvs):
  for li,q in zip(f.loop_indices,uv):d.uv_layers.active.data[li].uv=q
 o=bpy.data.objects.new(name,d);c.objects.link(o);o['role']='decorative';o['shadow']=False;new.append(o)
assert fingerprint(new)==before,'Every native face/material/UV must survive the partition'
bpy.data.batch_remove(ids=old);s['capital_painted_blade_batches_v79']=1
receipt={'beforeMeshes':len(old),'afterMeshes':len(new),'cells':sorted(set((x,y) for x,y,m in groups)),'triangles':len(before),'everyNativeFaceMaterialUVExact':True,'reason':'Keep sparse planted-property blades local to authored32m stream cells','fingerprintSHA256':hashlib.sha256(json.dumps(before).encode()).hexdigest(),'parts':[o.name for o in new]}
(O/'blade-batches.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
