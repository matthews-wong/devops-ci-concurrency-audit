#!/usr/bin/env python3
"""Fail when a pull request workflow does not cancel its own stale runs."""

import sys
from pathlib import Path

import yaml

WORKFLOW_GLOBS = ("*.yml", "*.yaml")
WORKFLOW_DIR = Path(".github/workflows")
PR_EVENTS = ("pull_request", "pull_request_target")
# PyYAML (YAML 1.1) loads the bare key `on` as the boolean True.
ON_KEYS = ("on", True)


def triggers(doc):
    """Event names a workflow runs on, whatever shape `on:` is written in."""
    for key in ON_KEYS:
        if key not in doc:
            continue
        value = doc[key]
        if isinstance(value, str):
            return [value]
        if isinstance(value, (list, dict)):
            return list(value)
    return []


def concurrency_blocks(doc):
    """(location, block) for the workflow-level and every job-level block."""
    blocks = []
    if "concurrency" in doc:
        blocks.append(("workflow", doc["concurrency"]))
    for name, job in doc["jobs"].items():
        if isinstance(job, dict) and "concurrency" in job:
            blocks.append((f"job '{name}'", job["concurrency"]))
    return blocks


def audit_workflow(path):
    """Return one message per concurrency problem found in `path`."""
    try:
        doc = yaml.safe_load(path.read_text())
    except OSError as exc:
        return [f"{path}: cannot read: {exc.strerror}"]
    except yaml.YAMLError as exc:
        return [f"{path}: not valid YAML: {exc}"]
    if not isinstance(doc, dict) or not isinstance(doc.get("jobs"), dict):
        return [f"{path}: no jobs mapping found"]
    if not any(event in PR_EVENTS for event in triggers(doc)):
        return []

    blocks = concurrency_blocks(doc)
    if not blocks:
        return [f"{path}: runs on pull requests but sets no concurrency"]
    return []


def collect(paths):
    if paths:
        return [Path(p) for p in paths]
    return sorted(f for pattern in WORKFLOW_GLOBS for f in WORKFLOW_DIR.glob(pattern))


def main(argv=None):
    files = collect(sys.argv[1:] if argv is None else argv)
    if not files:
        print(f"no workflow files found under {WORKFLOW_DIR}", file=sys.stderr)
        return 1
    findings = [m for f in files for m in audit_workflow(f)]
    for message in findings:
        print(message)
    print(f"{len(files)} workflow(s) checked, {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
