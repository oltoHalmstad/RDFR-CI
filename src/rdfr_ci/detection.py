
"""Detection-gap and threshold-selection helpers (Manuscript Section 3.4, Eqs. 4-5)."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, average_precision_score

def detection_gap(recalls, criticality_weights) -> float:
    """Return D = 1 - sum(q_i Recall_i) / sum(q_i)."""
    r = np.asarray(recalls, dtype=float)
    q = np.asarray(criticality_weights, dtype=float)
    if r.shape != q.shape or r.size == 0:
        raise ValueError("recalls and criticality_weights must have the same non-empty shape")
    if np.any((r < 0) | (r > 1)) or np.any(q < 0) or q.sum() <= 0:
        raise ValueError("recalls must be in [0,1] and criticality weights non-negative with positive sum")
    return float(1.0 - np.dot(q, r) / q.sum())

@dataclass(frozen=True)
class OperatingPoint:
    threshold: float
    precision: float
    recall: float
    f1: float
    fpr: float
    roc_auc: float
    pr_auc: float
    criticality_weighted_recall: float
    detection_gap: float

def _class_recalls(y_true, y_pred, classes, class_values):
    vals = []
    for cv in class_values:
        m = classes == cv
        pos = (y_true[m] == 1)
        denom = int(pos.sum())
        vals.append(float(((y_pred[m] == 1) & pos).sum() / denom) if denom else 0.0)
    return vals

def evaluate_threshold(y_true, scores, threshold, asset_classes=None,
                       class_values=None, criticality_weights=None) -> OperatingPoint:
    """Evaluate one detector threshold, including criticality-weighted recall and D."""
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(scores, dtype=float)
    if y.shape != s.shape or y.ndim != 1:
        raise ValueError("y_true and scores must be one-dimensional and the same length")
    pred = (s >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y, pred, average='binary', zero_division=0)
    neg = y == 0
    fp = int(((pred == 1) & neg).sum())
    fpr = float(fp / neg.sum()) if neg.sum() else 0.0
    try:
        roc_auc = float(roc_auc_score(y, s))
        pr_auc = float(average_precision_score(y, s))
    except ValueError:
        roc_auc = float('nan'); pr_auc = float('nan')
    if asset_classes is None:
        cw_recall = float(recall)
        D = 1.0 - cw_recall
    else:
        classes = np.asarray(asset_classes)
        if class_values is None:
            class_values = list(dict.fromkeys(classes.tolist()))
        if criticality_weights is None:
            criticality_weights = np.ones(len(class_values), dtype=float)
        recalls = _class_recalls(y, pred, classes, class_values)
        D = detection_gap(recalls, criticality_weights)
        cw_recall = 1.0 - D
    return OperatingPoint(float(threshold), float(precision), float(recall), float(f1), float(fpr),
                          roc_auc, pr_auc, float(cw_recall), float(D))

def threshold_sweep(y_true, scores, asset_classes=None, class_values=None,
                    criticality_weights=None, thresholds=None):
    """Evaluate a deterministic grid of thresholds."""
    s = np.asarray(scores, dtype=float)
    if thresholds is None:
        thresholds = np.linspace(max(0.0, float(np.nanmin(s))), min(1.0, float(np.nanmax(s))), 201)
    return [evaluate_threshold(y_true, scores, t, asset_classes, class_values, criticality_weights)
            for t in thresholds]

def select_global_f1(points):
    """Select the threshold maximizing global F1; ties prefer the higher threshold."""
    return max(points, key=lambda p: (p.f1, p.threshold))

def select_authority_point(points, phi: float):
    """Select the threshold minimizing D subject to FPR <= phi.

    Ties prefer lower FPR and then the higher threshold.
    """
    if not 0 <= phi <= 1:
        raise ValueError("phi must lie in [0,1]")
    feasible = [p for p in points if p.fpr <= phi + 1e-12]
    if not feasible:
        raise ValueError("no threshold satisfies the requested FPR budget")
    return min(feasible, key=lambda p: (p.detection_gap, p.fpr, -p.threshold))
