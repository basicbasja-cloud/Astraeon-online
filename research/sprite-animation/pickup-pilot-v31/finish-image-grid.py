"""Specialize the shared reviewer for surface-only observations; no joint fiction."""
from pathlib import Path
p=Path(__file__).resolve().parent/'image-grid-review.html';s=p.read_text().replace("joint='right.knee'","joint='surface.reaching_cuff'").replace('Grid + joint tracking review','Pickup visible-surface review').replace("const joints=Object.keys(P.tracks.frames[0].points);","const joints=Object.keys(P.tracks.frames[0].points).filter(n=>n.startsWith('surface.'));")
s=s.replace('คลิกจุดจากภาพจริง • blue=ขวา orange=ซ้าย • optical flow เป็นproposal ไม่ใช่ข้อต่อที่ยืนยันแล้ว • source overlayไม่ใช่image observation','จุดผิวรองเท้า/ขอบถุงมือไม่ใช่ข้อต่อที่ซ่อน • anatomical joints ยัง unknown • ใช้ surface markers เท่านั้น • source อยู่บอร์ดแยก ไม่โอน approval').replace('ตรวจanatomical ownerจากภาพแล้ว','Anatomical ownerยังunknownสำหรับsurface proxy')
s=s.replace("window.jointReview={","$('owner').disabled=true;window.jointReview={")
p.write_text(s)
