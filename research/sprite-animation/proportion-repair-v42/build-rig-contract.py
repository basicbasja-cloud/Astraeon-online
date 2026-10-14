from pathlib import Path
import hashlib,json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[2];R=P/'rig-render-6'
def bind(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
b=json.loads((R/'bindings.json').read_text());frames=[]
for i in range(8):
 f=dict(index=i,**{k:bind(R/f'{folder}/{i:02}.png') for k,folder in dict(full='full',back='body_outfit_back',head='head',front='body_outfit_front',scene='scene',prop='prop').items()});f['isolated']={name:bind(R/f'isolated/{name}/{i:02}.png') for name in b['draw_order']};frames.append(f)
sections={}
for side in ['left','right']:
 for part,interval in [('upperarm',[21,29]),('forearm',[21,29]),('shin',[31,39]),('hand',[12,24])]:sections[side+'.'+part]=dict(fraction=.9 if part=='hand' else .5,max_variation_px=2,width_interval_px=interval)
c=dict(schema='rig-material-continuity-v1',asset_root=str(P.relative_to(ROOT)),rig_binding=bind(R/'bindings.json'),prop_binding=bind(R/'prop-bindings.json'),source=bind(P/'source/source.json'),approval_receipt=bind(P.parent/'rear-motion-v40/user-v39-acceptance.json'),approved_references=[bind(P.parent/f'recovery-key-v39/{name}') for name in ['review-source.gif','review-game.gif']]+[bind(P.parent/f'recovery-key-v39/renders/review/full/{i:02}.png') for i in range(8)],frames=frames,sections=sections,support_windows={'left.foot':[136,467,190,481],'right.foot':[194,455,248,467]},support_rgba_budget=1,reference_height_px=399,reference_ground_y=480,minimum_neck_overlap_pixels=8,contact_budget_px=2,threshold_scope='Provisional engineering limits for this authored rig/material family, not universal anatomy/perception. Width target ranges motivated by approved visible slim sleeves and boots; cross-view anatomical ratios are not asserted.')
(P/'rig-continuity-contract.json').write_text(json.dumps(c,indent=2)+'\n');s=importlib.util.spec_from_file_location('qa',ROOT/'skills/modular-eight-direction-sprites/scripts/rig-material-continuity.py');qa=importlib.util.module_from_spec(s);s.loader.exec_module(qa);q=qa.run(c,ROOT);(P/'rig-continuity-qa.json').write_text(json.dumps(q,indent=2)+'\n');print(q['checks']);print(q['feet']);print('neck',q['neck_overlap_pixels'],'contact',q['contact_pixel_distance'])
