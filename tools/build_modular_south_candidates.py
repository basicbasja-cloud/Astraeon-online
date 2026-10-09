#!/usr/bin/env python3
"""Seal rejected South candidates without pretending the visual gate passed.

New components remain independent source bytes. No whole-character extraction,
alpha-bounds fitting, garment warping, missing-layer sprites or direction stubs.
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from build_painted_swordsman import grid

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'authoring/characters/true-modular/swordsman-male-v2'
OUT = ROOT/'assets/characters/swordsman-true-modular-v2'
REVIEW = ROOT/'docs/review/character-true-modular-v2'
MD = ROOT/'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return str(p.relative_to(ROOT))
def write(p,d): p.write_text(json.dumps(d,indent=2)+'\n')
def opaque_bounds(im,threshold=128):
    ys,xs=np.where(np.array(im)[:,:,3]>threshold)
    return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None

def build():
    OUT.mkdir(parents=True,exist_ok=True); REVIEW.mkdir(parents=True,exist_ok=True)
    c=json.loads((SRC/'pose-contract.json').read_text()); t=json.loads(MD.read_text())
    contract_sha=digest(SRC/'pose-contract.json'); pose=c['pose']['poseId']
    records={}; images={}; transforms={}
    for name,prompt in [('bodycore','bodycore-repair'),('headbase','headbase'),('face','face'),('outfit-a','outfit-repair')]:
        raw=SRC/'sources'/f'{name}-raw.png'; source=Image.open(raw).convert('RGBA')
        if source.width!=source.height: raise ValueError('Whole shared canvas must be square: '+name)
        im=source.resize((320,320),Image.Resampling.LANCZOS)
        # One recorded initial BodyCore root calibration; no per-layer repairs
        # are applied to the failed Outfit or Face to hide their misregistration.
        offset=(0,-3) if name=='bodycore' else (0,0)
        if offset!=(0,0):
            translated=Image.new('RGBA',(320,320));translated.alpha_composite(im,offset);im=translated
        target=OUT/f'{name}.png';im.save(target)
        images[name]=im
        p=SRC/f'{prompt}-prompt.txt'
        records[name]={'rawSource':rel(raw),'rawSHA256':digest(raw),'file':rel(target),'rasterSHA256':digest(target),
          'canvas':[320,320],'prompt':rel(p),'promptSHA256':digest(p),'provider':'built-in ImageGen','poseId':pose,
          'normalization':'whole-canvas resample; no alpha cutting or bounds fitting',
          'candidateReview':'REJECTED' if name in ['face','outfit-a'] else 'PROVISIONAL'}
        transforms[name]={'rawCanvas':list(source.size),'scale':320/source.width,'translation':list(offset),
          'opaqueBounds':opaque_bounds(im),'sourcePreserved':True}

    # Preserve useful originally-isolated v1 sword authoring. Crop its designated
    # source SHEET CELL, never pixels from a complete painted character.
    sword_source=ROOT/'authoring/characters/appearance/weapons/swordsman-sword/generated/weapons-raw.png'
    sword=grid(sword_source,6,4,primary=True)[0]
    bb=sword.getbbox(); crop=sword.crop(bb); ratio=crop.width/crop.height
    size=(max(7,round(101*ratio*.58)),101)
    tile=Image.new('RGBA',(48,128));xy=((48-size[0])//2,(128-size[1])//2)
    tile.alpha_composite(crop.resize(size,Image.Resampling.LANCZOS),xy)
    pivot=[xy[0]+size[0]*.5,xy[1]+size[1]*.86]
    a=c['pose']['anchors']['mainHand'];co=math.cos(a['rotation']);si=math.sin(a['rotation'])
    scale=a['scale'];ia=co/scale;ib=si/scale;ic=pivot[0]-ia*a['x']-ib*a['y']
    id_=-si/scale;ie=co/scale;iff=pivot[1]-id_*a['x']-ie*a['y']
    im=tile.transform((320,320),Image.Transform.AFFINE,(ia,ib,ic,id_,ie,iff),Image.Resampling.BICUBIC)
    target=OUT/'weapon-a.png';im.save(target);images['weapon-a']=im
    job_path=ROOT/'authoring/characters/builds/swordsman-male/repair-and-component-jobs.json'
    job=next(j for j in json.loads(job_path.read_text()) if j['name']=='weapon-components')
    p=SRC/'weapon-baseline-prompt.txt';p.write_text(job['prompt']+'\n')
    records['weapon-a']={'rawSource':rel(sword_source),'rawSHA256':digest(sword_source),'sourceRegion':{'grid':[6,4],'cell':0},
      'file':rel(target),'rasterSHA256':digest(target),'canvas':[320,320],'prompt':rel(p),'promptSHA256':digest(p),
      'provider':'built-in ImageGen (baseline reuse)','poseId':pose,'candidateReview':'PROVISIONAL',
      'baselineReceipt':rel(job_path),'normalization':'v1 isolated sword cell and grip pivot; shared South mainHand anchor'}
    transforms['weapon-a']={'sourceCell':0,'canonicalTile':[48,128],'size':list(size),'pivot':pivot,'sharedAnchor':a,'opaqueBounds':opaque_bounds(im)}

    slots={'BodyCore':{'required':True,'layers':['BodyCore']},'HeadBase':{'required':True,'layers':['HeadBase']},
      'Face':{'required':True,'layers':['Face']},'Outfit':{'required':True,'layers':['OutfitFront']},
      'Hair':{'required':True,'layers':['HairBack','HairFront']},'Weapon':{'required':False,'layers':['Weapon']}}
    layer_names={'bodycore':('BodyCore','BodyCore'),'headbase':('HeadBase','HeadBase'),'face':('Face','Face'),
      'outfit-a':('Outfit','OutfitFront'),'weapon-a':('Weapon','Weapon')}
    parts={name:{'slot':slot,'poseId':pose,'contractSHA256':contract_sha,'authorship':'ISOLATED_COMPONENT_FROM_INCEPTION',
      'layers':{layer:records[name]}} for name,(slot,layer) in layer_names.items()}
    manifest={'schemaVersion':'2.0-authoring','packId':'swordsman-male-true-modular-south-candidate-v2','classId':'Swordsman',
      'bodyVariant':'male','status':'REQUIRES_OWNER_VISUAL_REVIEW','ownerApproval':'PENDING','directionOrder':t['directions'],
      'mirroring':'none','motionTemplateId':t['motionTemplateId'],'registration':t['registration'],'poseId':pose,
      'contractSHA256':contract_sha,'availablePoses':[pose],'authorship':'ISOLATED_COMPONENT_FROM_INCEPTION',
      'authoritativeSources':'independent painted rasters','slots':slots,
      'defaultParts':dict(BodyCore='bodycore',HeadBase='headbase',Face='face',Outfit='outfit-a',Hair=None,Weapon='weapon-a'),
      'parts':parts,'drawOrder':['HairBack','BodyCore','HeadBase','Face','OutfitFront','HairFront','Weapon'],
      'gates':{'south':'VISUAL_FAIL','cosmeticSwaps':'NOT_STARTED_GATE3_BLOCKED','eightDirectionIdle':'NOT_STARTED_GATE3_BLOCKED',
        'Walk':'NOT_STARTED_GATE3_BLOCKED','BasicAttack':'NOT_STARTED_GATE3_BLOCKED'},
      'missingComponents':['HairBack','HairFront'],'runtimeInstallation':False,
      'nextMethod':'Coordinate-constrained layered painting or lossless layer export from an art document. Do not repeat unconstrained whole-canvas component generation.'}
    write(SRC/'source-manifest.json',manifest)
    write(SRC/'normalization-receipt.json',{'contractSHA256':contract_sha,'sourceTransforms':transforms,'rasterSources':records,
      'rawROPixelsUsed':False,'destructiveCharacterDecomposition':False,'sourceHashValidation':'required on each read'})
    failures={'southGate':'VISUAL_FAIL','ownerApproval':'PENDING','sourceCoverageComplete':False,
      'checks':{'outfitTopOutsideHeadZone':transforms['outfit-a']['opaqueBounds'][1]>=128,
        'faceWithinHeadZone':transforms['face']['opaqueBounds'][3]<=150},
      'measurements':{'HeadBase':transforms['headbase']['opaqueBounds'],'Face':transforms['face']['opaqueBounds'],
        'Outfit':transforms['outfit-a']['opaqueBounds']},
      'issues':['Outfit collar/shoulder/hand proportions do not match BodyCore after two attempts.',
        'Face contains a skin patch rather than only isolated feature strokes; it is below HeadBase.',
        'BodyCore is too muscular for compact identity; HeadBase/neck still provisional.',
        'HairBack/HairFront were not authored because the shared registration method failed; no empty sources substituted.',
        'Sword was originally authored independently; shared grip placement needs a passing outfit before visual approval.']}
    write(REVIEW/'visual-gate.json',failures)
    # One compact failed-decomposition board; missing sources are text panels,
    # never transparent raster assets that pretend to complete the contract.
    board=Image.new('RGBA',(1280,720),'#344352'); d=ImageDraw.Draw(board)
    names=['bodycore','headbase','face','outfit-a','HairBack MISSING','HairFront MISSING','weapon-a','FAILED COMPOSITE']
    comp=Image.new('RGBA',(320,320))
    for n in ['bodycore','headbase','face','outfit-a','weapon-a']: comp.alpha_composite(images[n])
    comp.save(REVIEW/'south-failed-composite.png')
    for i,n in enumerate(names):
        x=i%4*320;y=i//4*360;d.text((x+12,y+10),n,fill='#f8cc91' if 'MISSING' in n or 'FAILED' in n else 'white')
        if n in images:board.alpha_composite(images[n],(x,y+30))
        elif n=='FAILED COMPOSITE':board.alpha_composite(comp,(x,y+30))
    board.save(REVIEW/'south-candidate-decomposition.png')
    sheet=Image.new('RGBA',(1000,710),'#536575');d=ImageDraw.Draw(sheet)
    for scale,x in [(1,10),(2,340)]:
        d.text((x,10),f'{scale}x canonical canvas — VISUAL FAIL',fill='white')
        sheet.alpha_composite(comp.resize((320*scale,320*scale),Image.Resampling.LANCZOS),(x,35))
    sheet.save(REVIEW/'south-game-size-failure.png')
    print('Sealed5 available isolated candidate layers; Hair missing; South VISUAL_FAIL. No later gate or runtime pack produced.')

if __name__=='__main__': build()
