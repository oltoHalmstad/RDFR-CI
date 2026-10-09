#!/usr/bin/env python3
"""C-Town action-consequence simulation and policy outcome comparison, implementing Section D of PREREGISTRATION.md.

EPANET 2.2 via WNTR, pressure-dependent demand (required 15 m, minimum 0 m), 168 h, original control rules.
Attacks and defensive actions are time-bounded EPANET rules with priorities above the original controls
(attack 6, action 7), so an action overrides an attack on the same element.

Usage (from the repository root):
    python experiments/ctown_consequence.py --inp data/batadal/raw/CTOWN.INP --batadal-dir data/batadal/raw \
        --attacks data/batadal/batadal_attacks.csv --out-dir results/ctown [--no-new-a3 | --cached-only]
"""
from __future__ import annotations
import argparse, json, os, sys, warnings, hashlib, platform
import numpy as np, pandas as pd, wntr
from wntr.network.controls import Rule, AndCondition, SimTimeCondition, ControlAction
warnings.filterwarnings('ignore')
H = 3600
REQ_P = 15.0
STATIONS = {'A1': dict(links=['PU1', 'PU2'], tank='T1'), 'A2': dict(links=['PU10', 'PU11'], tank='T7'),
            'A3': dict(links=['PU6', 'PU7'], tank='T4'), 'A4': dict(links=['V2'], tank='T2')}
ACTIONS = {'a0': 'no automated action', 'a1': 'station shutdown', 'a2': 'manual fallback (force on)', 'a3': 'zone isolation (tank pipe closed)'}
ATTACK = (24 * H, 96 * H)


def model(inp):
    wn = wntr.network.WaterNetworkModel(inp)
    wn.options.hydraulic.demand_model = 'PDD'; wn.options.hydraulic.required_pressure = REQ_P; wn.options.hydraulic.minimum_pressure = 0.0
    return wn


def force(wn, name, links, status, t0, t1, prio):
    for l in links:
        link = wn.get_link(l)
        cond = AndCondition(SimTimeCondition(wn, '>=', int(t0)), SimTimeCondition(wn, '<', int(t1)))
        wn.add_control(f'{name}_{l}', Rule(cond, [ControlAction(link, 'status', status)], name=f'{name}_{l}', priority=prio))


class SimFailed(Exception):
    pass


def model_rebuild(inp, station, attack, action, t0, t1):
    wn = model(inp); st = STATIONS[station] if station else None
    if attack: force(wn, 'atk', st['links'], 0, *ATTACK, 6)
    if action == 'a1': force(wn, 'act', st['links'], 0, t0, t1, 7)
    elif action == 'a2': force(wn, 'act', st['links'], 1, t0, t1, 7)
    elif action == 'a3': force(wn, 'act', wn.get_links_for_node(st['tank']), 0, t0, t1, 7)
    return wn


def simulate(inp, station=None, attack=False, action='a0', t0=None, t1=None):
    wn = model(inp); st = STATIONS[station] if station else None
    if attack: force(wn, 'atk', st['links'], 0, *ATTACK, 6)
    if action == 'a1': force(wn, 'act', st['links'], 0, t0, t1, 7)
    elif action == 'a2': force(wn, 'act', st['links'], 1, t0, t1, 7)
    elif action == 'a3': force(wn, 'act', wn.get_links_for_node(st['tank']), 0, t0, t1, 7)
    # DEVIATIONS.md item 2: WNTRSimulator instead of EPANET 2.2, whose pressure-dependent solution diverged when a tank was isolated
    n_expected = int(wn.options.time.duration // wn.options.time.report_timestep) + 1
    r = wntr.sim.WNTRSimulator(wn).run_sim(convergence_error=False)
    if len(r.node['demand'].index) < n_expected:                                # retry once with more Newton iterations and backtracking
        r = wntr.sim.WNTRSimulator(model_rebuild(inp, station, attack, action, t0, t1)).run_sim(
            convergence_error=False, solver_options={'MAXITER': 10000, 'BACKTRACKING': True})
    if len(r.node['demand'].index) < n_expected:
        raise SimFailed(float(r.node['demand'].index[-1]) / H)
    J = [j for j in wn.junction_name_list]
    exp = wntr.metrics.expected_demand(wn)[J]; dem = r.node['demand'][J]; P = r.node['pressure']
    dt = np.diff(np.r_[dem.index.values, dem.index.values[-1] + 900]).astype(float)
    unserved = ((exp - dem).clip(lower=0).sum(1) * dt)                       # m3 per report step
    demand_j = [j for j in J if exp[j].max() > 0]
    lowp = (P[demand_j] < REQ_P).sum(1) * dt / H                              # junction-hours per step
    envt = pd.DataFrame({t: ((P[t] <= 0.2) | (P[t] >= wn.get_node(t).max_level - 0.05)) for t in wn.tank_name_list}).mul(dt / H, axis=0)
    env = envt.sum(1)
    expv = exp.sum(1) * dt
    assert (unserved <= expv + 1e-6).all(), 'unserved demand exceeds expected demand'
    out = pd.DataFrame(dict(unserved=unserved, lowp=lowp, env=env, expected=expv, minp=P[demand_j].min(1)), index=dem.index)
    for t in envt: out['env_' + t] = envt[t].values
    return out


CACHE = os.environ.get('RDFR_CTOWN_CACHE', 'results/ctown/cache')    # per-run results; reused when present


def _job(args):
    inp, key, station, attack, action, t0, t1, w0, w1 = args
    f = os.path.join(CACHE, '_'.join(str(k) for k in key) + '.json')
    if os.path.exists(f): return key, json.load(open(f))
    try:
        d = simulate(inp, station, attack, action, t0, t1)
        res = window(d, w0, w1).to_dict() | {'minp': float(d['minp'].min()), 'status': 'ok'}
    except SimFailed as e:
        res = {'unserved': float('nan'), 'lowp': float('nan'), 'env': float('nan'), 'expected': float('nan'), 'minp': float('nan'),
               'status': f'no convergence after {e.args[0]:.1f} h'}
    json.dump(res, open(f, 'w'))
    return key, res


def window(df, a, b):
    m = (df.index >= a) & (df.index < b); return df[m].sum()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--inp', required=True); ap.add_argument('--batadal-dir', required=True)
    ap.add_argument('--attacks', required=True); ap.add_argument('--out-dir', required=True)
    ap.add_argument('--prereg', default='preregistration/batadal_ctown/PREREGISTRATION.md')
    ap.add_argument('--cached-only', action='store_true', help='summarize cached runs only; missing runs are reported as pending')
    ap.add_argument('--no-new-a3', action='store_true', help='do not start uncached zone-isolation runs under attack (DEVIATIONS.md item 12)')
    a = ap.parse_args(); os.makedirs(a.out_dir, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import batadal_evaluation as B
    from concurrent.futures import ProcessPoolExecutor
    attacks = pd.read_csv(a.attacks); feats, _, _ = B.build(a.batadal_dir, attacks, 24)
    det, _ = B.run(feats, 'isolation_forest', 42, 24, variants=('training_referenced',))
    delays = {op: int(np.ceil(r['test']['median_delay_h'])) for op, r in det['training_referenced'].items()}
    timings = sorted({dl + dh for dl in delays.values() for dh in (0, 1, 4)})
    jobs = [(a.inp, ('base', 'fa'), None, False, 'a0', None, None, 48 * H, 96 * H), (a.inp, ('base', 'cal'), None, False, 'a0', None, None, 48 * H, 72 * H),
            (a.inp, ('base', 'atk'), None, False, 'a0', None, None, 24 * H, 168 * H)]
    jobs += [(a.inp, ('fa', s, act), s, False, act, 48 * H, 72 * H, 48 * H, 96 * H) for s in STATIONS for act in ('a1', 'a2', 'a3')]
    jobs += [(a.inp, ('atk', s, 'a0', None), s, True, 'a0', None, None, 24 * H, 168 * H) for s in STATIONS]
    jobs += [(a.inp, ('atk', s, act, tm), s, True, act, ATTACK[0] + tm * H, ATTACK[1], 24 * H, 168 * H)
             for act in ('a2', 'a3') for s in STATIONS for tm in timings]                # slow zone-isolation runs last
    # DEVIATIONS.md item 5: during an attack, a1 forces the attacked elements to the status the attack already imposes,
    # over a sub-interval of the attack, so its hydraulics are identical to a0; the a0 run is reused
    R = {}
    if a.no_new_a3:
        keep = []
        for j in jobs:
            f = os.path.join(CACHE, '_'.join(str(k) for k in j[1]) + '.json')
            if j[1][0] == 'atk' and j[1][2] == 'a3' and not os.path.exists(f):
                R[j[1]] = {'unserved': np.nan, 'lowp': np.nan, 'env': np.nan, 'expected': np.nan, 'minp': np.nan, 'status': 'not run (compute budget)'}
            else: keep.append(j)
        jobs = keep
    if a.cached_only:
        for j in jobs:
            f = os.path.join(CACHE, '_'.join(str(k) for k in j[1]) + '.json')
            R[j[1]] = json.load(open(f)) if os.path.exists(f) else {'unserved': np.nan, 'lowp': np.nan, 'env': np.nan, 'expected': np.nan,
                                                                  'minp': np.nan, 'status': 'pending'}
        jobs = []
    with ProcessPoolExecutor(max_workers=2) as ex:
        for i, (k, v) in enumerate(ex.map(_job, jobs), 1):
            R[k] = v; print(f'run {i}/{len(jobs)}', k, flush=True)
    for s in STATIONS:
        for tm in timings:
            R[('atk', s, 'a1', tm)] = R[('atk', s, 'a0', None)]
    sub = lambda x, y: {m: x[m] - y[m] for m in ('unserved', 'lowp', 'env')}
    out = dict(meta=dict(inp_sha256=hashlib.sha256(open(a.inp, 'rb').read()).hexdigest(), wntr=wntr.__version__, python=platform.python_version(), simulator='WNTRSimulator',
                         prereg_sha256=hashlib.sha256(open(a.prereg, 'rb').read()).hexdigest(),
                         min_pressure_over_runs=float(np.nanmin([v['minp'] for v in R.values()])),
                         failed_runs={'_'.join(map(str, k)): v['status'] for k, v in R.items() if v['status'] != 'ok'}),
               baseline=R[('base', 'atk')], detection_delays_h=delays)
    # ---- 1. consequence of an incorrect action (false alarm: no attack, action 48-72 h, metrics 48-96 h)
    fa = []; expv = R[('base', 'cal')]['expected']
    for s in STATIONS:
        for act in ('a1', 'a2', 'a3'):
            w = sub(R[('fa', s, act)], R[('base', 'fa')]); ok = R[('fa', s, act)]['status'] == 'ok'
            tanks = [k for k in R[('fa', s, act)] if k.startswith('env_')]
            added = sum(max(0.0, R[('fa', s, act)][k] - R[('base', 'fa')][k]) for k in tanks) if tanks else max(0.0, w['env'])
            w['env'] = added                                       # DEVIATIONS.md item 7: positive per-tank additions, no netting across tanks
            c_serv = min(1.0, max(0.0, w['unserved']) / (0.05 * expv)) if ok else np.nan
            c_safe = min(1.0, max(0.0, w['env']) / 24) if ok else np.nan
            fa.append(dict(station=s, action=act, status=R[('fa', s, act)]['status'], negative_pressure=bool(R[('fa', s, act)]['minp'] < 0), unserved_m3=w['unserved'], lowp_junction_h=w['lowp'], envelope_h=w['env'],
                           min_pressure=R[('fa', s, act)]['minp'], C_service=c_serv, C_safety=c_safe, C_meas=max(c_serv, c_safe) if ok else np.nan,
                           G_S=('fail' if w['env'] > 1e-9 else 'pass') if ok else 'not computable',
                           G_V=('fail' if c_serv > 0.20 else 'pass') if ok else 'not computable'))
    FA = pd.DataFrame(fa); out['false_alarm'] = fa
    # ---- 2. attack impact by action and response time (metrics 24-168 h)
    atk = []
    for s in STATIONS:
        atk.append(dict(station=s, action='a0', start_h=None, status=R[('atk', s, 'a0', None)]['status'], **sub(R[('atk', s, 'a0', None)], R[('base', 'atk')])))
        for act in ('a1', 'a2', 'a3'):
            for tm in timings:
                atk.append(dict(station=s, action=act, start_h=tm, status=R[('atk', s, act, tm)]['status'],
                                negative_pressure=bool(R[('atk', s, act, tm)]['minp'] < 0), **sub(R[('atk', s, act, tm)], R[('base', 'atk')])))
    AT = pd.DataFrame(atk); out['attack'] = atk
    # ---- 3. policy outcome comparison on the BATADAL test period (primary detector, seed 42)
    a_tr = None
    raw, _ = B.raw_scores(feats, 'isolation_forest', 42); m0, s0 = B.med_mad(raw['training'])
    A = {k: B.logistic(v, m0, s0) for k, v in raw.items()}
    # DEVIATIONS.md item 4: C_meas values within 0.01 are ties, broken by the protocol's listing order a1, a2, a3
    FA['order'] = FA.action.map({'a1': 1, 'a2': 2, 'a3': 3})
    def pick(df):
        out = {}
        for st_, g in df.dropna(subset=['C_meas']).groupby('station'):
            g = g[g.C_meas <= g.C_meas.min() + 0.01]; out[st_] = g.sort_values('order').action.iloc[0]
        return out
    best = pick(FA[(FA.G_S == 'pass') & (FA.G_V == 'pass')]); lowest = pick(FA)
    # clarification (DEVIATIONS.md, item 1): where no action passes G_S and G_V, gates-only hands the lowest-C_meas action to a human,
    # and the full policy treats every candidate action as prohibited for that station (a0: no AI-recommended action)
    gates_auto = {s: best[s] for s in STATIONS if s in best}
    full_rec = {s: best.get(s, 'a0') for s in STATIONS}
    pol = []
    for op, r in det['training_referenced'].items():
        if not op.startswith('Nominal'): continue
        thr = r['threshold']; f = feats['test']; flag = (A['test'] >= thr) & ~f['w_attack']
        ft = f['ends'][flag]; fa_eps = 0 if len(ft) == 0 else 1 + int((np.diff(ft) >= 24).sum())
        level = r['test']['level']; dl = delays[op]; budget = float(op.split()[1].rstrip('%')) / 100
        gate_exceed = any(bool(r[k]['rate'] > budget and r[k]['wilson_block'][0] > budget) for k in ('later1_train2', 'later2_test'))
        k = r['test']['detected']; n = r['test']['episodes']
        def fa_cost(act):
            x = FA[FA.action == act]; return x.unserved_m3.clip(lower=0).mean(), x.envelope_h.clip(lower=0).mean(), ((x.G_S == 'fail') | (x.G_V == 'fail')).mean()
        def atk_cost(act_by_station, start):
            u = e = 0.0
            for s in STATIONS:
                act = act_by_station[s] if isinstance(act_by_station, dict) else act_by_station
                row = AT[(AT.station == s) & (AT.action == act) & (AT.start_h == start)] if act != 'a0' else AT[(AT.station == s) & (AT.action == 'a0')]
                u += float(row.unserved.iloc[0]); e += float(row.env.iloc[0])
            u, e = u / len(STATIONS), e / len(STATIONS)
            if start is None: return u, e
            u0_, e0_ = atk_cost('a0', None)                      # DEVIATIONS.md item 8: missed attacks take the no-action outcome
            return (k / n) * u + (1 - k / n) * u0_, (k / n) * e + (1 - k / n) * e0_
        u0, e0 = atk_cost('a0', None)
        for dh in (1, 4):
            for rr in (1.0, 0.9, 0.5):
                rows = {}
                def fa_st(st_, act):                                     # consequence of one false action at one station (clipped at zero)
                    if act == 'a0': return 0.0, 0.0, 0.0
                    x = FA[(FA.station == st_) & (FA.action == act)].iloc[0]
                    return max(0.0, x.unserved_m3), max(0.0, x.envelope_h), float(x.G_S == 'fail' or x.G_V == 'fail')
                def mix(plan):                                           # plan: station -> (action, start_h, autonomous?)
                    au_ = {s_: v_ for s_, v_ in plan.items()}
                    u = e = 0.0
                    for s_, (act, st_, _) in au_.items():
                        if act == 'a0': row = AT[(AT.station == s_) & (AT.action == 'a0')]
                        else: row = AT[(AT.station == s_) & (AT.action == act) & (AT.start_h == st_)]
                        u += float(row.unserved.iloc[0]) / len(STATIONS); e += float(row.env.iloc[0]) / len(STATIONS)
                    return (k / n) * u + (1 - k / n) * u0, (k / n) * e + (1 - k / n) * e0   # DEVIATIONS.md item 8
                def false_burden(plan):                                  # alarms attributed to the four stations with equal probability
                    auto = un = en = unsafe = 0.0
                    for s_, (act, _, autonomous) in plan.items():
                        fu_, fe_, ff_ = fa_st(s_, act); w_ = fa_eps / len(STATIONS) * (1.0 if autonomous else (1 - rr))
                        un += w_ * fu_; en += w_ * fe_
                        if autonomous: auto += fa_eps / len(STATIONS); unsafe += fa_eps / len(STATIONS) * ff_
                    return dict(autonomous_false_actions=auto, false_unserved_m3=un, false_envelope_h=en, unsafe_autonomous=unsafe)
                # DEVIATIONS.md item 6: at level 1 (AI path withheld) the operator responds independently with the manual fallback a2
                # after the same detection time plus d_h, identically for Score-only and Full; no AI recommendation reaches the operator
                indep = {s_: ('a2', dl + dh, False) for s_ in STATIONS}
                plans = {'Playbook': ({s_: ('a1', dl, True) for s_ in STATIONS}, None, 'autonomous a1'),
                         'Gates-only': ({s_: ((gates_auto[s_], dl, True) if s_ in gates_auto else (lowest[s_], dl + dh, False)) for s_ in STATIONS}, None,
                                        f'autonomous where gates pass ({len(gates_auto)}/4 stations), else human after {dh} h')}
                plans['Score-only'] = (({s_: ('a1', dl + dh, False) for s_ in STATIONS}, None, f'human executes AI recommendation a1 after {dh} h')
                                       if level == 2 else (indep, 'withheld', f'AI path withheld; operator fallback after {dh} h'))
                lvl = min(level, 1) if gate_exceed else level
                plans['Full RDFR-CI'] = (({s_: (full_rec[s_], dl + dh, False) for s_ in STATIONS}, None, f'human executes gate-selected recommendation after {dh} h')
                                         if lvl == 2 else (indep, 'withheld', f'AI path withheld; operator fallback after {dh} h'))
                for name, (plan, mode, desc) in plans.items():
                    fb = false_burden(plan) if mode is None else dict(autonomous_false_actions=0.0, false_unserved_m3=0.0, false_envelope_h=0.0, unsafe_autonomous=0.0)
                    au, ae = mix(plan)
                    rows[name] = fb | dict(response=desc, attack_unserved_m3=au, attack_envelope_h=ae)
                for p, v in rows.items():
                    pol.append(dict(operating_point=op, provisional_level=level, final_level_full=lvl, human_delay_h=dh, reject_rate=rr, detected=f'{k}/{n}',
                                    false_alarm_episodes=fa_eps, detection_delay_h=dl, policy=p, **v, attack_unserved_no_action_m3=u0, attack_envelope_no_action_h=e0))
    out['best_gate_passing_action'] = best; out['lowest_C_action'] = lowest; out['policy'] = pol
    json.dump(out, open(os.path.join(a.out_dir, 'ctown_results.json'), 'w'), indent=1, default=float)
    FA.to_csv(os.path.join(a.out_dir, 'ctown_false_alarm_consequence.csv'), index=False)
    AT.to_csv(os.path.join(a.out_dir, 'ctown_attack_response.csv'), index=False)
    pd.DataFrame(pol).to_csv(os.path.join(a.out_dir, 'ctown_policy_outcomes.csv'), index=False)
    pd.set_option('display.width', 250)
    print('baseline', out['baseline']); print(FA.round(3).to_string()); print('best', best, 'delays', delays)
    print(AT.round(1).to_string())
    print(pd.DataFrame(pol).query('reject_rate==0.9 and human_delay_h==1').round(1).to_string())


if __name__ == '__main__':
    main()
