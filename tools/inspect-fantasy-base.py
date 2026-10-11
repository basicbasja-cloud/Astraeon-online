"""Inspect the owner's new FBX in an isolated Blender process; do not alter it.

Use --background --factory-startup --python this_file -- --workspace PATH.
Archive contents are data only. The original mesh and UVs are preserved.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--workspace', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
base = Path(args.workspace)
cache = base / '.character-tools/free-assets/user-fantasy-308e5578d99c'
out = base / 'authoring/characters/swordsman-production/fantasy-base-01'
(out / 'renders').mkdir(parents=True, exist_ok=True)
native = base / '.character-tools/checkpoints/fantasy-base-01-inspection.blend'
native.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
s = bpy.context.scene
s.name = 'ASTRAEON_FANTASY_BASE_01_INSPECTION'
fbx = next(cache.glob('*.fbx'))
bpy.ops.import_scene.fbx(filepath=str(fbx), use_anim=True)
source = list(s.objects)
meshes = [o for o in source if o.type == 'MESH']
rigs = [o for o in source if o.type == 'ARMATURE']
report = {'kind': 'user_supplied_source_inspection', 'ownerApproved': False,
          'runtimeAdmitted': False, 'archiveSHA256': '308e5578d99cf9a3193fb4d43f9820dbbf9f100f42a326d44d633f4fcf5f385a',
          'source': fbx.name, 'sourceSHA256': hashlib.sha256(fbx.read_bytes()).hexdigest(),
          'files': [{'name': str(p.relative_to(cache)).replace('\\','/'), 'bytes': p.stat().st_size,
                     'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(cache.rglob('*')) if p.is_file()],
          'licenseEvidence': 'No license or creator attribution document is included in this archive.',
          'objects': [], 'materials': [], 'images': [], 'actions': []}
for o in source:
    d = {'name': o.name, 'type': o.type, 'parent': o.parent.name if o.parent else None,
         'location': list(o.location), 'rotation': list(o.rotation_euler), 'scale': list(o.scale)}
    if o.type == 'MESH':
        bm = bmesh.new(); bm.from_mesh(o.data)
        # Count actual connected components without relying on object separation.
        seen = set(); components = []
        for v in bm.verts:
            if v in seen: continue
            stack = [v]; seen.add(v); count = 0
            while stack:
                current = stack.pop(); count += 1
                for edge in current.link_edges:
                    other = edge.other_vert(current)
                    if other not in seen: seen.add(other); stack.append(other)
            components.append(count)
        d.update(vertices=len(o.data.vertices), polygons=len(o.data.polygons),
                 triangles=sum(len(p.vertices)-2 for p in o.data.polygons),
                 boundaryEdges=sum(e.is_boundary for e in bm.edges),
                 nonmanifoldEdges=sum(not e.is_manifold for e in bm.edges),
                 looseVertices=sum(not v.link_edges for v in bm.verts),
                 connectedComponents=sorted(components, reverse=True),
                 uvLayers=[uv.name for uv in o.data.uv_layers],
                 materialSlots=[sl.material.name if sl.material else None for sl in o.material_slots],
                 vertexGroups=[g.name for g in o.vertex_groups],
                 modifiers=[{'name':m.name,'type':m.type} for m in o.modifiers],
                 shapeKeys=[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else [])
        bm.free()
    elif o.type == 'ARMATURE':
        d['bones'] = [{'name': b.name,'parent':b.parent.name if b.parent else None,
                       'head':list(b.head_local),'tail':list(b.tail_local)} for b in o.data.bones]
    report['objects'].append(d)
for m in bpy.data.materials:
    if not any(m == slot.material for o in meshes for slot in o.material_slots): continue
    report['materials'].append({'name':m.name,'nodes':[
        {'name':n.name,'type':n.bl_idname,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None}
        for n in m.node_tree.nodes] if m.use_nodes else []})
for im in bpy.data.images:
    if im.source != 'FILE': continue
    # Restore archive-relative textures only; do not fetch remote resources.
    match = next((p for p in cache.rglob('*') if p.is_file() and p.name == Path(im.filepath.replace('\\','/')).name), None)
    if match: im.filepath = str(match); im.reload()
    report['images'].append({'name':im.name,'size':list(im.size),'loaded':im.has_data,
                              'colorSpace':im.colorspace_settings.name,'file':str(match.relative_to(cache)) if match else None})
    if im.has_data: im.pack()
for a in bpy.data.actions:
    report['actions'].append({'name':a.name,'frameRange':list(a.frame_range)})
coords = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector([min(c[i] for c in coords) for i in range(3)])
hi = Vector([max(c[i] for c in coords) for i in range(3)])
report['worldBounds'] = {'min':list(lo),'max':list(hi),'size':list(hi-lo)}
report['rigged'] = bool(rigs)
report['modularObjects'] = len(meshes)
root = bpy.data.objects.new('ROOT_FantasyInspection',None); s.collection.objects.link(root)
root.location = ((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)
for o in source:
    if o.parent is None:
        mw = o.matrix_world.copy(); o.parent = root; o.matrix_world = mw
height = hi.z-lo.z
target = Vector((root.location.x,root.location.y,lo.z+height*.49))
bpy.ops.object.camera_add()
cam = bpy.context.object; cam.name = 'CAM_FantasyInspection'
cam.data.type = 'ORTHO'; cam.data.ortho_scale = max(height*1.2,(hi.x-lo.x)*1.2)
cam.rotation_euler = (math.radians(75),0,0)
cam.location = target - (cam.rotation_euler.to_matrix() @ Vector((0,0,-1))) * (height*5)
s.camera = cam
world = bpy.data.worlds.new('FantasyInspectionWorld'); world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.32,.32,.32,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.65;s.world=world
for name,loc,power,size in [('Key',(-3,-4,5),800,5),('Fill',(4,-1,3),400,4),('Rim',(1,4,4),600,4)]:
    bpy.ops.object.light_add(type='AREA', location=root.location + Vector(loc)*height*.5)
    light=bpy.context.object; light.name='LIGHT_Fantasy'+name
    light.data.energy=power*(height/2)**2;light.data.shape='DISK';light.data.size=size*height*.5
    light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=640;s.render.resolution_y=640
s.render.resolution_percentage=100;s.render.film_transparent=True
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
s.view_settings.view_transform='Standard';s.view_settings.look='None'
s['sourceInspectionReport']=json.dumps(report);s['ownerApproved']=False;s['runtimeAdmitted']=False
(out/'inspection.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(native))
for direction,yaw in [('S',0),('SW',-45),('W',-90),('NW',-135),('N',-180),('NE',-225),('E',-270),('SE',45)]:
    root.rotation_euler.z=math.radians(yaw)
    s.render.filepath=str(out/'renders'/(direction+'-source.png'))
    bpy.ops.render.render(write_still=True)
    print('FANTASY_INSPECTION_VIEW '+direction,flush=True)
print('FANTASY_INSPECTION_COMPLETE '+json.dumps({'meshes':len(meshes),'rigs':len(rigs),'actions':len(report['actions']),'native':str(native)}),flush=True)
