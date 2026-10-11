// One authoritative action time; body poses and effect decay need different samples.
// This bounds a baked ribbon's final exposure. It is not continuous trail geometry.
export function createAttackSampler(clip, trail) {
  const delays = clip.frame_delays_ms;
  if (!Array.isArray(delays) || !delays.length || delays.some(n => !Number.isFinite(n) || n <= 0)) throw Error('Invalid attack delays');
  const starts = delays.map((_, i) => delays.slice(0, i).reduce((a, b) => a + b, 0));
  const total = delays.reduce((a, b) => a + b, 0);
  const [emitStart, emitEnd] = trail.emitting_seconds.map(n => n * 1000);
  const expires = Math.round(emitEnd + trail.lifetime_seconds * 1000);
  const lastActive = Math.max(...trail.active_key_indices);
  const fadeStart = Math.max(emitEnd, starts[lastActive]);
  if (!(emitStart >= 0 && emitEnd > emitStart && expires > fadeStart && expires <= total)) throw Error('Invalid trail window');
  return function sample(elapsed, interrupted = false) {
    const ms = Math.max(0, Math.min(elapsed, total));
    let frame = starts.length - 1;
    for (let i = 0; i < delays.length; i++) if (ms < starts[i] + delays[i]) { frame = i; break; }
    let fxGain = 0;
    if (!interrupted && ms >= emitStart && ms < expires && trail.active_key_indices.includes(frame)) {
      fxGain = ms < fadeStart ? 1 : (expires - ms) / (expires - fadeStart);
    }
    return {frame, fxGain, effect_expires_ms: expires};
  };
}
