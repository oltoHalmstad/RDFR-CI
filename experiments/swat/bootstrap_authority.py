#!/usr/bin/env python3
"""Attack-episode bootstrap for D(phi) and RDFR-CI authority uncertainty."""
import numpy as np


def state_rank(score):
    if score<.20:return 0
    if score<.35:return 1
    if score<.50:return 2
    if score<.65:return 3
    return 4


def bootstrap_episode_recall(event_detected,n_boot=10000,seed=42):
    x=np.asarray(event_detected,dtype=float)
    if x.size==0: raise ValueError('event_detected must contain at least one episode')
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,len(x),size=(int(n_boot),len(x)))
    return x[idx].mean(axis=1)


def bootstrap_water_authority(event_detected,n_boot=10000,seed=42):
    recall=bootstrap_episode_recall(event_detected,n_boot,seed)
    D=1-recall
    scores=.430+.20*D
    states=np.array([state_rank(x) for x in scores])
    probs=np.bincount(states,minlength=5)/len(states)
    return {'mean_D':float(D.mean()),'mean_R_CI':float(scores.mean()),
            'p_bounded':float(probs[0]),'p_human_approved':float(probs[1]),'p_assisted':float(probs[2]),
            'p_shadow':float(probs[3]),'p_rollback':float(probs[4])}
