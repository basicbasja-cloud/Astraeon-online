"""Capture isolated weighted anatomy from frozen native Blender poses.

Only render geometry is isolated; rig, motion, floor correction and camera are
unchanged. These are partial drawing guides, never complete character sprites.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import bpy

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['skeleton','rig','reference-guide','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--mesh-name',default='F01_BodyOutfit');p.add_argument('--groups',nargs='+',required=True);p.add_argument('--directions',nargs='+',default=['NE']);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Choose a fresh isolated anatomy guide')
    reference=json.loads((a.reference_guide/'pilot-receipt.json').read_text());core=a.reference_guide/'renderer-source.py'
    if len(a.directions)!=len(set(a.directions))or set(a.directions)-set(reference['views']):raise ValueError('Unknown or duplicate real camera direction')
    if sha(core)!=reference['implementation_sha256']or sha(a.rig)!=reference['rig_sha256']:raise ValueError('Frozen camera/rig implementation changed')
    frozen={str(f):sha(f)for f in [a.skeleton,a.rig,a.reference_guide/'pilot-receipt.json',core]};implementation=sha(__file__);counts=[]
    def render_part(scene,rig,camera,frame):
        body=bpy.data.objects[a.mesh_name];indices={body.vertex_groups[n].index for n in a.groups if n in body.vertex_groups}
        if len(indices)!=len(a.groups):raise ValueError('Canonical mesh is missing selected anatomical weights')
        depsgraph=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(depsgraph);mesh=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=depsgraph)
        weights=[sum(g.weight for g in vertex.groups if g.group in indices)for vertex in mesh.vertices]
        if not weights or max(weights)<.5:raise ValueError('Evaluated mesh did not preserve anatomical deform weights')
        vertices=[tuple(evaluated.matrix_world@v.co)for v in mesh.vertices];faces=[tuple(poly.vertices)for poly in mesh.polygons if sum(weights[i]for i in poly.vertices)/len(poly.vertices)>.5];evaluated.to_mesh_clear()
        if len(faces)<20:raise ValueError('Selected anatomy contains too few faces')
        data=bpy.data.meshes.new('IsolatedNativeAnatomy');data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj)
        before={o:o.hide_render for o in scene.objects if o.type in ['MESH','CURVE']and o!=obj}
        try:
            for o in before:o.hide_render=True
            bpy.ops.render.render(write_still=True)
        finally:
            for o,value in before.items():o.hide_render=value
            bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(data)
        counts.append({'index':frame['index'],'direction':Path(scene.render.filepath).parent.name,'selected_faces':len(faces),'world_matrices':{n:[list(r)for r in rig.matrix_world@rig.pose.bones[n].matrix]for n in a.groups},'rest_world_matrices':{b.name:[list(r)for r in rig.matrix_world@b.matrix_local]for b in rig.data.bones}})
    tree=ast.parse(core.read_text());tree.body=[n for n in tree.body if not isinstance(n,ast.If)];replacements=[]
    class Part(ast.NodeTransformer):
        def visit_Call(self,node):
            if ast.unparse(node.func)=='bpy.ops.render.render':
                replacements.append(1);return ast.Call(func=ast.Name(id='_capture_part',ctx=ast.Load()),args=[ast.Name(id=k,ctx=ast.Load())for k in ['scene','rig','camera','frame']],keywords=[])
            return self.generic_visit(node)
    tree=ast.fix_missing_locations(Part().visit(tree))
    if len(replacements)!=1:raise ValueError('Frozen render boundary changed')
    scope={'__name__':'isolated_native_anatomy','__file__':str(core),'_capture_part':render_part};exec(compile(tree,str(core),'exec'),scope)
    sys.argv=[sys.argv[0],'--','--skeleton',str(a.skeleton),'--rig',str(a.rig),'--output',str(a.output),'--directions',*a.directions,'--weapon',reference['weapon']];scope['main']()
    internal=a.output/'pilot-receipt.json';receipt=json.loads(internal.read_text());internal.unlink()
    if sha(__file__)!=implementation or any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Native anatomy inputs changed')
    receipt.update({'status':'ISOLATED_NATIVE_ANATOMY_GUIDE_NOT_FINAL_ART','mesh_name':a.mesh_name,'groups':a.groups,'selected_geometry':counts,'input_sha256':frozen,'canonical_implementation_sha256':sha(core),'implementation_sha256':implementation,'camera_changed':False,'rig_modified':False,'runtime_admitted':False})
    (a.output/'part-guide-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(a.output/'part-renderer-source.py').write_bytes(Path(__file__).read_bytes())
    print('ISOLATED_NATIVE_PART_CAPTURES',len(counts),flush=True)

if __name__=='__main__':main()
