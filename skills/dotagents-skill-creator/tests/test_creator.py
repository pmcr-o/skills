import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills/dotagents-skill-creator/scripts/bootstrap_workspace.py"
VALIDATOR = ROOT / "skills/dotagents-skill-creator/scripts/validate_workspace.py"


def run(*args):
    return subprocess.run([sys.executable, *args], text=True, capture_output=True)


class CreatorTests(unittest.TestCase):
    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            result = run(str(SCRIPT), "--root", str(workspace), "--skill", "sample-skill", "--plugin", "personal")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(workspace.exists())


    def test_apply_validate_and_repeat(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            args = [str(SCRIPT), "--root", str(workspace), "--skill", "sample-skill", "--plugin", "personal", "--apply"]
            first = run(*args)
            self.assertEqual(first.returncode, 0, first.stderr)
            checked = run(str(VALIDATOR), "--root", str(workspace))
            self.assertEqual(checked.returncode, 0, checked.stderr)
            second = run(*args)
            self.assertEqual(second.returncode, 0, second.stderr)
            manifest = json.loads((workspace / "dotagents.manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["sourceOfTruth"], ".agents/skills")
            self.assertIn("personal/sample-skill", manifest["components"])
            request = json.loads((workspace / ".agents/requests/create-skill/personal--sample-skill.json").read_text(encoding="utf-8"))
            self.assertEqual(request["requiredInvoker"], "create-skill")


    def test_unknown_conflict_halts(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            target = workspace / ".agents/skills/sample-skill/SKILL.md"
            target.parent.mkdir(parents=True)
            target.write_text("user-owned", encoding="utf-8")
            result = run(str(SCRIPT), "--root", str(workspace), "--skill", "sample-skill", "--plugin", "personal", "--apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown conflicting file", result.stderr)


if __name__ == "__main__":
    unittest.main()
