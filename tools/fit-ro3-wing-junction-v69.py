"""Omit the one ground window buried by a retained attached-wing junction."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert not scene.get('ro3_junction_omissions_json')
c=bpy.data.collections['district-garden-row-house'];name='ro3-v69-district-garden-row-house-ground-side-1-0-glass';glass=bpy.data.objects[name];root=glass.parent
pts=[v.co.copy() for v in glass.data.vertices];center=sum(pts,Vector())/len(pts)
# This saved side is +X in its model frame; fill exactly its original aperture.
width=max(p.y for p in pts)-min(p.y for p in pts)+.18;height=max(p.z for p in pts)-min(p.z for p in pts)+.18
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];kit=Kit(c,root);kit.prefix='ro3-v69-'
# Face/core X was glass X + .110. Fill inward from that face by .20.
center.x+=.110-.10
plug=kit.box(c.name+'-wing-junction-fill',tuple(center),(.20,width,height),'streetBrickLime')
# Use face Y/Z physical mortar registration, like the rest of this native side.
for f in plug.data.polygons:
 for li in f.loop_indices:
  p=plug.data.vertices[plug.data.loops[li].vertex_index].co;plug.data.uv_layers.active.data[li].uv=(p.y/2.4,p.z/2.4)
stem=name.removesuffix('-glass');shutter='ro3-v69-'+c.name+'-shutter-1-0-'
bpy.data.batch_remove(ids=[o for o in c.objects if o.name.startswith(stem) or o.name.startswith(shutter)])
review=json.loads(scene['ro3_street_review_json'])
for record in review['buildings']:
 if record['owner']==c.name:
  for face in record['faces']:
   if face['edge']==1:face['openings']-=1
scene['ro3_street_review_json']=json.dumps(review);scene['ro3_junction_omissions_json']=json.dumps([{'window':name,'reason':'buried at retained wing junction','nativeFill':plug.name}])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Omitted and filled one buried main-house side window at the wing junction')
