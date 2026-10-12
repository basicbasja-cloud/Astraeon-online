"""Reopen the approved original source and inventory actual rig/part ownership."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--approval',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=json.loads(a.approval.read_text());b=r['source_binding'];path=Path(b['blend_path'])
 if sha(path)!=b['blend_sha256']:raise ValueError('Changed approved source')
 bpy.ops.wm.open_mainfile(filepath=str(path));rig=bpy.data.objects['original.walk.rig'];bones={x.name:{'parent':x.parent.name if x.parent else None,'rest_head':list(x.head_local),'rest_tail':list(x.tail_local)} for x in rig.data.bones};parts={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  slot=o.get('slot')
  if not slot:raise ValueError('Source mesh lacks declared slot: '+o.name)
  weights={g.name for g in o.vertex_groups};unknown=weights-set(bones)
  if unknown:raise ValueError('Non-rig weight groups: '+o.name)
  orphan=sum(not any(g.weight>0 for g in v.groups) for v in o.data.vertices)
  if orphan:raise ValueError('Unweighted source vertices: '+o.name)
  parts.setdefault(slot,[]).append({'mesh':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'weight_bones':sorted(weights),'armature_modifiers':[m.object.name if m.object else None for m in o.modifiers if m.type=='ARMATURE']})
 active=rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None
 if active!='original.compact.contact-walk':raise ValueError('Wrong active source action')
 out={'schema':'actual-factory-source-inventory-v1','approval_path':str(a.approval),'approval_sha256':sha(a.approval),'blend_path':str(path),'blend_sha256':sha(path),'blender':bpy.app.version_string,'active_action':active,'bones':bones,'source_item_groups':parts,'source_item_groups_count':len(parts),'meshes':sum(len(x) for x in parts.values()),'unweighted_vertices':0,'painted_parts_complete':False,'hidden_painted_content_verified':False,'source_scope':'Actual reopened original source geometry/weights only. Item-group existence is not painted replacement completeness; hair.silver and hair.auburn are alternative items, not two simultaneous hair slots. Export camera/canvas is authoritative in the approved ground receipt, not inherited motion metadata.','production_ready':False}
 if sha(path)!=b['blend_sha256']:raise ValueError('Source changed during inventory')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print('FACTORY_SOURCE',out['meshes'],len(bones),len(parts),active)
if __name__=='__main__':main()
