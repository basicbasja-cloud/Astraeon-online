"""Actual delivered-frame checks and source-coordinate ROI regression control."""
from pathlib import Path
import json,hashlib,importlib.util,copy
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def tool(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'tools'/('sprite-'+n+'-review.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
motion=tool('motion');contact=tool('contact');layer=tool('layer-contact');rows={}
for v in ['N','W','E','S']:
 p=P/'profiles';m=motion.evaluate(json.loads((p/(v+'-motion.json')).read_text()),p);c=(layer if v=='S'else contact).evaluate(json.loads((p/(v+'-contact.json')).read_text()),p);assert m['motion_profile_pass']and c['layer_contact_pass'if v=='S'else'visible_surface_contact_pass'];rows[v]={'motion':m,'contact':c}
p=P/'profiles';bad=json.loads((p/'N-contact.json').read_text());source=json.loads((P.parent/'ro-motion-lab-v51/pickup-contact-case.json').read_text());bad['surfaces']=source['surfaces'];negative=contact.evaluate(bad,p);assert not negative['visible_surface_contact_pass']
files=[P/'compile-pickup-profiles.py',P/'profile-provenance.json',P.parent/'ro-core-views-v52/stage-manifest.json']+list(p.glob('*.json'))
r={'pass':True,'delivered_png_profiles':rows,'old_source_ROI_on_common_canvas_rejected':True,'negative_result':negative,'dependencies':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()for f in files}}
(P/'compiled-profiles-review.json').write_text(json.dumps(r,indent=2)+'\n');print({'pass':True,'views':4,'wrong_source_ROI_rejected':True})
