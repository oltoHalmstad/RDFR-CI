# RDFR-CI v1.3.0 equations and authority semantics

The publication source of truth is `paper/equations.csv`. Equations (1)-(13) are reproduced there exactly as rendered in the aligned manuscript.

## Authority scale

All v1.3.0 code uses the same scale as manuscript Table 4:

- `0` — Rollback / isolation
- `1` — Shadow / restricted
- `2` — Assisted defense
- `3` — Human-approved intervention
- `4` — Bounded automation

Higher codes therefore mean more permitted AI action. This replaces the inverse restriction-rank convention used by v1.2.1.

## Equation (10): gates and priority stop

For an action that is not explicitly prohibited and whose capability scope is authorized:

`Authority_final = min(Authority_R, G_S, G_V, G_FA, G_A, G_H)`.

The priority prohibition/scope check precedes this minimum. `UNKNOWN` is missing/expired evidence and applies the conservative Table 3 cap; documented `N/A` imposes no cap.

## Equation (12): delegated authority

`Authority_child = min(Authority_parent, Authority_R,child, S_child, G_S,child, G_V,child, G_FA,child, G_A,child, G_H,child)`.

`Authority_R,child` is recomputed from the child's local action, target, state, and evidence. Tool permission is additionally constrained to the intersection of parent-delegable capabilities, child-requested capabilities, and policy-allowed capabilities.
