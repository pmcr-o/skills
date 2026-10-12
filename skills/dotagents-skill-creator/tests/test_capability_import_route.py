import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROUTER = ROOT / "skills/dotagents-skill-creator/scripts/route_create_skill.py"


def run(*args):
    return subprocess.run([sys.executable, *args], text=True, capture_output=True)


def capability_import(skill="example-mcp", plugin="integration"):
    return {
        "schemaVersion": 1,
        "kind": "capability.import",
        "status": "generated-unchecked",
        "importId": "mcp:example-mcp:123456789abc",
        "source": {
            "type": "mcp",
            "sourceRef": "fixture://example",
            "nativeId": "example",
            "nativeVersion": None,
            "description": None,
        },
        "transport": {
            "protocol": "mcp",
            "binding": "stdio",
            "protocolVersion": None,
            "endpointRef": None,
            "commandRef": "config://example/command",
            "argsRef": None,
            "authRef": None,
            "secretMaterialIncluded": False,
        },
        "tools": [
            {
                "capabilityId": "example-mcp.read",
                "nativeName": "read",
                "description": "read",
                "inputSchemaRef": "example-mcp.read.input",
                "outputSchemaRef": None,
                "effect": "read",
                "executionAuthorityGranted": False,
                "nativeAnnotations": {"readOnlyHint": True},
            }
        ],
        "resources": [
            {
                "resourceId": "example-mcp.resource.docs",
                "nativeName": "docs",
                "kind": "resource",
                "uri": "repo://docs",
                "uriTemplate": None,
                "description": None,
                "mimeType": "text/markdown",
                "executable": False,
            }
        ],
        "prompts": [
            {
                "promptId": "example-mcp.prompt.review",
                "nativeName": "review",
                "description": None,
                "argumentsSchemaRef": "example-mcp.prompt.review.arguments",
                "inert": True,
                "requiresRuntimeGet": True,
            }
        ],
        "schemas": [
            {
                "schemaId": "example-mcp.read.input",
                "ownerRef": "example-mcp.read",
                "role": "input",
                "schema": {"type": "object"},
            },
            {
                "schemaId": "example-mcp.prompt.review.arguments",
                "ownerRef": "example-mcp.prompt.review",
                "role": "arguments",
                "schema": {"type": "object"},
            },
        ],
        "effects": {
            "classifications": [{"capabilityId": "example-mcp.read", "effect": "read"}],
            "containsUnknown": False,
            "containsDestructive": False,
            "executionAuthorityGranted": False,
        },
        "provenance": {
            "importer": "pmcro-capability-import/mcp",
            "snapshotSha256": "0" * 64,
            "snapshotImmutable": True,
            "rawSeed": "import this exact seed",
            "rawSeedSha256": "1" * 64,
        },
        "skillProjection": {
            "target": {"skill": skill, "plugin": plugin},
            "requiredCore": ["SKILL.md", "agents/"],
            "suggestedLayers": ["assets", "references"],
            "reuseByAdapter": True,
            "registrationRequiresIndependentCheck": True,
            "scriptsRequired": False,
        },
    }


class CapabilityImportRouteTests(unittest.TestCase):
    def test_routes_normalized_import_into_skill_creator_request(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            imported = root / "capability-import.json"
            catalog.write_text(json.dumps({"kind": "marketplace-catalog", "entries": []}), encoding="utf-8")
            imported.write_text(json.dumps(capability_import()), encoding="utf-8")
            result = run(
                str(ROUTER),
                "--catalog", str(catalog),
                "--skill", "example-mcp",
                "--plugin", "integration",
                "--capability-import", str(imported),
                "--with-tests",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            request = json.loads(result.stdout)

        self.assertEqual(request["kind"], "skill.create.request")
        self.assertEqual(request["requiredInvoker"], "dotagents-skill-creator")
        self.assertEqual(request["capabilityImport"]["kind"], "capability.import")
        self.assertEqual(request["rules"]["generatedLayers"], ["assets", "references", "tests"])
        self.assertTrue(request["rules"]["importDoesNotGrantExecutionAuthority"])
        self.assertTrue(request["rules"]["preserveImportedSchemas"])
        self.assertEqual(request["rawSeed"], "import this exact seed")
        self.assertTrue(request["rawSeedImmutable"])

    def test_rejects_target_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            imported = root / "capability-import.json"
            catalog.write_text(json.dumps({"kind": "marketplace-catalog", "entries": []}), encoding="utf-8")
            imported.write_text(json.dumps(capability_import(skill="other-skill")), encoding="utf-8")
            result = run(
                str(ROUTER),
                "--catalog", str(catalog),
                "--skill", "example-mcp",
                "--plugin", "integration",
                "--capability-import", str(imported),
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("target does not match", result.stderr)

    def test_rejects_execution_authority_grant(self):
        value = capability_import()
        value["tools"][0]["executionAuthorityGranted"] = True
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            imported = root / "capability-import.json"
            catalog.write_text(json.dumps({"kind": "marketplace-catalog", "entries": []}), encoding="utf-8")
            imported.write_text(json.dumps(value), encoding="utf-8")
            result = run(
                str(ROUTER),
                "--catalog", str(catalog),
                "--skill", "example-mcp",
                "--plugin", "integration",
                "--capability-import", str(imported),
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("deny execution authority", result.stderr)


if __name__ == "__main__":
    unittest.main()
