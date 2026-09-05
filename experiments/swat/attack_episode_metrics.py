#!/usr/bin/env python3
"""Event-level metrics for contiguous SWaT attack episodes."""
import numpy as np


def contiguous_event_ids(labels):
    y=np.asarray(labels,dtype=int); ids=np.full(len(y),-1,dtype=int)
    eid=-1; active=False
    for i,v in enumerate(y):
        if v and not active:
            eid+=1; active=True
        elif not v:
            active=False
        if v: ids[i]=eid
    return ids


def event_metrics(labels,predictions,sample_period_seconds=1.0):
    y=np.asarray(labels,dtype=int); p=np.asarray(predictions,dtype=int)
    ids=contiguous_event_ids(y); eids=sorted(set(ids[ids>=0].tolist()))
    detected=0; delays=[]
    for e in eids:
        idx=np.where(ids==e)[0]
        hits=idx[p[idx]==1]
        if len(hits):
            detected+=1; delays.append(float((hits[0]-idx[0])*sample_period_seconds))
    normal=(y==0)
    false_alarms=int(((p==1)&normal).sum())
    normal_hours=max(normal.sum()*sample_period_seconds/3600.0,1e-12)
    return {'events':len(eids),'event_detection_rate':float(detected/len(eids)) if eids else float('nan'),
            'median_ttd_seconds':float(np.median(delays)) if delays else float('nan'),
            'false_alarms_per_hour':float(false_alarms/normal_hours)}
