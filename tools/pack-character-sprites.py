"""Package complete painted modules, their depth, and deterministic 2D previews.

Depth is a 2D visibility map, not runtime geometry. RG bytes carry the source
16-bit monotonic depth code losslessly. Occluded anatomy remains in each module.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
MODULES=['BodyOutfit','HeadHair','Weapon','Cape','Headgear']
DIRECTIONS=['S','SW','W','NW','N','NE','E','SE']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def compose(colors,depths,enabled=None):
    enabled=MODULES if enabled is None else enabled
    if not enabled:return np.zeros_like(colors[MODULES[0]])
    rgba=np.stack([colors[m] for m in enabled]).astype(np.float32)/255
    z=np.stack([depths[m] for m in enabled])
    order=np.argsort(z,axis=0,kind='stable')[::-1]
    rgba=np.take_along_axis(rgba,order[:,:,:,None],axis=0)
    rgb=np.zeros_like(rgba[0,:,:,:3]);alpha=np.zeros_like(rgba[0,:,:,3:4])
    for image in rgba:
        a=image[:,:,3:4];rgb=image[:,:,:3]*a+rgb*(1-a);alpha=a+alpha*(1-a)
    result=np.concatenate([np.divide(rgb,alpha,out=np.zeros_like(rgb),where=alpha>0),alpha],axis=2)
    return np.uint8(np.clip(np.rint(result*255),0,255))
def frame(folder,direction,index):
    prefix=direction+'-'+str(index).zfill(3)
    color=np.asarray(Image.open(folder/(prefix+'-tile.png')).convert('RGBA'))
    depth=np.asarray(Image.open(folder/(prefix+'-depth.png')))
    assert color.shape==(320,320*(len(MODULES)+1),4) and depth.shape==(320,320*(len(MODULES)+1)) and depth.dtype==np.uint16
    colors={m:color[:,(i+1)*320:(i+2)*320].copy() for i,m in enumerate(MODULES)}
    depths={m:depth[:,(i+1)*320:(i+2)*320].copy() for i,m in enumerate(MODULES)}
    reference=color[:,:320];combined=compose(colors,depths)
    delta=np.abs(combined.astype(np.int16)-reference.astype(np.int16));opaque=reference[:,:,3]>224
    edges=(reference[:,:,3]>0)&~opaque
    mismatches=int(np.sum((combined[:,:,3]>128)!=(reference[:,:,3]>128)))
    stats={'nativeOpaqueMeanRGBError':float(delta[:,:,:3][opaque].mean()) if opaque.any() else 0,
           'nativeOpaqueMeanAlphaError':float(delta[:,:,3][opaque].mean()) if opaque.any() else 0,
           'nativeCoverageMismatchPixels':mismatches,'maximumNativeAlphaError':int(delta[:,:,3].max()),
           'nativeEdgeMeanAlphaError':float(delta[:,:,3][edges].mean()) if edges.any() else 0,
           'clippedBorderPixels':int(np.sum(combined[0,:,3]>64)+np.sum(combined[-1,:,3]>64)+np.sum(combined[:,0,3]>64)+np.sum(combined[:,-1,3]>64)),
           'weaponVisiblePixels':int(np.sum(colors['Weapon'][:,:,3]>64)),
           'headgearVisiblePixels':int(np.sum(colors['Headgear'][:,:,3]>0)),
           'bodyWithoutCapePixels':int(np.sum((1-np.prod(np.stack([1-colors[m][:,:,3].astype(np.float32)/255 for m in ['BodyOutfit','HeadHair','Weapon']]),axis=0))>64/255))}
    return colors,depths,combined,reference,stats

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--native',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--partial',action='store_true');args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    source_hash=digest(args.native);exporter_hash=digest(ROOT/'tools/bake-character-sprites.py')
    key=hashlib.sha256((source_hash+exporter_hash).encode()).hexdigest()[:16];cache=ROOT/'.character-tools/sprite-bakes'/key
    matrix=json.loads((ROOT/'docs/character-factory/new-production-matrix.json').read_text())
    planned=[c for c in matrix['actions'] if c['swordsmanContract']!='excluded']
    clips=[];missing=[];checks={}
    for entry in planned:
        action=entry['action'];folder=cache/action;path=folder/'receipt.json'
        if not path.is_file():missing.append(action);continue
        receipt=json.loads(path.read_text())
        if receipt['directions']!=DIRECTIONS or receipt['bakedFrames']!=list(range(1,receipt['frames']+1)):
            missing.append(action);continue
        assert receipt['nativeSHA256']==source_hash and receipt['exporterSHA256']==exporter_hash
        dest=out/'atlases'/action;dest.mkdir(parents=True,exist_ok=True);strips={};records=[]
        for direction in DIRECTIONS:
            images={m:Image.new('RGBA',(receipt['frames']*320,320)) for m in MODULES+['Composite','NativeReference']}
            zimages={m:Image.new('RGB',(receipt['frames']*320,320)) for m in MODULES}
            for f in range(1,receipt['frames']+1):
                colors,depths,combined,reference,stats=frame(folder,direction,f)
                records.append({'direction':direction,'frame':f,**stats})
                offset=((f-1)*320,0)
                images['Composite'].paste(Image.fromarray(combined),offset);images['NativeReference'].paste(Image.fromarray(reference),offset)
                for module in MODULES:
                    images[module].paste(Image.fromarray(colors[module]),offset)
                    z=depths[module];encoded=np.zeros((320,320,3),dtype=np.uint8);encoded[:,:,0]=z>>8;encoded[:,:,1]=z&255
                    zimages[module].paste(Image.fromarray(encoded),offset)
            strips[direction]={}
            for module,image in images.items():
                p=dest/(module+'-'+direction+'.png');image.save(p,compress_level=2);strips[direction][module]=p.relative_to(out).as_posix()
            for module,image in zimages.items():
                p=dest/('Depth-'+module+'-'+direction+'.png');image.save(p,compress_level=2);strips[direction]['Depth-'+module]=p.relative_to(out).as_posix()
        checks[action]=records;clips.append({**receipt,'strips':strips})
    if missing and not args.partial:raise RuntimeError('Incomplete actions: '+', '.join(missing))
    Image.new('RGBA',(320,320)).save(out/'empty-headgear.png')
    required=[c for c in clips if c['contract']=='required'];allchecks=[c for cs in checks.values() for c in cs]
    issues=[]
    if missing:issues.append('Missing full bakes: '+', '.join(missing))
    if any(c['clippedBorderPixels'] for c in allchecks):issues.append('A composite clips the source canvas')
    if any(c['nativeOpaqueMeanRGBError']>4 or c['nativeOpaqueMeanAlphaError']>3 or c['nativeCoverageMismatchPixels']>64 for c in allchecks):issues.append('Independent part raster differs materially from native composite')
    package={'id':'swordsman-fantasy-production-01','status':'REQUIRES_OWNER_ART_REVIEW','ownerApproved':False,'runtimeAdmitted':False,
             'nativeSHA256':source_hash,'exporterSHA256':exporter_hash,'packerSHA256':digest(Path(__file__)),'cacheKey':key,
             'canvas':[320,320],'root':[160,264],'displayScale':.5,'directions':DIRECTIONS,
             'modules':MODULES,'headgear':{'equipped':any(c['headgearVisiblePixels'] for c in allchecks),'empty':'empty-headgear.png'},
             'compositing':'per-pixel back-to-front source-over from independent RGBA + RG16 depth PNGs',
             'depthEncoding':'unsigned 16-bit monotonic camera-depth code: R high byte, G low byte; point sampling; background 65535',
             'swapScope':'Complete body/outfit, head/hair and cape pixels survive removals. Weapon omits actual holding-hand coverage. Replacements must fit the shared rig, canvas, pose and depth convention.',
             'requiredFramePositionsRendered':8*sum(c['frames'] for c in required),'totalFramePositionsRendered':8*sum(c['frames'] for c in clips),
             'missingActions':missing,'clips':clips,'runtimeContract':'Standalone authoring/2D review; game runtime and existing approved packages are unchanged.'}
    validation={'technicalVerdict':'PASS' if not issues else 'FAIL','visualVerdict':'REQUIRES_ART_REVIEW','ownerApproved':False,'runtimeAdmitted':False,
                'issues':issues,'requiredFramePositionsRendered':package['requiredFramePositionsRendered'],'totalFramePositionsRendered':package['totalFramePositionsRendered'],
                'maximumNativeOpaqueMeanRGBError':max((c['nativeOpaqueMeanRGBError'] for c in allchecks),default=0),
                'maximumNativeOpaqueMeanAlphaError':max((c['nativeOpaqueMeanAlphaError'] for c in allchecks),default=0),
                'maximumNativeCoverageMismatchPixels':max((c['nativeCoverageMismatchPixels'] for c in allchecks),default=0),
                'maximumNativeAlphaError':max((c['maximumNativeAlphaError'] for c in allchecks),default=0),
                'boundaryNote':'Independently antialiased depth sprites can differ at shared subpixel boundaries from one multisampled native render. Metrics above retain those differences.',
                'frames':checks}
    write(out/'package.json',package);write(out/'validation.json',validation)
    write(out/'artifact-manifest.json',{p.relative_to(out).as_posix():{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='artifact-manifest.json'})
    print(json.dumps({k:validation[k] for k in ['technicalVerdict','issues','requiredFramePositionsRendered','totalFramePositionsRendered','maximumNativeOpaqueMeanRGBError','maximumNativeCoverageMismatchPixels']},indent=2))
if __name__=='__main__':main()
