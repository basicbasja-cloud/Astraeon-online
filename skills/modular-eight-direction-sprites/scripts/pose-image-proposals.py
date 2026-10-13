#!/usr/bin/env python3
"""DWPose ONNX/OpenCV CPU proposals, inverse-mapped to unchanged image pixels.
Independent single-frame detection experiment; raw scores are NOT calibrated
accuracy probabilities. No anatomical owner/contact/production approval.
Preprocessing follows the official DWPose OpenCV/SimCC coordinate convention.
"""
import argparse,hashlib,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
BODY={'left.shoulder':5,'right.shoulder':6,'left.elbow':7,'right.elbow':8,'left.wrist':9,'right.wrist':10,'left.hip':11,'right.hip':12,'left.knee':13,'right.knee':14,'left.ankle':15,'right.ankle':16,'left.toe':17,'right.toe':20}
def infer(net,rgba,roi=None):
 h,w=rgba.shape[:2];box=np.array(roi if roi is not None else [0,0,w,h],float);center=(box[:2]+box[2:])/2;scale=(box[2:]-box[:2])*1.25
 if min(scale)<=0:raise ValueError('Empty model ROI')
 aspect=288/384
 if scale[0]>scale[1]*aspect:scale[1]=scale[0]/aspect
 else:scale[0]=scale[1]*aspect
 mat=np.array([[288/scale[0],0,144-center[0]*288/scale[0]],[0,384/scale[1],192-center[1]*384/scale[1]]],np.float32)
 rgb=np.rint(rgba[:,:,:3]*(rgba[:,:,3:4]/255)+39*(1-rgba[:,:,3:4]/255)).astype(np.uint8)
 crop=cv2.warpAffine(rgb,mat,(288,384),flags=cv2.INTER_LINEAR)
 blob=((crop.astype(np.float32)-np.array([123.675,116.28,103.53],np.float32))/np.array([58.395,57.12,57.375],np.float32)).transpose(2,0,1)[None]
 net.setInput(blob);outputs=net.forward(net.getUnconnectedOutLayersNames())
 if len(outputs)!=2:raise ValueError('Expected two SimCC axes')
 sx,sy=outputs
 if sx.shape[-1]!=576 or sy.shape[-1]!=768:raise ValueError('Unexpected model shape; verify actual checkpoint/input convention')
 xs=np.argmax(sx[0],axis=1)/2;ys=np.argmax(sy[0],axis=1)/2;scores=np.minimum(sx[0].max(axis=1),sy[0].max(axis=1));points={}
 for name,i in BODY.items():
  xy=np.array([xs[i],ys[i]])/np.array([288,384])*scale+center-scale/2;score=float(scores[i]);inside=0<=xy[0]<w and 0<=xy[1]<h
  points[name]={'xy':xy.tolist(),'raw_model_score':score,'status':'proposal' if inside and score>.3 else 'unknown','anatomical_identity_verified':False,'score_is_accuracy_probability':False}
 return {'points':points,'model_input_roi_xyxy':box.tolist(),'image_to_model_affine':mat.tolist(),'model_to_image_affine':cv2.invertAffineTransform(mat).tolist(),'image_pixels_modified':False,'production_pass':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--images',type=Path,nargs='+',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cv2.setNumThreads(2);net=cv2.dnn.readNetFromONNX(str(a.model));net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV);net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU);results=[]
 for f in a.images:
  with Image.open(f) as image:rgba=np.array(image.convert('RGBA'))
  r=infer(net,rgba);r.update(file=str(f),image_sha256=hashlib.sha256(f.read_bytes()).hexdigest());results.append(r)
 report={'schema':'dwpose-raw-image-proposals-v1','model_sha256':hashlib.sha256(a.model.read_bytes()).hexdigest(),'opencv':cv2.__version__,'results':results,'source_method':'https://github.com/IDEA-Research/DWPose/tree/opencv_onnx','pose_model_trained_on_our_sprites':False,'accuracy_on_painted_art':None,'production_pass':False};a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'images':len(results),'production_pass':False}))
if __name__=='__main__':main()
