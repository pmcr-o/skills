import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills/pmcro-clean-architecture"


def test_skill_shape_and_contract():
    for folder in ("agents", "scripts", "references", "assets", "tests"):
        assert (SKILL / folder).is_dir()
        assert any(path.is_file() for path in (SKILL / folder).iterdir())
    assert (SKILL / "assets/README.md").is_file()
    surface = json.loads((SKILL / "agents/clean-architecture.json").read_text())
    assert "pmcro-generic-crud" in surface["dependencies"]
    assert "unit_of_work_contract" in surface["outputs"]
    assert set(surface["runtimeAdapters"]) == {"maf-workflows", "codeact-style-executor", "harness-policy-boundary", "maf-mcp-tools"}


def test_simulation_projects_all_layers():
    result = subprocess.run(
        [sys.executable, str(SKILL / "scripts/simulate_architecture.py"), str(SKILL / "assets/application-request.json")],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["simulation"] is True
    assert payload["verified"] is False
    assert payload["architecture"]["layers"] == ["Domain", "Application", "Infrastructure", "API/worker", "Tests"]
    assert any("IGenericRepository" in path for path in payload["output"]["artifacts"])
    assert payload["runtime"]["codeAct"] == "bounded-maker-or-worker-executor"
    assert payload["runtime"]["harness"] == "host-policy-sandbox-budget-evidence"
