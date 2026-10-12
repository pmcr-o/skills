#!/usr/bin/env python3
"""Normalize an exported MCP discovery snapshot into CAPABILITY_IMPORT IR.

This importer is intentionally offline. It does not start an MCP server, open a
network connection, retrieve secrets, or invoke imported tools.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SAFE_TRANSPORT_KEYS = ("endpointRef", "commandRef", "argsRef", "authRef")
SAFE_ANNOTATION_KEYS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")


class ImportError(Exception):
    pass


def fail(message: str) -> None:
    raise ImportError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def valid_name(value: str, label: str) -> str:
    if not NAME_RE.fullmatch(value):
        fail(f"{label} must match lowercase letters, digits, and single hyphens: {value}")
    return value


def slug(value: object, fallback: str) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or fallback


def nullable_text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def normalize_annotations(value: object) -> dict:
    source = value if isinstance(value, dict) else {}
    return {key: bool(source[key]) for key in SAFE_ANNOTATION_KEYS if key in source}


def classify_effect(annotations: dict) -> str:
    read_only = annotations.get("readOnlyHint") is True
    destructive = annotations.get("destructiveHint") is True
    if read_only and destructive:
        return "conflicting-annotations"
    if read_only:
        return "read"
    if destructive:
        return "destructive"
    return "side-effect-unknown"


def add_schema(registry: list[dict], owner_ref: str, role: str, schema: object) -> str:
    normalized = schema if isinstance(schema, dict) else {"type": "object"}
    schema_id = f"{owner_ref}.{role}"
    registry.append({
        "schemaId": schema_id,
        "ownerRef": owner_ref,
        "role": role,
        "schema": normalized,
    })
    return schema_id


def prompt_arguments_schema(arguments: object) -> dict:
    properties: dict[str, dict] = {}
    required: list[str] = []
    for item in arguments if isinstance(arguments, list) else []:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name:
            continue
        entry: dict[str, object] = {"type": "string"}
        if isinstance(item.get("description"), str) and item["description"]:
            entry["description"] = item["description"]
        properties[name] = entry
        if item.get("required") is True:
            required.append(name)
    schema: dict[str, object] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = sorted(required)
    return schema


def normalize_snapshot(snapshot: dict, raw_bytes: bytes, *, skill: str, plugin: str, source_ref: str, raw_seed: str | None) -> dict:
    server = snapshot.get("server") if isinstance(snapshot.get("server"), dict) else {}
    native_id = server.get("name") or snapshot.get("serverName") or skill
    native_id = str(native_id)

    native_transport = snapshot.get("transport") if isinstance(snapshot.get("transport"), dict) else {}
    binding = native_transport.get("type") or native_transport.get("binding") or "unknown"
    transport: dict[str, object] = {
        "protocol": "mcp",
        "binding": str(binding),
        "protocolVersion": nullable_text(snapshot.get("protocolVersion") or native_transport.get("protocolVersion")),
        "endpointRef": None,
        "commandRef": None,
        "argsRef": None,
        "authRef": None,
        "secretMaterialIncluded": False,
    }
    for key in SAFE_TRANSPORT_KEYS:
        if isinstance(native_transport.get(key), str) and native_transport[key]:
            transport[key] = native_transport[key]

    schemas: list[dict] = []
    tools: list[dict] = []
    effects: list[dict] = []
    for index, item in enumerate(snapshot.get("tools", []) if isinstance(snapshot.get("tools"), list) else []):
        if not isinstance(item, dict):
            continue
        native_name = item.get("name")
        if not isinstance(native_name, str) or not native_name:
            fail(f"tools[{index}] is missing a non-empty name")
        capability_id = f"{skill}.{slug(native_name, f'tool-{index + 1}')}"
        input_ref = add_schema(schemas, capability_id, "input", item.get("inputSchema"))
        output_ref = None
        if isinstance(item.get("outputSchema"), dict):
            output_ref = add_schema(schemas, capability_id, "output", item["outputSchema"])
        annotations = normalize_annotations(item.get("annotations"))
        effect = classify_effect(annotations)
        tools.append({
            "capabilityId": capability_id,
            "nativeName": native_name,
            "description": nullable_text(item.get("description")),
            "inputSchemaRef": input_ref,
            "outputSchemaRef": output_ref,
            "effect": effect,
            "executionAuthorityGranted": False,
            "nativeAnnotations": annotations,
        })
        effects.append({"capabilityId": capability_id, "effect": effect})

    resources: list[dict] = []
    raw_resources = snapshot.get("resources", []) if isinstance(snapshot.get("resources"), list) else []
    raw_templates = snapshot.get("resourceTemplates", []) if isinstance(snapshot.get("resourceTemplates"), list) else []
    for kind, entries in (("resource", raw_resources), ("resource-template", raw_templates)):
        for index, item in enumerate(entries):
            if not isinstance(item, dict):
                continue
            locator = item.get("uri") if kind == "resource" else item.get("uriTemplate")
            native_name = item.get("name") or locator or f"{kind}-{index + 1}"
            resource_id = f"{skill}.resource.{slug(native_name, f'{kind}-{index + 1}')}"
            resources.append({
                "resourceId": resource_id,
                "nativeName": str(native_name),
                "kind": kind,
                "uri": nullable_text(item.get("uri")),
                "uriTemplate": nullable_text(item.get("uriTemplate")),
                "description": nullable_text(item.get("description")),
                "mimeType": nullable_text(item.get("mimeType")),
                "executable": False,
            })

    prompts: list[dict] = []
    for index, item in enumerate(snapshot.get("prompts", []) if isinstance(snapshot.get("prompts"), list) else []):
        if not isinstance(item, dict):
            continue
        native_name = item.get("name")
        if not isinstance(native_name, str) or not native_name:
            fail(f"prompts[{index}] is missing a non-empty name")
        prompt_id = f"{skill}.prompt.{slug(native_name, f'prompt-{index + 1}')}"
        args_ref = add_schema(schemas, prompt_id, "arguments", prompt_arguments_schema(item.get("arguments")))
        prompts.append({
            "promptId": prompt_id,
            "nativeName": native_name,
            "description": nullable_text(item.get("description")),
            "argumentsSchemaRef": args_ref,
            "inert": True,
            "requiresRuntimeGet": True,
        })

    layers = {"assets"}
    if resources:
        layers.add("references")

    provenance: dict[str, object] = {
        "importer": "pmcro-capability-import/mcp",
        "snapshotSha256": sha256_bytes(raw_bytes),
        "snapshotImmutable": True,
    }
    if raw_seed is not None:
        provenance["rawSeed"] = raw_seed
        provenance["rawSeedSha256"] = sha256_text(raw_seed)

    return {
        "schemaVersion": 1,
        "kind": "capability.import",
        "status": "generated-unchecked",
        "importId": f"mcp:{skill}:{sha256_bytes(raw_bytes)[:12]}",
        "source": {
            "type": "mcp",
            "sourceRef": source_ref,
            "nativeId": native_id,
            "nativeVersion": nullable_text(server.get("version")),
            "description": nullable_text(server.get("description")),
        },
        "transport": transport,
        "tools": tools,
        "resources": resources,
        "prompts": prompts,
        "schemas": schemas,
        "effects": {
            "classifications": effects,
            "containsUnknown": any(item["effect"] in {"side-effect-unknown", "conflicting-annotations"} for item in effects),
            "containsDestructive": any(item["effect"] in {"destructive", "conflicting-annotations"} for item in effects),
            "executionAuthorityGranted": False,
        },
        "provenance": provenance,
        "skillProjection": {
            "target": {"skill": skill, "plugin": plugin},
            "requiredCore": ["SKILL.md", "agents/"],
            "suggestedLayers": sorted(layers),
            "reuseByAdapter": True,
            "registrationRequiresIndependentCheck": True,
            "scriptsRequired": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, help="exported MCP discovery snapshot JSON")
    parser.add_argument("--skill", required=True, help="target portable skill name")
    parser.add_argument("--plugin", required=True, help="target plugin projection name")
    parser.add_argument("--source-ref", help="pinned repository/ref or immutable discovery source reference")
    parser.add_argument("--raw-seed", help="optional immutable raw seed to preserve in provenance")
    parser.add_argument("--output", help="write normalized IR to this path; stdout when omitted")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        skill = valid_name(args.skill, "skill")
        plugin = valid_name(args.plugin, "plugin")
        snapshot_path = Path(args.snapshot).expanduser()
        raw_bytes = snapshot_path.read_bytes()
        try:
            snapshot = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            fail(f"invalid UTF-8 JSON snapshot: {exc}")
        if not isinstance(snapshot, dict):
            fail("snapshot root must be a JSON object")
        source_ref = args.source_ref or snapshot.get("sourceRef") or snapshot_path.name
        if not isinstance(source_ref, str) or not source_ref:
            fail("source reference must be a non-empty string")
        normalized = normalize_snapshot(
            snapshot,
            raw_bytes,
            skill=skill,
            plugin=plugin,
            source_ref=source_ref,
            raw_seed=args.raw_seed,
        )
        rendered = json.dumps(normalized, indent=2, sort_keys=True) + "\n"
        if args.output:
            output = Path(args.output).expanduser()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
            print(f"PASS: generated-unchecked CAPABILITY_IMPORT written to {output}")
        else:
            print(rendered, end="")
        return 0
    except (ImportError, OSError) as exc:
        print(f"HALT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
