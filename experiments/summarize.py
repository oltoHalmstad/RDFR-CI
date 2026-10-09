"""Cross-dataset summary (Table D4 draft) and pre-registered prediction outcomes."""
import json, os, sys
import pandas as pd, numpy as np
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."   # repository root
B = (0.01, 0.05, 0.10)
rows = []
# HAI 21.03 (revision 4 results), HAI 22.04 / 23.05 (replication), BATADAL (pre-registered)
h21 = json.load(open(os.path.join(ROOT, 'results/hai/hai21.03/hai_results.json')))['results']['training_statistics_eq14']
for p in B:
    op = f'Nominal {int(100*p)}%'; e = h21[op]['heldout_pooled']
    exc = e['fpr'] > p and e['fpr_wilson_block'][0] > p
    rows.append(dict(dataset='HAI 21.03', detector='Isolation Forest', budget=op, attacks=e['episodes'], detected=e['episodes_detected'],
                     heldout_fpr=100*e['fpr'], later_rate=np.nan, exceed_heldout=exc, exceed_later=None, provisional=e['level'],
                     mechanism='+'.join([m for m, c in (('gate', exc), ('score', e['level'] <= 1)) if c]) or 'none'))
for v in ('22.04', '23.05'):
    r = json.load(open(os.path.join(ROOT, f'results/hai/hai{v}/hai{v}_results.json')))['results']['training_statistics_eq14']
    for p in B:
        op = f'Nominal {int(100*p)}%'; e = r[op]['heldout_pooled']; l = r[op]['later_pooled']
        exh = e['fpr'] > p and e['fpr_wilson_block'][0] > p; exl = l['flag_rate'] > p and l['wilson_block'][0] > p
        mech = '+'.join([m for m, c in (('gate', exh or exl), ('score', e['level'] <= 1)) if c]) or 'none'
        rows.append(dict(dataset=f'HAI {v}', detector='Isolation Forest', budget=op, attacks=e['episodes'], detected=e['episodes_detected'],
                         heldout_fpr=100*e['fpr'], later_rate=100*l['flag_rate'], exceed_heldout=exh, exceed_later=exl, provisional=e['level'], mechanism=mech))
bt = json.load(open(os.path.join(ROOT, 'results/batadal/batadal_results.json')))
for det, name in (('isolation_forest', 'Isolation Forest'), ('autoencoder', 'Autoencoder')):
    r = bt['primary'][det]['training_referenced']
    for p in B:
        op = f'Nominal {int(100*p)}%'; e = r[op]['test']; pr = bt['predictions'][det][op]
        exl = pr['P1']; exh = pr['P1_exceedance']['later2_test']
        mech = '+'.join([m for m, c in (('gate', exl), ('score', e['level'] <= 1)) if c]) or 'none'
        rows.append(dict(dataset='BATADAL', detector=name, budget=op, attacks=e['episodes'], detected=e['detected'], heldout_fpr=100*e['rate'],
                         later_rate=100*r[op]['later_pooled']['rate'], exceed_heldout=exh, exceed_later=pr['P1_exceedance']['later1_train2'],
                         provisional=e['level'], mechanism=mech))
T = pd.DataFrame(rows); T['final_level'] = np.where(T.mechanism.str.contains('gate'), np.minimum(T.provisional, 1), T.provisional)
T['later_rate_note'] = 'pooled later attack-free periods'
T.to_csv(os.path.join(ROOT, 'results/summary/cross_dataset_summary.csv'), index=False)
pd.set_option('display.width', 220); print(T.round(2).to_string())
