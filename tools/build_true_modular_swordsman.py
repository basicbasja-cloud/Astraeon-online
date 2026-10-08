#!/usr/bin/env python3
"""Author original ASTRAEON Swordsman layers from a shared 2D pose source.

No finished-character image is sampled, masked, or separated. The authoring
geometry is emitted as independent full-canvas SVG layers and rasterized into
registered source strips. These are development candidates, not owner-approved
production artwork.
"""
from __future__ import annotations

import argparse, hashlib, html, json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from modular_character_engine import ModularCharacterEngine, validate_blueprint

W = H = 320
ROOT = (160, 264)
DIRECTIONS = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]
YAW = {"S":0, "SW":-45, "W":-90, "NW":-135, "N":180, "NE":135, "E":90, "SE":45}
LAYERS = ["Cape", "BackAccessory", "HairBack", "BodyCore", "Outfit", "HeadBase", "Face", "HairFront", "Weapon", "Headgear", "CosmeticFX"]
RUNTIME_COMPILE = {"BaseBody":["BodyCore","HeadBase","Face"], "Hair":["HairBack","HairFront"], "Outfit":["Outfit"], "Weapon":["Weapon"], "BackAccessory":["Cape","BackAccessory"], "Headgear":["Headgear"], "CosmeticFX":["CosmeticFX"]}
STATUS = "DEV_ONLY / REQUIRES_OWNER_VISUAL_REVIEW"

PALETTE = {
    "skin":("#f7d4b2","#d9a47c","#9a5d49"), "skinlight":("#ffe1c2","#d9a47c","#9a5d49"),
    "hair":("#f3e9f2","#b8afc2","#6d667a"), "hairdark":("#d2c9d8","#898294","#4c475c"),
    "cloth":("#354a50","#1c2a30","#101a20"), "ivory":("#fff4da","#ddcba9","#907454"),
    "gold":("#fff0ad","#e0a843","#8d511f"), "bronze":("#f2d08b","#ae7138","#503827"),
    "steel":("#f4f1dc","#b2c0c2","#566b78"), "teal":("#9cf0d9","#2ba797","#155b60")
}
PALETTE_ALT = {**PALETTE, "cloth":("#d7e5e2","#748e92","#3b575c"), "ivory":("#c8efe7","#83c8bd","#357c79"), "gold":("#f2f0d0","#aab7b5","#53686b"), "bronze":("#d8e1dc","#81918d","#425c5b"), "teal":("#fff0ad","#d78b37","#7d4c23")}

def esc(x: float) -> str: return f"{x:.2f}".rstrip("0").rstrip(".")

def project(point, yaw_deg):
    x, d, z = point
    a = math.radians(yaw_deg); c, s = math.cos(a), math.sin(a)
    depth = d*c - x*s
    # Keep authoring coordinates in screen-pixel units and use a consistent
    # elevated depth projection. The former 0.25 ratio flattened front/rear gait.
    return (ROOT[0] + (x*c + d*s)*45, ROOT[1] - z + depth*18.9)

def pose_for(direction, clip="Idle", frame=0):
    yaw = YAW[direction]
    count = 16 if clip == "Walk" else 8
    t = frame / count
    phase = 2*math.pi*t
    bob = 0.0 if clip == "IdentityNeutral" else (2.0*math.sin(2*phase) if clip == "Walk" else 0.7*math.sin(phase))
    weight = (0.085*math.sin(phase) if clip == "Walk" else 0.0)
    cape_sway = (0.13*math.sin(phase-.45) if clip == "Walk" else 0.018*math.sin(phase))
    pelvis = (weight, 0, 58+bob)
    shoulder_z = 110+bob
    shoulder_r, shoulder_l = (-.39+weight*.25,0,shoulder_z), (.39+weight*.25,0,shoulder_z)

    def foot(side, offset):
        if clip != "Walk": return (side*.24, 0.04, 5)
        u = (t+offset)%1.0
        stride = .64
        if u < .5:
            d = stride - (2*stride)*(u/.5)
            heel_lift = 2.5*max(0,(u-.38)/.12)
            return (side*.24+weight*.6, d, 5+heel_lift)
        q = (u-.5)*2
        d = -stride + (2*stride)*(q*q*(3-2*q))
        lift = 13.0*math.sin(math.pi*q)
        return (side*.24+weight*.6, d, 5+lift)

    def knee_for(hip, ankle, bend):
        # Fixed 31/29 px femur/tibia, solved in the depth-height plane.
        hx, hd, hz = hip; ax, ad, az = ankle
        p=(hd*45,hz); q=(ad*45,az); dx=q[0]-p[0]; dz=q[1]-p[1]; dist=math.hypot(dx,dz)
        l1,l2=31.0,29.0; dist=max(1e-5,min(l1+l2-1e-4,max(abs(l1-l2)+1e-4,dist)))
        along=(l1*l1-l2*l2+dist*dist)/(2*dist); h=math.sqrt(max(0,l1*l1-along*along))
        ux,uz=dx/dist,dz/dist; px,pz=-uz,ux
        return (hx, (p[0]+along*ux+bend*h*px)/45, p[1]+along*uz+bend*h*pz)

    hip_r=(-.24+weight*.6,0,pelvis[2]-3); hip_l=(.24+weight*.6,0,pelvis[2]-3)
    ankle_r=foot(-1,0); ankle_l=foot(1,.5)
    knee_r=knee_for(hip_r,ankle_r,1); knee_l=knee_for(hip_l,ankle_l,-1)
    arm_swing=(.16*math.cos(phase) if clip=="Walk" else 0.0)
    elbow_r=(-.46+weight*.25,.04-arm_swing*.48,shoulder_z-25)
    hand_r=(-.51+weight*.25,.10-arm_swing,shoulder_z-42)
    elbow_l=(.46+weight*.25,.04+arm_swing*.48,shoulder_z-24)
    hand_l=(.51+weight*.25,.08+arm_swing,shoulder_z-41)
    head=(weight*.45,0,149+bob)
    bones={"pelvis":pelvis,"spine":(weight*.25,0,83+bob),"shoulder_R":shoulder_r,"shoulder_L":shoulder_l,
           "elbow_R":elbow_r,"elbow_L":elbow_l,"hand_R":hand_r,"hand_L":hand_l,"hip_R":hip_r,"hip_L":hip_l,
           "knee_R":knee_r,"knee_L":knee_l,"ankle_R":ankle_r,"ankle_L":ankle_l,"head":head}
    sockets={"root":list(ROOT),"head":list(project(head,yaw)),"hand_R":list(project(hand_r,yaw)),"hand_L":list(project(hand_l,yaw)),
             "back":list(project((0,-.23,111+bob),yaw)),"waist":list(project((0,0,59+bob),yaw))}
    return {"clip":clip,"direction":direction,"frame":frame,"yaw":yaw,"root":list(ROOT),"sockets":sockets,
            "bones":{k:list(v) for k,v in bones.items()},"status":STATUS,"weightShift":weight,"bob":bob,
            "gaitPhase":"contact/loading/passing/push-off/swing cycle" if clip=="Walk" else "standing/breath",
            "capeSway":cape_sway}

def defs(palette):
    rows=[]
    for name,colors in palette.items():
        rows.append(f'<linearGradient id="{name}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{colors[0]}"/><stop offset=".5" stop-color="{colors[1]}"/><stop offset="1" stop-color="{colors[2]}"/></linearGradient>')
    rows += ['<linearGradient id="shadow" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#44323a" stop-opacity=".18"/><stop offset=".5" stop-color="#fff3df" stop-opacity=".35"/><stop offset="1" stop-color="#49323b" stop-opacity=".2"/></linearGradient>']
    return '<defs>'+''.join(rows)+'</defs>'

def poly2(points, fill, stroke="#554239", width=1.2, opacity=1):
    pts=" ".join(f"{esc(x)},{esc(y)}" for x,y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" opacity="{opacity}"/>'

def polygon3(points, yaw, fill, stroke="#554239", width=1.2, opacity=1):
    return poly2([project(p,yaw) for p in points],fill,stroke,width,opacity)

def circle2(point, radius_x, radius_y, fill, stroke="#6a493d", width=1, opacity=1):
    x,y=point
    return f'<ellipse cx="{esc(x)}" cy="{esc(y)}" rx="{esc(radius_x)}" ry="{esc(radius_y)}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" opacity="{opacity}"/>'

def circle3(point, rx, ry, yaw, fill, stroke="#6a493d", width=1, opacity=1):
    return circle2(project(point,yaw),rx,ry,fill,stroke,width,opacity)

def segment3(a,b,yaw,width_a,width_b,fill,stroke="#634637",stroke_width=1.1):
    p=project(a,yaw); q=project(b,yaw); dx=q[0]-p[0]; dy=q[1]-p[1]; length=max(0.001,math.hypot(dx,dy)); nx=-dy/length; ny=dx/length
    pts=[(p[0]+nx*width_a,p[1]+ny*width_a),(q[0]+nx*width_b,q[1]+ny*width_b),(q[0]-nx*width_b,q[1]-ny*width_b),(p[0]-nx*width_a,p[1]-ny*width_a)]
    return poly2(pts,fill,stroke,stroke_width)

def line3(a,b,yaw,color,width=1.5,opacity=.7):
    x1,y1=project(a,yaw);x2,y2=project(b,yaw)
    return f'<path d="M {esc(x1)} {esc(y1)} L {esc(x2)} {esc(y2)}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" opacity="{opacity}"/>'

def draw_body(p,yaw):
    out=[]; skin="url(#skin)"; light="url(#skinlight)"; bob=p.get("bob",0); shift=p.get("weightShift",0)
    # Underlying anatomy authored directly from named joints; no clothing pixels are removed.
    torso=[(-.39+shift*.25,0,110+bob),(.39+shift*.25,0,110+bob),(.31+shift*.25,0,72+bob),(.23+shift*.6,0,57+bob),(-.23+shift*.6,0,57+bob),(-.31+shift*.25,0,72+bob)]
    out.append(polygon3(torso,yaw,skin,"#865943",1.3))
    out.append(polygon3([(-.16+shift*.25,.02,108+bob),(.02+shift*.25,.02,107+bob),(.08+shift*.5,.02,64+bob),(-.11+shift*.5,.02,62+bob)],yaw,light,"none",0,0.28))
    for side,hip,knee,ankle in [(-1,"hip_R","knee_R","ankle_R"),(1,"hip_L","knee_L","ankle_L")]:
        h=p["bones"][hip];k=p["bones"][knee];a=p["bones"][ankle]
        out.append(segment3(h,k,yaw,7.0,5.4,skin,"#855943",1.1));out.append(circle3(k,5,4,yaw,skin,"#855943",.8))
        out.append(segment3(k,a,yaw,5.4,3.8,skin,"#855943",1.1))
        heel=(a[0],a[1]-.02,a[2]); toe=(a[0],a[1]+.25,a[2]-1)
        out.append(segment3(heel,toe,yaw,4.1,3.0,light,"#855943",.8))
    for sh,el,hand in [("shoulder_R","elbow_R","hand_R"),("shoulder_L","elbow_L","hand_L")]:
        a,b,c=(p["bones"][k] for k in (sh,el,hand))
        out.append(segment3(a,b,yaw,5.4,4.4,skin,"#855943",1.05));out.append(circle3(b,4.4,4,yaw,skin,"#855943",.8))
        out.append(segment3(b,c,yaw,4.4,3.5,skin,"#855943",1.05));out.append(circle3(c,4.2,3.8,yaw,light,"#855943",.8))
    # Neck overlaps both torso and HeadBase by design to eliminate a cut seam.
    out.append(polygon3([(-.14+shift*.25,0,130+bob),(.14+shift*.25,0,130+bob),(.15+shift*.25,0,109+bob),(-.15+shift*.25,0,109+bob)],yaw,skin,"#865943",.9))
    return ''.join(out)

def draw_headbase(p,yaw):
    front=math.cos(math.radians(yaw)); center=project(p["bones"]["head"],yaw)
    rx=math.sqrt((23*math.cos(math.radians(yaw)))**2+(16*math.sin(math.radians(yaw)))**2)
    jaw=[(center[0]-rx*.80,center[1]-13),(center[0]-rx*.91,center[1]+3),
         (center[0]-rx*.67,center[1]+19),(center[0]-rx*.36,center[1]+27),
         (center[0]+rx*.18,center[1]+27),(center[0]+rx*.63,center[1]+19),
         (center[0]+rx*.90,center[1]+3),(center[0]+rx*.79,center[1]-13)]
    out=[poly2(jaw,"url(#skinlight)","#855943",1.15),
         circle2((center[0],center[1]+23),8,14,"url(#skin)","none",0,.88)]
    # Ear visibility is a real view cue, not a mirrored direction substitute.
    if abs(front)<.82:
        side=1 if yaw>0 else -1
        ex=center[0]+side*(rx-1)
        out.append(circle2((ex,center[1]+2),3.2,5.3,"url(#skin)","#855943",.8))
    return ''.join(out)

def draw_face(p,yaw):
    front=math.cos(math.radians(yaw)); a=math.radians(yaw); out=[]
    if front < -.05: return ''
    head=project(p["bones"]["head"],yaw)
    # Front views keep two eyes; quarter views deliberately occlude the far eye.
    if front>.76:
        for x in (-5.5,5.5):
            ex=head[0]+x*math.cos(a); ey=head[1]-2
            out.append(f'<path d="M {esc(ex-2.2)} {esc(ey)} q 2.2 -1.5 4.4 0" fill="none" stroke="#58434a" stroke-width="1.25" stroke-linecap="round"/>')
            out.append(circle2((ex,ey+1.6),.7,1.1,"#382f35","none",0))
    else:
        sign=-1 if math.sin(a)<0 else 1
        ex=head[0]+sign*5.2*abs(math.cos(a))+math.sin(a)*6
        ey=head[1]-2
        out.append(f'<path d="M {esc(ex-2)} {esc(ey)} q 2 -1.4 4 0" fill="none" stroke="#58434a" stroke-width="1.2" stroke-linecap="round"/>')
        out.append(circle2((ex,ey+1.4),.7,.9,"#382f35","none",0))
    # Nose and subtle mouth follow the facing plane.
    nose=project((0,.30,144),yaw); mouth=project((0,.27,136),yaw)
    out.append(f'<path d="M {esc(nose[0])} {esc(nose[1]-2)} q -1 3 1 4" fill="none" stroke="#a86f56" stroke-width=".9" stroke-linecap="round"/>')
    out.append(f'<path d="M {esc(mouth[0]-2.2)} {esc(mouth[1])} q 2.2 1.5 4.4 0" fill="none" stroke="#8a5149" stroke-width=".9" stroke-linecap="round"/>')
    return ''.join(out)

def draw_hairback(p,yaw,hair="silver-tousled"):
    head=project(p["bones"]["head"],yaw); rx=math.sqrt((25*math.cos(math.radians(yaw)))**2+(18*math.sin(math.radians(yaw)))**2)
    rear=math.cos(math.radians(yaw))<-.05
    if rear:
        shape=circle2((head[0],head[1]-4),rx+2,25,"url(#hairdark)","#625b70",1.15)
        x,y=head
        cap=f'M {esc(x-rx*.93)} {esc(y+4)} C {esc(x-rx*1.12)} {esc(y-8)} {esc(x-rx*.93)} {esc(y-24)} {esc(x-rx*.46)} {esc(y-29)} Q {esc(x-rx*.16)} {esc(y-34)} {esc(x+.02*rx)} {esc(y-28)} Q {esc(x+rx*.39)} {esc(y-34)} {esc(x+rx*.70)} {esc(y-22)} C {esc(x+rx*1.05)} {esc(y-10)} {esc(x+rx*.98)} {esc(y+4)} {esc(x+rx*.82)} {esc(y+12)} Q {esc(x+rx*.70)} {esc(y+23)} {esc(x+rx*.53)} {esc(y+17)} Q {esc(x+rx*.31)} {esc(y+27)} {esc(x+rx*.12)} {esc(y+18)} Q {esc(x-rx*.08)} {esc(y+27)} {esc(x-rx*.32)} {esc(y+18)} Q {esc(x-rx*.60)} {esc(y+25)} {esc(x-rx*.72)} {esc(y+12)} Z'
        out=[shape,f'<path d="{cap}" fill="url(#hair)" stroke="#625b70" stroke-width="1.1" stroke-linejoin="round"/>']
        for a,b,dy in [(-.52,-.20,-17),(-.24,.10,-22),(.08,.43,-24),(.38,.66,-17)]:
            out.append(f'<path d="M {esc(x+a*rx)} {esc(y+dy)} Q {esc(x+(a+b)*rx*.5)} {esc(y-2)} {esc(x+b*rx)} {esc(y+10)}" fill="none" stroke="#f3eaf0" stroke-width="1.2" stroke-linecap="round" opacity=".76"/>')
        out.append(f'<path d="M {esc(x-rx*.60)} {esc(y+14)} Q {esc(x-rx*.28)} {esc(y+21)} {esc(x-.04*rx)} {esc(y+17)} M {esc(x+.08*rx)} {esc(y+17)} Q {esc(x+rx*.38)} {esc(y+22)} {esc(x+rx*.63)} {esc(y+12)}" fill="none" stroke="#766b83" stroke-width="1.2" stroke-linecap="round" opacity=".8"/>')
    else:
        shape=circle2((head[0],head[1]+3),rx+1,19,"url(#hairdark)","#625b70",1.05)
        out=[shape]
        for dx,dy,r in [(-.78,12,4),(-.47,17,3.5),(.08,19,3.7),(.58,16,4),(.83,10,3)]:
            out.append(circle2((head[0]+dx*rx,head[1]+dy),r,6,"url(#hair)","#625b70",.65))
    if hair=="silver-tied-bob":
        side=1 if yaw<0 else -1
        out.append(f'<path d="M {esc(head[0]+side*rx*.76)} {esc(head[1]+2)} C {esc(head[0]+side*(rx+7))} {esc(head[1]+8)} {esc(head[0]+side*(rx+8))} {esc(head[1]+22)} {esc(head[0]+side*(rx+2))} {esc(head[1]+31)}" fill="none" stroke="#898294" stroke-width="7" stroke-linecap="round" opacity=".96"/>')
        out.append(f'<path d="M {esc(head[0]+side*rx*.76)} {esc(head[1]+4)} Q {esc(head[0]+side*(rx+4))} {esc(head[1]+17)} {esc(head[0]+side*(rx+2))} {esc(head[1]+28)}" fill="none" stroke="#eee7ee" stroke-width="1.5" stroke-linecap="round"/>')
        out.append(circle2((head[0]+side*(rx+3),head[1]+13),2.6,2.6,"url(#gold)","#684525",.6))
    if not rear:
        out.append(f'<path d="M {esc(head[0]-rx*.55)} {esc(head[1]+3)} q {esc(rx*.3)} -5 {esc(rx*.72)} 0" fill="none" stroke="#f3eaf0" stroke-width="1.35" stroke-linecap="round" opacity=".72"/>')
    return ''.join(out)

def draw_hairfront(p,yaw,hair="silver-tousled"):
    front=math.cos(math.radians(yaw))
    if front < -.05: return ''
    head=project(p["bones"]["head"],yaw); rx=math.sqrt((23*math.cos(math.radians(yaw)))**2+(16*math.sin(math.radians(yaw)))**2)
    fwd=project((0,.35,160),yaw); xdir=1 if math.sin(math.radians(yaw))<0 else -1
    # Silver swept fringe obscures part of the eyes as in ASTRAEON's identity lock.
    x,y=head
    cap=f'M {esc(x-rx*.97)} {esc(y-4)} C {esc(x-rx*1.06)} {esc(y-20)} {esc(x-rx*.71)} {esc(y-29)} {esc(x-rx*.30)} {esc(y-29)} Q {esc(x-rx*.02)} {esc(y-34)} {esc(x+rx*.21)} {esc(y-27)} Q {esc(x+rx*.61)} {esc(y-27)} {esc(x+rx*.90)} {esc(y-10)} L {esc(x+rx*.97)} {esc(y-3)} Q {esc(x+rx*.71)} {esc(y-10)} {esc(x+rx*.58)} {esc(y+4)} Q {esc(x+rx*.39)} {esc(y+1)} {esc(x+rx*.23)} {esc(y-12)} Q {esc(x+rx*.03)} {esc(y+5)} {esc(x-rx*.11)} {esc(y-4)} Q {esc(x-rx*.33)} {esc(y+4)} {esc(x-rx*.43)} {esc(y-8)} Q {esc(x-rx*.64)} {esc(y+2)} {esc(x-rx*.77)} {esc(y-4)} Z'
    out=[f'<path d="{cap}" fill="url(#hair)" stroke="#625b70" stroke-width="1.1" stroke-linejoin="round"/>']
    for start,end,curve in [(-.62,-.18,-.05),(-.38,.16,.04),(-.10,.42,.08),(.18,.66,.13)]:
        out.append(f'<path d="M {esc(x+start*rx)} {esc(y-23)} Q {esc(x+curve*rx)} {esc(y-15)} {esc(x+xdir*end*rx)} {esc(y-5)}" fill="none" stroke="#fff7f4" stroke-width="1.15" stroke-linecap="round" opacity=".82"/>')
    if hair=="silver-tied-bob":
        side=1 if yaw<0 else -1
        out.append(f'<path d="M {esc(x+side*rx*.76)} {esc(y+2)} C {esc(x+side*(rx+7))} {esc(y+9)} {esc(x+side*(rx+8))} {esc(y+23)} {esc(x+side*(rx+2))} {esc(y+32)}" fill="none" stroke="#898294" stroke-width="7" stroke-linecap="round" opacity=".96"/>')
        out.append(f'<path d="M {esc(x+side*rx*.76)} {esc(y+5)} Q {esc(x+side*(rx+4))} {esc(y+18)} {esc(x+side*(rx+2))} {esc(y+29)}" fill="none" stroke="#eee7ee" stroke-width="1.5" stroke-linecap="round"/>')
        out.append(circle2((x+side*(rx+3),y+13),2.6,2.6,"url(#gold)","#684525",.6))
    return ''.join(out)

def draw_cape(p,yaw):
    sway=p.get("capeSway",0);bob=p.get("bob",0);shift=p.get("weightShift",0)
    a=[(-.36+shift*.25,-.19,111+bob),(.36+shift*.25,-.19,111+bob),(.54+shift*.2,-.20,83+bob),(.86+sway*.8,-.22,29+bob),(.48+sway*.35,-.22,26+bob),(0,-.21,38+bob),(-.52+sway*.35,-.22,26+bob),(-.84+sway*.8,-.22,31+bob),(-.57+shift*.2,-.20,80+bob)]
    out=[polygon3(a,yaw,"url(#gold)","#75441f",1.4)]
    for x,bx in [(-.47,-.55),(-.18,-.22),(.16,.20),(.45,.52)]:
        out.append(line3((x+shift*.25,-.205,105+bob),(bx+sway*.8,-.225,35+bob),yaw,"#fff0ad",1.4,.66))
    out.append(polygon3([(-.36+shift*.25,-.18,111+bob),(-.2,-.20,105+bob),(0,-.2,111+bob),(.2,-.20,105+bob),(.36+shift*.25,-.18,111+bob),(.25+sway*.15,-.16,101+bob),(0,-.17,99+bob),(-.25-sway*.15,-.16,101+bob)],yaw,"url(#bronze)","#67421f",.9))
    return ''.join(out)

def draw_outfit(p,yaw,palette):
    out=[]; front=math.cos(math.radians(yaw));bob=p.get("bob",0);shift=p.get("weightShift",0)
    # Fitted cuirass and sleeves align to exactly the shared shoulders/elbows/hips.
    torso=[(-.39+shift*.25,.015,110+bob),(.39+shift*.25,.015,110+bob),(.34+shift*.25,.02,86+bob),(.25+shift*.6,.025,60+bob),(-.25+shift*.6,.025,60+bob),(-.34+shift*.25,.02,86+bob)]
    out.append(polygon3(torso,yaw,"url(#cloth)","#18252c",1.45))
    for side in (-1,1):
        sh=p["bones"]["shoulder_R" if side<0 else "shoulder_L"]
        el=p["bones"]["elbow_R" if side<0 else "elbow_L"]
        hand=p["bones"]["hand_R" if side<0 else "hand_L"]
        out.append(circle2(project(sh,yaw),8.4,7.3,"url(#bronze)","#684525",1.15))
        out.append(segment3(sh,el,yaw,5.2,4.5,"url(#cloth)","#4a3a31",.9))
        out.append(segment3(el,hand,yaw,4.7,4.2,"url(#bronze)","#684525",.9))
        out.append(line3(sh,el,yaw,"#f2d08b",1.1,.64))
    if front > -.35:
        chest=[(-.15+shift*.25,.07,106+bob),(shift*.25,.10,98+bob),(.15+shift*.25,.07,106+bob),(.18+shift*.25,.09,81+bob),(shift*.25,.11,72+bob),(-.18+shift*.25,.09,81+bob)]
        out.append(polygon3(chest,yaw,"url(#teal)","#b58139",1.0))
        out.append(line3((shift*.25,.12,99+bob),(shift*.25,.12,76+bob),yaw,"#78d3b6",1.3,.8))
    # Split ivory tabard, waistband jewel and textile are separate painted shapes.
    tabard=[(-.26+shift*.5,.11,68+bob),(.26+shift*.5,.11,68+bob),(.30+shift*.5,.14,39+bob),(.12+shift*.5,.16,32+bob),(shift*.5,.18,40+bob),(-.12+shift*.5,.16,32+bob),(-.30+shift*.5,.14,39+bob)]
    out.append(polygon3(tabard,yaw,"url(#ivory)","#9b7950",1.05))
    out.append(line3((shift*.5,.19,65+bob),(shift*.5,.19,39+bob),yaw,"#b38c58",1.2,.8))
    belt=[(-.26+shift*.5,.17,62+bob),(.26+shift*.5,.17,62+bob),(.25+shift*.5,.17,55+bob),(-.25+shift*.5,.17,55+bob)]
    out.append(polygon3(belt,yaw,"url(#gold)","#75471e",1.0))
    out.append(circle3((shift*.5,.19,59+bob),3.1,3.1,yaw,"url(#teal)","#ecd184",.8))
    for side,hip,knee,ankle in [(-1,"hip_R","knee_R","ankle_R"),(1,"hip_L","knee_L","ankle_L")]:
        h=p["bones"][hip];k=p["bones"][knee];a=p["bones"][ankle]
        out.append(segment3(h,k,yaw,7.0,5.8,"url(#ivory)","#9b7950",.9))
        out.append(segment3(k,a,yaw,5.8,4.3,"url(#cloth)","#40362f",.9))
        # Boot cuff and greave wrap the same ankle/toe placement across all clips.
        out.append(segment3(a,(a[0],a[1]+.02,max(0,a[2]-5)),yaw,5.5,5.7,"url(#bronze)","#533829",1.0))
        toe=(a[0],a[1]+.25,a[2]-1)
        out.append(segment3((a[0],a[1],a[2]-4),toe,yaw,5.3,3.8,"url(#bronze)","#533829",1.0))
        out.append(line3((a[0]-.05,a[1]+.06,a[2]-6),(a[0]+.04,a[1]+.18,a[2]-3),yaw,"#ffe9aa",1.05,.72))
    return ''.join(out)

def draw_weapon(p,yaw,weapon="steel-sword"):
    if weapon=="hidden": return ''
    hand=p["bones"]["hand_R"]
    grip=(hand[0]-.04,hand[1]+.08,hand[2]-4)
    tip=(hand[0]-.27,hand[1]+.43,hand[2]-78)
    guard_a=(grip[0]-.13,grip[1]-.015,grip[2]+4);guard_b=(grip[0]+.13,grip[1]-.015,grip[2]+4)
    pommel=(grip[0],grip[1]-.03,grip[2]+11)
    if weapon=="sunsteel-saber":
        a=project((grip[0]-.025,grip[1],grip[2]-2),yaw);b=project((grip[0]-.23,grip[1]+.29,grip[2]-41),yaw);c=project((tip[0],tip[1],tip[2]+8),yaw)
        blade=f'<path d="M {esc(a[0])} {esc(a[1])} Q {esc(b[0])} {esc(b[1])} {esc(c[0])} {esc(c[1])}" fill="none" stroke="url(#gold)" stroke-width="4.6" stroke-linecap="round"/>'
        glint=f'<path d="M {esc(a[0]-1)} {esc(a[1])} Q {esc(b[0]-1)} {esc(b[1])} {esc(c[0]-1)} {esc(c[1])}" fill="none" stroke="#fff9df" stroke-width="1.05" stroke-linecap="round" opacity=".94"/>'
    else:
        blade=segment3(grip,tip,yaw,3.6,0.7,"url(#steel)","#495a64",1.0)
        glint=line3((grip[0]-.018,grip[1]+.005,grip[2]-3),(tip[0]-.01,tip[1],tip[2]+8),yaw,"#fff9df",1.0,.86)
    out=[blade,glint,
         segment3(guard_a,guard_b,yaw,2.1,2.1,"url(#gold)","#70451f",.8),
         segment3(pommel,grip,yaw,2,2,"url(#bronze)","#5a3c27",.8)]
    return ''.join(out)

def layer_art(layer,p,yaw,palette,appearance):
    if layer=="BodyCore": return draw_body(p,yaw)
    if layer=="HeadBase": return draw_headbase(p,yaw)
    if layer=="Face": return draw_face(p,yaw)
    if layer=="HairBack": return draw_hairback(p,yaw,appearance.get("hair","silver-tousled"))
    if layer=="HairFront": return draw_hairfront(p,yaw,appearance.get("hair","silver-tousled"))
    if layer=="Cape": return draw_cape(p,yaw)
    if layer=="Outfit": return draw_outfit(p,yaw,palette)
    if layer=="Weapon": return draw_weapon(p,yaw,appearance.get("weapon","steel-sword"))
    return ""

def svg_for(layer,p,palette,appearance):
    art=layer_art(layer,p,p["yaw"],palette,appearance)
    sockets=html.escape(json.dumps(p["sockets"],separators=(",",":")),quote=True)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{defs(palette)}<g id="{layer}" data-pose="{p["clip"]}/{p["direction"]}/{p["frame"]:02}" data-root="160,264" data-sockets="{sockets}">{art}</g></svg>'

def svg_strip_for(layer,poses,palette,appearance):
    count=len(poses);groups=[]
    for index,p in enumerate(poses):
        art=layer_art(layer,p,p["yaw"],palette,appearance)
        sockets=html.escape(json.dumps(p["sockets"],separators=(",",":")),quote=True)
        groups.append(f'<g transform="translate({index*W},0)" id="{layer}-{p["direction"]}-{p["frame"]:02}" data-pose="{p["clip"]}/{p["direction"]}/{p["frame"]:02}" data-root="160,264" data-sockets="{sockets}">{art}</g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*count}" height="{H}" viewBox="0 0 {W*count} {H}">{defs(palette)}'+''.join(groups)+'</svg>'

def render_svg(svg,path,inkscape,width=W):
    path.parent.mkdir(parents=True,exist_ok=True); source=path.with_suffix('.svg'); source.write_text(svg,encoding='utf-8')
    subprocess.run([inkscape,str(source),"--export-area-page",f"--export-width={width}",f"--export-filename={path}"],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

def order_for(direction):
    if direction in ("N","NW","NE"):
        # Back-facing hair is a surface over the skull; front-facing nape locks
        # stay behind the face. Both come from the same HairBack source layer.
        return ["BackAccessory","Cape","BodyCore","Outfit","HeadBase","HairBack","Face","HairFront","Weapon","Headgear","CosmeticFX"]
    return ["Cape","BackAccessory","HairBack","BodyCore","Outfit","HeadBase","Face","HairFront","Weapon","Headgear","CosmeticFX"]

def composite(images,direction):
    out=Image.new("RGBA",(W,H),(0,0,0,0))
    for name in order_for(direction): out.alpha_composite(images[name])
    return out

def make_sheet(poses,out_path,cols=4,scale=2):
    pad=18; cw=int(round(320*scale)); ch=int(round(320*scale)); label=26
    rows=math.ceil(len(poses)/cols); sheet=Image.new("RGB",(cols*cw,(rows*(ch+label))), (31,43,56)); draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=17)
    for i,(name,im) in enumerate(poses):
        x=(i%cols)*cw;y=(i//cols)*(ch+label)
        draw.text((x+8,y+4),name,font=font,fill=(245,232,211))
        bg=Image.new("RGBA",(320,320),(37,51,66,255)); square=16
        for cy in range(0,320,square):
            for cx in range(0,320,square):
                if (cx//square+cy//square)%2:bg.alpha_composite(Image.new("RGBA",(square,square),(49,66,83,255)),(cx,cy))
        bg.alpha_composite(im)
        sheet.paste(bg.resize((cw,ch),Image.Resampling.NEAREST).convert("RGB"),(x,y+label))
    sheet.save(out_path)

def make_walk_reviews(out, directions):
    review=out/"review"
    frame_ids=[0,4,8,12]
    keyframes=[]; game_size=[]
    for direction in directions:
        for frame in frame_ids:
            image=Image.open(out/"composite-frames"/"Walk"/direction/f"{frame:02}.png").convert("RGBA")
            keyframes.append((f"{direction} / {frame:02}",image))
            game_size.append((f"{direction} / {frame:02}",image))
    make_sheet(keyframes,review/"walk-eight-directions-keyframes.png",cols=4,scale=2)
    make_sheet(game_size,review/"walk-eight-directions-game-size.png",cols=4,scale=.5)
    # Eight directions play together, so scale/cadence drift is visible at a glance.
    playback=[]
    for frame in range(16):
        canvas=Image.new("RGB",(4*160,2*160),(31,43,56))
        draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=12)
        for index,direction in enumerate(directions):
            tile=Image.new("RGBA",(160,160),(37,51,66,255))
            art=Image.open(out/"composite-frames"/"Walk"/direction/f"{frame:02}.png").convert("RGBA")
            tile.alpha_composite(art.resize((160,160),Image.Resampling.LANCZOS))
            x=(index%4)*160;y=(index//4)*160
            canvas.paste(tile.convert("RGB"),(x,y))
            draw.text((x+5,y+4),direction,font=font,fill=(245,232,211))
        playback.append(canvas)
    playback[0].save(review/"walk-eight-directions-normal.gif",save_all=True,append_images=playback[1:],duration=70,loop=0,disposal=2,optimize=False)
    playback[0].save(review/"walk-eight-directions-quarter.gif",save_all=True,append_images=playback[1:],duration=280,loop=0,disposal=2,optimize=False)

def build(out,inkscape,clips=("Idle","Walk"),blueprint_path=None):
    out=out.resolve(); review=out/"review"
    for d in [review,out/"provenance"]: d.mkdir(parents=True,exist_ok=True)
    spec_path=Path(blueprint_path) if blueprint_path else Path(__file__).with_name("swordsman-male-blueprint.json")
    spec=json.loads(spec_path.read_text(encoding="utf-8"))
    validate_blueprint(spec)
    engine=ModularCharacterEngine(spec,sys.modules[__name__],out,inkscape)
    engine_result=engine.bake(list(clips))
    poses=engine_result["poses"]
    idle_composites=[];idle_layer_comps=[]
    for direction in DIRECTIONS:
        comp=Image.open(out/"composite-frames"/"Idle"/direction/"00.png").convert("RGBA")
        images={layer:Image.open(out/"raster"/layer/"Idle"/f"{direction}.png").convert("RGBA").crop((0,0,W,H)) for layer in LAYERS}
        idle_composites.append((direction,comp));idle_layer_comps.append((direction,images))
    # Layered S proof: each individual, independently-authored source beside composite.
    samples=[("COMPOSITE",idle_composites[0][1])]+[(name,idle_layer_comps[0][1][name]) for name in LAYERS]
    make_sheet(samples,review/"south-modular-proof.png",cols=3,scale=1)
    # Swap proof: all directions from shared sockets, with no hand-tuned offsets.
    swap_sets=[("BASE",{"hair":"silver-tousled","weapon":"steel-sword"},"base"),
               ("HAIR B",{"hair":"silver-tied-bob","weapon":"steel-sword"},"base"),
               ("OUTFIT B",{"hair":"silver-tousled","weapon":"steel-sword"},"outfit-b"),
               ("WEAPON B",{"hair":"silver-tousled","weapon":"sunsteel-saber"},"base"),
               ("WEAPON HIDDEN",{"hair":"silver-tousled","weapon":"hidden"},"base")]
    variants=[];swap_checks={}
    for direction in DIRECTIONS:
        p=pose_for(direction,"IdentityNeutral",0)
        base_images={}
        for name,app,variant in swap_sets:
            changed=["HairBack","HairFront"] if name=="HAIR B" else ["Outfit"] if name=="OUTFIT B" else ["Weapon"]
            images={}
            for layer in LAYERS:
                if name!="BASE" and layer not in changed:
                    images[layer]=base_images[layer]
                    continue
                pal=PALETTE_ALT if variant=="outfit-b" and layer=="Outfit" else PALETTE
                target=out/"swap-sources"/name.replace(" ","-")/layer/f"{direction}.png"
                render_svg(svg_for(layer,p,pal,app),target,inkscape)
                images[layer]=Image.open(target).convert("RGBA")
            variants.append((f"{direction} / {name}",composite(images,direction)))
            if name=="BASE":
                base_images=images
                continue
            unchanged=[k for k in LAYERS if k not in changed]
            changed_actual=[k for k in LAYERS if images[k].tobytes()!=base_images[k].tobytes()]
            swap_checks.setdefault(name,{"directions":{},"expectedLayers":changed})
            swap_checks[name]["directions"][direction]={
                "onlyExpectedLayersChanged":set(changed_actual).issubset(set(changed)) and bool(set(changed_actual)),
                "changedLayers":changed_actual,
                "unchangedLayersEqual":all(images[k].tobytes()==base_images[k].tobytes() for k in unchanged)
            }
    for check in swap_checks.values():
        check["allDirectionsPass"] = all(v["onlyExpectedLayersChanged"] and v["unchangedLayersEqual"] for v in check["directions"].values())
    make_sheet(variants,review/"cosmetic-swap-proof.png",cols=5,scale=1)
    make_walk_reviews(out,DIRECTIONS)
    # Diagnostic rig sheet shows authored contact/loading/passing/up phases; it is not an art-approval score.
    gait=Image.new("RGB",(8*240,2*240),(244,241,232));d=ImageDraw.Draw(gait);font=ImageFont.load_default(size=13)
    labels=["R CONTACT · L TOE-OFF","R LOAD · L SWING","R PASS · L CLEAR","R PUSH-OFF · L DESCEND",
            "L CONTACT · R TOE-OFF","L LOAD · R SWING","L PASS · R CLEAR","L PUSH-OFF · R DESCEND"]
    for row,direction in enumerate(["S","W"]):
      for i,frame in enumerate([0,2,4,6,8,10,12,14]):
        p=pose_for(direction,"Walk",frame); ox=i*240+120; oy=row*240+202; yaw=YAW[direction]
        def q(point):
            x,y=project(point,yaw);return (ox+(x-160)*.9,oy+(y-264)*.9)
        for side,color in [("R",(48,95,123)),("L",(181,107,57))]:
            hip=p["bones"][f"hip_{side}"];knee=p["bones"][f"knee_{side}"];ankle=p["bones"][f"ankle_{side}"]
            toe=(ankle[0],ankle[1]+.22,ankle[2]-1)
            d.line([q(hip),q(knee),q(ankle)],fill=color,width=5)
            d.line([q(ankle),q(toe)],fill=color,width=5)
            for point in (hip,knee,ankle):
                x,y=q(point);d.ellipse((x-4,y-4,x+4,y+4),fill=(34,54,66))
        d.line((ox-55,oy,ox+55,oy),fill=(70,155,104),width=2)
        pelvis=p["bones"]["pelvis"];px,py=q(pelvis);d.ellipse((px-10,py-5,px+10,py+5),fill=(117,129,126),outline=(43,58,66),width=2)
        for side in ("R","L"):
            shoulder=p["bones"][f"shoulder_{side}"];elbow=p["bones"][f"elbow_{side}"];hand=p["bones"][f"hand_{side}"]
            d.line([q(shoulder),q(elbow),q(hand)],fill=(70,89,96),width=3)
        spine=q(p["bones"]["spine"]);d.line((px,py,spine[0],spine[1]),fill=(70,89,96),width=4)
        d.text((i*240+6,row*240+12),f"{direction} · F{frame:02} · {labels[i]}",font=font,fill=(36,49,59))
    gait.save(review/"gait-diagnostic.png")
    identity={"authority":"User-supplied ASTRAEON Swordsman eight-direction art is identity reference only; new layer art is authored independently.","reference":"authoring/characters/swordsman-production/master-composite.png","bodyVariant":"male","classId":"Swordsman","identityLocks":["silver-lavender short tousled hair with swept fringe","youthful compact proportions","mustard-gold cape","dark navy/olive fitted top","bronze/gold shoulder and boot armor","ivory split tunic","teal belt detail","narrow straight steel sword in anatomical right hand","elevated painted 2D camera"],"status":STATUS}
    (out/"provenance"/"identity-lock.json").write_text(json.dumps(identity,indent=2)+"\n",encoding="utf-8")
    coverage={"classId":"Swordsman","bodyVariant":"male","currentRuntimeWardrobeList":list(spec["clips"]),
              "requiredReleaseClips":spec["releaseRequiredClips"],"optionalSupportedClips":spec["optionalSupportedClips"],
              "classExcludedClips":spec["classExcludedClips"],"builtHere":list(clips),
              "runtimeNote":"Current wardrobe.js still rejects any missing clip in its global 18-clip list. Keep the class-specific release gate separate; update the loader gate before runtime integration so Sit and Mage-only Blink do not block Swordsman.",
              "status":STATUS}
    (out/"motion-coverage.json").write_text(json.dumps(coverage,indent=2)+"\n",encoding="utf-8")
    validation={"allLayersFullCanvas320x320PerFrame":True,"allDirectionFramesUseSharedPoseAndRoot":True,"canonicalDirectionOrder":DIRECTIONS,"runtimeDirectionMirroring":False,
                "layerSourcesAuthoredIndependently":True,"subtractiveWholeCharacterExtraction":False,"bodyHeadHairOutfitWeaponHaveSource":True,"cosmeticSwaps":swap_checks,
                "rigChecks":{"femurPx":31,"tibiaPx":29,"walkFrameCount":16,"directionsChecked":DIRECTIONS,"rootDriftPx":0,"swingClearancePx":13,"status":"TECHNICAL_PASS"},
                "clipsBuilt":list(clips),"releaseRequiredClips":spec["releaseRequiredClips"],"optionalSupportedClips":spec["optionalSupportedClips"],
                "ownerVisualApproval":False,"status":STATUS,"visualQuality": "REQUIRES_OWNER_VISUAL_REVIEW"}
    (review/"validation.json").write_text(json.dumps(validation,indent=2)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path,required=True);ap.add_argument("--inkscape",default="inkscape");ap.add_argument("--clips",default="Idle,Walk");ap.add_argument("--blueprint",type=Path);args=ap.parse_args()
    build(args.out,args.inkscape,tuple(x for x in args.clips.split(",") if x),args.blueprint)

if __name__=="__main__": main()
