#!/usr/bin/env python3
"""Generate the versioned 30-scenario illustrative RDFR-CI catalog."""
from pathlib import Path
import csv, json, sys
import numpy as np
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rdfr_ci.aggregation import weighted_arithmetic, weighted_power_mean, worst_dimension_blend
from rdfr_ci.authority import authority_from_score, label, boundary_margin
from rdfr_ci.gates import final_authority

W={'E':0.20,'D':0.20,'A':0.15,'F':0.20,'C':0.25}
BETA={'H':0.30,'V':0.25,'K':0.20,'T':0.10,'R_c':0.15}
CAPS={'G_S':1,'G_V':1,'G_FA':2,'G_A':3,'G_H':2}
PASS={k:'pass' for k in CAPS}

def state_changed(v):
    scores=[weighted_arithmetic(v,W), weighted_power_mean(v,W,2), weighted_power_mean(v,W,3), worst_dimension_blend(v,W)]
    return len({int(authority_from_score(s)) for s in scores})>1

def base_record(sid,title,sector,asset,attack,action,rev,blast,effect,v,gate_states=None):
    score=weighted_arithmetic(v,W); prov=authority_from_score(score)
    gates=dict(PASS); gates.update(gate_states or {})
    final,binding=final_authority(prov,gates,CAPS)
    return {
        'scenario_id':sid,'title':title,'sector':sector,'asset_type':asset,
        'attack_description':attack,'defensive_action':action,'reversibility':rev,
        'blast_radius':blast,'physical_process_effect':effect,
        **{k:round(float(v[k]),6) for k in ('E','D','A','F','C')},
        'weights':dict(W),'beta_vector':dict(BETA),
        # The manuscript supplies C directly for the illustrative catalog. Equal-valued
        # components preserve that score exactly while making the beta vector auditable.
        'consequence_components':{k:round(float(v['C']),6) for k in BETA},
        'gate_states':gates,'gate_caps':dict(CAPS),
        'provisional_authority':label(prov),'final_authority':label(final),
        'binding_constraint':binding,'boundary_margin':round(boundary_margin(score),6),
        'assumptions':['Illustrative demonstration input; not a measured sector risk level.',
                       'C decomposition is a neutral equal-component reproduction of the manuscript-level C score; operational use requires elicitation of H, V, K, T and R_c.'],
        'evidence_status':'synthetic/illustrative governance scenario',
        'illustrative_or_empirical':'illustrative'
    }

# Six manuscript showcases, kept exactly aligned with Table 10 point inputs.
records=[]
records.append(base_record('CDI-001','Critical digital infrastructure DDoS response','cloud/digital infrastructure','edge routing and scrubbing service','Volumetric and application-layer denial of service','Rate limiting, traffic scrubbing and bounded route changes','high','low','primarily network-level',{'E':.30,'D':.10,'A':.08,'F':.08,'C':.25}))
records.append(base_record('MFG-001','Smart manufacturing supply-chain compromise','smart manufacturing','engineering workstation and PLC management plane','Signed update contains malicious functionality and begins PLC-management communication','Quarantine package, block C2, revoke credentials; PLC logic change remains approval-gated','medium','medium','production-line effect possible',{'E':.40,'D':.22,'A':.16,'F':.10,'C':.55},{'G_H':'fail'}))
records.append(base_record('SUB-001','Electric-grid substation anomalous remote commands','substations','protection and control equipment','Abnormal remote commands consistent with lateral movement and manipulation','Preserve evidence and segment malicious sessions; trip/switch commands require qualified approval','medium','high','protection-state change possible',{'E':.45,'D':.15,'A':.10,'F':.08,'C':.75},{'G_S':'fail','G_H':'fail'}))
records.append(base_record('RAIL-001','Rail signalling anomaly response','rail','signalling controller and traffic-management network','Anomalous signalling/control messages','Preserve evidence, simulate containment and recommend operator action','medium','high','unsafe service disruption possible',{'E':.35,'D':.20,'A':.12,'F':.15,'C':.85},{'G_H':'fail'}))
records.append(base_record('HOSP-001','Hospital ransomware containment','hospitals','identity, endpoint and clinical-support infrastructure','Credential compromise develops into lateral movement and ransomware behavior','Terminate clearly malicious sessions and preserve evidence; clinical isolation requires operational review','medium','high','care delivery disruption possible',{'E':.70,'D':.25,'A':.18,'F':.20,'C':.65},{'G_V':'fail'}))
records.append(base_record('WATER-001','Water-treatment sensor manipulation','water treatment','PLC, engineering interface and process sensors','Manipulated observations and attempted setpoint changes','Evidence collection and corroboration only; no autonomous setpoint change','low','high','unsafe treatment state possible',{'E':.55,'D':.35,'A':.30,'F':.25,'C':.90},{'G_S':'fail','G_V':'fail','G_FA':'fail','G_A':'fail','G_H':'fail'}))

meta=[
('POWER-001','Electric power EMS credential misuse','electric power','energy management system','Privileged credential misuse triggers anomalous dispatch requests','Revoke session and isolate management channel','high','medium','dispatch degradation possible'),
('BUILD-001','Building automation remote-access compromise','building automation','building management system gateway','External compromise creates unauthorized HVAC and controls maintenance path','Block remote path and preserve gateway evidence','high','medium','building service and occupancy impact possible'),
('SUB-002','Substation relay configuration drift','substations','protective relay configuration','Configuration differs from approved baseline after suspicious access','Freeze remote write access and request engineer validation','high','medium','incorrect relay state could affect protection'),
('WATER-002','Water historian poisoning','water treatment','historian and anomaly-detection feed','Poisoned telemetry biases security analytics','Quarantine data feed and revert to trusted baseline','high','low','indirect process-decision effect'),
('WW-001','Wastewater internet-facing PLC compromise','wastewater','pump-station PLC','Internet-exposed PLC is accessed using stolen credentials','Disable remote access and switch to local/manual monitoring','medium','high','pump control and overflow risk'),
('WW-002','Wastewater HMI ransomware','wastewater','operator HMI','Ransomware encrypts operator workstation','Isolate HMI and fail over to known-good station','medium','medium','loss of visibility/control possible'),
('RAIL-002','Rail maintenance VPN compromise','rail','maintenance VPN and engineering laptop','Compromised maintenance path reaches signalling support network','Terminate VPN and isolate engineering endpoint','high','medium','maintenance outage; no direct signalling write'),
('ROAD-001','Traffic-signal command injection','road/traffic management','intersection controller','Unauthorized command messages target signal timing','Block source and freeze remote timing changes','medium','high','traffic-safety disruption possible'),
('ROAD-002','Traffic-management sensor spoofing','road/traffic management','roadside sensors and control center','Spoofed sensor streams distort congestion response','Quarantine sensor source and retain advisory-only mode','high','medium','misrouting and congestion possible'),
('HEALTH-001','Healthcare identity anomaly','healthcare','regional healthcare identity service','Credential stuffing and impossible-travel activity','Revoke suspicious tokens and require step-up authentication','high','low','limited direct patient-care effect'),
('HEALTH-002','Medical IoT network anomaly','healthcare','networked medical devices','Lateral scanning and anomalous device communication','Micro-segment suspicious source after device-class validation','medium','medium','device availability risk'),
('HOSP-002','Hospital backup compromise','hospitals','backup and recovery infrastructure','Attacker attempts backup deletion before ransomware','Block destructive credentials and preserve immutable snapshots','high','medium','recovery-time consequence'),
('MFG-002','PLC logic integrity mismatch','smart manufacturing','PLC program and engineering station','PLC program hash differs from approved baseline','Block further writes and require engineer diff/restore','medium','high','production or safety effect possible'),
('CHEM-001','Chemical process remote-command anomaly','chemical industry','distributed control system','Unexpected remote commands target process controller','Restrict network path and require process engineer approval','medium','high','process-safety consequence possible'),
('CHEM-002','Safety-instrumented-system access anomaly','chemical industry','SIS engineering interface','Unauthorized access attempt reaches SIS management plane','Disable remote account and preserve forensic image','high','high','safety system availability risk'),
('OIL-001','Pipeline compressor station intrusion','oil and gas','compressor station PLC','Remote maintenance compromise produces abnormal control traffic','Block remote session and transition to approved fallback','medium','high','pressure/flow consequence possible'),
('OIL-002','Pipeline leak-detection data poisoning','oil and gas','leak detection analytics','Manipulated telemetry suppresses anomaly evidence','Quarantine suspect feed and use redundant sensors','high','medium','delayed detection consequence'),
('TEL-001','Telecommunications core DDoS','telecommunications','core network service','High-rate traffic degrades control-plane service','Rate limit and scrub traffic under pre-authorized policy','high','medium','service availability effect'),
('TEL-002','5G management-plane credential compromise','telecommunications','5G management/orchestration','Privileged credentials used for suspicious configuration access','Revoke token and freeze config writes','high','medium','regional service impact possible'),
('CDI-002','Cloud control-plane identity compromise','cloud/digital infrastructure','cloud IAM and orchestration','Compromised privileged identity attempts resource changes','Revoke token, freeze destructive API methods, preserve logs','high','medium','multi-tenant service impact possible'),
('DC-001','Data-center cooling control anomaly','data centers','building/cooling management','Suspicious commands target cooling setpoints','Block remote write and hold deterministic safe setpoints','medium','high','thermal availability consequence'),
('PA-001','Public administration identity compromise','public administration','citizen-services identity platform','Credential compromise and anomalous administrative access','Revoke sessions and rotate privileged credentials','high','low','digital service disruption'),
('FOOD-001','Cold-chain warehouse control anomaly','food supply','refrigeration controller','Unauthorized setpoint changes target cold storage','Freeze remote changes and require local verification','medium','medium','product safety/spoilage risk'),
('LOG-001','Logistics warehouse automation compromise','logistics','warehouse control and robotics','Compromised control service issues abnormal task commands','Pause affected zone and isolate command source','medium','medium','operational delay and equipment risk'),
]
# 24 remaining: deliberately choose 16 aggregation-sensitive and 8 stable scenarios so the
# 30-scenario catalog reproduces the manuscript statement that 21/30 change provisional state
# under at least one alternative operator (the six fixed showcases contribute five changes).
want_changed=[True]*16+[False]*8
# Ten total binding constraints are targeted: fixed showcases have two strict G_H binders.
extra_gate_targets={0:'G_A',2:'G_A',4:'G_H',7:'G_A',9:'G_FA',12:'G_A',16:'G_H',19:'G_A'}
rng=np.random.default_rng(20260905)
for idx,(m,need_change) in enumerate(zip(meta,want_changed)):
    gate=extra_gate_targets.get(idx)
    for attempt in range(200000):
        # Heterogeneous inputs make power-mean sensitivity visible. Consequence is drawn
        # slightly higher than the other dimensions for cyber-physical scenarios.
        vals=rng.beta(1.8,2.4,size=5)
        vals[4]=np.clip(vals[4]*.75+.18,0.08,.95)
        v=dict(zip(('E','D','A','F','C'),map(float,vals)))
        state=int(authority_from_score(weighted_arithmetic(v,W)))
        if gate in ('G_H','G_FA') and state>1: continue
        if gate=='G_A' and state>2: continue
        if state_changed(v)!=need_change: continue
        # Keep stable examples away from boundaries so uncertainty/aggregation stability is meaningful.
        if not need_change and boundary_margin(weighted_arithmetic(v,W))<.035: continue
        break
    else:
        raise RuntimeError('could not generate scenario')
    gates={gate:'fail'} if gate else None
    records.append(base_record(*m,v,gates))

assert len(records)==30
assert len({r['sector'] for r in records})==18
change_count=sum(state_changed({k:r[k] for k in ('E','D','A','F','C')}) for r in records)
assert change_count==21, change_count
binding_counts={}
for r in records: binding_counts[r['binding_constraint']]=binding_counts.get(r['binding_constraint'],0)+1
assert binding_counts.get('Score')==20, binding_counts
assert binding_counts.get('G_A',0)==5, binding_counts

# Write authoritative YAML plus JSON and flattened CSV views.
(ROOT/'scenarios/scenario_catalog.yaml').write_text(yaml.safe_dump({'schema_version':'1.0','notice':'Illustrative demonstration inputs — not measured sector risk levels.','scenarios':records},sort_keys=False,allow_unicode=True),encoding='utf-8')
(ROOT/'scenarios/scenario_catalog.json').write_text(json.dumps({'schema_version':'1.0','notice':'Illustrative demonstration inputs — not measured sector risk levels.','scenarios':records},indent=2,ensure_ascii=False),encoding='utf-8')
flat=[]
for r in records:
    x={k:r[k] for k in ['scenario_id','title','sector','asset_type','attack_description','defensive_action','reversibility','blast_radius','physical_process_effect','E','D','A','F','C','provisional_authority','final_authority','binding_constraint','boundary_margin','evidence_status','illustrative_or_empirical']}
    x['weights']=json.dumps(r['weights'],sort_keys=True); x['beta_vector']=json.dumps(r['beta_vector'],sort_keys=True); x['gate_states']=json.dumps(r['gate_states'],sort_keys=True); x['gate_caps']=json.dumps(r['gate_caps'],sort_keys=True); x['assumptions']=' | '.join(r['assumptions'])
    flat.append(x)
with (ROOT/'scenarios/scenario_catalog.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(flat[0])); w.writeheader(); w.writerows(flat)

showcase_map={'electric_power':'SUB-001','water_treatment':'WATER-001','rail_traffic':'RAIL-001','healthcare':'HOSP-001','smart_manufacturing':'MFG-001','digital_infrastructure':'CDI-001'}
for fn,sid in showcase_map.items():
    r=next(x for x in records if x['scenario_id']==sid)
    (ROOT/f'scenarios/showcases/{fn}.yaml').write_text(yaml.safe_dump(r,sort_keys=False,allow_unicode=True),encoding='utf-8')
print(f'Generated {len(records)} scenarios across {len(set(r["sector"] for r in records))} sectors; aggregation-sensitive={change_count}; bindings={binding_counts}')
