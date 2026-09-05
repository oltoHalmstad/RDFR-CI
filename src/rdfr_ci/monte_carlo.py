
"""Synthetic cyber-physical loss-channel Monte Carlo demonstrations."""
from __future__ import annotations
import numpy as np

def simulate_loss_channels(n=100_000, seed=42, scale=1.0, safety_probability=0.003,
                           cascade_probability=0.02):
    """Generate illustrative event-loss channels.

    This is a reproducible demonstration of threshold-like safety loss, not an
    empirical estimate for any real sector. Monetary units are arbitrary.
    """
    rng = np.random.default_rng(seed)
    cyber = rng.lognormal(mean=np.log(0.8*scale), sigma=.75, size=n)
    operations = rng.lognormal(mean=np.log(0.6*scale), sigma=.85, size=n)
    recovery = rng.lognormal(mean=np.log(0.35*scale), sigma=.70, size=n)
    safety = (rng.random(n) < safety_probability) * rng.lognormal(mean=np.log(28*scale), sigma=.65, size=n)
    cascade = (rng.random(n) < cascade_probability) * rng.lognormal(mean=np.log(4.0*scale), sigma=.9, size=n)
    total = cyber + operations + recovery + safety + cascade
    return {"cyber":cyber,"operations":operations,"recovery":recovery,"safety":safety,"cascade":cascade,"total":total}

def tail_var(values, q=.95):
    x = np.asarray(values, dtype=float)
    var = float(np.quantile(x,q))
    tail = x[x>=var]
    return var, float(tail.mean())
