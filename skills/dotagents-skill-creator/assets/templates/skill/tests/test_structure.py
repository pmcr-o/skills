from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]


def test_required_shape_and_agent_surface():
    for folder in ("agents", "scripts", "references", "assets", "tests"):
        assert (ROOT / folder).is_dir()
        assert any(path.is_file() for path in (ROOT / folder).iterdir())
    data = json.loads((ROOT / "agents/agent.json").read_text(encoding="utf-8"))
    assert data["independentSurface"] is True
    assert data["samplePromptsRef"] == "references/sample-prompts.md"
    assert data["maxDepth"] == 1
    assert "ollama" in data["providers"]
