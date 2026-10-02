"""Third review: route clearance, registered masks and district frontage."""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];kit=runpy.run_path(str(ROOT/'tools/blender-v3-kit.py'));mesh=kit['mesh'];scene=bpy.context.scene;terrain=bpy.data.collections['court-terrain']
def road(id,points,width,role='street'):
 for o in list(terrain.objects):
  if o.name.startswith(id+'-'):bpy.data.objects.remove(o,do_unlink=True)
 for j,(a,b) in enumerate(zip(points,points[1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];n=(dx*dx+dy*dy)**.5;nx,ny=-dy/n*width/2,dx/n*width/2
  vs=[(a[0]+nx,a[1]+ny,.005),(b[0]+nx,b[1]+ny,.005),(b[0]-nx,b[1]-ny,.005),(a[0]-nx,a[1]-ny,.005)]
  o=mesh(terrain,id+'-'+str(j),vs,[[0,1,2,3]],'paving','decorative',False);o['surface_role']=role if role in ['service','field'] else 'residential';o['road_segment']=True;o['legacy_role']=role
road('north-passage',[[20.94,6.8],[20.94,-3]],.55)
bpy.data.objects['tree-2-placement'].location=(10.8,9.0,0)
for id in ['forest-transition','forest-transition-approach']:
 o=bpy.data.objects[id];o.location.x=20.94-o.parent.location.x
root=bpy.data.objects['market-shop-placement'];m=json.loads(root['structure_json']);body=bpy.data.objects['market-shop-body'];points=[list(v.co)[:2] for v in body.data.vertices[:4]];depths=[14*x+22*y for x,y in points];rear=points[depths.index(min(depths))];front=points[depths.index(max(depths))]
for index,l in enumerate(m['layers']):l['depth']=rear if index==0 else front
root['structure_json']=json.dumps(m)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-court.blend'));runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
