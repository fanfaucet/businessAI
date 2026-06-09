from __future__ import annotations
import json
from pathlib import Path
from .report import build_markdown_report


def export_result(result: dict, output_dir: str = "outputs") -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "result.json"
    md_path = out / "report.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown_report(result), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
