"""Remove stone image pads; grow short native grass inside existing paving joints."""
import bpy,json,random,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert not scene.get('ro3_integrated_path_grass_version');review=json.loads(scene['ro3_path_wear_review_json']);exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=exporter['export'](scene);terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');verts=[];faces=[];uvs=[];materials=[]
for s in w['terrain']['surfaces']:
 if not s['walkable']:continue
 base=len(verts);verts.extend(s['vertices'])
 for fi,f in enumerate(s['faces']):
  for j in range(1,len(f)-1):
   corners=(0,j,j+1);faces.append(tuple(base+f[k] for k in corners));uvs.append([s['uvs'][fi][k] for k in corners] if s.get('uvs') else None);materials.append(s['material'])
floor=BVHTree.FromPolygons(verts,faces,all_triangles=True);file=w['materials']['paving']['texture']['file'];im=Image.open(ROOT/file).convert('RGB');pixels=im.load();width,height=im.size

def contact(p):
 hit,normal,index,distance=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150);assert hit is not None
 if not uvs[index] or w['materials'][materials[index]].get('texture',{}).get('file')!=file:return hit,None
 a,b,c=[Vector(verts[k]) for k in faces[index]];ab=b-a;ac=c-a;ap=hit-a;d00=ab.dot(ab);d01=ab.dot(ac);d11=ac.dot(ac);den=d00*d11-d01*d01;v=(d11*ap.dot(ab)-d01*ap.dot(ac))/den;t=(d00*ap.dot(ac)-d01*ap.dot(ab))/den
 uv=[uvs[index][0][k]+v*(uvs[index][1][k]-uvs[index][0][k])+t*(uvs[index][2][k]-uvs[index][0][k]) for k in (0,1)];rgb=pixels[int((uv[0]%1)*width)%width,int((1-uv[1]%1)*height)%height];luma=(.2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2])/255;return hit,luma
r=random.Random(694501);regions=[];count=0
for record in review['patches']:
 pad=bpy.data.objects[record['id']];a,b,c,d=[pad.matrix_world@v.co for v in pad.data.vertices];grass=[]
 for ob in terrain.objects:
  if not ob.get('path_wear_grass_v69'):continue
  root=(ob.matrix_world@ob.data.vertices[0].co+ob.matrix_world@ob.data.vertices[1].co)/2
  if any((root-Vector(p)).length<.0001 for p in record['roots']):grass.append((ob,root))
 assert len(grass)==len(record['roots'])==8,record['id']
 candidates=[]
 for u in range(2,39):
  for v in range(2,39):
   p=a+(b-a)*u/40+(d-a)*v/40;hit,luma=contact(p)
   if luma is not None and luma<.57:candidates.append((hit,luma))
 r.shuffle(candidates);chosen=[]
 for hit,luma in candidates:
  if all((hit.xy-p.xy).length>.19 for p,_ in chosen):chosen.append((hit,luma))
  if len(chosen)==len(grass):break
 assert len(chosen)==len(grass),(record['id'],len(candidates),len(chosen))
 roots=[]
 for (ob,old),(hit,luma) in zip(sorted(grass,key=lambda pair:pair[0].name),chosen):
  root=hit+Vector((0,0,.012));inv=ob.matrix_world.inverted()
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;delta=p-old;delta.z*=1.3;v.co=inv@(root+delta)
  ob['integrated_paving_joint_v69']=True;ob['paving_joint_root']=list(root);ob['paving_joint_luma']=luma;roots.append({'id':ob.name,'point':list(root),'jointLuma':luma});count+=1
 regions.append({'formerPad':pad.name,'road':record['road'],'location':record['location'],'vertices':[list(p) for p in (a,b,c,d)],'joints':roots});bpy.data.objects.remove(pad,do_unlink=True)
# The abandoned image-pad artwork stays in git history/provenance, but is unused.
bpy.data.materials.remove(bpy.data.materials['agedPathPatch'])
final={'regions':regions,'jointGrassClumps':count,'bladesPerClump':3,'stoneImagePads':0,'removedStonePads':len(regions),'nativeGroundOffset':.012,'jointArtwork':file,'jointThreshold':.57,'placement':'Existing rectangular paving mortar/crack joints at building-side walks and broad road shoulders; continuous native paving is retained','collisionAndWalkableFloorChanged':False,'omittedPavingTransitions':review['omittedPavingTransitions']};scene['ro3_path_wear_review_json']=json.dumps(final);scene['ro3_integrated_path_grass_version']=69
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS integrated paving:',len(regions),'stone image pads removed;',count,'native tufts rooted in actual continuous paving joints; floors unchanged')
