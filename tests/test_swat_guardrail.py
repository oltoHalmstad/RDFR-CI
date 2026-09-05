from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]

def test_swat_runner_refuses_missing_data(tmp_path):
    p=subprocess.run([sys.executable,str(ROOT/'experiments/swat/run_swat_experiment.py'),'--data-dir',str(tmp_path)],capture_output=True,text=True)
    assert p.returncode==2
    assert 'No empirical SWaT metrics have been generated.' in p.stderr
