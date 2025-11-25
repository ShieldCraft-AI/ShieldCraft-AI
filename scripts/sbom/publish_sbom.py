from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from generate_sbom import generate_sbom

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "sbom"
DEFAULT_ARTIFACT_NAME = "shieldcraft-sbom.json"


def publish_sbom(
    destination_dir: Path | str | None = None,
    artifact_name: str = DEFAULT_ARTIFACT_NAME,
) -> Path:
    target_dir = Path(destination_dir) if destination_dir else DEFAULT_ARTIFACT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = target_dir / artifact_name
    generate_sbom(output_path=artifact_path)
    return artifact_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Publish the deterministic SBOM into artifacts/sbom/."
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=None,
        help="Optional destination directory. Defaults to artifacts/sbom/.",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default=DEFAULT_ARTIFACT_NAME,
        help="Artifact file name. Defaults to shieldcraft-sbom.json.",
    )
    args = parser.parse_args()
    artifact_path = publish_sbom(args.destination, args.filename)
    print(str(artifact_path))


if __name__ == "__main__":
    main()
