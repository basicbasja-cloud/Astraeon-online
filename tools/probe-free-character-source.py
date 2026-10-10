"""Blender headless compatibility probe for the pinned local MPFB release."""
from pathlib import Path
import sys
import json
import bpy

ROOT = Path(__file__).resolve().parents[1]
tool_source = ROOT / '.character-tools/mpfb-2.0.17/mpfb2-2.0.17/src'
bpy.context.preferences.extensions.repos.new(name='ASTRAEON local tools', module='character_local', custom_directory=str(tool_source))
bpy.ops.preferences.addon_enable(module='bl_ext.character_local.mpfb')
from bl_ext.character_local.mpfb.services.humanservice import HumanService
from bl_ext.character_local.mpfb.services.targetservice import TargetService

out = ROOT / 'authoring/characters/swordsman-production/free-master-01'
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
macro = TargetService.get_default_macro_info_dict()
macro.update(gender=1.0, age=0.22, muscle=0.4, weight=0.45)
body = HumanService.create_human(macro_detail_dict=macro)
rig = HumanService.add_builtin_rig(body, 'default_no_toes')
receipt = {
    'blender': bpy.app.version_string, 'mpfb': '2.0.17',
    'status': 'BODY_AND_WEIGHTED_RIG_CREATED', 'macro': macro,
    'vertices': len(body.data.vertices), 'faces': len(body.data.polygons),
    'dimensions': list(body.dimensions),
    'vertexGroups': [g.name for g in body.vertex_groups],
    'bones': {b.name: {'head': list(b.head_local), 'tail': list(b.tail_local)} for b in rig.data.bones},
    'shapeKeys': [k.name for k in body.data.shape_keys.key_blocks],
    'bodyBounds': {a: [min(v.co[i] for v in body.data.vertices), max(v.co[i] for v in body.data.vertices)] for i, a in enumerate('xyz')},
}
(out / 'compatibility.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'mpfb-baseline.blend'))
print('MPFB_PROBE_PASS', json.dumps({k: receipt[k] for k in ('blender', 'mpfb', 'status', 'vertices', 'faces', 'dimensions')}))
