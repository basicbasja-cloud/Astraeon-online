from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,sys
sys.path.insert(0,'tools/character_factory_v3')
from build_ranged_visible_cutouts import split_frame
b=Path('authoring/characters/factory-v3/patch-0.0.1/review');master=b/'archer-coherent-recovery-masters-v2-20261026/female/NE/Master/003.png';head=b/'archer-remaining-view-head-complete-proposals-v6-20261027/female/NE/003.png';out=b/'archer-female-ne003-native-bow-study-v2-20261028';out.mkdir(exist_ok=False)
annotation={'head_polygon':[(0,0),(1,0),(1,1)],'weapon_paths':[{'points':[(207,135),(208,141),(205,149),(199,161),(194,174),(192,184),(192,198)],'width':7},{'points':[(195,219),(197,230),(203,242),(210,254),(215,267),(213,275)],'width':7},{'points':[(209,139),(228,179)],'width':2},{'points':[(228,218),(223,245)],'width':2},{'points':[(134,214),(189,202)],'width':5}], 'weapon_polygons':[[(132,211),(139,209),(145,211),(138,215)]], 'hand_polygons':[[(185,197),(202,196),(213,199),(215,213),(205,221),(186,219),(183,209)]]}
im=Image.open(master).convert('RGBA');original=np.array(im);old=np.array(Image.open(head).convert('RGBA'));from scipy import ndimage
headmask=old[:,:,3]>0;yy,xx=np.indices(headmask.shape);fringe=ndimage.binary_dilation(headmask,iterations=2)&(original[:,:,3]>0)&(yy<178)&(xx>225);headmask|=fringe;newhead=original.copy();newhead[~headmask]=0;parts,labels,report=split_frame(im,annotation,{'scale':1,'offset':[0,0]},Image.fromarray(newhead))
for role,img in parts.items():img.save(out/(role+'.png'))
labels.save(out/'labels.png');page=Image.new('RGBA',(1500,500),'#ddd')
for col,(name,im)in enumerate([('master',im),('Weapon proposal',parts['Weapon']),('BodyCostume',parts['BodyCostume']),('HeadHair',parts['HeadHair']),('recompose',im)]):
 tile=im.crop((110,110,310,310)).resize((300,300),Image.Resampling.NEAREST);page.alpha_composite(tile,(col*300,45));ImageDraw.Draw(page).text((col*300+5,5),name,fill='black')
page.convert('RGB').save(out/'parts-review.jpg',quality=98);(out/'annotation.json').write_text(json.dumps({'frame':3,'view':'NE','sex':'female','master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'head_sha256':hashlib.sha256(head.read_bytes()).hexdigest(),'annotation':annotation,'result':report,'status':'NATIVE_SAME_FRAME_PROPOSAL_REQUIRES_SEMANTIC_REVIEW','runtime_admitted':False,'limitations':['Bow is visible-only: hidden bow behind glove has not been painted.','Arrow and string paths require close review for exact ownership.','One frame is not an action or a runtime character.']},indent=2)+'\n');(out/'build-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(report))
