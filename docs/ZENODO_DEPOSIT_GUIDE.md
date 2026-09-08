# Zenodo Deposit Guide — RDFR-CI v1.2.1

## File to upload

Upload the clean archival file:

`RDFR-CI-v1.2.1-Zenodo.zip`

The archive intentionally excludes restricted SWaT raw files, `.git` history, virtual environments, caches, and labeled A1/A2 result folders.

## Recommended Zenodo metadata

**Upload type:** Software  
**Title:** RDFR-CI: Reference Implementation, Scenario Library and Evaluation Harness  
**Version:** 1.2.1  
**Publication date:** 2026-09-08  
**Access:** Open  
**License:** MIT  
**Language:** English

**Creators:**

1. Olga Torstensson — Halmstad University
2. Dmytro Prokopovych-Tkachenko — University of Customs and Finance

**Description:**

Supplementary and reproducibility package for the RDFR-CI paper. The archive contains the reference implementation, 30-scenario cross-sector library, uncertainty and sensitivity analyses, multi-agent authority demonstrations, reproducible figures and tables, the pre-specified SWaT A1/A2 validation workflow, and the executed SWaT A11 normal-operation threshold-transfer analysis. The A11 package also contains a separately labeled synthetic perturbation challenge for event-level detection, `D(phi)`, RDFR-CI authority propagation, and bootstrap authority uncertainty. Restricted SWaT raw files are not redistributed.

**Keywords:** critical infrastructure; operational technology; industrial control systems; artificial intelligence; AI governance; forensic readiness; autonomous cyber defense; SWaT; reproducibility

**Related identifier:** `https://github.com/oltoHalmstad/RDFR-CI` (URL; repository associated with the software archive)

## DOI workflow

The DOI reserved for this deposit is **10.5281/zenodo.22662284**.

1. Keep the existing Zenodo draft that owns this reserved DOI.
2. Replace the earlier archive in that draft with the DOI-synchronized `RDFR-CI-v1.2.1-Zenodo-DOI.zip` before publishing.
3. Confirm the metadata against `.zenodo.json` and `ZENODO_DEPOSIT_METADATA.md`.
4. Preview the record and verify that version 1.2.1, both creators, MIT license, and the reserved DOI are correct.
5. Publish the Zenodo record. Publication activates DOI `10.5281/zenodo.22662284`.
6. If the journal article DOI is assigned later, add it as a related identifier with the relation “is supplement to”.
7. Keep the GitHub release and manuscript citation synchronized with this Zenodo DOI.

## Scientific integrity check before publishing

- Confirm no raw SWaT CSV is inside the archive.
- Confirm `results/swat/` contains no unauthorized labeled A1/A2 outputs.
- Keep A11 normal-only empirical results distinct from synthetic perturbation results.
- Do not describe the synthetic challenge as real attack-detection performance.
