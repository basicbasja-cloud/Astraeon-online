"""Local experimental portable character export, not game admission."""
import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'original-character.blend'));sc=bpy.context.scene;sc.frame_set(1);bpy.ops.object.select_all(action='DESELECT');names=[]
for o in sc.objects:
 if o.name=='Astraeon_Free_Local' or o.type=='MESH' and 'runtime_slot' in o:o.select_set(True);names.append(o.name)
bpy.ops.export_scene.gltf(filepath=str(P/'original-character-experimental.glb'),export_format='GLB',use_selection=True,export_skins=True,export_animations=True,export_frame_range=True,export_force_sampling=True,export_extras=True)
(P/'export-receipt.json').write_text(json.dumps(dict(blend_sha256=hashlib.sha256((P/'original-character.blend').read_bytes()).hexdigest(),export_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((P/'original-character-experimental.glb').read_bytes()).hexdigest(),selected_objects=names,scope='Experimental fully weighted character; original procedural local geometry, PBR colors, body_outfit/complete_head extras. Export samples30fps, 1.3sec. Collectible intentionally excluded: runtime inventory/contact event and visibility not exported. No engine import or final art approval.',production_pass=False),indent=2)+'\n')
