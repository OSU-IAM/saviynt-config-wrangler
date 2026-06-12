#!/opt/python/current/bin/python -Wall
"""Convert a Saviynt Technical Rules Excel export to per-rule Markdown files.

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
        description="Convert Saviynt Technical Rules Excel export to per-rule Markdown files"
    )
    parser.add_argument(
        "excel_file", help="Path to the Saviynt Technical Rules Excel export (.xlsx)"
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
        "--status-file",
        required=True,
        help=(
            "Path to JSON file mapping rule names to Active/Inactive status. "
            "Created with all rules defaulting to Active if it does not exist."
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


def load_status_file(path: str, rule_names: list[str]) -> dict[str, str]:
    """Load rule statuses from a JSON file, creating it if it does not exist.

    If the file does not exist, writes it with every rule defaulting to Active
    and warns the operator to review it before re-running.

    If the file exists but is missing rules present in the current export,
    adds them as Active and warns. Stale entries (in the file but not in the
    current export) are also warned about.

    Args:
        path: Path to the JSON status file.
        rule_names: Rule names from the current export.

    Returns:
        Dict mapping rule name to "Active" or "Inactive".
    """
    status_path = Path(path)
    statuses: dict[str, str] = {}

    if not status_path.exists():
        statuses = {name: "Active" for name in rule_names}
        status_path.write_text(
            json.dumps(statuses, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        logger.warning(
            "Status file %s did not exist — created it with all %d rules set to Active. "
            "Review and update it, then re-run the script.",
            path,
            len(statuses),
        )
        return statuses

    statuses = json.loads(status_path.read_text(encoding="utf-8"))

    export_set = set(rule_names)
    file_set = set(statuses.keys())

    new_rules = export_set - file_set
    if new_rules:
        for name in sorted(new_rules):
            statuses[name] = "Active"
            logger.warning(
                "Rule %r is in the export but not in the status file — defaulting to Active. "
                "Update %s if this is incorrect.",
                name,
                path,
            )
        status_path.write_text(
            json.dumps(statuses, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    for name in sorted(file_set - export_set):
        logger.warning(
            "Rule %r is in the status file but not in the current export — "
            "it may have been deleted or renamed.",
            name,
        )

    return statuses


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


def build_actions_section(actions: list[dict]) -> str:
    """Render the Actions section of a rule's Markdown.

    Args:
        actions: Row dicts from the Rule Action sheet for this rule.

    Returns:
        Markdown string for the Actions section.
    """
    if not actions:
        return "## Actions\n\n_No actions._"

    headers = ["Organization", "Object Type", "Object", "Object Attribute"]
    rows = []
    for action in actions:
        rows.append(
            [
                action.get("ORGANIZATION", ""),
                action.get("OBJECT_TYPE", ""),
                action.get("OBJECT", ""),
                action.get("OBJECT_ATTRIBUTE", ""),
            ]
        )

    return "## Actions\n\n" + md_table(headers, rows)


def build_rule_markdown(
    rule: dict,
    conditions: list[dict],
    actions: list[dict],
    env: str = "",
    status: str = "Active",
) -> str:
    """Build the complete Markdown document for a single rule.

    Args:
        rule: Row dict from the Rule sheet.
        conditions: Row dicts from the Rule Condition sheet for this rule.
        actions: Row dicts from the Rule Action sheet for this rule.
        env: Environment label (e.g. "DEV" or "PROD") shown in the title.
        status: Rule status ("Active" or "Inactive").

    Returns:
        Markdown string for the rule.
    """
    rule_name = rule.get("RULE_NAME", "")
    description = rule.get("RULE_DESCRIPTION", "")
    detective = rule.get("DETECTIVE", "")
    birthright = rule.get("BIRTHRIGHT", "")
    remove_birthright = rule.get("REMOVE_BIRTHRIGHT_ACCESS", "")

    header_lines = [f"# Technical Rule - {rule_name} ({env})", ""]
    if description:
        header_lines.append(f"**Description:** {description}  ")
    header_lines.append(f"**Status:** {status}  ")
    header_lines.append(f"**Detective:** {detective}  ")
    header_lines.append(f"**Birthright:** {birthright}  ")
    header_lines.append(f"**Remove Birthright Access:** {remove_birthright}")

    sections = [
        "\n".join(header_lines),
        build_conditions_section(conditions),
        build_actions_section(actions),
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
    actions_by_rule = group_by_rule(read_sheet(wb["Rule Action"]))
    logger.info(
        "Read %d rules, %d condition rows, %d action rows",
        len(rules),
        sum(len(v) for v in conditions_by_rule.values()),
        sum(len(v) for v in actions_by_rule.values()),
    )

    rule_names = [r.get("RULE_NAME", "") for r in rules if r.get("RULE_NAME", "")]
    statuses = load_status_file(args.status_file, rule_names)

    output_dir = Path(args.output_dir)
    written = 0
    for rule in sorted(rules, key=lambda r: r.get("RULE_NAME", "")):
        rule_name = rule.get("RULE_NAME", "")
        if not rule_name:
            continue

        markdown = build_rule_markdown(
            rule,
            conditions_by_rule.get(rule_name, []),
            actions_by_rule.get(rule_name, []),
            env=args.env,
            status=statuses.get(rule_name, "Active"),
        )

        slug = rule_name_to_slug(rule_name)
        output_path = output_dir / f"technical-rule-{args.env.lower()}-{slug}.md"
        output_path.write_text(markdown, encoding="utf-8")
        logger.debug("Wrote %s", output_path)
        written += 1

    logger.info("Wrote %d rule file(s) to %s", written, args.output_dir)


if __name__ == "__main__":
    main()
