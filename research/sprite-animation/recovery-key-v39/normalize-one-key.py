"""Known whole-canvas resolution normalization, never silhouette/foot fitting."""
from pathlib import Path
from PIL import Image
import hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
raw=P/'repair-raw.png';im=Image.open(raw).convert('RGBA');w,h=im.size
assert w==h,'Requested source plate is square; refuse an unknown output layout'
# Source cell was scaled2x and placed at(128,0) in a1024square.
# Inverse sampling from the actual returned square resolution is fixed by that
# plate contract. No visible feature, bbox, shoe, collar or pose enters this fit.
matrix=[w/512,0,w/8,0,h/512,0]
out=im.transform((384,512),Image.Transform.AFFINE,matrix,Image.Resampling.BICUBIC)
out.save(P/'body-key.png')
bind=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
(P/'normalization.json').write_text(json.dumps(dict(source=bind(raw),output=bind(P/'body-key.png'),native_size=[w,h],known_source_plate=[1024,1024],canonical_size=[384,512],inverse_sampling_affine=matrix,interpolation='Pillow bicubic; one known-canvas resample',foreground_or_foot_fit_used=False),indent=2)+'\n')
