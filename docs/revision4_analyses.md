# Revision-4 analyses: design summary

| Analysis | Data and roles | Protocol | Outputs |
|---|---|---|---|
| HAI 21.03 corrected | train1 80/20 training/calibration; test1–2 F₁ selection; test3 from 13 Jul 2020 12:00:01, test4, test5 held-out | 60 s windows, 5 s step; Isolation Forest (300 trees); training-referenced Eq. (14); block-basis Wilson, moving-block bootstrap, Clopper–Pearson; Eq. (15); seeds 1–20 | Tables 16, D1, D2; Figure 7 |
| HAI 22.04 / 23.05 replication | Earliest normal file 80/20; later labeled files held-out (51 / 52 episodes); remaining normal files as later attack-free periods (253 h / 171 h) | Unchanged | Table D3 |
| BATADAL second system | Training set 1 80/20; 2016 set: F₁ selection and later period 1; 2017 test set: held-out and later period 2 | 24 h windows, 1 h step, 24 h blocks; Isolation Forest and autoencoder; predictions P1–P3 frozen before analysis | Table D4 |
| C-Town consequence simulation | `CTOWN.INP`; 4 attack classes; 3 candidate actions | WNTR, pressure-dependent demand (15 m), 168 h; C_meas, G_S, G_V; policy outcomes under stated assumptions | Tables D5, D6 |

See `preregistration/batadal_ctown/` for the frozen protocol and the record of deviations.
