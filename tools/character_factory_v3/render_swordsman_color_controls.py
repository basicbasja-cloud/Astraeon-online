"""Material-only guide controls on the original Mesh2Motion rig, never final art."""
import argparse,ast,hashlib,json,math,struct,sys
from pathlib import Path
import bpy
from mathutils import Vector
from PIL import Image,ImageChops
PALETTE={'hair':'b3a7b7','skin':'d7a078','scarf':'c79a2e','cloth':'202939','cream':'e4d4b6','bronze':'957043','leather':'65452d','pants':'52513a'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def geometry(mesh):
 h=hashlib.sha256()
 for v in mesh.vertices:h.update(struct.pack('<3f',*v.co))
 for p in mesh.polygons:h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference-manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--direction',default='SW');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 if a.output.exists() or a.output.is_symlink():raise ValueError('Fresh guide output required')
 reference=json.loads(a.reference_manifest.read_text());job=dict(reference['job']);direction=a.direction
 if direction not in reference['views'] or job['source_actions']!=['Walk']:raise ValueError('Expected original Walk source')
 core=Path(__file__).with_name('render_patch001_guides.py');assert sha(core)==job['renderer_sha256'];job['directions']=[direction];job['id']='swordsman-walk-color-control-20261104';a.output.mkdir(parents=True);jobpath=a.output/'job.json';jobpath.write_text(json.dumps(job,indent=2)+'\n');records=[];applied=False
 def render(scene,rig):
  nonlocal applied
  if not applied:
   materials={}
   for name,value in PALETTE.items():
    rgb=[int(value[i:i+2],16)/255 for i in (0,2,4)];linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb];mat=bpy.data.materials.new('SwordsmanGuide_'+name);mat.diffuse_color=(*linear,1);materials[name]=mat
   for obj in bpy.data.objects:
    if obj.type!='MESH' or obj.hide_render or not obj.vertex_groups:continue
    before=geometry(obj.data);indices={g.index:g.name for g in obj.vertex_groups};keys=list(materials);base=len(obj.data.materials)
    for mat in materials.values():obj.data.materials.append(mat)
    counts={}
    for face in obj.data.polygons:
     weights={};point=Vector((0,0,0))
     for index in face.vertices:
      v=obj.data.vertices[index];point+=obj.matrix_world@v.co
      for g in v.groups:weights[indices[g.group]]=weights.get(indices[g.group],0)+g.weight
     point/=len(face.vertices)
     if not weights:continue
     bone=max(weights,key=weights.get);normal=obj.matrix_world.to_3x3()@face.normal;role='cloth'
     if bone=='head':
      anchor=rig.matrix_world@rig.data.bones[bone].head_local;axis=(rig.matrix_world.to_3x3()@(rig.data.bones[bone].tail_local-rig.data.bones[bone].head_local)).normalized();role='hair' if (point-anchor).dot(axis)>.10 else 'skin'
     elif bone.startswith('neck'):role='scarf'
     elif bone.startswith(('hand_','index_','middle_','ring_','pinky_','thumb_')):role='leather'
     elif bone.startswith('lowerarm_'):role='bronze'
     elif bone.startswith('upperarm_'):
      b=rig.data.bones[bone];anchor=rig.matrix_world@b.head_local;axis=rig.matrix_world.to_3x3()@(b.tail_local-b.head_local);t=(point-anchor).dot(axis)/max(axis.length_squared,1e-8);role='bronze' if t<.3 else 'cloth'
     elif bone.startswith(('foot_','ball_','calf_')):role='leather'
     elif bone.startswith(('thigh_','pelvis')):role='pants'
     elif bone.startswith('spine'):
      pelvis=rig.matrix_world@rig.data.bones['pelvis'].head_local;role='cream' if abs(point.x-pelvis.x)<.11 and normal.y<-.15 else 'cloth'
     face.material_index=base+keys.index(role);counts[role]=counts.get(role,0)+1
    assert geometry(obj.data)==before;records.append({'mesh':obj.name,'geometry_sha256':before,'faces_by_color_role':counts})
   scene.view_settings.view_transform='Standard';applied=True
  bpy.ops.render.render(write_still=True)
 tree=ast.parse(core.read_text());tree.body=[n for n in tree.body if not(isinstance(n,ast.If) and ast.unparse(n.test).startswith('__name__'))];calls=[]
 class Inject(ast.NodeTransformer):
  def visit_Call(self,node):
   if ast.unparse(node.func)=='bpy.ops.render.render':calls.append(1);return ast.Call(func=ast.Name(id='_color_render',ctx=ast.Load()),args=[ast.Name(id='sc',ctx=ast.Load()),ast.Name(id='rig',ctx=ast.Load())],keywords=[])
   return self.generic_visit(node)
 tree=ast.fix_missing_locations(Inject().visit(tree));assert len(calls)==1
 scope={'__file__':str(core),'__name__':'material_control_capture','_color_render':render};exec(compile(tree,str(core),'exec'),scope);sys.argv=[sys.argv[0],'--','--job',str(jobpath),'--output',str(a.output)];scope['main']()
 result=json.loads((a.output/'manifest.json').read_text());maximum=0.;alpha_mismatches=[]
 for i,(original,now) in enumerate(zip(reference['views'][direction]['frames'],result['views'][direction]['frames'])):
  for name,xy in original['landmarks'].items():maximum=max(maximum,math.dist(xy,now['landmarks'][name]))
  original_alpha=Image.open(a.reference_manifest.parent/direction/f'{i:03}.png').getchannel('A');current_alpha=Image.open(a.output/direction/f'{i:03}.png').getchannel('A');alpha_mismatches.append(ImageChops.difference(original_alpha,current_alpha).getbbox() is not None)
 if maximum>1e-4 or any(alpha_mismatches):raise ValueError('Guide geometry/camera silhouette changed')
 (a.output/'color-control-proof.json').write_text(json.dumps({'status':'MATERIAL_ONLY_GUIDE_NOT_FINAL_ART','reference_sha256':sha(a.reference_manifest),'wrapper_sha256':sha(__file__),'original_renderer_sha256':sha(core),'palette':PALETTE,'geometry':records,'frames':len(alpha_mismatches),'projected_landmark_max_error_px':maximum,'alpha_mismatch_frames':sum(alpha_mismatches),'limitations':['Color regions are structural hints, not approved clothing masks or costume geometry.','No anatomical fit, contact or painted character approval.','Rig, motion, camera and mesh positions are not modified.']},indent=2)+'\n');print('COLOR_CONTROL_VERIFIED',len(alpha_mismatches),flush=True)
if __name__=='__main__':main()
