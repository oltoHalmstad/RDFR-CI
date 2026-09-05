# RDFR-CI Framework

RDFR-CI is a deployment-governance method for deciding how much operational authority an AI-enabled cybersecurity capability should receive in critical infrastructure. It does not assume that better detection performance automatically justifies more automation.

The workflow is:

```text
Observe -> Preserve -> Contextualize -> Assess -> Recommend -> Authorize -> Act -> Verify -> Learn
```

The deliberate control point is the transition from recommendation to action. AI confidence alone is never sufficient authorization for a process-affecting action.

## Five risk dimensions

- **E — Threat exposure:** likelihood, exposure, loss and control-effectiveness context.
- **D — Detection capability gap:** criticality-weighted missed-detection risk, evaluated under a declared false-positive budget.
- **A — AI-specific risk:** drift, adversarial manipulation, grounding failure and unsafe/policy-violating action.
- **F — Forensic-readiness risk:** the complement of evidence completeness, provenance, timestamp integrity, chain of custody and independent witnessing/replayability.
- **C — Cyber-physical consequence and cascading risk:** consequence if the *defensive action is wrong*, including safety, essential-service availability, dependency/cascade, restoration time and cross-system propagation.

The arithmetic composite is intentionally compensatory. Non-compensability is enforced through independent deployment gates rather than hidden inside the score.

## Independent gates

- `G_S` Safety
- `G_V` Availability
- `G_FA` Forensic accountability
- `G_A` AI assurance
- `G_H` Human authority

Each applicable gate resolves to an authority cap. A failed or unevaluated gate may maintain or reduce authority but can never increase it.

## Authority as a distribution

RDFR-CI reports point scores for transparency but treats values near band boundaries as uncertain decisions. The supplementary analysis propagates `sigma = 0.05` input uncertainty through the model and reports `P(state)` and the probability that uncertainty alone changes the point-estimate authority band.

## Evidence classification

The scenario library is illustrative. It demonstrates governance behavior and computational properties; it does not estimate real sector risk. SWaT is treated separately as an external detector-to-authority validation protocol that requires authorized official data.
