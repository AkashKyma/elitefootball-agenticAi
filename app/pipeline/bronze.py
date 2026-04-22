from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.pipeline.io import list_files, write_json


def build_bronze_manifest() -> dict[str, object]:
    sources = {
        "transfermarkt": {
            "raw": Path(settings.raw_data_dir),
            "parsed": Path(settings.parsed_data_dir),
        },
        "fbref": {
            "raw": Path(settings.fbref_raw_data_dir),
            "parsed": Path(settings.fbref_parsed_data_dir),
        },
    }

    artifacts: list[dict[str, object]] = []
    for source, directories in sources.items():
        for artifact_type, directory in directories.items():
            pattern = "*.html" if artifact_type == "raw" else "*.json"
            for path in list_files(directory, pattern):
                artifacts.append(
                    {
                        "source": source,
                        "artifact_type": "raw_html" if artifact_type == "raw" else "parsed_json",
                        "artifact_path": str(path),
                        "slug": path.stem,
                        "captured_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
                    }
                )

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    manifest_path = write_json(Path(settings.bronze_data_dir) / "manifest.json", manifest)
    return {"manifest_path": manifest_path, "manifest": manifest}
