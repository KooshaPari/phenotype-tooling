#!/usr/bin/env python3
"""WP-22 dependency license checker.

Reads a CycloneDX SBOM, extracts the licenses of every component,
and reports any non-allowlisted license as a violation. Exits non-zero
if any violations are found. License list source-of-truth is
`LICENSE_ALLOWLIST.toml` in the repo root.

Used by `.github/workflows/license-check.yml` on every PR to block
introductions of copyleft or unknown-licensed dependencies.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any


def load_allowlist(path: Path) -> dict[str, Any]:
    """Load allowlist config from a TOML file."""
    with path.open("rb") as fh:
        return tomllib.load(fh)


def extract_component_licenses(sbom: dict[str, Any]) -> list[dict[str, str]]:
    """Walk CycloneDX components and return [{name, version, license}]."""
    out: list[dict[str, str]] = []
    for comp in sbom.get("components", []):
        name = comp.get("name", "?")
        version = comp.get("version", "?")
        licenses = comp.get("licenses", []) or []
        if not licenses:
            out.append({"name": name, "version": version, "license": "UNKNOWN"})
            continue
        for lic in licenses:
            lic_obj = lic.get("license", {}) or {}
            lic_id = lic_obj.get("id") or lic_obj.get("name") or "UNKNOWN"
            out.append({"name": name, "version": version, "license": lic_id})
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sbom", required=True, help="Path to CycloneDX JSON SBOM")
    parser.add_argument(
        "--allowlist",
        default="LICENSE_ALLOWLIST.toml",
        help="Path to allowlist config (default: repo root)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    sbom_path = Path(args.sbom)
    allowlist_path = Path(args.allowlist)

    if not sbom_path.exists():
        print(f"ERROR: SBOM not found at {sbom_path}", file=sys.stderr)
        return 2
    if not allowlist_path.exists():
        print(f"ERROR: allowlist not found at {allowlist_path}", file=sys.stderr)
        return 2

    with sbom_path.open("r", encoding="utf-8") as fh:
        sbom = json.load(fh)

    allowlist = load_allowlist(allowlist_path)
    allowed: set[str] = set(allowlist.get("licenses", {}).get("allow", []))
    denied: set[str] = set(allowlist.get("licenses", {}).get("deny", []))
    review_required: set[str] = set(
        allowlist.get("licenses", {}).get("review_required", [])
    )

    components = extract_component_licenses(sbom)

    violations: list[dict[str, str]] = []
    review: list[dict[str, str]] = []
    for comp in components:
        lic = comp["license"].upper().strip()
        if lic in denied:
            violations.append({**comp, "reason": "denied license"})
        elif lic not in allowed:
            if lic in review_required:
                review.append({**comp, "reason": "review-required license"})
            else:
                violations.append({**comp, "reason": "not in allowlist"})

    if args.format == "json":
        print(
            json.dumps(
                {
                    "sbom": str(sbom_path),
                    "components_scanned": len(components),
                    "violations": violations,
                    "review": review,
                },
                indent=2,
            )
        )
    else:
        print(f"Scanned {len(components)} components")
        if violations:
            print(f"\n{len(violations)} violations:")
            for v in violations:
                print(f"  {v['name']}@{v['version']}: {v['license']} ({v['reason']})")
        if review:
            print(f"\n{len(review)} need review:")
            for r in review:
                print(f"  {r['name']}@{r['version']}: {r['license']}")

    if violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())