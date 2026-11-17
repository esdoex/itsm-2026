# ai-generated: implementation for Lab 5 baked off by the course rules
"""bakeoff.py - scanner SARIF + a labels file -> a per-tool confusion matrix (CI-SPEC.md P-23).

This skeleton has the command line and the output shape and nothing of the rules: sections 3.1 to 3.3 of
CI-SPEC.md are yours to implement. Standard library only - it runs as `python3 -S -E bakeoff.py`.

    python3 bakeoff.py --labels labels.json a.sarif b.sarif > bakeoff.json
"""

from __future__ import annotations

import argparse
import json
import sys


def confusion_matrix(labels: dict, sarif_documents: list[dict]) -> dict:
    """The matrix of P-21 and P-22 for the labels and parsed SARIF documents."""
    import re
    from urllib.parse import unquote

    tool_names = {
        "trivy": "trivy",
        "grype": "grype",
        "osv-scanner": "osv-scanner",
        "gitleaks": "gitleaks",
    }
    semgrep_names = {"semgrep", "semgrep oss", "semgrep ce",
                     "semgrep community edition", "semgrep pro"}
    classes = {
        "secret": {259, 260, 321, 798},
        "injection": {74, 77, 78, 79, 80, 88, 89, 90, 91, 94, 95, 96, 611, 776, 917, 943, 1336},
        "deserialization": {502},
        "weak-crypto": {261, 326, 327, 328, 330, 331, 338, 759, 760, 916},
        "insecure-transport": {295, 297, 319, 322, 757},
        "path-traversal": {22, 23, 35, 36, 73},
        "ssrf": {918},
        "vulnerable-dependency": {937, 1035, 1104, 1395},
        "misconfiguration": {16, 215, 250, 489, 668, 732, 1188},
        "access-control": {284, 285, 639, 862, 863},
    }
    set_root = labels["set"]
    defects = labels["defects"]
    tools_results: dict[str, list[dict]] = {}

    def tool_id(name):
        if not isinstance(name, str):
            return "unknown"
        name = name.strip()
        if not name:
            return "unknown"
        lowered = name.lower()
        if lowered in tool_names:
            return tool_names[lowered]
        if lowered in semgrep_names:
            return "semgrep"
        normalized = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
        return normalized or "unknown"

    def is_empty(value):
        return value is None or value == [] or value == {} or value is False or value == 0 or value == ""

    for document in sarif_documents:
        runs = document.get("runs")
        if not isinstance(runs, list):
            continue
        for run in runs:
            if not isinstance(run, dict):
                continue
            tool = run.get("tool")
            driver = tool.get("driver") if isinstance(tool, dict) else None
            name = driver.get("name") if isinstance(driver, dict) else None
            tid = tool_id(name)
            bucket = tools_results.setdefault(tid, [])
            rules = driver.get("rules") if isinstance(driver, dict) else None
            if not isinstance(rules, list):
                rules = []
            results = run.get("results")
            if not isinstance(results, list):
                continue
            for result in results:
                if not isinstance(result, dict):
                    continue
                kind = result.get("kind")
                if kind is not None and kind != "fail":
                    continue
                suppressions = result.get("suppressions")
                if not is_empty(suppressions):
                    continue
                locations = result.get("locations")
                if not isinstance(locations, list) or not locations or not isinstance(locations[0], dict):
                    continue
                physical = locations[0].get("physicalLocation")
                if not isinstance(physical, dict):
                    continue
                artifact = physical.get("artifactLocation")
                if not isinstance(artifact, dict) or not isinstance(artifact.get("uri"), str) or not artifact["uri"]:
                    continue
                uri = unquote(artifact["uri"])
                if uri[:7].lower() == "file://":
                    uri = uri[7:]
                if uri.startswith("./"):
                    uri = uri[2:]
                components = uri.split("/")
                if set_root not in components:
                    continue
                index = len(components) - 1 - components[::-1].index(set_root)
                file_path = "/".join(components[index:])
                region = physical.get("region")
                region = region if isinstance(region, dict) else {}
                start = region.get("startLine")
                if not isinstance(start, int) or isinstance(start, bool) or start < 1:
                    start = None
                    end = None
                else:
                    candidate_end = region.get("endLine")
                    if not isinstance(candidate_end, int) or isinstance(candidate_end, bool) or candidate_end < start:
                        end = start
                    else:
                        end = candidate_end
                rule_id = result.get("ruleId")
                rule = None
                if isinstance(rule_id, str):
                    for candidate in rules:
                        if isinstance(candidate, dict) and candidate.get("id") == rule_id:
                            rule = candidate
                            break
                result_tags = []
                own_props = result.get("properties")
                if isinstance(own_props, dict):
                    tags = own_props.get("tags")
                    if isinstance(tags, list):
                        result_tags.extend(t for t in tags if isinstance(t, str))
                rule_tags = []
                if isinstance(rule, dict):
                    props = rule.get("properties")
                    if isinstance(props, dict):
                        tags = props.get("tags")
                        if isinstance(tags, list):
                            rule_tags.extend(t for t in tags if isinstance(t, str))
                result_classes = set()
                props = result.get("properties")
                if isinstance(props, dict) and isinstance(props.get("class"), str):
                    own_class = props["class"]
                    if own_class in classes:
                        result_classes.add(own_class)
                if not result_classes:
                    if tid == "gitleaks":
                        result_classes.add("secret")
                    elif tid in {"grype", "osv-scanner"}:
                        result_classes.add("vulnerable-dependency")
                    elif tid == "trivy":
                        tags_lower = {tag.lower() for tag in rule_tags}
                        if "vulnerability" in tags_lower:
                            result_classes.add("vulnerable-dependency")
                        if "secret" in tags_lower:
                            result_classes.add("secret")
                        if "misconfiguration" in tags_lower:
                            result_classes.add("misconfiguration")
                if not result_classes:
                    cwe_tags = result_tags + rule_tags
                    for tag in cwe_tags:
                        for match in re.finditer(r"(?<![A-Za-z0-9])CWE-(\d+)", tag, re.IGNORECASE):
                            number = int(match.group(1))
                            for class_name, numbers in classes.items():
                                if number in numbers:
                                    result_classes.add(class_name)
                if not result_classes:
                    result_classes.add("other")
                message = result.get("message")
                message_text = message.get("text") if isinstance(message, dict) and isinstance(message.get("text"), str) else None
                bucket.append({
                    "file": file_path,
                    "start": start,
                    "end": end,
                    "ruleId": rule_id if isinstance(rule_id, str) else None,
                    "classes": result_classes,
                    "message": message_text,
                })

    tools = {}
    for tid, results in tools_results.items():
        matched_defects = set()
        for defect in defects:
            for result in results:
                if result["file"] != defect["file"] or not (set(result["classes"]) & {defect["class"]}):
                    continue
                if defect["class"] == "vulnerable-dependency":
                    if not isinstance(result["message"], str):
                        continue
                    package = defect["package"]
                    normalized_package = re.sub(r"[-_.]+", "-", package.lower())
                    tokens = re.findall(r"[A-Za-z0-9._-]+", result["message"])
                    found = False
                    for token in tokens:
                        token = token.strip(".-_")
                        if re.sub(r"[-_.]+", "-", token.lower()) == normalized_package:
                            found = True
                            break
                    if not found:
                        continue
                else:
                    if result["start"] is None:
                        continue
                    if not (result["start"] <= defect["end_line"] and defect["start_line"] <= result["end"]):
                        continue
                matched_defects.add(defect["id"])
        fp_keys = set()
        for result in results:
            matched = False
            for defect in defects:
                if result["file"] != defect["file"] or not (set(result["classes"]) & {defect["class"]}):
                    continue
                if defect["class"] == "vulnerable-dependency":
                    if not isinstance(result["message"], str):
                        continue
                    normalized_package = re.sub(r"[-_.]+", "-", defect["package"].lower())
                    tokens = re.findall(r"[A-Za-z0-9._-]+", result["message"])
                    if not any(re.sub(r"[-_.]+", "-", token.strip(".-_").lower()) == normalized_package for token in tokens):
                        continue
                else:
                    if result["start"] is None or not (result["start"] <= defect["end_line"] and defect["start_line"] <= result["end"]):
                        continue
                matched = True
                break
            if not matched:
                fp_keys.add((result["ruleId"], result["file"], result["start"], result["end"]))
        tp = len(matched_defects)
        fp = len(fp_keys)
        fn = len(defects) - tp
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else None
        tools[tid] = {"tp": tp, "fp": fp, "fn": fn,
                      "precision": precision, "recall": recall, "f1": f1}
    return {"set": set_root, "defects": len(defects), "tools": tools}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="per-tool confusion matrix of SARIF against labels (CI-SPEC.md P-23)")
    parser.add_argument("--labels", required=True, help="the labels file (P-14)")
    parser.add_argument("sarif", nargs="+", help="SARIF 2.1.0 files")
    args = parser.parse_args(argv)
    with open(args.labels, encoding="utf-8") as fh:
        labels = json.load(fh)
    documents = []
    for path in args.sarif:
        with open(path, encoding="utf-8") as fh:
            documents.append(json.load(fh))
    json.dump(confusion_matrix(labels, documents), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
