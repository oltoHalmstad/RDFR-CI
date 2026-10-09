#!/usr/bin/env python3
"""Isolation Forest baseline with an explicit reference segment for Equation (14).

Patched replacement for experiments/swat/train_isolation_forest.py (release v1.3.0).

In v1.3.0, anomaly_scores() computed the median and MAD on the array being scored, so the
calibration segment, the target capture and every perturbed copy were each normalised by
their own statistics ("segment-wise" form). Equation (14) of the manuscript describes the
"training-referenced" form, in which the statistics of the training segment are fixed once
and reused for every scored segment. Both forms are available here and the choice is explicit.

    scaler, model = train_isolation_forest(X_train)
    ref = fit_score_reference(scaler, model, X_train)          # (median, MAD) of the training segment
    a_cal = anomaly_scores(scaler, model, X_cal, reference=ref)     # Equation (14), training-referenced
    a_tgt = anomaly_scores(scaler, model, X_target, reference=ref)
    a_old = anomaly_scores(scaler, model, X_target, reference='segment')   # v1.3.0 behaviour
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def train_isolation_forest(X_train, seed=42):
    scaler = StandardScaler().fit(X_train)
    model = IsolationForest(n_estimators=300, contamination='auto', random_state=seed, n_jobs=-1).fit(scaler.transform(X_train))
    return scaler, model


def raw_scores(scaler, model, X):
    """r(t) = -s_IF(t); higher is more anomalous."""
    return -model.score_samples(scaler.transform(X))


def fit_score_reference(scaler, model, X_reference):
    """Median and MAD of the raw scores on the reference segment S of Equation (14)."""
    raw = raw_scores(scaler, model, X_reference)
    med = float(np.median(raw))
    mad = float(np.median(np.abs(raw - med))) + 1e-9
    return med, mad


def anomaly_scores(scaler, model, X, reference):
    """Robust logistic transform of Equation (14).

    reference: (median, MAD) tuple from fit_score_reference() for the training-referenced form,
               or the string 'segment' to reproduce the segment-wise behaviour of release v1.3.0.
    The argument is required so that the form in use is always stated by the caller.
    """
    raw = raw_scores(scaler, model, X)
    if isinstance(reference, str):
        if reference != 'segment':
            raise ValueError("reference must be a (median, MAD) tuple or 'segment'")
        med = float(np.median(raw)); mad = float(np.median(np.abs(raw - med))) + 1e-9
    else:
        med, mad = reference
    return 1.0 / (1.0 + np.exp(-(raw - med) / (1.4826 * mad)))
