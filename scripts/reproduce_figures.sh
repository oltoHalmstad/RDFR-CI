#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python experiments/generate_static_materials.py
python experiments/run_scenario_analysis.py
python experiments/run_authority_ceiling.py
python experiments/run_detection_threshold_demo.py
python experiments/run_weight_sensitivity.py
