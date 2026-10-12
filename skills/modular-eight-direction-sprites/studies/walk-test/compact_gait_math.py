"""Authored endpoint curves; these are design choices, not recovered RO bones."""
import math
def foot_path(phase,stride=.42,stance=.60,lift=.040):
 if not all(math.isfinite(v) for v in [phase,stride,stance,lift]) or stride<=0 or not 0<stance<1 or lift<0:raise ValueError('Finite phase/positive stride, 0<stance<1 and nonnegative lift required')
 phase=phase%1;front=-stride/3
 if phase<stance:return front+stride*phase,0
 q=(phase-stance)/(1-stance);start=front+stride*stance;end=front;m=stride*(1-stance)
 y=(2*q**3-3*q**2+1)*start+(q**3-2*q**2+q)*m+(-2*q**3+3*q**2)*end+(q**3-q**2)*m
 return y,lift*math.sin(math.pi*q)**2
def smooth(q):q=max(0,min(1,q));return q*q*(3-2*q)
def roll(phase):
 if not math.isfinite(phase):raise ValueError('Finite phase required')
 p=phase%1
 if p<.07:return math.radians(-10)*(1-smooth(p/.07))
 if p<.50:return 0
 if p<.60:return math.radians(15)*smooth((p-.50)/.10)
 return math.radians(15-25*smooth((p-.60)/.40))
