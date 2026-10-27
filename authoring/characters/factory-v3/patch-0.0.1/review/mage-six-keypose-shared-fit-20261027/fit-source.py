"""Fit one shared scale and whole-frame translations to paired contact annotations.

This cannot fix anatomy or certify a paintover. Never fit one scale per frame.
"""
import numpy as np
from PIL import Image


def fit_contacts(painted, guide):
    painted=np.asarray(painted,dtype=float);guide=np.asarray(guide,dtype=float)
    if painted.shape!=guide.shape or painted.ndim!=3 or painted.shape[1:]!=(2,2) or not len(painted):
        raise ValueError('Expected matching frame x two feet x xy points')
    if not np.isfinite(painted).all() or not np.isfinite(guide).all():raise ValueError('Invalid contacts')
    a=painted-painted.mean(axis=1,keepdims=True);b=guide-guide.mean(axis=1,keepdims=True)
    denominator=float((a*a).sum())
    if denominator<1e-9:raise ValueError('Coincident contacts cannot establish scale')
    scale=float((a*b).sum()/denominator)
    if scale<=0:raise ValueError('Inconsistent contact ordering')
    translations=guide.mean(axis=1)-painted.mean(axis=1)*scale
    residuals=np.linalg.norm(painted*scale+translations[:,None,:]-guide,axis=2)
    return scale,translations,residuals


def transform_master(image, scale, translation):
    pixels=np.asarray(image.convert('RGBA'));ys,xs=np.nonzero(pixels[:,:,3]>0)
    points=np.column_stack([xs,ys])*scale+translation
    if (points<1).any() or (points[:,0]>=image.width-1).any() or (points[:,1]>=image.height-1).any():
        raise ValueError('Shared transform would clip visible pixels')
    return image.convert('RGBA').transform(image.size,Image.Transform.AFFINE,
       (1/scale,0,-translation[0]/scale,0,1/scale,-translation[1]/scale),resample=Image.Resampling.BICUBIC)
