#!/opt/python/current/bin/python -Wall
"""Scrape config values from Saviynt connection markup or transport export.

Copyright 2023 Oregon State University.  All Rights Reserved.

Requests for more information can be directed to iamteam@oregonstate.edu |
advantage@oregonstate.edu 
"""

import argparse
import datetime
import json
import logging
import lxml
import os
import re

import sqlparse

import saviynt_config_wrangler as wrangler

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s",
)


def is_dir(arg_text):
    """Argparse type validator ensuring valid directory."""
    if os.path.isdir(arg_text):
        return arg_text
    raise argparse.ArgumentTypeError(f"Directory '{arg_text}' does not exist!")


def get_args_parser():
    """Define command line arguments."""

    script_description = """
This script extracts the details of a Saviynt connector from the HTML markup of
a saved configuration page (Admin->Identity Repository->Connections) OR from a
Transport export downloaded as zip, as available at Admin->Transport->Export.

For HTML, the markup contained in `input_filename` MUST include the
following elements described by XPath:
1. connection name (input with an id='connectionname'): //input[@id='connectionname']
2. configuration fields (textarea(s) with a name attribute): //textarea[@name]

For Transport export, the zip must include a
Connection_YYYY-MM-DD_HH-MM-SS(UTC).json and an
ObjectSummary_YYYY-MM-DD_HH-MM-SS(UTC).json.  """

    parser = argparse.ArgumentParser(
        description=script_description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("env", help="Which env is this?", choices=["DEV", "PROD"])
    parser.add_argument("input_filename")
    parser.add_argument(
        "--output-dir",
        help="Path to a directory where output file will be written.",
        default=".",
        type=is_dir,
    )
    return parser


def main():
    """This is the entry point when run from CLI.

    Parse `args.input_filename` and accumulate strings of interest from it into
    a file in `args.output_dir`.
    """

    # Get CLI args
    args = get_args_parser().parse_args()

    # Read the file we got, setup dependent vars
    if args.input_filename.endswith(".html"):
        connections = [wrangler.parse_config_from_html_file(args.input_filename)]
        export_timestamp = "not available (manual export via HTML scrape)"
    else:
        # .zip export is parsed into an object
        export = wrangler.ConfigExport(zipfile_path=args.input_filename)
        connections = export.connections.values()
        export_timestamp = export.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Loop over connections:
    # 1. Calculate header info
    # 2. Process attributes
    # 3. Write output to file
    for connection in connections:
        # Build up a string, `output`, containing headers and config info
        output = (
            f"# Connector configuration - {connection.name.strip()} ({args.env})\n\n"
            f"{'Exported:':<12}{str(export_timestamp)}\n"
            f"{'Generated:':<12}{datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}\n\n"
        )

        # Loop over connection attributes:
        # 1. Determine outer language
        # 2. Format according to outer language, capturing error info
        # 3. For JSON objects, find any embedded code blocks
        embedded_code_blocks = {}
        for name, value in connection.attributes.items():
            output += f"\n## {name}\n"
            if value is None:
                continue

            # Determine outer language
            outer_lang = wrangler.determine_outer_language(value)
            if outer_lang is None:
                outer_lang = "text"

            # Try to get a formatted version of the raw string
            try:
                formatted = wrangler.format_snippet(outer_lang, value)
                output += f"\n```{outer_lang}" f"\n{formatted}" f"\n```" f"\n\n"

                # Look for embedded code blocks
                try:
                    # JSON
                    if outer_lang == "json":
                        embedded_code_blocks.update(
                            wrangler.extract_code_snippets_from_json(value, [name])
                        )
                    # XML
                    if outer_lang == 'xml':
                        tree = lxml.etree.fromstring(value, parser = lxml.etree.XMLParser(strip_cdata=False))
                        sql = tree.xpath('.//sql-query/text()')
                        for statement in sql:
                            if statement.strip() == '':
                                continue
                            if wrangler.determine_outer_language(statement) == 'sql':
                                embedded_code_blocks.update({f'{name}->sql-query': sqlparse.format(statement, reindent=True)})
                except Exception as e:
                    logger.warning(
                        "Failed parsing embedded code blocks, message was: %s", e
                    )
                    # Add information about the error to output
                    output += (
                        "Failed to parse embedded code blocks:\n\n"
                        "```shell\n"
                        f"{e}\n"
                        "```"
                    )

            except json.JSONDecodeError as e:
                # There are attributes that should contain JSON but contain
                # Groovy or other syntax that causes JSON parser to fail.
                #
                # The assumption that they should contain JSON is based in part
                # on the attribute names e.g., 'UPDATEUSERJSON'.

                # Log the problem
                logger.warning("Problem parsing JSON, message was: %s", e)

                # How many chars of error context to show
                context_window = 20

                # Get the problematic line (e.lineno) then, using
                # context_window, slice out the section containing the
                # error
                problem_in_context = value.split("\n")[e.lineno][
                    e.colno - context_window : e.colno + context_window
                ]

                # Add information about the error to output
                output += (
                    # Declare the problem
                    f"Error parsing/formatting as {outer_lang}:\n\n"
                    "```shell\n"
                    f"{e}\n```"
                    "\n\n"
                    # Show the problem
                    f"In context ({context_window} chars either side of line "
                    f"{e.lineno} col {e.colno}): `{problem_in_context}`.\n\n"
                    # Add the attribute value un-formatted
                    f"```{outer_lang}\n"
                    f"{value}\n"
                    "```\n\n"
                )
            except Exception as e:
                # Failed formatting something other than JSON

                # Log the error
                logger.warning("Exception was: %s", e)

                # Add information about the error to output
                output += (
                    # Declare the problem
                    f"Error parsing/formatting as {outer_lang}:\n\n"
                    f"```shell\n{e}\n"
                    f"```\n"
                    # Add the attribute value un-formatted
                    f"```{outer_lang}\n"
                    f"{value}\n"
                    "```\n\n"
                )

        # Transport->export results in a .zip that contains \r\n; make sure
        # they don't make their way through to the output file.
        output = output.replace("\r\n", "\n")

        # Write `output` to file
        # First, calculate the file name by replacing spaces in the connection
        # name with hyphen, then collapse sequences of repeated hyphen into a
        # single instance.
        filesystem_safe_name = re.sub(
            r"-{2,}", "-", connection.name.strip().replace(" ", "-").lower()
        )
        file_to_write = (
            f"{args.output_dir.rstrip('/')}/"
            f"connector-config-{args.env.lower()}-{filesystem_safe_name}.md"
        )

        # Open the file and write
        with open(file_to_write, "w", encoding="utf-8", newline="\n") as output_file:
            # Write the formatted and language-hinted blocks
            output_file.write(output)
            # Write out any embedded blocks at the end of the file
            if len(embedded_code_blocks) > 0:
                embedded_code_header = (
                    "\n\n" "---" "\n\n" "## Embedded code blocks" "\n\n"
                )
                output_file.write(embedded_code_header)
                for k, v in embedded_code_blocks.items():
                    # Get language hint
                    lang = wrangler.determine_outer_language(v)
                    # Write the header (k) then the block
                    output_file.write("\n\n" f"## {k}\n" f"```{lang}\n" f"{v}\n" "```")

            logger.info(
                "Done writing details for '%s' to file %s",
                connection.name,
                file_to_write,
            )


if __name__ == "__main__":
    main()
