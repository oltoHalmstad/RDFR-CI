#!/usr/bin/env python3
"""Lightweight reconstruction autoencoder using scikit-learn MLPRegressor."""
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np


def train_autoencoder(X_train, seed=42):
    scaler=StandardScaler().fit(X_train)
    X=scaler.transform(X_train)
    hidden=max(4,min(64,max(4,X.shape[1]//2)))
    model=MLPRegressor(hidden_layer_sizes=(hidden,),activation='relu',solver='adam',
                       max_iter=150,random_state=seed,early_stopping=True,validation_fraction=.10)
    model.fit(X,X)
    return scaler,model


def reconstruction_scores(scaler,model,X):
    Z=scaler.transform(X)
    recon=model.predict(Z)
    err=np.mean((Z-recon)**2,axis=1)
    med=np.median(err); mad=np.median(np.abs(err-med))+1e-9
    z=(err-med)/(1.4826*mad)
    return 1.0/(1.0+np.exp(-z))
