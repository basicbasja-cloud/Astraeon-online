"""Free local GIF + lossless browser review. No pose registration or art approval."""
import argparse, base64, hashlib, html, json
from pathlib import Path
from PIL import Image, ImageDraw

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def visible_digest(image):
    # Invisible RGB garbage is not a new drawing. Preserve source files exactly.
    data = bytearray(image.tobytes())
    for k in range(0, len(data), 4):
        if data[k+3] == 0:
            data[k:k+3] = b'\0\0\0'
    return hashlib.sha256(data).hexdigest()

def read_clip(path):
    path = Path(path).resolve()
    data = json.loads(path.read_text())
    rows = data['frames']
    if not rows:
        raise ValueError('empty clip')
    images = []
    for row in rows:
        duration = row['duration_ms']
        if type(duration) is not int or not 0 < duration <= 655350 or duration % 10:
            raise ValueError('GIF requires positive integer multiples of 10ms; no silent retiming')
        file = path.parent / row['path']
        if sha(file) != row['sha256']:
            raise ValueError('stale source frame')
        image = Image.open(file).convert('RGBA')
        if list(image.size) != data['canvas']:
            raise ValueError('canvas mismatch')
        images.append(image)
    unique = len({visible_digest(im) for im in images})
    if data.get('minimum_unique_drawings', 0) > unique:
        raise ValueError(f'only {unique} unique RGBA drawings; exposures are not new drawings')
    return path, data, images, unique

def build(source, out):
    path, data, images, unique = read_clip(source)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    durations = [r['duration_ms'] for r in data['frames']]
    opaque = []
    for im in images:
        background = Image.new('RGBA', im.size, '#343941')
        background.alpha_composite(im)
        opaque.append(background.convert('RGB'))
    # A single palette prevents different per-frame palettes from flickering.
    # This affects GIF previews ONLY; original PNGs and browser data remain RGBA.
    w, h = images[0].size
    sample = Image.new('RGB', (w, h * len(images)))
    for i, im in enumerate(opaque):
        sample.paste(im, (0, h * i))
    palette = sample.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    quantized = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in opaque]
    gif = out / 'preview.gif'
    quantized[0].save(gif, save_all=True, append_images=quantized[1:],
                      duration=durations, loop=0, disposal=1, optimize=False)
    decoded = Image.open(gif)
    actual = []
    for i in range(decoded.n_frames):
        decoded.seek(i)
        actual.append((decoded.convert('RGB').copy(), decoded.info['duration']))
    # GIF may coalesce adjacent duplicates: compare playback at every original
    # exposure boundary rather than claiming encoded-frame count equals poses.
    start = 0
    for target, duration in zip(quantized, durations):
        clock = 0
        found = None
        for image, delay in actual:
            if clock <= start < clock + delay:
                found = image
                break
            clock += delay
        if found is None or found.tobytes() != target.convert('RGB').tobytes():
            raise ValueError('GIF playback mismatch')
        start += duration
    if sum(d for _, d in actual) != sum(durations):
        raise ValueError('GIF total duration changed')
    sheet = Image.new('RGB', (w * 4, (h + 28) * ((len(images) + 3) // 4)), '#343941')
    draw = ImageDraw.Draw(sheet)
    for i, im in enumerate(opaque):
        x, y = i % 4 * w, i // 4 * (h + 28)
        sheet.paste(im, (x, y + 28))
        draw.text((x + 5, y + 5), f'{i:02} / {durations[i]}ms', fill='white')
    sheet.save(out / 'contact-sheet.png')
    encoded = ['data:image/png;base64,' + base64.b64encode((path.parent / r['path']).read_bytes()).decode()
               for r in data['frames']]
    payload = json.dumps({'images': encoded, 'durations': durations, 'canvas': data['canvas']})
    page = '''<!doctype html><meta charset="utf-8"><title>Sprite review</title>
<style>body{background:#20252c;color:#eee;font:16px system-ui;margin:24px}canvas{background:#343941;max-width:95vw}button,input,select{margin:8px}p{max-width:900px}</style>
<h1>__TITLE__</h1><p>Review candidate · __COUNT__ exposures / __UNIQUE__ unique RGBA drawings. GIF is a palette preview; this player uses original PNG pixels. No registration, scaling or warp.</p>
<p><button id="play">เล่น/หยุด</button><select id="rate"><option value="1">1×</option><option value="0.25">¼×</option></select><input id="seek" type="range" min="0" max="__MAX__" value="0"><label><input id="onion" type="checkbox">ภาพก่อนหน้า</label><label><input id="floor" type="checkbox">เส้นพื้นจากเฟรมแรก</label></p><p id="status"></p><canvas id="view"></canvas><script>
const D=__PAYLOAD__,c=document.querySelector('#view'),ctx=c.getContext('2d');[c.width,c.height]=D.canvas;
let images=[],time=0,playing=false,index=0,last=0;const total=D.durations.reduce((a,b)=>a+b,0);
function at(t){t=((t%total)+total)%total;let end=0;for(let i=0;i<D.durations.length;i++){end+=D.durations[i];if(t<end)return i;}return D.durations.length-1;}
let floorY=0;function draw(i){index=i;ctx.clearRect(0,0,c.width,c.height);if(document.querySelector('#onion').checked){ctx.globalAlpha=.25;ctx.drawImage(images[(i+images.length-1)%images.length],0,0);ctx.globalAlpha=1;}ctx.drawImage(images[i],0,0);if(document.querySelector('#floor').checked){ctx.strokeStyle='#ff6c74';ctx.beginPath();ctx.moveTo(0,floorY+.5);ctx.lineTo(c.width,floorY+.5);ctx.stroke();}document.querySelector('#seek').value=i;document.querySelector('#status').textContent=`${i+1}/${images.length} · ${D.durations[i]}ms`;}
function select(i){playing=false;time=D.durations.slice(0,i).reduce((a,b)=>a+b,0);draw(i);}
document.querySelector('#seek').oninput=e=>select(+e.target.value);for(const name of ['onion','floor'])document.querySelector('#'+name).onchange=()=>draw(index);
document.querySelector('#play').onclick=()=>{playing=!playing;last=performance.now();};
function tick(now){if(playing){time+=(now-last)*+document.querySelector('#rate').value;draw(at(time));}last=now;requestAnimationFrame(tick);}
window.review={at,select,draw,ctx,get index(){return index},get playing(){return playing},durations:D.durations,total};
Promise.all(D.images.map(src=>new Promise((resolve,reject)=>{let im=new Image;im.onload=()=>resolve(im);im.onerror=reject;im.src=src;}))).then(result=>{images=result;ctx.drawImage(images[0],0,0);const a=ctx.getImageData(0,0,c.width,c.height).data;for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++)if(a[(y*c.width+x)*4+3]>=128)floorY=y;draw(0);window.READY=true;requestAnimationFrame(tick);}).catch(e=>window.LOAD_ERROR=String(e));
</script>'''
    page = page.replace('__TITLE__', html.escape(data.get('title', 'Sprite review')))
    page = page.replace('__COUNT__', str(len(images))).replace('__UNIQUE__', str(unique))
    page = page.replace('__MAX__', str(len(images) - 1)).replace('__PAYLOAD__', payload)
    (out / 'review.html').write_text(page)
    receipt = {'technical_review_pack_pass': True, 'source_sha256': sha(path),
               'exposures': len(images), 'unique_rgba_drawings': unique,
               'authored_durations_ms': durations, 'encoded_gif_frames': len(actual),
               'decoded_gif_durations_ms': [d for _, d in actual], 'total_ms': sum(durations),
               'gif_sha256': sha(gif), 'gif_palette_only': True,
               'source_pixels_transformed': False, 'art_approval_granted': False,
               'production_pass': False}
    (out / 'review-pack.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('clip', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.clip, args.out), indent=2))
