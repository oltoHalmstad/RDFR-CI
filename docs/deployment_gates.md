# Independent Deployment Gates

The arithmetic score is compensatory, so RDFR-CI carries non-compensable constraints in explicit gates.

| Gate | Question | Default failure cap |
|---|---|---|
| `G_S` | Could the response violate a defined safety envelope? | Human-approved intervention; stricter action-specific cap permitted |
| `G_V` | Could the response exceed maximum tolerable service disruption? | Human-approved intervention |
| `G_FA` | Is evidence complete, independently witnessed, attributable and replayable? | Assisted defense |
| `G_A` | Is the model within its validated operating region and security policy? | Shadow / restricted |
| `G_H` | Does policy, regulation or the safety case require qualified human authorization? | Assisted defense |

## Status semantics

- `pass`: no additional restriction.
- `fail`: apply the configured failure cap.
- `not_evaluated`: treated conservatively like a failure.
- `not_applicable`: no cap is imposed.

The software does not compound simultaneous gate failures by default. It selects the most restrictive applicable cap. Organizations can implement an additional compounding policy if desired, but that is outside the reference implementation.

Every operational gate decision should carry a rationale and evidence reference. The synthetic catalog stores statuses and caps; real deployments must populate evidence references from their own audit trail.
