"""Check actual ordered atlas pixels and bounded equipment substitutions."""
import hashlib,importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'authoring/characters/swordsman-production/fantasy-base-01';DEST=OUT/'runtime'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('depth_packer',ROOT/'tools/pack-character-sprites.py');pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
d=read(DEST/'assets/characters/fantasy-golden-01/sprite.json');sets=read(DEST/'appearance-sets.json');p=read(OUT/'package.json');bank=read(OUT/'factory/swap-bank.json')
swapkey=hashlib.sha256((bank['bankSHA256']+sha(ROOT/'tools/bake-fantasy-swap-bank.py')).encode()).hexdigest()[:16]
base=ROOT/'.character-tools/sprite-bakes'/p['cacheKey'];swap=ROOT/'.character-tools/swap-bakes'/swapkey
cases={'default':{'outfit':'default','weapon':'default','headgear':'none','offhand':'none','cape':'default'},
       'equipment':{'outfit':'default','weapon':'default','headgear':'default','offhand':'default','cape':'default'},
       'alternate':{'outfit':'alternate','weapon':'alternate','headgear':'default','offhand':'default','cape':'default'},
       'capeRemoved':{'outfit':'default','weapon':'default','headgear':'default','offhand':'default','cape':'none'}}
evidence=[];garment_geometry_pixels=0
for action in ['Idle','Walk','BasicAttack','Guard','Death']:
    count=len(d['clips'][action]['durations']);indices=sorted(set([0,count//2,count-1]));atlas={}
    for part in d['parts'].values():
        for id,ref in part['frames'].items():
            if '_'+action+'_' in id and ref['atlasId'] not in atlas:atlas[ref['atlasId']]=np.asarray(Image.open(DEST/d['atlases'][ref['atlasId']]['file']).convert('RGBA'))
    for direction in p['directions']:
        for index in indices:
            tag=f'{direction}-{index+1:03}';a=np.asarray(Image.open(base/action/(tag+'-tile.png')).convert('RGBA'));az=np.asarray(Image.open(base/action/(tag+'-depth.png')))
            b=np.asarray(Image.open(swap/action/(tag+'-tile.png')).convert('RGBA'));bz=np.asarray(Image.open(swap/action/(tag+'-depth.png')))
            if action=='Idle' and direction=='SE' and index==0:
                garment_geometry_pixels=int(np.sum((a[:,320:640,3]>224)&(b[:,:320,3]>224)&(np.abs(az[:,320:640].astype(np.int32)-bz[:,:320].astype(np.int32))>1)))
            for case,choices in cases.items():
                appearance={s:part for group,choice in choices.items() for s,part in sets[group][choice].items()}
                colors={'BodyOutfit':b[:,:320] if choices['outfit']=='alternate' else a[:,320:640],'HeadHair':a[:,640:960],
                        'Weapon':b[:,320:640] if choices['weapon']=='alternate' else a[:,960:1280],
                        'Cape':a[:,1280:1600] if choices['cape']=='default' else np.zeros((320,320,4),np.uint8),
                        'Headgear':b[:,640:960] if choices['headgear']=='default' else np.zeros((320,320,4),np.uint8),
                        'Offhand':b[:,960:1280] if choices['offhand']=='default' else np.zeros((320,320,4),np.uint8)}
                depths={'BodyOutfit':bz[:,:320] if choices['outfit']=='alternate' else az[:,320:640],'HeadHair':az[:,640:960],'Weapon':bz[:,320:640] if choices['weapon']=='alternate' else az[:,960:1280],
                        'Cape':az[:,1280:1600],'Headgear':bz[:,640:960],'Offhand':bz[:,960:1280]}
                expected=pack.compose(colors,depths,list(colors));rgb=np.zeros((320,320,3),np.float32);alpha=np.zeros((320,320,1),np.float32)
                for slot in d['drawOrder']:
                    partid=appearance.get(slot,d['defaultParts'][slot]);id=f"{d['characterId']}_{partid}_{action}_{direction}_{index:02}";ref=d['parts'][partid]['frames'][id]
                    x,y,w,h=ref['rect'];image=atlas[ref['atlasId']][y:y+h,x:x+w].astype(np.float32)/255;a2=image[:,:,3:4];rgb=image[:,:,:3]*a2+rgb*(1-a2);alpha=a2+alpha*(1-a2)
                result=np.uint8(np.rint(np.clip(np.concatenate([np.divide(rgb,alpha,out=np.zeros_like(rgb),where=alpha>0),alpha],axis=2)*255,0,255)))
                error=int(np.max(np.abs(result.astype(np.int16)-expected.astype(np.int16))))
                assert error<=2,(case,action,direction,index,error)
                evidence.append({'case':case,'action':action,'direction':direction,'frame':index+1,'maximumRGBAError':error})
    del atlas
compat=read(OUT/'factory/runtime-compatibility.json');covered=sum(r['opaqueHandCoveredWeaponPixels'] for r in compat['holdout']);bad=sum(r['residualPixelsAbove96'] for r in compat['holdout'])
assert covered>5000 and bad/covered<.05,(covered,bad)
assert garment_geometry_pixels>30, ('Alternate outfit has no meaningful geometric depth change',garment_geometry_pixels)
report={'technicalVerdict':'PASS','nativeSHA256':p['nativeSHA256'],'cases':len(evidence),'maximumRGBAError':max(r['maximumRGBAError'] for r in evidence),
        'coveredHiltPixels':covered,'coveredHiltResidualPixelsAbove96':bad,'coveredHiltResidualFraction':bad/covered,
        'holdoutNote':'Independent multisampled cells can disagree at subpixel edges; opaque hand/weapon overlap residuals retained, bounded below 5%.',
        'alternateGarmentChangedDepthPixelsSE':garment_geometry_pixels,'clippedEquipmentBorders':compat['clippedEquipmentBorders'],
        'motionReauthoredForVariations':False,'bodyGeometryChangedForWeaponSwap':False,'rendererChanged':False,'ownerApproved':False,'evidence':evidence}
(OUT/'factory/runtime-test-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='evidence'},indent=2))
