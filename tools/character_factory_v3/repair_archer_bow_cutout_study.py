"""Rejected historical experiment: attaching a bow to the near release hand is wrong.
Retained for provenance only. Never use its output in production.
"""
raise SystemExit("REJECTED_WRONG_HAND_ATTACHMENT: omitted far left arm requires source-guided repaint")

from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy.ndimage import label
p=Path('authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-male-basicattack/NW');out=p/'grip-repair';out.mkdir(exist_ok=True)
def cutout(path):
 a=np.array(Image.open(path).convert('RGBA'));bg=a[:,:,:3].min(axis=2)>242;a[bg]=0;return Image.fromarray(a)
master=cutout(p/'frame-11-before.png');a=np.array(master);ids,n=label(a[:,:,3]>0,structure=np.ones((3,3)));seed=(230,100);bowid=ids[seed[1],seed[0]]
if not bowid:raise ValueError('Bow seed not on visible bow')
bow=a.copy();bow[ids!=bowid]=0;body=a.copy();body[ids==bowid]=0
mask=Image.new('L',master.size);d=ImageDraw.Draw(mask);d.polygon([(177,100),(181,100),(185,96),(188,92),(192,90),(195,93),(199,94),(202,98),(202,106),(197,109),(190,111),(184,113),(179,112)],fill=255);body[np.array(mask)>0]=0
source=cutout(p/'frame-10-before.png');gmask=Image.new('L',source.size);ImageDraw.Draw(gmask).polygon([(210,87),(218,84),(224,86),(228,92),(227,102),(220,105),(214,106),(209,102)],fill=255);glove=np.array(source);glove[np.array(gmask)==0]=0
# Rigid visible-part assembly only; body pose never scaled or warped.
layer=Image.fromarray(glove);layer=layer.rotate(16,Image.Resampling.BICUBIC,center=(212,101));moved=Image.new('RGBA',master.size);moved.paste(layer,(-33,10))
bow_layer=Image.new('RGBA',master.size);bow_layer.paste(Image.fromarray(bow),(-40,2))
body_image=Image.fromarray(body);merged=body_image.copy();merged.alpha_composite(bow_layer);merged.alpha_composite(moved)
for name,im in [('BodyCostume',body_image),('Weapon',bow_layer),('WeaponHandOccluder',moved),('corrected-frame',merged)]:im.save(out/(name+'.png'))
bg=Image.new('RGBA',merged.size,'white');bg.alpha_composite(merged);bg.convert('RGB').resize((942,942)).save('/workspace/outputs/archer-bow-grip-repair-zoom.png')
(out/'receipt.json').write_text(json.dumps({'status':'ADJACENT_FRAME_VISIBLE_PART_REUSE_REQUIRES_WRIST_REVIEW','target_frame_index':11,'glove_donor_frame_index':10,'body_pose_warped':False,'bow_translation_px':[-40,2],'glove_translation_px':[-33,10],'glove_rotation_degrees':16,'hidden_surfaces_generated':False,'owner_approved':False,'runtime_admitted':False,'limitations':['Glove is reused from adjacent matching arm orientation; compare source wrist before promotion.','Original open-hand mask and floating-bow component removed from the frame; no body redraw.','This single-frame repair is not a complete four-view action.']},indent=2)+'\n')
