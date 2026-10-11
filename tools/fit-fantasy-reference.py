"""Calibrate the new base against measured approved head/height proportions.

One source-space fit and one fixed camera serve every view/action. Source UVs,
digit lengths and body anatomy are retained; no bone pose scaling is used.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;rig=bpy.data.objects[s['rigObject']];root=bpy.data.objects[s['rootObject']]
assert 'referenceCalibration' not in s,'Fit once from the pre-calibration source.'
base=Path(__file__).resolve().parents[1]
reference=json.loads((base/'authoring/characters/swordsman-production/reference-fit-01/fit-spec.json').read_text())
head=bpy.data.objects['F01_HeadHair'];pivot=Vector((0,.028,.813));head_scale=1.48;origin_y=.054
for v in head.data.vertices:v.co=pivot+(v.co-pivot)*head_scale
# Anchor the midpoint of the projected soles rather than the original import's
# arbitrary FBX origin. All meshes and fitted rest bones move together on floor.
for o in s.objects:
    if o.type=='MESH':
        for v in o.data.vertices:v.co.y+=origin_y
        o.data.update()
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for b in rig.data.edit_bones:
    if b.name!='root':b.head.y+=origin_y;b.tail.y+=origin_y
bpy.ops.object.mode_set(mode='OBJECT')
contact=json.loads(s['swordContact']);contact['centerModel'][1]+=origin_y;s['swordContact']=json.dumps(contact)
old_span=s.camera.data.ortho_scale;new_span=old_span*1.14
s.camera.location+=Vector((0,math.cos(math.radians(65)),math.sin(math.radians(65))))*((new_span-old_span)*104/320)
s.camera.data.ortho_scale=new_span;s['originShiftY']=origin_y
calibration={'reference':reference['reference'],'referenceSHA256':reference['referenceSha256'],
             'referenceBounds':reference['alphaBounds'],'referenceRoot':reference['referenceRoot'],
             'referenceHeadFraction':(reference['landmarks']['chin'][1]-reference['landmarks']['hair_top'][1])/(reference['alphaBounds'][3]-reference['alphaBounds'][1]),
             'preFitSEHeadBounds':[137,95,174,133],'preFitSECompositeBounds':[96,95,199,278],
             'headScale':head_scale,'bodyScale':1,'groundOriginShiftY':origin_y,'orthoScale':new_span,
             'canvas':[320,320],'root':[160,264],'directionsShareFit':True,'ownerApproved':False,
             'note':'One measured fit; hidden anatomy and perspective remain source inferences, not owner-approved geometry.'}
s['referenceCalibration']=json.dumps(calibration)
(base/'authoring/characters/swordsman-production/fantasy-base-01/reference-calibration.json').write_text(json.dumps(calibration,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(base/'.character-tools/checkpoints/fantasy-base-01-fitted.blend'))
print('FANTASY_REFERENCE_CALIBRATED '+json.dumps(calibration),flush=True)
