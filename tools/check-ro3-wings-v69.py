"""Read-only outward pane rays through the native attached-wing openings."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
violations=[];rays=0;windows=0
for c in bpy.data.collections:
 glass=[o for o in c.objects if o.get('wing69_normal') is not None]
 if not glass:continue
 vertices=[];faces=[];owners=[]
 for o in c.objects:
  if o.type!='MESH' or not o.get('render_visible',True) or o.data.materials[0].name=='frontageGlazing':continue
  off=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles()
  for f in o.data.loop_triangles:faces.append(tuple(off+i for i in f.vertices));owners.append(o.name)
 tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True)
 for o in glass:
  n=Vector(o['wing69_normal']);t=Vector((-n.y,n.x,0));pts=[v.co for v in o.data.vertices];center=sum(pts,Vector())/len(pts);direction=(o.parent.matrix_world.to_3x3()@n).normalized()
  width=max(v.dot(t) for v in pts)-min(v.dot(t) for v in pts);height=max(v.z for v in pts)-min(v.z for v in pts)
  for x in (-1,0,1):
   for y in (-1,0,1):
    p=o.parent.matrix_world@(center+t*width*x/3+Vector((0,0,height*y/3)))+direction*.035
    hit,_,idx,dist=tree.ray_cast(p,direction,.65);rays+=1
    if hit is not None:violations.append({'window':o.name,'obstruction':owners[idx],'distance':dist})
  windows+=1
report={'sourcePass':69,'attachedWings':len(json.loads(bpy.context.scene['ro3_wing_detail_review_json'])),'windows':windows,'paneRays':rays,'violations':violations}
Path(sys.argv[sys.argv.index('--')+1]).write_text(json.dumps(report,indent=2)+'\n')
assert windows>0;assert not violations,json.dumps(violations[:12])
print('PASS',windows,'attached-wing windows;',rays,'clear pane rays')
