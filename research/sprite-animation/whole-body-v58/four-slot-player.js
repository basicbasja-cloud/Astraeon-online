/* One complete body raster per pose. No joint transforms or limb assembly. */
export const SLOT_NAMES = Object.freeze(['body', 'head', 'weapon', 'trail']);
export function validateClip(clip) {
  if (!Array.isArray(clip.canvas) || clip.canvas.length !== 2 || clip.canvas.some(x => !Number.isInteger(x) || x <= 0)) throw Error('Invalid shared canvas');
  if (clip.bodyPolicy !== 'complete-posed-body-raster') throw Error('A complete posed body is required');
  if (!Array.isArray(clip.frames) || !clip.frames.length) throw Error('No frames');
  for (const f of clip.frames) {
    if (!(Number.isFinite(f.duration_ms) && f.duration_ms > 0)) throw Error('Invalid exposure');
    if (!f.slots?.body || !f.slots?.head) throw Error('Body and complete head required');
    if (Object.keys(f.slots).some(k => !SLOT_NAMES.includes(k))) throw Error('Unexpected runtime body fragment');
    if (!Array.isArray(f.order) || f.order.length !== 4 || new Set(f.order).size !== 4 || f.order.some(k => !SLOT_NAMES.includes(k))) throw Error('Explicit four-slot ordering required');
    for (const slot of Object.values(f.slots)) {
      if (slot === null) continue;
      if (Object.keys(slot).some(k => !['asset','sha256'].includes(k)) || typeof slot.asset !== 'string' || !/^[a-f0-9]{64}$/.test(slot.sha256)) throw Error('Untransformed full-canvas slot image required');
    }
  }
  return true;
}
export function frameAt(clip, milliseconds, loop = true) {
  const total = clip.frames.reduce((n, f) => n + f.duration_ms, 0);
  let t = loop ? ((milliseconds % total) + total) % total : Math.max(0, Math.min(milliseconds, total));
  for (let i = 0; i < clip.frames.length; i++) {
    if (t < clip.frames[i].duration_ms || i === clip.frames.length - 1) return i;
    t -= clip.frames[i].duration_ms;
  }
}
export function drawFrame(context, clip, images, index) {
  const f = clip.frames[index];
  if (!f) throw Error('Unknown frame');
  context.clearRect(0, 0, ...clip.canvas);
  for (const name of f.order) {
    const slot = f.slots[name];
    if (!slot) continue;
    const image = images.get(slot.asset);
    if (!image || image.width !== clip.canvas[0] || image.height !== clip.canvas[1]) throw Error('Slot must preserve shared canvas');
    context.drawImage(image, 0, 0);
  }
}
