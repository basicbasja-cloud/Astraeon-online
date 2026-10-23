"""Capture one colored mannequin diagnostic without changing canonical guide code.

Only material assignments change. This is a source-pose painting reference, never
final art or a replacement ledger guide. Runs inside Blender with --job/--output
arguments accepted by render_patch001_guides.py (normally also --static).
"""
from pathlib import Path
import hashlib,json,sys
import bpy
from bpy.app.handlers import persistent
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_patch001_guides

PALETTE={'head':(.65,.42,.27,1),'cloth':(.17,.25,.12,1),'sleeve':(.76,.71,.57,1),'glove':(.20,.095,.035,1),'pants':(.20,.23,.12,1),'boot':(.23,.12,.055,1)}

@persistent
def material_reference(scene):
    for obj in scene.objects:
        if obj.type!='MESH'or obj.hide_render or obj.name=='Icosphere':continue
        names={g.index:g.name for g in obj.vertex_groups}
        if not names:continue
        mats={}
        for role,color in PALETTE.items():
            name='Diagnostic_'+role;mat=bpy.data.materials.get(name)or bpy.data.materials.new(name);mat.diffuse_color=color;obj.data.materials.append(mat);mats[role]=len(obj.data.materials)-1
        for face in obj.data.polygons:
            weights={}
            for index in face.vertices:
                for group in obj.data.vertices[index].groups:
                    name=names.get(group.group,'');weights[name]=weights.get(name,0)+group.weight
            name=max(weights,key=weights.get)if weights else ''
            if name.startswith(('head','neck')):role='head'
            elif name.startswith(('thumb','index','middle','ring','pinky','hand')):role='glove'
            elif name.startswith(('upperarm','lowerarm','clavicle')):role='sleeve'
            elif name.startswith(('calf','foot','ball')):role='boot'
            elif name.startswith(('thigh','pelvis')):role='pants'
            else:role='cloth'
            face.material_index=mats[role]

bpy.app.handlers.render_pre.append(material_reference)
argv=sys.argv[sys.argv.index('--')+1:];job=json.loads(Path(argv[argv.index('--job')+1]).read_text())
try:
    if job.get('render_pose_freeze_revision'):
        from render_frozen_patch001_guides import run_capture
        run_capture(render_patch001_guides.main)
    else:render_patch001_guides.main()
finally:
    if material_reference in bpy.app.handlers.render_pre:bpy.app.handlers.render_pre.remove(material_reference)
argv=sys.argv[sys.argv.index('--')+1:];out=Path(argv[argv.index('--output')+1]);path=out/'manifest.json';receipt=json.loads(path.read_text());receipt['status']='NONCANONICAL_COLORED_MANNEQUIN_DIAGNOSTIC_NOT_FINAL_ART';receipt['material_diagnostic']={'handler_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'palette':PALETTE,'geometry_changed':False,'canonical_guide_replaced':False,'runtime_admitted':False};path.write_text(json.dumps(receipt,indent=2)+'\n')
