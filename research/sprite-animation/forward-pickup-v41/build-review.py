"""Fixed-grid native crops; ONE bank-wide display transform, no foot fitting."""
import argparse,base64,hashlib,importlib.util,json
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def binding(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def module(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'skills/modular-eight-direction-sprites/scripts'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--attempt',type=int,required=True);p.add_argument('--size-profile',type=Path);a=p.parse_args();bank=P/('size-locked-review' if a.size_profile else f'attempt{a.attempt}-review');bank.mkdir(exist_ok=True)
    native=Image.open(P/f'attempt{a.attempt}-raw.png').convert('RGBA')
    if native.size!=(1536,1024):raise ValueError('Unexpected native grid; do not silently fit')
    matrix=json.loads(a.size_profile.read_text())['matrix'] if a.size_profile else [.87,0,0,.87,24.96,50];s,tx,ty=matrix[0],matrix[4],matrix[5];inverse=[1/s,0,-tx/s,0,1/s,-ty/s]
    frames=[];native_frames=[]
    for i in range(8):
        raw=native.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512));raw.save(bank/f'native-{i:02}.png');native_frames.append(raw)
        raw.transform((384,512),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC).save(bank/f'{i:02}.png');frames.append(binding(bank/f'{i:02}.png'))
    norm=dict(raw=binding(P/f'attempt{a.attempt}-raw.png'),display_matrix=matrix,inverse=inverse,scope='One declared uniform bank-wide review scale/anchor. No frame-specific crop fitting, translation, scale, warp, cloned shoe, threshold cleanup or row correction. Full native atlas retained; no final game asset admission.')
    if a.size_profile:norm['size_profile']=binding(a.size_profile.resolve())
    (bank/'normalization.json').write_text(json.dumps(norm,indent=2)+'\n')
    approval=binding(P.parent/'rear-motion-v40/user-v39-acceptance.json');refs=json.loads((P/'approved-gif-reference.json').read_text())['references'];g=module('approved-gif-compare');f=module('visible-floor-surfaces')
    windows=dict(near=dict(roi=[65,455,235,510],edge='min'),far=dict(roi=[245,440,330,510],edge='max'))
    if a.size_profile:windows=dict(near=dict(roi=[64,477,232,511],edge='min',material='foreground'),far=dict(roi=[244,453,331,511],edge='max',material='foreground'))
    equivalent=f.run(native_frames,windows,6,s)
    raster_windows={name:dict(roi=[round(w['roi'][0]*s+tx),round(w['roi'][1]*s+ty),round(w['roi'][2]*s+tx),round(w['roi'][3]*s+ty)],edge=w['edge']) for name,w in windows.items()}
    if a.size_profile:raster_windows=dict(near=dict(roi=[85,460,225,490],edge='min',material='foreground'),far=dict(roi=[236,440,308,488],edge='max',material='foreground'))
    raster=f.run([Image.open(ROOT/r['path']).convert('RGBA') for r in frames],raster_windows,6,1)
    fq=dict(native_equivalent=equivalent,raster=raster,surface_checks_pass=equivalent['surface_checks_pass'] and raster['surface_checks_pass'],production_pass=False)
    (bank/'floor-qa.json').write_text(json.dumps(fq,indent=2)+'\n')
    for ref in refs:
        hashes=[f['sha256'] for f in frames]
        observations=dict(frame_sha256=hashes,visible_tracks={},planted_surfaces={name:[o.get('xy') for o in t['observations']] for name,t in raster['tracks'].items()},manual_action_review=dict(pass_=False,frame_sha256=hashes,reason='Actual painted boot surfaces fail6px; hidden chains/prop contact/cell contour also need review'),scope='Actual raster window/material observer output: contour extrema, not anatomical joints. No hidden hand/leg inference.')
        observations['manual_action_review']['pass']=False
        c=dict(reference=dict(path=ref['approved_gif_path'],sha256=ref['approved_gif_sha256']),approval_receipt=approval,candidate_frames=frames,durations_ms=[r['duration_ms'] for r in ref['frames']],contact_index=3,support_budget_px=6,required_support_tracks=['near','far'],observations=observations)
        (bank/f'{ref["clock"]}-comparison-contract.json').write_text(json.dumps(c,indent=2)+'\n')
        q=g.run(c,ROOT,bank/ref['clock']);(bank/ref['clock']/'approved-gif-qa.json').write_text(json.dumps(q,indent=2)+'\n')
        shown=[]
        for r in frames:
            im=Image.open(ROOT/r['path']).convert('RGBA');bg=Image.new('RGBA',im.size,'#344351');bg.alpha_composite(im);shown.append(bg.convert('RGB'))
        shown[0].save(bank/f'review-{ref["clock"]}.gif',save_all=True,append_images=shown[1:],duration=c['durations_ms'],loop=0,disposal=2)
    d=dict(candidate_frames=frames,normalization=norm,reference=refs,source=json.loads((P/'source/source.json').read_text()),floor_qa=fq)
    (bank/'review-data.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(attempt=a.attempt,floor_checks=raster['checks'],raster_ranges={k:v['range_display_px'] for k,v in raster['tracks'].items()},native_equivalent_ranges={k:v['range_display_px'] for k,v in equivalent['tracks'].items()})))
if __name__=='__main__':main()
