"""Utilities supporting Saviynt configuration management.

Copyright 2023 Oregon State University.  All Rights Reserved.

Requests for more information can be directed to iamteam@oregonstate.edu |
advantage@oregonstate.edu 
"""
import dataclasses
import datetime
import json
import logging
import zipfile

from bs4 import BeautifulSoup
import sqlparse

logger = logging.getLogger(__name__)


def determine_outer_language(lang_text):
    """Heuristic for determining the language.

    Given the very small set of languages/formats in scope (Groovy, JSON, SQL,
    XML) with mutually exclusive starting characters or words, let it be
    sufficient to determine the language based on the first character or word.
    """

    # Don't attempt to guess a language for non-string inputs.
    if not isinstance(lang_text, str):
        return None

    # In this context, Groovy code blocks start this way
    if lang_text.startswith("${"):
        return "groovy"

    # JSON should start with '{'
    if lang_text.startswith("{"):
        return "json"

    # SQL starts with DML keywords
    for keyword in ["SELECT", "UPDATE", "INSERT", "DELETE", "ALTER"]:
        if lang_text.startswith(keyword):
            return 'sql'

    # XML is easy to spot amongst these others
    if lang_text.startswith("<"):
        return "xml"
    return None


def format_snippet(lang, snippet):
    """Return a pretty-formatted version of the input snippet.

    @TODO: Implement better formatting for groovy and xml.
    """
    match lang:
        case "groovy":
            return snippet

        case "json":
            preprocessed = snippet.replace("\n", "")
            return json.dumps(
                json.loads(preprocessed, strict=False), sort_keys=True, indent=4
            )

        case "sql":
            return sqlparse.format(snippet, reindent=True, keyword_case="upper")

        case "xml":
            return snippet

        case _:
            return snippet


def extract_code_snippets_from_json(json_str, name, path_sep="->"):
    """Walk the JSON tree recognizing and formatting embedded code.

    As each node is processed, code blocks are captured, formatted, and stored
    in a dict whose keys are the path, from root to leaf, where the code was
    found.

    Args:
        json_str: JSON-parse-able string to be traversed
        name: name of the root of the JSON tree, used as the first path segment
            of keys in the dict returned.
        path_sep: string to be used to separate path segments in keys of the
            returned dict

    Returns: dict containing code snippets, keyed by path in the JSON tree.
    """

    def process_json_tree(json_tree, level=None):
        """Recursive function processing dict-like JSON trees.

        For str and list nodes, look for a code snippet in the value; for dict
        nodes, recurse.

        Args:
            json_tree: dict (or sub-dict) created by json.loads.
            level: str representing the current level of the tree. At the
                top-level, this is 'name' passed in from the outer function. At
                subsequent levels, this is the current key. It's a depth gauge.

        Returns:
            code_found, a dict where keys are path_sep-delimited strings
                representing the hierarchy of the JSON tree at which each entry
                was found.
        """
        # Accumulate results here with string keys generated whenever a code
        # block is found by joining the path elements in level
        code_found = {}

        # Since each level of the tree is represented as an element in a list,
        # then the top level (the root) of the tree is the empty list.
        if level is None:
            level = []

        # Iterate over each node (key/value pair) at this level of the tree.
        for node, contents in json_tree.items():
            # Use a copy so we don't update the `level` passed in from other
            # levels of recursion.
            current_level = level.copy()

            # Add the current attr name to the tail of the list
            current_level.append(node)

            # Process this node according to type
            if isinstance(contents, dict):
                # Recurse, passing passing current_level so that the value dict
                # returned includes correct depth information.
                value = process_json_tree(contents, current_level)
                code_found.update(value)

            elif isinstance(contents, list):
                # Multiple values (list) found for this node, use numeric
                # indexes to distinguish one from the next in the code_found
                # dict.

                index = 0
                # Index is incremented for each list element, whether or not it
                # contains anything interesting. Therefore, loop counter
                # incrementation happens at the top of the loop, before any
                # condition results in 'continue'.
                current_level.append(index)
                for item in contents:
                    # Update the tail element of the current_level list with index
                    current_level[-1] = str(index)

                    # Increment for next iteration
                    index += 1

                    # Determine the language, if any, of item
                    language = determine_outer_language(item)

                    # Skip no-language and JSON items
                    if language is None or language == "json":
                        continue

                    # Found something!
                    # Mint a new key from current_level and format the code to
                    # be stored as its value.
                    code_found[path_sep.join(current_level)] = format_snippet(
                        language, item
                    )
            else:
                # Determine the language, if any, of item
                language = determine_outer_language(contents)

                # Skip no-language and JSON items
                if language is None or language == "json":
                    continue

                # Found something!
                # Mint a new key from current_level and format the code to
                # be stored as its value.
                code_found[path_sep.join(current_level)] = format_snippet(
                    language, contents
                )

        # Return
        return code_found

    # Load json_str -> json_tree
    json_tree = json.loads(json_str)
    extract = process_json_tree(json_tree, name)
    return extract


@dataclasses.dataclass(kw_only=True)
class Connection:
    """Sparse model of the connections data structure.

    As returned by Saviynt as JSON generated by Admin -> Transport -> Export.
    """

    name: str
    attributes: dict
    status: bool = True
    description: str = None
    timestamp: datetime = None


@dataclasses.dataclass(kw_only=True)
class ConfigExport:
    """Model of the relevant information bundled in a connections export.

    Attributes:
        zipfile_path: str filesystem path where __post_init__ will try to read
            a zip file. Zip file contains ObjectSummary<datestamp>.json which
            is parsed for export metadata such as timestamp. Connection
            information comes from the Connection<datestamp>.json included in
            the zip.

        connections: Dict[str,Connection] parsed from
            Connection<datestamp>.json, keyed by connection name.
        timestamp: UTC parsed from ObjectSummary[Information][Exported On]
        system: str identifying the hostname generating the export
    """

    zipfile_path: str
    connections: dict = dataclasses.field(default_factory=dict)
    timestamp: datetime.datetime = None
    system: str = None

    def __post_init__(self):
        """Parse self.zipfile (only mandatory param) into other attr values."""

        with zipfile.ZipFile(self.zipfile_path) as zip_archive:
            for zip_member in zip_archive.infolist():
                # Parse exported JSON metadata from ObjectSummary
                if zip_member.filename.startswith("ObjectSummary"):
                    with zip_archive.open(zip_member.filename) as f:
                        metadata = json.loads(f.read())

                    self.timestamp = datetime.datetime.strptime(
                        metadata["Information"]["Exported On"], "%Y-%m-%d %H:%M:%S"
                    )

                    self.system = metadata["Information"]["System"]

                # Extract connection info
                if zip_member.filename.startswith("Connection"):
                    with zip_archive.open(zip_member.filename) as f:
                        connections = json.loads(f.read())

                    # This is a hand-curated list of attributes names whose
                    # contents should be kept secret
                    encrypted_attrs = [
                        "SERVICE_ACCOUNT_KEY_JSON",
                        "SSH_KEY",
                        "ConnectionJSON",
                    ]

                    # Make a connection object for each entry
                    for connection_name in connections:
                        params = {
                            "name": connections[connection_name]["connectionname"],
                            "description": connections[connection_name][
                                "connectiondescription"
                            ],
                            "status": bool(connections[connection_name]["status"]),
                            "timestamp": self.timestamp,
                            "attributes": {},
                        }
                        # Accumulate attributes into params[attributes]
                        for attr in connections[connection_name]["EXTERNAL_ATTR"]:
                            name = attr["attributename"]

                            # Replace sensitive values with placeholder chars.
                            value = (
                                attr["encryptedattributevalue"]
                                if name not in encrypted_attrs
                                else "##########"
                            )

                            # Convert empty string to None
                            if value == "":
                                value = None

                            # Add to params dict
                            params["attributes"][name] = value

                        # Pass params to the Connection constructor, adding an
                        # entry to self.connections
                        self.connections[connection_name] = Connection(**params)


def parse_config_from_html_file(filename):
    """Process the HTML saved from a Saviynt connection configuration page.

    Args:
        filename: path to a file containing HTML

    Returns: Connection
    """

    # Init a BeautifulSoup object with the contents of filename.
    with open(filename, "r", encoding='utf-8') as html:
        soup = BeautifulSoup(html, "html.parser")

    # Get connection name
    name = soup.find("input", {"id": "connectionname"})["value"].strip()

    # Iterate over textareas, extracting names and details
    attributes = {}
    for field in soup("textarea"):
        attributes[field["name"]] = field.string

    return Connection(name=name, attributes=attributes)
