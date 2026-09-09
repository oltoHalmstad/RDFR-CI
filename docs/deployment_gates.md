# RDFR-CI v1.3.0 deployment gates

This document mirrors manuscript Section 3.8 and Table 3.

Gate records distinguish `PASS`, `UNKNOWN`, `NOT_APPLICABLE`, and established failure/prohibition. `UNKNOWN` means required evidence is missing or expired; it is not evidence that a violation has occurred. `NOT_APPLICABLE` is allowed only with a recorded rationale.

Default UNKNOWN caps are: `G_S=2`, `G_V=2`, `G_FA=2`, `G_A=1`, and `G_H=2`. Established safety or intolerable-continuity prohibitions select level 0. A forensic-capability failure caps at 2. An AI-assurance failure caps at 1 unless execution enforcement itself is compromised, in which case the priority stop selects 0. A valid required human approval permits only the approved action and caps that action at level 3; when no per-action approval is required, `G_H` may permit up to 4 with documented policy basis.

Changed target, widened scope, changed process state, expired evidence, or expired approval invalidates reuse of the earlier decision.
