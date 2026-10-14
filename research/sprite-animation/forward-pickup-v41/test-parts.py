"""Actual pixel observations + abstention/anti-false-positive controls."""
import copy,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def module(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'skills/modular-eight-direction-sprites/scripts'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('part-proportion-audit');sz=module('character-size-audit');c=json.loads((P/'part-proportion-contract.json').read_text());q=m.run(c,ROOT);checks=[]
def check(name,ok):
 assert ok,name
 checks.append(dict(name=name,pass_=True))
def row(q,a,b,k):return next(x for x in q['comparisons'] if x['frames']==[a,b] and x['metric']==k)
check('actual same-view neutral shoe expands21.56percent and fails',row(q,'candidate0','candidate7','boot_length')['status']=='FAIL' and 1.21<row(q,'candidate0','candidate7','boot_length')['projected_ratio']<1.22)
check('different front/rear visible shaft ratio1.4 is diagnostic not anatomical error',row(q,'approved0','candidate0','leg_thickness')['status']=='UNKNOWN' and row(q,'approved0','candidate0','leg_thickness')['projected_ratio']==1.4)
check('clipped rear head remains unknown',q['measurements']['candidate7']['head_width']['status']=='UNKNOWN')
check('hidden pelvis and shoulder width are never inferred from cape',all(q['measurements']['candidate0'][k]['status']=='UNKNOWN' for k in ['pelvis_width','shoulder_breadth']))
check('ratio denominator remains399 not per-frame height420',q['measurements']['candidate7']['leg_thickness']['fraction_of_fixed_family_height']==52/399)
d=copy.deepcopy(c);d['frames'][1]['image']['sha256']='0'*64;check('pixel hash mismatch blocks approval',not m.run(d,ROOT)['checks']['all_input_hashes'])
d=copy.deepcopy(c);d['frames'][0]['image']=d['frames'][1]['image'];check('unapproved image cannot serve as accepted master',not m.run(d,ROOT)['checks']['approved_images_covered_by_acceptance'])
d=copy.deepcopy(c);d['comparisons']=[dict(frames=['candidate0','candidate7'])];check('only self-comparison cannot replace approved reference',not m.run(d,ROOT)['checks']['every_candidate_compared_with_approved'])
d=copy.deepcopy(c);d['frames'][8]['observations']['boot_length']['protocol']='other';check('changing visible-surface protocol abstains',row(m.run(d,ROOT),'candidate0','candidate7','boot_length')['status']=='UNKNOWN')
d=copy.deepcopy(c);d['frames'][1]['observations']['boot_length']['points']=[[5,5],[10,10]];check('points on empty background are rejected',m.run(d,ROOT)['measurements']['candidate0']['boot_length']['status']=='UNKNOWN')
d=copy.deepcopy(c);d['frames'][1]['observations']['boot_length']['reviewed_on_pixels']=False;check('unreviewed points cannot become measurements',m.run(d,ROOT)['measurements']['candidate0']['boot_length']['status']=='UNKNOWN')
d=copy.deepcopy(c);d['frames'][8]['image']=copy.deepcopy(d['frames'][1]['image']);d['frames'][8]['observations']=copy.deepcopy(d['frames'][1]['observations']);ident=m.run(d,ROOT);check('identical visible shoe is positive metric control but not complete character approval',row(ident,'candidate0','candidate7','boot_length')['status']=='PASS' and not ident['part_proportion_pass'])
sc=json.loads((P/'size-locked-contract.json').read_text());s=sz.run(sc,ROOT);check('height-matched399px cannot bypass part-size gate',s['neutral_comparison'][0]['pass_'] and not s['checks']['part_dimensions_and_ratios'])
d=copy.deepcopy(sc);d['part_proportion_contract']['sha256']='0'*64;check('stale part contract cannot be used by size gate',not sz.run(d,ROOT)['checks']['part_dimensions_and_ratios'])
check('all18required metrics remain enforced with partial annotations',len(q['required_metrics'])==18 and not q['checks']['every_required_part_observed'])
(P/'part-test-receipt.json').write_text(json.dumps(dict(checks=checks,production_pass=False),indent=2)+'\n');print(f'{len(checks)} part-size/unknown controls passed')
