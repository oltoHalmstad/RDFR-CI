# Conceptual Regulatory and Standards Mapping

RDFR-CI is a deployment-governance layer. It **does not constitute a conformity assessment, compliance certification, legal opinion, or guarantee of compliance**.

The mappings below describe how RDFR-CI can support, map to, complement, or provide operational evidence for existing governance structures.

| Source | RDFR-CI relationship |
|---|---|
| NIST CSF 2.0 | Can support Govern, Identify, Protect, Detect, Respond and Recover decisions by making AI authority, evidence and stop conditions explicit. |
| NIST SP 800-82 Rev. 3 | Provides OT-specific safety, reliability and availability context that informs `C`, `G_S`, `G_V` and action classification. |
| NIST AI RMF | Can inform lifecycle governance of AI risk and assurance, especially `A`, `G_A`, monitoring and authority demotion. |
| NIST Generative AI Profile | Can inform grounding, hallucination, prompt/tool risk and human oversight controls. |
| NIST adversarial-ML taxonomy | Provides threat categories that can inform `A` and hard `G_A` triggers. |
| NISTIR 8428 | Can inform OT forensic collection, readiness, preservation and reconstruction represented by `F` and `G_FA`. |
| Emerging NIST critical-infrastructure AI profile | Can complement RDFR-CI's treatment of bounded operating regions, graceful degradation, deterministic safeguards and fail-safe behavior. |
| NIS2 | Can provide organizational cybersecurity-risk and incident-governance context for operator policies and `G_H`. |
| Critical Entities Resilience Directive | Can inform essential-service continuity, dependency/cascading consequences and `G_V`. |
| EU AI Act | Can inform AI-risk governance, human oversight and deployment-context decisions where applicable. |
| Cyber Resilience Act | Can provide product-lifecycle cybersecurity evidence for `E`, `D`, `A`, `G_A`, availability and connected-system effects. |
| IEC 62443 principles | Can inform zone/conduit design, control effectiveness, security levels, asset context and OT-specific action constraints. |

## Cyber Resilience Act distinction

The CRA addresses product cybersecurity lifecycle and product obligations for products with digital elements. RDFR-CI addresses a different operational question: after an AI-enabled cybersecurity capability is deployed in a critical-infrastructure environment, how much decision and execution authority should it receive?

CRA-related product evidence can inform:

- `E` through exposure and control evidence;
- `D` through security monitoring/test evidence;
- `A` and `G_A` through secure-development, vulnerability handling and lifecycle assurance;
- `V`, `K` and `R_c` through essential-function and connected-system effects.

RDFR-CI extends this evidence into operational forensic readiness, cyber-physical consequence, authority gates, human authorization, rollback and independent witnessing.

Official-source references used in the manuscript include NIST CSF 2.0, NIST SP 800-82 Rev. 3, NIST AI RMF, NISTIR 8428, NIS2, Directive (EU) 2022/2557, Regulation (EU) 2024/1689 and Regulation (EU) 2024/2847.
