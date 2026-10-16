"""Bounded tool regressions and actual exported/native pixel checks. No art approval."""
import copy, hashlib, importlib.util, json, tempfile
from pathlib import Path
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
spec=importlib.util.spec_from_file_location('review_pack',ROOT/'tools/sprite-review-pack.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
scratch=ROOT/'work/v60-checks';scratch.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(dir=scratch) as tmp:
    tmp=Path(tmp);source=json.loads((P/'reverse-recovery.json').read_text())
    for f in source['frames']:f['path']=str((P/f['path']).resolve())
    source_path=tmp/'input.json'
    def trial(name, change):
        data=copy.deepcopy(source);change(data);source_path.write_text(json.dumps(data))
        try:m.read_clip(source_path)
        except (ValueError,KeyError,FileNotFoundError):rows.append({'name':name,'pass':True});return
        raise AssertionError('accepted negative '+name)
    trial('zero_duration',lambda d:d['frames'][0].update(duration_ms=0))
    trial('negative_duration',lambda d:d['frames'][0].update(duration_ms=-10))
    trial('non_gif_clock_9ms',lambda d:d['frames'][0].update(duration_ms=9))
    trial('float_clock',lambda d:d['frames'][0].update(duration_ms=90.0))
    trial('bool_clock',lambda d:d['frames'][0].update(duration_ms=True))
    trial('stale_sha',lambda d:d['frames'][0].update(sha256='0'*64))
    trial('missing_frame',lambda d:d['frames'][0].update(path=str(tmp/'missing.png')))
    trial('canvas_changed',lambda d:d.update(canvas=[1,1]))
    trial('empty_frames',lambda d:d.update(frames=[]))
    trial('false_16_unique_drawings',lambda d:d.update(minimum_unique_drawings=16))
    original=Image.new('RGBA',(4,4));hidden=original.copy();hidden.putpixel((1,1),(255,72,13,0))
    assert m.visible_digest(original)==m.visible_digest(hidden)
    rows.append({'name':'hidden_RGB_does_not_count_as_new_art','pass':True})
    hidden.putpixel((1,1),(255,72,13,1));assert m.visible_digest(original)!=m.visible_digest(hidden)
    rows.append({'name':'visible_alpha_difference_is_preserved','pass':True})
    source_path.write_text(json.dumps(source));receipt=m.build(source_path,tmp/'positive')
    assert receipt['exposures']==16 and receipt['unique_rgba_drawings']==8
    assert receipt['total_ms']==1900 and receipt['encoded_gif_frames']==15
    assert not receipt['art_approval_granted'] and not receipt['production_pass']
    rows.append({'name':'actual_GIF_collapses_peak_hold_but_preserves_clock_and_pixels','pass':True})
    try:m.build(source_path,tmp/'positive')
    except FileExistsError:rows.append({'name':'refuse_output_overwrite','pass':True})
    else:raise AssertionError('overwrote review evidence')

native=P/'native-editable/export';errors=[]
for i in range(16):
    a=np.array(Image.open(P/f'reverse-recovery-frames/{i:02}.png').convert('RGBA'),dtype=float)
    b=np.array(Image.open(native/f'{i:02}.png').convert('RGBA'),dtype=float)
    assert np.array_equal(a[:,:,3],b[:,:,3])
    error=float(abs(a[:,:,:3]*a[:,:,3:]/255-b[:,:,:3]*b[:,:,3:]/255).max())
    assert error<=1.1;errors.append(error)
rows.append({'name':'actual_native_all16_roundtrip','pass':True,'max_premultiplied_error':max(errors)})
clip=json.loads((P/'reverse-recovery-slots.json').read_text())
inspection=json.loads((P/'native-editable/native-inspection.json').read_text())
assert [f['duration_ms']for f in inspection['frames']]==[f['duration_ms']for f in clip['frames']]
assert [l['name']for l in sorted(inspection['layers'],key=lambda l:l['path'])]==['trail','weapon','body','head']
rows.append({'name':'saved_native_layers_and_authored_clock','pass':True})
assert json.loads((P/'reverse-recovery-motion-review.json').read_text())['motion_profile_pass']
assert not json.loads((P/'reverse-recovery-right-forefoot-review.json').read_text())['visible_surface_contact_pass']
rows.append({'name':'motion_only_pass_cannot_hide_contact_failure','pass':True})
browser_errors=[]
for name in ['original','reverse-recovery','accepted-control','old-head','corrected-head']:
    data=json.loads((P/f'{name}.json').read_text())
    for i,frame in enumerate(data['frames']):
        a=np.array(Image.open(P/frame['path']).convert('RGBA'),dtype=float)
        b=np.array(Image.open(ROOT/f'work/v60-browser/{name}/{i:02}.png').convert('RGBA'),dtype=float)
        assert np.array_equal(a[:,:,3],b[:,:,3])
        error=float(abs(a[:,:,:3]*a[:,:,3:]/255-b[:,:,:3]*b[:,:,3:]/255).max())
        assert error<=1.1;browser_errors.append(error)
rows.append({'name':'actual_five_players_80_PNG_frames','pass':True,
             'max_premultiplied_error':max(browser_errors)})
report={'pass':True,'controls':rows,'control_count':len(rows),'production_pass':False,
        'scope':'Tool guards, file roundtrip and retained art rejection; not anatomy acceptance.'}
(P/'test-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
