"""Record free-asset licenses and read-only validation of the anatomy study."""
from pathlib import Path
import json,hashlib,struct,urllib.request
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
out=root/'authoring/characters/swordsman-production/anatomy-base-05'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=True)+'\n',encoding='utf-8',newline='\n')
concept=out.parent/'fresh-2d/candidate-01/candidate.png'
assert sha(concept)=='2fa0145d82ae3eabd6c04aadbf89d485b2bf0b0db3c228d278ca95b7f463253b'
assets=[]
specs=[
 ('vroid-base-male','extracted/Base_Male.vrm','https://opengameart.org/sites/default/files/base_male.zip','active anatomy/head donor'),
 ('vroid-fumiriya','Sakurada_Fumiriya.vrm','https://raw.githubusercontent.com/madjin/vrm-samples/master/vroid/beta/Sakurada_Fumiriya.vrm','inspection and inactive hair comparison; not selected'),
 ('vroid-hair-male','HairSample_Male.vrm','https://raw.githubusercontent.com/madjin/vrm-samples/master/vroid/beta/HairSample_Male.vrm','inactive hair comparison; did not match approved design'),
 ('vroid-shibu','Sendagaya_Shibu.vrm','https://raw.githubusercontent.com/madjin/vrm-samples/master/vroid/beta/Sendagaya_Shibu.vrm','download inspected as JSON; not imported')]
for folder,name,url,use in specs:
    path=root/'.character-tools/free-assets'/folder/name;data=path.read_bytes()
    length=struct.unpack_from('<I',data,12)[0];document=json.loads(data[20:20+length]);meta=document['extensions']['VRM']['meta']
    assert meta['licenseName']=='CC0' and meta['commercialUssageName']=='Allow'
    item={'name':meta['title'],'creator':'pixiv Inc. / VRoid Project','license':'CC0-1.0','use':use,'cache':str(path.relative_to(root)).replace('\\','/'),'downloadURL':url,'sha256':sha(path),'bytes':len(data),'embeddedMetadata':meta}
    if folder=='vroid-base-male':
        archive=path.parent.parent/'source.zip';item['archive']={'sha256':sha(archive),'bytes':archive.stat().st_size}
    assets.append(item)
license_path=out/'publisher-license-evidence.json'
if not license_path.exists():
    url='https://vroid.pixiv.help/api/v2/help_center/en-us/articles/4402614652569.json'
    with urllib.request.urlopen(url,timeout=30) as response:evidence=json.load(response)
    article=evidence['article'];assert 'CC0' in article['body']
    write(license_path,{'retrieved':'2026-10-11','url':url,'article':article})
write(out/'FREE_ASSET_PROVENANCE.json',{'authorization':'Owner explicitly authorized free asset downloads and polishing on 11 October 2026','publisherLicenseEvidence':'publisher-license-evidence.json','publisherURL':'https://vroid.pixiv.help/hc/en-us/articles/4402614652569-Do-VRoid-Studio-s-sample-models-come-with-conditions-of-use-','assets':assets,'paidJobs':[],'rawDownloadsVendored':False})
receipt=json.loads((out/'source-receipts.json').read_text(encoding='utf-8'))
directions={};proof={};weapon={}
for d in receipt['modules']['directions']:
    image=Image.open(out/f'renders/{d}-current.png').convert('RGBA');assert image.size==(320,320)
    a=np.asarray(image);mask=a[:,:,3]>128;y,x=np.where(mask)
    directions[d]={'bounds':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],'height':int(y.max()-y.min()+1),'canvas':[320,320]}
    merged=Image.new('RGBA',(320,320))
    for part in receipt['modules']['bakedParts']:
        layer=Image.open(out/f'renders/modular-{part}-{d}.png').convert('RGBA');assert layer.size==image.size
        merged=Image.alpha_composite(merged,layer)
    b=np.asarray(merged)
    proof[d]={'coverageMismatchPixels':int(np.sum(mask!=(b[:,:,3]>128))),'opaqueMeanRGBError':float(np.mean(np.abs(a[:,:,:3].astype(float)-b[:,:,:3].astype(float))[mask]))}
    weapon[d]={kind:int(np.sum(np.asarray(Image.open(out/f'renders/weapon-{kind}-{d}.png'))[:,:,3]>32)) for kind in ['visible','isolated']}
assert max(v['coverageMismatchPixels'] for v in proof.values())<30,proof
native=root/'.character-tools/checkpoints/anatomy-base-05-native.blend';assert native.exists()
scripts=['build-anatomical-hand-study.py','refine-anatomical-hand-study.py','build-vroid-anatomy-source-study.py','polish-vroid-anatomy-source-study.py','correct-anatomy-source-contact.py','refine-anatomy-source-face-pose.py','probe-anatomy-weapon-clearance.py','refine-anatomy-weapon-clearance.py','polish-anatomy-source-clothing.py','compare-free-fumiriya-hair.py','bake-new-anatomy-source-checks.py','bake-anatomy-source-modules.py','record-anatomy-source-study.py']
write(out/'provenance.json',{'date':'2026-10-11','branch':'character/production-factory-v2','conceptSHA256':sha(concept),'nativeWorkingCopy':{'path':str(native),'sha256':sha(native),'bytes':native.stat().st_size,'scope':'Local working project with isolated reference scenes; not a release package'},'scripts':{name:sha(root/'tools'/name) for name in scripts},'ownerApproved':False,'runtimeAdmitted':False,'paidJobs':[]})
write(out/'validation.json',{'verdict':'NO_SHIP','ownerApproved':False,'runtimeAdmitted':False,'motionCoverage':[],'source':receipt['source']['topology'],'directions':directions,'modularProof':proof,'weaponPixels':weapon,'preservedConceptSHA256':sha(concept),'defects':['Approved painted likeness and costume silhouette not reached','Rear sword visibility needs review','Static fitted anatomy is inferred; no accepted production bind','Body has 156 boundary edges; topology and joint deformation gate unresolved','No production rig or action coverage','Equipped layers are combination-specific, not arbitrary substitution proof']})
write(out/'artifact-manifest.json',{str(p.relative_to(out)).replace('\\','/'):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='artifact-manifest.json'})
print(json.dumps({'freeAssets':len(assets),'weaponPixels':weapon,'modularProof':proof,'nativeBytes':native.stat().st_size,'conceptUnchanged':True},indent=2))
