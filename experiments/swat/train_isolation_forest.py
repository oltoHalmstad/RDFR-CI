#!/usr/bin/env python3
"""Isolation Forest baseline for the pre-specified SWaT protocol."""
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np


def train_isolation_forest(X_train, seed=42):
    scaler=StandardScaler().fit(X_train)
    Xt=scaler.transform(X_train)
    model=IsolationForest(n_estimators=300,contamination='auto',random_state=seed,n_jobs=-1).fit(Xt)
    return scaler,model


def anomaly_scores(scaler,model,X):
    # Higher is more anomalous and mapped to [0,1] by empirical logistic transform.
    raw=-model.score_samples(scaler.transform(X))
    med=np.median(raw); mad=np.median(np.abs(raw-med))+1e-9
    z=(raw-med)/(1.4826*mad)
    return 1.0/(1.0+np.exp(-z))
