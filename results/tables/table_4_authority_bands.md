| Composite score     | State                       | Permitted AI activity                                                            |
|:--------------------|:----------------------------|:---------------------------------------------------------------------------------|
| R_CI < 0.20         | Bounded automation          | Reversible, pre-authorized, low-blast-radius actions inside tested safety limits |
| 0.20 <= R_CI < 0.35 | Human-approved intervention | AI proposes containment; qualified human authorizes execution                    |
| 0.35 <= R_CI < 0.50 | Assisted defense            | Detection, prioritization, evidence collection, simulation and recommendations   |
| 0.50 <= R_CI < 0.65 | Shadow / restricted         | Outputs logged and evaluated; no direct process-affecting action                 |
| R_CI >= 0.65        | Rollback / isolation        | AI removed from the live decision path until revalidation                        |