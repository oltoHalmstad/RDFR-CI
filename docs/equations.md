# Equations and Implementation Map

## Composite deployment risk

`R_CI = w_E*E + w_D*D + w_A*A + w_F*F + w_C*C`

Implementation: `src/rdfr_ci/risk.py`

Default illustrative weights: `(0.20, 0.20, 0.15, 0.20, 0.25)`.

## Threat exposure

`E = min(1, TailVaR95 / RiskAppetite)`

Implementation: `src/rdfr_ci/exposure.py`

A normalized scenario-based alternative is included for organizations without financial tail-risk modeling.

## Detection capability gap

`D = 1 - sum(q_i * Recall_i) / sum(q_i)`

Operationally, the threshold is selected under `FPR <= phi`, with `phi` explicitly declared.

Implementation: `src/rdfr_ci/detection.py`

## AI-specific risk

`A = alpha1*B + alpha2*P + alpha3*G + alpha4*U`

Implementation: `src/rdfr_ci/ai_risk.py`

Hard events such as successful prompt injection, action-policy bypass or privilege violation can fail `G_A` directly instead of being averaged away.

## Forensic readiness

`Q_F = eta1*EC + eta2*PC + eta3*TI + eta4*CC + eta5*RW`

`F = 1 - Q_F`

Implementation: `src/rdfr_ci/forensic.py`

## Cyber-physical consequence

`C = beta1*H + beta2*V + beta3*K + beta4*T + beta5*R_c`

Implementation: `src/rdfr_ci/consequence.py`

The beta vector must accompany every operational calculation. In the illustrative 30-scenario catalog, the manuscript-level C values are preserved with a neutral equal-component decomposition solely to make the supplied C score reproducible; this is not an empirical decomposition.

## Independent gate cap

Paper form: `Authority_final = min(Authority_R, G_S, G_V, G_FA, G_A, G_H)` on a permissiveness scale.

Software stores a **restriction rank** where `0` is most permissive and `4` most restrictive. The equivalent operation is therefore the maximum rank among the provisional state and applicable gate caps.

Implementation: `src/rdfr_ci/gates.py`

## Authority ceiling

`R_CI >= w_C*C`

`R_min = w_C*C`

Implementation: `src/rdfr_ci/authority.py`

With `w_C = 0.25`, bounded automation becomes unreachable when `C >= 0.80`, because the best possible composite score is then at least `0.20`.

## Agentic/multi-agent authority

Paper form: `Authority_child = min(Authority_parent, S_child, G_S, G_V, G_FA, G_A, G_H)` on a permissiveness scale.

Implementation: `src/rdfr_ci/agent_authority.py` using the software restriction-rank convention.
