"""Supplement canonical Mage guides with locked class colors, not new poses.

Only materials change. Check every projected joint, camera and alpha silhouette
against the original canonical capture. This is painting guidance, not final art.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

import bpy


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assign_palette(rig, assignments):
    palette = {'coat': (.055,.085,.16,1), 'cream': (.85,.77,.60,1),
               'skin': (.73,.47,.30,1), 'hair': (.37,.085,.035,1),
               'pants': (.075,.075,.075,1), 'boots': (.30,.14,.055,1)}
    materials = {}
    for role, color in palette.items():
        material = bpy.data.materials.new('MageGuideOnly_'+role)
        material.diffuse_color = color
        materials[role] = material
    keys = list(materials)
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or obj.hide_render:
            continue
        before = hashlib.sha256(repr([tuple(v.co) for v in obj.data.vertices]).encode()).hexdigest()
        groups = {g.index:g.name for g in obj.vertex_groups}
        labels = []
        for vertex in obj.data.vertices:
            strongest = max(vertex.groups,key=lambda g:g.weight,default=None)
            name = groups.get(strongest.group,'') if strongest else ''
            if obj.name=='F01_HeadHair':
                role = 'hair'
            elif name.startswith(('Hand','Index','Middle','Ring','Pinky','Thumb')):
                role = 'skin'
            elif name.startswith('Forearm'):
                role = 'cream'
            elif name.startswith(('Foot','Toe')) or (name.startswith('Shin') and vertex.co.z<.34):
                role = 'boots'
            elif name.startswith(('Thigh','Shin')):
                role = 'pants'
            elif name.startswith(('Neck','Chest')) and vertex.co.z>.77 and abs(vertex.co.x)<.18:
                role = 'cream'
            else:
                role = 'coat'
            labels.append(role)
        obj.data.materials.clear()
        for material in materials.values():
            obj.data.materials.append(material)
        counts = {role:0 for role in keys}
        for face in obj.data.polygons:
            roles = [labels[i] for i in face.vertices]
            role = max(keys,key=lambda k:(roles.count(k),-keys.index(k)))
            face.material_index = keys.index(role)
            counts[role] += 1
        after = hashlib.sha256(repr([tuple(v.co) for v in obj.data.vertices]).encode()).hexdigest()
        if before!=after:
            raise ValueError('Material guide changed mesh coordinates')
        assignments.append({'object':obj.name,'unchanged_vertex_sha256':before,'faces_by_material':counts})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['canonical-guide','skeleton','rig','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--direction',default='NE')
    parser.add_argument('--directions',nargs='+',help='Explicit multi-view material guide; --direction remains the single-view default')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():
        raise ValueError('Use a fresh supplementary material capture')
    canonical = json.loads((args.canonical_guide/'pilot-receipt.json').read_text())
    # Replay the actual captured implementation, even after the current core
    # gains new camera options. Historical capture hashes remain authoritative.
    renderer = args.canonical_guide/'renderer-source.py'
    if canonical['implementation_sha256']!=sha(renderer) or canonical['source_skeleton_sha256']!=sha(args.skeleton):
        raise ValueError('Canonical implementation/source differs')
    tree = ast.parse(renderer.read_text())
    tree.body = [node for node in tree.body if not isinstance(node,ast.If)]
    calls = []
    class Visitor(ast.NodeTransformer):
        def visit_Expr(self,node):
            if isinstance(node.value,ast.Call) and ast.unparse(node.value.func)=='rig.animation_data_clear':
                calls.append(1)
                return [node,ast.parse('_assign_palette(rig)').body[0]]
            return self.generic_visit(node)
    tree = ast.fix_missing_locations(Visitor().visit(tree))
    if len(calls)!=1:
        raise ValueError('Canonical material boundary differs')
    assignments = []
    scope = {'__name__':'supplementary_canonical_materials','__file__':str(renderer),
             '_assign_palette':lambda rig:assign_palette(rig,assignments)}
    exec(compile(tree,str(renderer),'exec'),scope)
    directions = args.directions if args.directions is not None else [args.direction]
    if len(set(directions))!=len(directions) or not set(directions).issubset(canonical['views']):
        raise ValueError('Material cameras must be unique captured canonical views')
    sys.argv = [sys.argv[0],'--','--skeleton',str(args.skeleton),'--rig',str(args.rig),
                '--output',str(args.output),'--directions',*directions]
    scope['main']()
    generated = json.loads((args.output/'pilot-receipt.json').read_text())
    # Blender's bundled runtime does not need Pillow for an exact alpha check.
    checks = []
    for direction in directions:
        reference = canonical['views'][direction]
        view = generated['views'][direction]
        if view['camera']!=reference['camera'] or len(view['frames'])!=len(reference['frames']):
            raise ValueError('Material capture changed camera/timeline')
        for a,b in zip(view['frames'],reference['frames']):
            if a['landmarks']!=b['landmarks'] or a['grip_world']!=b['grip_world'] or a['staff_tip_world']!=b['staff_tip_world']:
                raise ValueError('Material capture changed projected anatomy or prop controls')
            checks.append({'direction':direction,'index':a['index'],'projected_pose_changed':False})
    result = {'status':'SUPPLEMENTARY_CLASS_COLORS_POSE_CHECKED_ALPHA_REVIEW_PENDING',
              'canonical_receipt_sha256':sha(args.canonical_guide/'pilot-receipt.json'),
              'implementation_sha256':sha(__file__),'profile':'mage-navy-cream-cuffs-bare-hands-v1',
              'direction':directions[0] if len(directions)==1 else None,'directions':directions,
              'mesh_materials':assignments,'frames':checks,
              'source_geometry_changed':False,'runtime_admitted':False}
    (args.output/'material-guide-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    (args.output/'material-renderer-source.py').write_bytes(Path(__file__).read_bytes())


if __name__=='__main__':
    main()
