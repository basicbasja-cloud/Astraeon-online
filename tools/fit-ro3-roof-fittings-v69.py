"""Connect native house drains to roof gutters; frame retained wing gables."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_wing_detail_version')==69
assert not scene.get('ro3_roof_fitting_version')
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
records=[]
for c in sorted(bpy.data.collections,key=lambda c:c.name):
 drain=next((o for o in c.objects if o.type=='MESH' and o.name.startswith('life69-') and o.name.endswith('-drain')),None)
 roof=next((o for o in c.objects if o.type=='MESH' and o.name.startswith('ro3-v68-') and o.name.endswith('-main-roof')),None)
 if not drain or not roof:continue
 root=drain.parent;inv=root.matrix_world.inverted();kit=Kit(c,root);kit.prefix='roof69-'+c.name[:20]+'-'
 p=[inv@roof.matrix_world@v.co for v in roof.data.vertices]
 z=min(v.z for v in p);eaves=[v for v in p if abs(v.z-z)<.03];roofx0,roofx1=min(v.x for v in p),max(v.x for v in p);roofy0,roofy1=min(v.y for v in p),max(v.y for v in p)
 rows=all(abs(v.y-roofy0)<.03 or abs(v.y-roofy1)<.03 for v in eaves)
 lines=[(Vector((roofx0,yy,z-.07)),Vector((roofx1,yy,z-.07))) for yy in (roofy0,roofy1)] if rows else [(Vector((xx,roofy0,z-.07)),Vector((xx,roofy1,z-.07))) for xx in (roofx0,roofx1)]
 for j,(a,b) in enumerate(lines):kit.beam('gutter-'+str(j),tuple(a),tuple(b),.095,'iron')
 pp=[v.co for v in drain.data.vertices];bottom=sum(pp,Vector())/len(pp);bottom.z=max(v.z for v in pp)
 end=min([v for pair in lines for v in pair],key=lambda v:(v-bottom).length);upper=Vector((end.x,end.y,bottom.z+.38))
 kit.beam('drain-offset',tuple(bottom),tuple(upper),.075,'iron');kit.beam('drain-upper',tuple(upper),tuple(end),.075,'iron')
 gables=0
 for o in list(c.objects):
  if o.type!='MESH' or len(o.data.vertices)!=3 or 'wing' not in o.name or 'gable' not in o.name or not o.get('render_visible',True):continue
  pts=[inv@o.matrix_world@v.co for v in o.data.vertices];normal=(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized();centroid=sum(pts,Vector())/3
  # Match outward winding already stored by the native gable.
  pts=[v+normal*.045 for v in pts]
  for j,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):kit.beam('wing-gable-'+str(gables)+'-'+str(j),tuple(a),tuple(b),.13,'timber')
  peak=max(pts,key=lambda v:v.z);other=[v for v in pts if v!=peak];middle=sum(other,Vector())/len(other)
  kit.beam('wing-kingpost-'+str(gables),tuple(middle),tuple(peak),.12,'timber');gables+=1
 records.append({'owner':c.name,'gutters':len(lines),'connectedDrain':True,'wingGables':gables})
assert len(records)==37,len(records)
scene['ro3_roof_fitting_version']=69;scene['ro3_roof_fitting_review_json']=json.dumps(records)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Connected roof drainage on',len(records),'houses; framed',sum(r['wingGables'] for r in records),'retained wing gables')
