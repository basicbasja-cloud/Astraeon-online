"""Read-only raster metrics, license receipts, preservation and file manifests.

No image pixels are created, painted, resized or changed by this recorder.
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parents[1]
out=root/'authoring/characters/swordsman-production/asset-fit-04'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
reference=out.parent/'fresh-2d/candidate-01/candidate.png'
assert digest(reference)=='2fa0145d82ae3eabd6c04aadbf89d485b2bf0b0db3c228d278ca95b7f463253b'
preservation={}
for name in ['free-master-01','reference-fit-01','source-refinement-02']:
    folder=out.parent/name;manifest=json.loads((folder/'artifact-manifest.json').read_text(encoding='utf-8-sig'))
    changed=[p for p,m in manifest.items() if digest(folder/p)!=m['sha256']]
    assert not changed,(name,changed)
    preservation[name]={'filesChecked':len(manifest),'changedFiles':changed}
receipt=json.loads((out/'source-check-receipt.json').read_text(encoding='utf-8'))
modules=['BaseBody','Hair','Outfit','Weapon','BackAccessory'];directions={};proof={}
for d in ['S','SW','W','NW','N','NE','E','SE']:
    path=out/f'renders/{d}-final-static.png';im=Image.open(path).convert('RGBA');assert im.size==(320,320)
    a=np.asarray(im);mask=a[:,:,3]>128;y,x=np.where(mask)
    directions[d]={'canvas':[320,320],'alphaBounds':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],'alphaHeight':int(y.max()-y.min()+1)}
    merged=Image.new('RGBA',(320,320))
    for name in modules:
        part=Image.open(out/f'renders/equipped-layer-{name}-{d}.png').convert('RGBA');assert part.size==im.size
        merged=Image.alpha_composite(merged,part)
    b=np.asarray(merged)
    proof[d]={'coverageMismatchPixels':int(np.sum(mask!=(b[:,:,3]>128))),
              'opaqueMeanRGBError':float(np.mean(np.abs(a[:,:,:3].astype(float)-b[:,:,:3].astype(float))[mask]))}
weapon={d:{kind:int(np.sum(np.asarray(Image.open(out/f'renders/Weapon-{kind}-{d}-fullcanvas.png'))[:,:,3]>128)) for kind in ['visible','isolated']} for d in ['SE','W','NW','N']}
grip={d:{kind:int(np.sum(np.asarray(Image.open(out/f'renders/weapon-{kind}-{d}.png'))[:,:,3]>128)) for kind in ['isolated','hand-masked']} for d in ['SE','W','NW','N']}
assets=json.loads((out/'FREE_ASSET_PROVENANCE.json').read_text(encoding='utf-8'))
for record in assets['assets']:
    actual=digest(root/record['archive'])
    # Digest from the actual downloaded archive is authoritative. The initial
    # transcription is retained if it differed, never silently discarded.
    if record['sha256']!=actual:record['initialDigestTranscription']=record['sha256']
    record['sha256']=actual;record['bytes']=(root/record['archive']).stat().st_size
    if 'licenseCopy' in record:record['licenseSHA256']=digest(out/record['licenseCopy'])
write(out/'FREE_ASSET_PROVENANCE.json',assets)
scripts=['import-free-character-references.py','fit-free-character-study.py','refit-free-character-costume.py',
         'refine-free-character-style.py','repair-free-character-grip.py','finish-free-character-surfaces.py',
         'close-free-character-costume-gaps.py','inspect-free-character-grip.py',
         'bake-free-character-source-checks.py','record-free-character-source.py']
native=root/'.character-tools/checkpoints/asset-fit-04-native.blend';assert native.is_file()
write(out/'provenance.json',{'date':'2026-10-11','branch':'character/production-factory-v2','originalConceptSHA256':digest(reference),
 'scripts':{s:digest(root/'tools'/s) for s in scripts},'nativeWorkingCopy':{'path':str(native),'sha256':digest(native),'bytes':native.stat().st_size,'scope':'Local working project with inspection scenes; not standalone asset package'},
 'sourceTextureFix':'Correct eye-normal file loaded and packed; no 0x0 texture in active source',
 'sourceLicenseReceipt':'FREE_ASSET_PROVENANCE.json','paintAtlasSHA256':digest(out.parent/'source-lookdev-03/paint/material-atlas.png'),
 'ownerApproved':False,'runtimeAdmitted':False,'paidJobs':[]})
write(out/'validation.json',{'date':'2026-10-11','verdict':'NO_SHIP','ownerApproved':False,'runtimeAdmitted':False,'motionCoverage':[],
 'scene':receipt['scene'],'armatures':0,'sourceBody':{k:receipt[k] for k in ['vertices','faces','quads','triangles','boundaryEdges','nonmanifoldEdges','maxInheritedWeights','minInheritedWeightSum','maxInheritedWeightSum']},
 'canvas':[320,320],'root':[160,264],'runtimeScale':.5,'runtimeCanvas':[160,160],'runtimeRoot':[80,132],
 'directions':directions,'equippedLayerProof':{'scope':'All eight static equipped frames; visible-only modules, not arbitrary substitution','order':modules,'perDirection':proof},
 'weaponFullCanvasPixels':weapon,'diagnosticWeaponGripCoverage':grip,'preservation':preservation,
 'defects':['Approved likeness/painted quality not reached','NW full-character blade occluded','Inherited triangles/poles need joint topology review','FBX inherited weights need normalization and deformation review','No custom rig or actions','Visible-only layers are pose/equipment-specific']})
for folder in [out.parent/'source-lookdev-03',out]:
    files={str(p.relative_to(folder)).replace('\\','/'):{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='artifact-manifest.json' and not p.name.endswith('.blend1')}
    write(folder/'artifact-manifest.json',files)
print(json.dumps({'directions':directions,'layerProof':proof,'weaponPixels':weapon,'gripCoverage':grip,'preservation':preservation,'nativeBytes':native.stat().st_size},indent=2))
