from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json

root = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
base = root / 'authoring/characters/factory-v3/patch-0.0.1/review'
masters = base / 'mage-female-own-frame-head-recovery-20261028/Master'
parts = base / 'mage-female-head-fringe-ownership-v7-20261027'
frames, records = [], []
sheet = Image.new('RGB', (1200, 800), '#dddddd')
draw = ImageDraw.Draw(sheet)
for i in range(24):
    path = masters / f'{i:03d}.png'
    master = Image.open(path).convert('RGBA')
    body = Image.open(parts / 'BodyRest' / f'{i:03d}.png').convert('RGBA')
    head = Image.open(parts / 'HeadHair' / f'{i:03d}.png').convert('RGBA')
    composite = Image.alpha_composite(body, head)
    assert composite.getchannel('A').tobytes() == master.getchannel('A').tobytes()
    assert all(a == b for a, b in zip(composite.getdata(), master.getdata()) if a[3] or b[3])
    panel = Image.new('RGBA', (384, 384), '#dddddd')
    panel.alpha_composite(master.crop((192, 232, 576, 616)))
    frames.append(panel.convert('RGB'))
    detail = master.crop((335, 325, 425, 405)).resize((180, 160), Image.Resampling.NEAREST)
    x, y = (i % 6) * 200, (i // 6) * 200
    sheet.paste(detail, (x, y), detail)
    draw.text((x, y + 162), f'{i:02d}', fill='black')
    records.append({'index': i, 'master_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'head_sha256': hashlib.sha256((parts/'HeadHair'/f'{i:03d}.png').read_bytes()).hexdigest(), 'body_rest_sha256': hashlib.sha256((parts/'BodyRest'/f'{i:03d}.png').read_bytes()).hexdigest(), 'visible_recomposition_mismatch_pixels': 0})
sheet.save(out/'own-frame-neck-contact.png')
for label, multiplier in [('normal', 1), ('slow', 3)]:
    durations = [(round((i+1)*100/24)-round(i*100/24))*10*multiplier for i in range(24)]
    durations[-1] += 200
    frames[0].save(out/f'own-frame-{label}.gif', save_all=True, append_images=frames[1:], duration=durations, loop=0, disposal=2, optimize=False)
(out/'audit.json').write_text(json.dumps({'status':'SAME_FRAME_DIAGNOSTIC_NOT_GAME_READY','frames':records,'frame_count':24,'reuses_head_from_another_frame':False,'weapon_separate':False,'temporal_stability_approved':False,'runtime_admitted':False,'preview_restarts_for_review':True,'warning':'Exact compositing does not establish semantic ownership, anatomy or stable animation.'},indent=2)+'\n')
