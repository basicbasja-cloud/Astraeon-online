# Video-first sword performance v28 — prepared, generator not connected

ผู้ใช้ปฏิเสธท่า v27: แขนงอมากและฟันไร้จิตวิญญาณ
รอบนี้เปลี่ยนเป็น **ภาพตัวละคร → วิดีโอท่าฟันใหม่ → แคปทุกเฟรมจริง**
ใช้เฉพาะตัวตน/ชุด/คุณภาพภาพ ไม่ใช้ rig เดิมหรือภาพท่าโจมตีเก่าเป็นไกด์

**ยังไม่มีวิดีโอที่เจนหรือเฟรมตัวละครจากวิดีโอในรอบนี้**:
เครื่องมือ native สร้างได้เฉพาะภาพ ส่วน Runway ที่ค้นพบรองรับ image-to-video
แต่ยังไม่ติดตั้ง/เชื่อมบัญชี จึงไม่ได้ส่งงานสร้างวิดีโอหรือคิดค่าเครดิตของผู้ให้บริการ

- [ภาพตัวละครท่ายืนใหม่](character-input.png).
- [ภาพอินพุตที่เว้นพื้นที่ให้ท่าฟัน](video-input.png).
- [พรอมป์ต์วิดีโอ](video-prompt.txt) · [คำขอที่เตรียมไว้](video-request.json).
- [ผลตรวจเครื่องมือ](capabilities.json) · [ที่มาภาพ](input-provenance.json).
- [เสียงตอบรับที่ผูกกับ v27 GIF จริง](user-feedback.json).

## Performance direction

One committed diagonal cut, not an idle torso with a waved arm. The fighter loads,
steps or pivots, opens his sword arm into the cut, follows the momentum and regains
composure. Let a natural performance determine limb/weight timing. Do not prescribe
the old FK/IK keys, palm coordinates, frozen support pair or sparse sheet poses.
Use the same character and single sword, fixed full-body view, no trail/particles
for the first motion review. There is no guarantee a video model will preserve
anatomy, identity, grip or camera: inspect the actual result before selecting keys.

Proposed five-second clip. Provider model, supported dimensions, price and actual
API request remain unresolved until the connection is available. The JSON here is
a provider-neutral brief, not an invented successful provider receipt.

## Native frame capture, ready to use

`skills/modular-eight-direction-sprites/scripts/capture-generated-video.py`
requires a real video container and uses the existing decoded-ordinal extractor.
It preserves every presented frame, duplicate visual holds, original PTS and
exposure durations. It does not convert to a requested FPS, trim/recenter/resize
each frame, recover hidden skeletons or imply motion approval. Contact sheets and
unannotated landmark templates are emitted from real video pixels.

After a real video is downloaded, run with its actual provider asset URL/job ID:

```sh
python skills/modular-eight-direction-sprites/scripts/capture-generated-video.py /absolute/path/to/downloaded-video.mp4 --output /tmp/new-native-capture --source-url ACTUAL_PROVIDER_ASSET_URL --provider Runway --job-id ACTUAL_JOB_ID
```

Use a NEW empty output destination. There is deliberately no character MP4/GIF or
fake capture folder here. Missing final-frame duration is not replaced by guessed
average FPS. Actual camera motion remains unknown until reviewed, even though the
prompt requests a fixed camera. Decoding does not establish which generation
conditioners were used: that requires the actual provider receipt.

Four new actual-decoder tests plus five existing capture regressions pass: native
CFR frames with identical holds, unequal native PTS windows, unknown final exposure
refusal, and a renamed GIF refused as video. The synthetic solid-color fixtures
live only in temporary test directories and are NOT the requested sword motion.
No production motion, modular character bank or generated-video result is claimed.

## Continue when connected

Verify Runway connection and discover its current model/schema/credit quote before
submission. Use only `video-input.png` and the performance prompt. Keep the original
video and provider receipt. Review full-speed and slow playback without FX; reject
weak acting, arm collapse, inconsistent sword grip/shape, limb swaps, slipping or
camera changes. Then inspect every native frame, mark visible observations, keep
occluded joints unknown, and choose sparse sprite keys from the successful motion.
