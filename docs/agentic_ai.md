# Agentic and Multi-Agent Authority

RDFR-CI separates reasoning scale from action scale. Specialist agents may search, simulate, correlate or organize evidence inside a sandbox without gaining operational execution privilege.

A privilege-bearing handoff is a fresh authority event. A child agent is constrained by:

- parent authority;
- its own scoped authorization;
- action policy;
- safety, availability, forensic-accountability, AI-assurance and human-authority gates.

The core principles are:

```text
delegation != authority escalation
capability != authority
```

`experiments/run_agent_authority_demo.py` produces three synthetic demonstrations and a JSONL witness log:

1. a high-capability child agent capped at Assisted defense by scope;
2. individually compliant agents whose combined workflow fails a system-level safety gate;
3. authority revocation after an AI-assurance failure.

These are governance demonstrations, not evidence about a particular commercial agent platform.
