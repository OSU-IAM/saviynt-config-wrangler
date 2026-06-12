#!/opt/python/current/bin/python -Wall
"""Convert a Saviynt User Update Rules Excel export to per-rule Markdown files.

Reads the three-sheet Excel export (Rule, Rule Condition, Rule Action) and
writes one .md file per rule into the output directory.

Copyright 2023 Oregon State University.  All Rights Reserved.

Requests for more information can be directed to iamteam@oregonstate.edu |
advantage@oregonstate.edu
"""

import argparse
import json
import logging
import os
import re
from collections import defaultdict
from pathlib import Path

import openpyxl

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s",
)

# Exact column names as exported by Saviynt
OPEN_PAREN_COL = "(,(("
CLOSE_PAREN_COL = "),))"


def is_dir(arg_text):
    """Argparse type validator ensuring valid directory."""
    if os.path.isdir(arg_text):
        return arg_text
    raise argparse.ArgumentTypeError(f"Not a directory: {arg_text}")


def get_args_parser() -> argparse.ArgumentParser:
    """Define script args."""
    parser = argparse.ArgumentParser(
        description="Convert Saviynt User Update Rules Excel export to per-rule Markdown files"
    )
    parser.add_argument(
        "excel_file", help="Path to the Saviynt rules Excel export (.xlsx)"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        type=is_dir,
        help="Directory to write per-rule Markdown files into (default: current directory)",
    )
    parser.add_argument(
        "--env",
        required=True,
        choices=["DEV", "PROD"],
        help="Saviynt environment (DEV or PROD); included in output filenames",
    )
    parser.add_argument(
        "--extra-data-file",
        required=True,
        help=(
            "Path to JSON file storing rule statuses and missing action Objects. "
            "Created on first run; update it and re-run to populate missing values."
        ),
    )
    parser.add_argument("--debug", help="Set log level DEBUG", action="store_true")
    return parser


def cell_str(value) -> str:
    """Return str(value), or empty string if value is None.

    Args:
        value: Cell value from openpyxl (None for empty cells).

    Returns:
        String representation, or empty string for None.
    """
    if value is None:
        return ""
    return str(value).strip()


def read_sheet(ws) -> list[dict]:
    """Read a worksheet into a list of dicts using the first row as headers.

    Args:
        ws: openpyxl Worksheet object.

    Returns:
        List of row dicts; empty cells are represented as empty strings.
        Rows where every cell is empty are skipped.
    """
    row_iter = ws.iter_rows(values_only=True)
    headers = [cell_str(col) for col in next(row_iter)]
    rows = []
    for row in row_iter:
        row_dict = {headers[i]: cell_str(row[i]) for i in range(len(headers))}
        if any(row_dict.values()):
            rows.append(row_dict)
    return rows


def group_by_rule(rows: list[dict]) -> dict[str, list[dict]]:
    """Group a list of row dicts by RULE_NAME, skipping rows with no name.

    Args:
        rows: List of row dicts from read_sheet().

    Returns:
        Dict mapping rule name to list of row dicts for that rule.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        rule_name = row.get("RULE_NAME", "")
        if rule_name:
            groups[rule_name].append(row)
    return groups


def coalesce_actions(actions: list[dict]) -> list[dict]:
    """Coalesce flat action rows into groups with OBJECT collected into a list.

    Groups rows by (ACTION, OBJECT_TYPE, ORGANIZATION, OPERATION, EXECUTEON).
    Within each group, non-empty OBJECT values are collected into OBJECTS and
    rows with an empty OBJECT are counted in MISSING_COUNT.

    Args:
        actions: Flat action row dicts for one rule from the Rule Action sheet.

    Returns:
        List of coalesced action dicts, each with OBJECTS (list of str) and
        MISSING_COUNT (int).
    """
    group_data: dict[tuple, dict] = {}
    key_order: list[tuple] = []

    for action in actions:
        key = (
            action.get("ACTION", ""),
            action.get("OBJECT_TYPE", ""),
            action.get("ORGANIZATION", ""),
            action.get("OPERATION", ""),
            action.get("EXECUTEON", ""),
        )
        if key not in group_data:
            group_data[key] = {"objects": [], "missing_count": 0}
            key_order.append(key)
        obj = action.get("OBJECT", "")
        if obj:
            group_data[key]["objects"].append(obj)
        else:
            group_data[key]["missing_count"] += 1

    result = []
    for key in key_order:
        action_name, object_type, organization, operation, executeon = key
        data = group_data[key]
        result.append(
            {
                "ACTION": action_name,
                "OBJECT_TYPE": object_type,
                "ORGANIZATION": organization,
                "OPERATION": operation,
                "EXECUTEON": executeon,
                "OBJECTS": data["objects"],
                "MISSING_COUNT": data["missing_count"],
            }
        )
    return result


def _action_key(entry: dict) -> tuple:
    """Return the matching key for a coalesced action or file action entry."""
    return (
        entry.get("ACTION", ""),
        entry.get("OBJECT_TYPE", ""),
        entry.get("ORGANIZATION", ""),
        entry.get("OPERATION", ""),
        entry.get("EXECUTEON", ""),
    )


def _make_file_action_entry(coalesced: dict) -> dict:
    """Build an extra-data file entry for a coalesced action with missing Objects.

    Args:
        coalesced: Coalesced action dict with MISSING_COUNT > 0.

    Returns:
        Dict suitable for storage in the extra-data file's actions section,
        with one empty-string placeholder per missing Object.
    """
    entry: dict = {
        "ACTION": coalesced["ACTION"],
        "OBJECT_TYPE": coalesced["OBJECT_TYPE"],
    }
    for field in ("ORGANIZATION", "OPERATION", "EXECUTEON"):
        if coalesced.get(field):
            entry[field] = coalesced[field]
    entry["OBJECT"] = [""] * coalesced["MISSING_COUNT"]
    return entry


def load_extra_data(
    path: str,
    rule_names: list[str],
    coalesced_by_rule: dict[str, list[dict]],
) -> dict:
    """Load rule statuses and missing action Objects from the extra-data JSON file.

    Creates the file if it does not exist. On subsequent runs, adds entries for
    new rules or newly missing actions and warns about stale entries.

    Args:
        path: Path to the JSON extra-data file.
        rule_names: Rule names from the current export.
        coalesced_by_rule: Coalesced action lists keyed by rule name.

    Returns:
        Dict with keys "statuses" (dict[str, str]) and "actions"
        (dict[str, list[dict]]).
    """
    extra_data_path = Path(path)
    file_existed = extra_data_path.exists()

    if file_existed:
        extra_data = json.loads(extra_data_path.read_text(encoding="utf-8"))
        statuses: dict[str, str] = extra_data.get("statuses", {})
        file_actions: dict[str, list[dict]] = extra_data.get("actions", {})
    else:
        statuses = {}
        file_actions = {}

    dirty = False
    export_set = set(rule_names)
    file_status_set = set(statuses.keys())

    # Handle new rules missing from the status file
    for name in sorted(export_set - file_status_set):
        statuses[name] = "Active"
        dirty = True
        if file_existed:
            logger.warning(
                "Rule %r is in the export but not in the extra-data file"
                " — defaulting to Active. Update %s if incorrect.",
                name,
                path,
            )

    # Warn about stale status entries
    for name in sorted(file_status_set - export_set):
        logger.warning(
            "Rule %r is in the extra-data file but not in the current export"
            " — it may have been deleted or renamed.",
            name,
        )

    # Reconcile action entries
    for rule_name in sorted(export_set):
        coalesced_actions = coalesced_by_rule.get(rule_name, [])
        rule_file_actions: list[dict] = file_actions.get(rule_name, [])
        file_keys = {_action_key(e): e for e in rule_file_actions}
        new_file_actions = list(rule_file_actions)

        for coalesced in coalesced_actions:
            key = _action_key(coalesced)
            file_entry = file_keys.get(key)

            if coalesced["MISSING_COUNT"] == 0:
                if file_entry is not None:
                    logger.warning(
                        "Rule %r: action %r %r now has Objects in the export"
                        " — the extra-data entry in %s may be stale.",
                        rule_name,
                        coalesced["ACTION"],
                        coalesced["OBJECT_TYPE"],
                        path,
                    )
            else:
                if file_entry is None:
                    new_entry = _make_file_action_entry(coalesced)
                    new_file_actions.append(new_entry)
                    dirty = True
                    if file_existed:
                        logger.warning(
                            "Rule %r: action %r %r has %d missing Object(s)"
                            " — added placeholder(s) to %s. Fill them in and re-run.",
                            rule_name,
                            coalesced["ACTION"],
                            coalesced["OBJECT_TYPE"],
                            coalesced["MISSING_COUNT"],
                            path,
                        )
                else:
                    stored_count = len(file_entry.get("OBJECT", []))
                    if stored_count != coalesced["MISSING_COUNT"]:
                        logger.warning(
                            "Rule %r: action %r %r has %d missing Object(s) in the export"
                            " but %d stored in %s — counts differ.",
                            rule_name,
                            coalesced["ACTION"],
                            coalesced["OBJECT_TYPE"],
                            coalesced["MISSING_COUNT"],
                            stored_count,
                            path,
                        )

        # Warn about stale file action entries
        coalesced_keys = {_action_key(c) for c in coalesced_actions}
        for entry in rule_file_actions:
            if _action_key(entry) not in coalesced_keys:
                logger.warning(
                    "Rule %r: extra-data action entry %r %r not found in the export"
                    " — it may be stale.",
                    rule_name,
                    entry.get("ACTION", ""),
                    entry.get("OBJECT_TYPE", ""),
                )

        if new_file_actions:
            file_actions[rule_name] = new_file_actions
        elif rule_name in file_actions and not new_file_actions:
            del file_actions[rule_name]

    if not file_existed or dirty:
        extra_data_path.write_text(
            json.dumps(
                {"statuses": dict(sorted(statuses.items())), "actions": file_actions},
                indent=2,
                sort_keys=False,
            )
            + "\n",
            encoding="utf-8",
        )
        if not file_existed:
            logger.warning(
                "Extra-data file %s did not exist — created it with %d rule(s) set to Active"
                " and placeholder(s) for missing action Objects."
                " Review and update it, then re-run the script.",
                path,
                len(rule_names),
            )

    return {"statuses": statuses, "actions": file_actions}


def rule_name_to_slug(rule_name: str) -> str:
    """Convert a rule name to a filename-safe slug.

    Args:
        rule_name: Saviynt rule name string.

    Returns:
        Lowercase hyphen-separated slug suitable for use as a filename.
    """
    slug = rule_name.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug.strip("-")


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a Markdown table.

    Args:
        headers: Column header labels.
        rows: List of rows; each row is a list of cell strings.

    Returns:
        Markdown table as a string.
    """
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def build_condition_summary(conditions: list[dict]) -> str:
    """Build a SQL-like summary expression from a list of condition rows.

    Each basic condition becomes: {open}{ATTRIBUTE} {CONDITION} {VALUE}{close}
    Conditions are joined by their NEXTCONDITION connector (AND/OR).
    Advanced conditions contribute their raw query string.

    Args:
        conditions: Row dicts from the Rule Condition sheet for this rule.

    Returns:
        Single-line SQL-like expression string.
    """
    parts = []
    for cond in conditions:
        adv_query = cond.get("QUERYFORADVCONDITION", "")
        if adv_query:
            parts.append(adv_query)
        else:
            open_paren = cond.get(OPEN_PAREN_COL, "")
            close_paren = cond.get(CLOSE_PAREN_COL, "")
            attribute = cond.get("ATTRIBUTE", "")
            condition = (
                cond.get("CONDITION", "")
                .upper()
                .replace("NOT EQUALS", "!=")
                .replace("EQUALS", "=")
            )
            value = cond.get("OBJECTVALUE", "")

            token = open_paren
            token += attribute
            if condition:
                token += f" {condition}"
            if value:
                token += f" {value}"
            token += close_paren
            parts.append(token)

        next_cond = cond.get("NEXTCONDITION", "").upper()
        if next_cond:
            parts.append(next_cond)

    return " ".join(parts)


def build_conditions_section(conditions: list[dict]) -> str:
    """Render the Conditions section of a rule's Markdown.

    Args:
        conditions: Row dicts from the Rule Condition sheet for this rule.

    Returns:
        Markdown string for the Conditions section.
    """
    if not conditions:
        return "## Conditions\n\n_No conditions._"

    summary = build_condition_summary(conditions)

    headers = [
        "Type",
        "Open",
        "Object",
        "Attribute",
        "Condition",
        "Value",
        "Close",
        "Next",
    ]
    rows = []
    for cond in conditions:
        adv_query = cond.get("QUERYFORADVCONDITION", "")
        if adv_query:
            rows.append(
                [
                    cond.get("CONDITION_TYPE", ""),
                    "",
                    f"`{adv_query}`",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )
        else:
            rows.append(
                [
                    cond.get("CONDITION_TYPE", ""),
                    cond.get(OPEN_PAREN_COL, ""),
                    cond.get("OBJECT", ""),
                    cond.get("ATTRIBUTE", ""),
                    cond.get("CONDITION", ""),
                    cond.get("OBJECTVALUE", ""),
                    cond.get(CLOSE_PAREN_COL, ""),
                    cond.get("NEXTCONDITION", ""),
                ]
            )

    return "## Conditions\n\n`" + summary + "`\n\n" + md_table(headers, rows)


def build_actions_section(
    coalesced_actions: list[dict],
    file_actions: list[dict],
    rule_name: str = "",
) -> str:
    """Render the Actions section of a rule's Markdown.

    For coalesced action groups with missing Objects, looks up the stored Object
    list from file_actions and warns if the entry is absent or the count differs.

    Args:
        coalesced_actions: Coalesced action dicts from coalesce_actions().
        file_actions: Action entries from the extra-data file for this rule.
        rule_name: Rule name used in warning messages.

    Returns:
        Markdown string for the Actions section.
    """
    if not coalesced_actions:
        return "## Actions\n\n_No actions._"

    file_by_key = {_action_key(e): e for e in file_actions}

    headers = [
        "Action",
        "Organization",
        "Object Type",
        "Object",
        "Operation",
        "Execute On",
    ]
    rows = []
    for coalesced in coalesced_actions:
        objects = list(coalesced["OBJECTS"])

        if coalesced["MISSING_COUNT"] > 0:
            file_entry = file_by_key.get(_action_key(coalesced))
            if file_entry is None:
                logger.warning(
                    "Rule %r: action %r %r has %d missing Object(s)"
                    " — add an entry to the extra-data file and re-run.",
                    rule_name,
                    coalesced["ACTION"],
                    coalesced["OBJECT_TYPE"],
                    coalesced["MISSING_COUNT"],
                )
                objects += ["Missing from export"] * coalesced["MISSING_COUNT"]
            else:
                stored = file_entry.get("OBJECT", [])
                if len(stored) != coalesced["MISSING_COUNT"]:
                    logger.warning(
                        "Rule %r: action %r %r — extra-data has %d Object(s)"
                        " but export has %d missing; using what is stored.",
                        rule_name,
                        coalesced["ACTION"],
                        coalesced["OBJECT_TYPE"],
                        len(stored),
                        coalesced["MISSING_COUNT"],
                    )
                objects += [obj if obj else "Missing from export" for obj in stored]

        rows.append(
            [
                coalesced["ACTION"],
                coalesced["ORGANIZATION"],
                coalesced["OBJECT_TYPE"],
                ", ".join(objects) if objects else "Missing from export",
                coalesced["OPERATION"],
                coalesced["EXECUTEON"],
            ]
        )

    return "## Actions\n\n" + md_table(headers, rows)


def build_rule_markdown(
    rule: dict,
    conditions: list[dict],
    coalesced_actions: list[dict],
    file_actions: list[dict],
    env: str = "",
    status: str = "Active",
) -> str:
    """Build the complete Markdown document for a single rule.

    Args:
        rule: Row dict from the Rule sheet.
        conditions: Row dicts from the Rule Condition sheet for this rule.
        coalesced_actions: Coalesced action dicts from coalesce_actions().
        file_actions: Action entries from the extra-data file for this rule.
        env: Environment label (e.g. "DEV" or "PROD") shown in the title.
        status: Rule status ("Active" or "Inactive").

    Returns:
        Markdown string for the rule.
    """
    rule_name = rule.get("RULE_NAME", "")
    description = rule.get("RULE_DESCRIPTION", "")
    trigger = rule.get("TRIGGER_EVENT", "")
    detective = rule.get("INVOKE_BY_DETECTIVE", "")

    header_lines = [f"# Rule configuration - {rule_name} ({env})", ""]
    if description:
        header_lines.append(f"**Description:** {description}  ")
    header_lines.append(f"**Status:** {status}  ")
    header_lines.append(f"**Trigger Event:** {trigger}  ")
    header_lines.append(f"**Invoke By Detective:** {detective}")

    sections = [
        "\n".join(header_lines),
        build_conditions_section(conditions),
        build_actions_section(coalesced_actions, file_actions, rule_name=rule_name),
    ]
    return "\n\n".join(sections) + "\n"


def main() -> None:
    """Script entry point."""
    args = get_args_parser().parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Reading %s...", args.excel_file)
    wb = openpyxl.load_workbook(args.excel_file)

    rules = read_sheet(wb["Rule"])
    conditions_by_rule = group_by_rule(read_sheet(wb["Rule Condition"]))
    raw_actions_by_rule = group_by_rule(read_sheet(wb["Rule Action"]))
    coalesced_by_rule = {
        rule_name: coalesce_actions(actions)
        for rule_name, actions in raw_actions_by_rule.items()
    }
    logger.info(
        "Read %d rules, %d condition rows, %d action rows",
        len(rules),
        sum(len(v) for v in conditions_by_rule.values()),
        sum(len(v) for v in raw_actions_by_rule.values()),
    )

    rule_names = [r.get("RULE_NAME", "") for r in rules if r.get("RULE_NAME", "")]
    extra_data = load_extra_data(args.extra_data_file, rule_names, coalesced_by_rule)

    output_dir = Path(args.output_dir)
    written = 0
    for rule in sorted(rules, key=lambda r: r.get("RULE_NAME", "")):
        rule_name = rule.get("RULE_NAME", "")
        if not rule_name:
            continue

        markdown = build_rule_markdown(
            rule,
            conditions_by_rule.get(rule_name, []),
            coalesced_by_rule.get(rule_name, []),
            extra_data["actions"].get(rule_name, []),
            env=args.env,
            status=extra_data["statuses"].get(rule_name, "Active"),
        )

        slug = rule_name_to_slug(rule_name)
        output_path = output_dir / f"rule-{args.env.lower()}-{slug}.md"
        output_path.write_text(markdown, encoding="utf-8")
        logger.debug("Wrote %s", output_path)
        written += 1

    logger.info("Wrote %d rule file(s) to %s", written, args.output_dir)


if __name__ == "__main__":
    main()
