"""Bounded same-rest-basis FK and two-segment diagnostic; not a general retargeter."""
import math
import numpy as np

def rigid_matrix(value):
    m = np.array(value, dtype=float)
    if m.shape != (4, 4) or not np.isfinite(m).all() or not np.allclose(m[3], [0, 0, 0, 1]):
        raise ValueError('Finite affine transforms required')
    if not np.allclose(m[:3, :3].T @ m[:3, :3], np.eye(3), atol=2e-5) or np.linalg.det(m[:3, :3]) <= 0:
        raise ValueError('Adapter requires proper rigid rotation; reject scale/shear/reflection')
    return m

def fk(rest, local, factors, object_world):
    if set(rest) != set(local) or set(rest) != set(factors):
        raise ValueError('Exact complete bone mapping required')
    world = rigid_matrix(object_world)
    done, pending = {}, dict(rest)
    while pending:
        progress = False
        for name, entry in list(pending.items()):
            parent = entry['parent']
            if parent is not None and parent not in done: continue
            f = factors[name]
            if not math.isfinite(f) or f <= 0: raise ValueError('Positive finite edge scales required')
            m = rigid_matrix(local[name])
            m[:3, 3] *= f
            done[name] = (done[parent] @ m) if parent else (world @ m)
            del pending[name]; progress = True
        if not progress: raise ValueError('Missing parent or cyclic hierarchy')
    return done

def two_segment(base, pole, goal, first, second):
    """Preserve lengths/bend half-plane; explicitly report clamped unreachable goals.

    Caller-supplied pole is an observed source bend direction, not a guessed screen side.
    No leg stretching, root correction, surface contact or temporal solver is supplied.
    """
    b, p, g = (np.asarray(x, dtype=float) for x in [base, pole, goal])
    if any(x.shape != (3,) or not np.isfinite(x).all() for x in [b, p, g]):
        raise ValueError('Finite 3D points required')
    if not all(math.isfinite(x) and x > 0 for x in [first, second]): raise ValueError('Positive lengths required')
    d = np.linalg.norm(g - b)
    if d < 1e-10: raise ValueError('Coincident goal needs an authored direction')
    u = (g - b) / d; bend = p - b - u * np.dot(p - b, u)
    if np.linalg.norm(bend) < 1e-10: raise ValueError('Degenerate pole needs an authored bend plane')
    bend /= np.linalg.norm(bend)
    lo, hi = abs(first - second), first + second
    reach = min(max(d, max(lo, 1e-10)), hi)
    x = (first * first - second * second + reach * reach) / (2 * reach)
    y = math.sqrt(max(0, first * first - x * x))
    mid = b + x * u + y * bend; end = b + reach * u
    return {'middle': mid, 'end': end, 'residual': float(np.linalg.norm(end - g)),
            'reachable': bool(lo - 1e-10 <= d <= hi + 1e-10), 'reach_distance': float(d)}
