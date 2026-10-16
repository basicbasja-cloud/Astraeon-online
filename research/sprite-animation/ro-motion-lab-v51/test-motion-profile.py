"""Real old bounce is a negative; flattened, reordered and stale inputs also fail."""
from pathlib import Path
import importlib.util,json,copy
P=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('motion',P.parents[2]/'tools/sprite-motion-review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
c=json.loads((P/'pickup-motion-case.json').read_text());positive=m.evaluate(c,P);assert positive['motion_profile_pass'];checks={'actual_native_cleanup_profile':True}
old=json.loads((P/'rejected-v49-motion-case.json').read_text());negative=m.evaluate(old,P);assert not negative['motion_profile_pass'];checks['real_user_rejected_v49_bounce']=True
for label,change in [
 ('frozen_body',lambda x:x.update({'frames':[x['frames'][0]]*16})),
 ('reverse_bob',lambda x:x['frames'].__setitem__(3,x['frames'][0])),
 ('stale_pixel_receipt',lambda x:x['frames'][5].update({'sha256':'0'*64})),
 ('missing_frame',lambda x:x['frames'][2].update({'path':'missing-frame.png'})),
 ('invalid_zero_clock',lambda x:x['durations'].__setitem__(4,0)),
 ('insufficient_frames',lambda x:x.update({'frames':x['frames'][:2]}))]:
 d=copy.deepcopy(c);change(d);r=m.evaluate(d,P);assert not r['motion_profile_pass'],label;checks[label]=True
(P/'motion-profile-tests.json').write_text(json.dumps({'pass':True,'checks':checks,'positive_actual_measurements':positive['measurements'],'old_actual_measurements':negative['measurements'],'scope':'Pickup contour profile only; hidden joints/contact/appearance remain independent checks'},indent=2)+'\n');print(checks)
