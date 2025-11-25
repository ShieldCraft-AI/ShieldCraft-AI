from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Sequence, cast

try:
    from cyclonedx.model.bom import Bom  # type: ignore[import]
    from cyclonedx.model.component import Component, ComponentType  # type: ignore[import]
    from cyclonedx.model.tool import Tool  # type: ignore[import]
    from cyclonedx.output import OutputFormat, make_output  # type: ignore[import]
except ImportError:  # pragma: no cover - optional dependency
    Bom = None  # type: ignore[assignment]
    Component = None  # type: ignore[assignment]
    ComponentType = None  # type: ignore[assignment]
    Tool = None  # type: ignore[assignment]
    OutputFormat = None  # type: ignore[assignment]
    make_output = None  # type: ignore[assignment]

CYC_AVAILABLE = Bom is not None

try:  # Python 3.11+ standard library
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for older interpreters
    import tomli as tomllib  # type: ignore[import-not-found]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMPONENTS: Sequence[Dict[str, str]] = (
    {"name": "shieldcraft-core", "version": "1.0.0"},
    {"name": "guard-model", "version": "0.9.1"},
)


def _load_project_version(pyproject_path: Path) -> str:
    if not pyproject_path.is_file():
        return "0.0.0"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return str(data.get("tool", {}).get("poetry", {}).get("version", "0.0.0"))


def _load_dependency_components(pyproject_path: Path) -> List[Dict[str, str]]:
    if not pyproject_path.is_file():
        return list(DEFAULT_COMPONENTS)
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    components: List[Dict[str, str]] = []
    for name, version in dependencies.items():
        if name.lower() == "python":
            continue
        components.append({"name": name, "version": str(version)})
    if not components:
        return list(DEFAULT_COMPONENTS)
    components.sort(key=lambda item: item["name"].lower())
    return components


def _component_digest(component: Dict[str, str]) -> str:
    h = hashlib.sha256()
    h.update(component["name"].encode("utf-8"))
    h.update(component["version"].encode("utf-8"))
    return h.hexdigest()


def build_sbom_document() -> Dict[str, object]:
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    project_version = _load_project_version(pyproject_path)
    components = _load_dependency_components(pyproject_path)
    normalized_components = [
        {
            "name": comp["name"],
            "version": comp["version"],
            "type": "library",
            "purl": f"pkg:pypi/{comp['name']}@{comp['version']}",
            "sha256": _component_digest(comp),
        }
        for comp in components
    ]
    normalized_components.sort(key=lambda item: item["name"].lower())
    document = {
        "bom_format": "CycloneDX",
        "spec_version": "1.5",
        "serial_number": "urn:uuid:00000000-0000-0000-0000-000000000000",
        "version": 1,
        "metadata": {
            "component": {
                "name": "shieldcraft-ai",
                "type": "application",
                "version": project_version,
            },
            "tools": [
                {
                    "vendor": "ShieldCraft",
                    "name": "sbom-scaffold",
                    "version": "1.0.0",
                }
            ],
            "manufacture": "ShieldCraft Labs",
            "generated_at": "2025-01-01T00:00:00Z",
        },
        "components": normalized_components,
    }
    return document


def _build_with_cyclonedx(document: Dict[str, object]) -> Dict[str, object]:
    if not CYC_AVAILABLE:  # pragma: no cover - guarded by availability
        return document
    assert Bom is not None and Component is not None and ComponentType is not None
    assert Tool is not None and OutputFormat is not None and make_output is not None

    bom = Bom()
    metadata = cast(Dict[str, Any], document.get("metadata", {}))
    component_meta = cast(Dict[str, Any], metadata.get("component", {}))
    bom.metadata.component = Component(
        name=component_meta.get("name", "shieldcraft-ai"),
        version=component_meta.get("version", "0.0.0"),
        component_type=ComponentType.APPLICATION,
    )
    bom.metadata.component.purl = "pkg:application/shieldcraft-ai@{version}".format(
        version=component_meta.get("version", "0.0.0")
    )
    if hasattr(bom.metadata, "timestamp"):
        bom.metadata.timestamp = "2025-01-01T00:00:00Z"
    tool = Tool(vendor="ShieldCraft", name="sbom-scaffold", version="1.0.0")
    bom.metadata.tools.add(tool)

    for component in cast(List[Dict[str, Any]], document.get("components", [])):
        bom_component = Component(
            name=component["name"],
            version=component["version"],
            component_type=ComponentType.LIBRARY,
        )
        bom_component.purl = component["purl"]
        bom_component.properties.update({"sha256": component["sha256"]})
        bom.components.add(bom_component)

    outputter = make_output(bom, output_format=OutputFormat.JSON)
    rendered = json.loads(outputter.output_as_string())
    rendered["metadata"] = metadata
    rendered["components"] = document.get("components", [])
    rendered["serialNumber"] = document.get("serial_number")
    rendered["specVersion"] = document.get("spec_version")
    rendered["bomFormat"] = document.get("bom_format")
    rendered["version"] = document.get("version")
    return rendered


def generate_sbom(output_path: Path | str | None = None) -> Dict[str, object]:
    document = _build_with_cyclonedx(build_sbom_document())
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(document, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    return document


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a deterministic CycloneDX SBOM stub."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the generated SBOM JSON.",
    )
    args = parser.parse_args()
    document = generate_sbom(output_path=args.output)
    print(json.dumps(document, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
