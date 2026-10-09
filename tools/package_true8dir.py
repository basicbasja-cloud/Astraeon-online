"""Build the independent candidate pack; MotionTemplate and older packs remain immutable."""
import json,copy,math
from pathlib import Path
import numpy as np
from PIL import Image
from build_swordsman_registration import relative,tr
R=Path(__file__).resolve().parents[1];B=R/'authoring/characters/builds/swordsman-true8dir-v1';O=R/'assets/characters/swordsman-true8dir-v1';dest=R/'authoring/characters/appearance/swordsman-true8dir/appearance-pack.json'
old=json.loads((R/'authoring/characters/appearance/swordsman-basicattack-anatomy/appearance-pack.json').read_text());p=copy.deepcopy(old);m=json.loads((R/'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json').read_text());j=json.loads((B/'joint-review.json').read_text());samples=json.loads((B/'weapon-samples.json').read_text());heads=json.loads((B/'head-sets.json').read_text());D=p['bodyContract']['directions'];p['packId']='swordsman-true8dir-weapon-repair-v1';p['source']['method']='Raw RO1 audited phase structure; original surgical arm candidates, perspective weapon samples, combined head appearances';p['source']['baselineCommit']='fc7be02d56ac9c020652225af6fe6bff79b7e4fc';p['headAppearanceModel']='HeadIncludesHair'
# Palette proof changes only newly repaired body pixels; face is independent.
a=np.array(Image.open(O/'body-basicattack.png'));before=np.array(Image.open(R/old['atlases']['body-basicattack']['file']));royal=np.array(Image.open(R/old['atlases']['royal-basicattack']['file']));changed=np.any(a!=before,axis=2);new=a.copy();warm=(a[:,:,0]>a[:,:,2]*1.4)&(a[:,:,1]>a[:,:,2]*1.25)&(a[:,:,0]>95)&(a[:,:,3]>0);new[:,:,0][warm]=(new[:,:,0][warm]*.43).astype('uint8');new[:,:,1][warm]=(new[:,:,1][warm]*.88).astype('uint8');new[:,:,2][warm]=np.minimum(255,new[:,:,2][warm]*1.8+55).astype('uint8');royal[changed]=new[changed];Image.fromarray(royal).save(O/'royal-basicattack.png')
for name in ['body-basicattack','royal-basicattack']:p['atlases'][name]['file']=(O/(name+'.png')).relative_to(R).as_posix()
# Complete head styles own both face and hair. Independent headgear remains parented to head sockets.
for key in list(p['parts']):
 if p['parts'][key]['slot'] in ['Head','Hair']:del p['parts'][key]
del p['slots']['Hair'];del p['defaultParts']['Hair'];p['defaultParts']['Head']='head-style-a'
for style in ['a','b']:
 part=dict(slot='Head',mode='BODY_SYNC',space='canvas',anchor='head',timelines={})
 for action,dirs in heads[style].items():
  atlas=f'head-{style}-{action.lower()}';path=O/(atlas+'.png');im=Image.open(path);p['atlases'][atlas]=dict(file=path.relative_to(R).as_posix(),width=im.width,height=im.height);part['timelines'][action]={}
  for d,frames in dirs.items():part['timelines'][action][d]=dict(frames=[dict(layers={'HeadBase':dict(atlasId=atlas,rect=f['rect'],sockets=f['sockets'],sourceDirection=d,headIncludesHair=True)}) for f in frames])
 p['parts']['head-style-'+style]=part
# Combined heads occupy the former front-hair occlusion position.
for order in p['drawProfiles'].values():
 order.remove('HeadBase');order.insert(order.index('HairFront')+1,'HeadBase')
# Explicit authored per-frame phase, view and rotation schedules. Angle is unwrapped around the ready pose.
phase=['ready','ready','anticipation','anticipation','anticipation','anticipation','swing','contact','followThrough','followThrough','followThrough','followThrough','recovery','recovery','recovery','recovery']
angles={'SW':[-.3,-.35,-.4,-.5,-.6,-.65,-.95,-2.05,-2.3,-2.65,-2.85,-3.05,-3.7,-4.4,-5.25,-6.58],'W':[-.15,-.2,-.3,-.4,-.6,-.7,-1,-2.0,-2.35,-2.7,-2.9,-3.05,-3.65,-4.35,-5.25,-6.43],'NW':[.4,.35,.25,.15,.05,0,.65,1.6,2,2.4,2.65,2.85,2.5,1.7,1,.4],'NE':[.35,.3,.2,.1,0,0,.55,1.8,2.15,2.4,2.6,2.75,2.45,1.8,1,.35]}
for key in ['weapon-a','weapon-b']:
 part=p['parts'][key];part['mode']='BODY_SYNC';atlas=key+'-poses';p['atlases'][atlas]=dict(file=(O/(atlas+'.png')).relative_to(R).as_posix(),width=256,height=128)
 part['weaponDefinition']=dict(identity=key,compatibleBodyContract=p['bodyContract']['contractId'],compatibleMotionTemplates=p['compatibleMotionTemplates'],poseSetVersion=1,phases=list(dict.fromkeys(phase)),perspectiveVariants=[v['name'] for v in samples[key]])
 for action,dirs in m['actions'].items():
  for d,seq in dirs['directions'].items():
   entries=old['parts'][key]['timelines'][action][d]['phases'];frames=[];elapsed=0
   for i,f in enumerate(seq['frames']):
    t=elapsed/seq['totalDurationMs'];ref=copy.deepcopy(max((e for e in entries if e['at']<=t+1e-9),key=lambda e:e['at'])['layers']['MainHand']);elapsed+=f['durationMs']
    if action=='BasicAttack':
     chain=j['frames'][d][i]['joints'];grip=chain[3] if j['frames'][d][i].get('reauthored') else None
     oldreg=old['bodyContract']['anchorRegistration'][action][d][i]['mainHand'];base=f['anchors']['mainHand'];c,s=math.cos(base['rotation']),math.sin(base['rotation']);oldgrip=[base['x']+base['scale']*(c*oldreg['x']-s*oldreg['y']),base['y']+base['scale']*(s*oldreg['x']+c*oldreg['y'])]
     grip=grip or oldgrip;angle=angles[d][i] if d in angles else base['rotation']+oldreg['rotation']
     # Body equipment registration is the wrist; visible palm contact is independently measured.
     wrist=chain[2];equipment=tr(*wrist);p['bodyContract']['anchorRegistration'][action][d][i]['mainHand']=relative(base,equipment)
     variant=([0,0,0,1,1,1,1,2,2,3,3,3,3,0,1,0][i] if d in ['S','SW','N','NE','SE'] else [1,1,1,0,0,0,0,0,3,3,3,3,3,1,1,1][i]);variant=2 if d=='NW' and i in [7,8] else variant;v=samples[key][variant];pivot=v['equipmentAnchor'];gp=v['gripContactPoint'];tip=v['weaponTip'];cs,sn=math.cos(angle),math.sin(angle);dx,dy=gp[0]-pivot[0],gp[1]-pivot[1];guard=[grip[0]-(cs*dx-sn*dy),grip[1]-(sn*dx+cs*dy)]
     ref=dict(atlasId=atlas,rect=v['rect'],pivot=pivot,trim=dict(sourceSize=[64,128],offset=[0,0]),localTransform=tr(guard[0]-wrist[0],guard[1]-wrist[1],angle),sourceDirection=d,weaponPhase=phase[i],bladeTip=tip,guardCentre=pivot,weaponPoseFrame=dict(phase=phase[i],perspectiveVariant=v['name'],equipmentAnchor=pivot,gripContactPoint=gp,weaponTip=tip,localOffset=[guard[0]-wrist[0],guard[1]-wrist[1]],rotation=angle,scale=1,drawProfile=p['frameDrawProfiles'][action][d][i],handContactPoint=grip,slashProfile=None))
     worldtip=[guard[0]+cs*(tip[0]-pivot[0])-sn*(tip[1]-pivot[1]),guard[1]+sn*(tip[0]-pivot[0])+cs*(tip[1]-pivot[1])];p['bodyContract']['anchorRegistration'][action][d][i]['weaponTip']=relative(f['anchors']['weaponTip'],tr(*worldtip))
     polygon=[[round(grip[0]+6*math.cos(k*math.pi/4),3),round(grip[1]+6*math.sin(k*math.pi/4),3)] for k in range(8)]
     for body in ['swordsman-body-default','swordsman-body-royal-proof']:p['parts'][body]['timelines'][action][d]['frames'][i]['layers']['Body']['foregroundPasses']=[dict(afterLayer=layer,requiresLayer='MainHand',semantic='body-owned fingers cover visible sword handle',polygon=polygon) for layer in ['MainHand','HeadBase']]
    frames.append(dict(layers={'MainHand':ref}))
   part['timelines'][action][d]=dict(frames=frames)
dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(p,indent=2)+'\n');print(dest)
