#!/usr/bin/env python3
"""Threshold selection for SWaT under explicit false-positive budgets."""
import numpy as np
from sklearn.metrics import precision_recall_fscore_support,roc_auc_score,average_precision_score


def evaluate_thresholds(normal_scores,attack_scores,attack_labels,thresholds=None):
    if thresholds is None:
        thresholds=np.linspace(0.0,1.0,401)
    y=np.concatenate([np.zeros(len(normal_scores),dtype=int),np.asarray(attack_labels,dtype=int)])
    scores=np.concatenate([normal_scores,attack_scores])
    roc=float(roc_auc_score(y,scores)); pr=float(average_precision_score(y,scores))
    rows=[]
    for t in thresholds:
        pred=(scores>=t).astype(int)
        precision,recall,f1,_=precision_recall_fscore_support(y,pred,average='binary',zero_division=0)
        fpr=float((normal_scores>=t).mean())
        rows.append({'threshold':float(t),'precision':float(precision),'recall':float(recall),'f1':float(f1),
                     'fpr':fpr,'roc_auc':roc,'pr_auc':pr})
    return rows


def select_f1(rows):
    return max(rows,key=lambda r:(r['f1'],r['threshold']))


def select_fpr_constrained(rows,phi):
    feasible=[r for r in rows if r['fpr']<=phi+1e-12]
    if not feasible: raise ValueError(f'No threshold satisfies FPR <= {phi}')
    # Without asset-level criticality labels, SWaT baseline maps D=1-recall.
    # The full experiment may replace this key with criticality_weighted_recall.
    return max(feasible,key=lambda r:(r.get('criticality_weighted_recall',r['recall']),-r['fpr'],r['threshold']))
