# Authority States

RDFR-CI uses five half-open bands. The thresholds are proposed governance parameters, not empirically universal constants.

| Restriction rank | Score rule | State | Typical activity |
|---:|---|---|---|
| 0 | `R_CI < 0.20` | Bounded automation | Reversible, pre-authorized, low-blast-radius actions inside tested limits |
| 1 | `0.20 <= R_CI < 0.35` | Human-approved intervention | AI proposes; qualified human authorizes execution |
| 2 | `0.35 <= R_CI < 0.50` | Assisted defense | Detection, prioritization, evidence collection, simulation, recommendations |
| 3 | `0.50 <= R_CI < 0.65` | Shadow / restricted | Outputs logged and evaluated; no direct process-affecting action |
| 4 | `R_CI >= 0.65` | Rollback / isolation | AI removed from live decision path until revalidation |

A score exactly on `0.20`, `0.35`, `0.50`, or `0.65` enters the more restrictive band. `boundary_margin()` reports the distance to the nearest boundary.

Promotion should depend on the distribution under uncertainty, not only on the point score. A point estimate with `P(point state) < 0.90` is highlighted for review in the supplementary outputs.
