# Forensic Readiness and Independent Witnessing

RDFR-CI treats forensic readiness as an automation-enabling assurance property rather than only a post-incident concern.

The five quality components are:

- `EC` evidence completeness;
- `PC` provenance coverage;
- `TI` timestamp integrity;
- `CC` chain-of-custody completeness;
- `RW` independent witnessing and replayability.

`F = 1 - Q_F`, so better forensic quality reduces forensic-readiness risk.

## Evidence classes to preserve

Relevant evidence can include packet captures, firewall and switch records, historian data, PLC logic/configuration, HMI events, engineering-workstation artifacts, authentication records, sensor values, actuator commands, process state, model version, prompts, system prompts, retrieved context, tool calls, agent memory state, model output, uncertainty, human authorization, executed action, rollback and verification outcome.

## Independent witness principle

The acting AI agent must not be the sole source of the evidence later used to reconstruct its own behavior. Privilege-bearing transitions should be captured at a choke point outside the acting agent's direct control.

For multi-agent workflows, provenance should additionally capture sender and recipient identity, delegated scope, state/memory transferred, available tools, privilege activation/revocation, policy decision and resulting state change.
