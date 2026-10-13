import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
IMPORTER = ROOT / "skills/pmcro-capability-import/scripts/import_mcp.py"
SCHEMA = ROOT / ".pmcro/protocol/capability-import.schema.json"


def run(*args):
    return subprocess.run([sys.executable, *args], text=True, capture_output=True)


class McpCapabilityImportTests(unittest.TestCase):
    def test_normalizes_mcp_primitives_without_granting_execution_authority(self):
        snapshot = {
            "sourceRef": "repo://example@mcp-test-sha",
            "protocolVersion": "2025-06-18",
            "server": {
                "name": "Example MCP",
                "version": "1.2.3",
                "description": "Example discovery snapshot",
            },
            "transport": {
                "type": "streamable-http",
                "endpointRef": "config://example-mcp/url",
                "authRef": "secret-ref://example-mcp",
                "headers": {"Authorization": "DO-NOT-COPY"},
                "token": "DO-NOT-COPY",
                "env": {"API_KEY": "DO-NOT-COPY"},
            },
            "tools": [
                {
                    "name": "read_item",
                    "description": "Read one item",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"id": {"type": "string"}},
                        "required": ["id"],
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {"value": {"type": "string"}},
                    },
                    "annotations": {"readOnlyHint": True, "idempotentHint": True},
                },
                {
                    "name": "remove_item",
                    "description": "Remove one item",
                    "inputSchema": {"type": "object"},
                    "annotations": {"destructiveHint": True},
                },
            ],
            "resources": [
                {
                    "name": "Architecture",
                    "uri": "repo://architecture",
                    "description": "Architecture reference",
                    "mimeType": "text/markdown",
                }
            ],
            "resourceTemplates": [
                {
                    "name": "Document",
                    "uriTemplate": "repo://docs/{name}",
                    "mimeType": "text/markdown",
                }
            ],
            "prompts": [
                {
                    "name": "review",
                    "description": "Review an artifact",
                    "arguments": [
                        {"name": "artifact", "description": "Artifact ref", "required": True}
                    ],
                }
            ],
        }
        raw_seed = "need this MCP functionality, unchanged"
        with tempfile.TemporaryDirectory() as directory:
            snapshot_path = Path(directory) / "snapshot.json"
            raw_bytes = (json.dumps(snapshot, indent=2) + "\n").encode("utf-8")
            snapshot_path.write_bytes(raw_bytes)
            result = run(
                str(IMPORTER),
                "--snapshot", str(snapshot_path),
                "--skill", "example-mcp",
                "--plugin", "integration",
                "--raw-seed", raw_seed,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            imported = json.loads(result.stdout)

        self.assertTrue(SCHEMA.is_file())
        self.assertEqual(imported["kind"], "capability.import")
        self.assertEqual(imported["status"], "generated-unchecked")
        self.assertEqual(imported["source"]["type"], "mcp")
        self.assertEqual(imported["source"]["sourceRef"], "repo://example@mcp-test-sha")
        self.assertEqual(imported["transport"]["protocol"], "mcp")
        self.assertEqual(imported["transport"]["binding"], "streamable-http")
        self.assertEqual(imported["transport"]["endpointRef"], "config://example-mcp/url")
        self.assertEqual(imported["transport"]["authRef"], "secret-ref://example-mcp")
        self.assertFalse(imported["transport"]["secretMaterialIncluded"])
        self.assertNotIn("headers", imported["transport"])
        self.assertNotIn("token", imported["transport"])
        self.assertNotIn("env", imported["transport"])

        by_name = {item["nativeName"]: item for item in imported["tools"]}
        self.assertEqual(by_name["read_item"]["effect"], "read")
        self.assertEqual(by_name["remove_item"]["effect"], "destructive")
        self.assertTrue(all(item["executionAuthorityGranted"] is False for item in imported["tools"]))
        self.assertFalse(imported["effects"]["executionAuthorityGranted"])
        self.assertTrue(imported["effects"]["containsDestructive"])

        self.assertEqual({item["kind"] for item in imported["resources"]}, {"resource", "resource-template"})
        self.assertTrue(all(item["executable"] is False for item in imported["resources"]))
        self.assertEqual(imported["prompts"][0]["nativeName"], "review")
        self.assertTrue(imported["prompts"][0]["inert"])
        self.assertTrue(imported["prompts"][0]["requiresRuntimeGet"])
        self.assertIn("input", {item["role"] for item in imported["schemas"]})
        self.assertIn("output", {item["role"] for item in imported["schemas"]})
        self.assertIn("arguments", {item["role"] for item in imported["schemas"]})

        self.assertEqual(imported["provenance"]["snapshotSha256"], hashlib.sha256(raw_bytes).hexdigest())
        self.assertEqual(imported["provenance"]["rawSeed"], raw_seed)
        self.assertEqual(imported["provenance"]["rawSeedSha256"], hashlib.sha256(raw_seed.encode("utf-8")).hexdigest())
        self.assertEqual(imported["skillProjection"]["target"], {"skill": "example-mcp", "plugin": "integration"})
        self.assertEqual(imported["skillProjection"]["requiredCore"], ["SKILL.md", "agents/"])
        self.assertEqual(imported["skillProjection"]["suggestedLayers"], ["assets", "references"])
        self.assertFalse(imported["skillProjection"]["scriptsRequired"])
        self.assertTrue(imported["skillProjection"]["registrationRequiresIndependentCheck"])

    def test_conflicting_effect_annotations_remain_untrusted_evidence(self):
        snapshot = {
            "server": {"name": "conflict"},
            "tools": [
                {
                    "name": "ambiguous",
                    "inputSchema": {"type": "object"},
                    "annotations": {"readOnlyHint": True, "destructiveHint": True},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            snapshot_path = Path(directory) / "snapshot.json"
            snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
            result = run(
                str(IMPORTER),
                "--snapshot", str(snapshot_path),
                "--skill", "conflict-mcp",
                "--plugin", "integration",
                "--source-ref", "fixture://conflict",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            imported = json.loads(result.stdout)
        self.assertEqual(imported["tools"][0]["effect"], "conflicting-annotations")
        self.assertTrue(imported["effects"]["containsUnknown"])
        self.assertTrue(imported["effects"]["containsDestructive"])
        self.assertFalse(imported["effects"]["executionAuthorityGranted"])

    def test_missing_tool_name_halts(self):
        snapshot = {"server": {"name": "bad"}, "tools": [{"inputSchema": {"type": "object"}}]}
        with tempfile.TemporaryDirectory() as directory:
            snapshot_path = Path(directory) / "snapshot.json"
            snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
            result = run(
                str(IMPORTER),
                "--snapshot", str(snapshot_path),
                "--skill", "bad-mcp",
                "--plugin", "integration",
                "--source-ref", "fixture://bad",
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing a non-empty name", result.stderr)


if __name__ == "__main__":
    unittest.main()
