This repository provides tooling to help users manually track Saviynt configuration.

It was developed while working with Saviynt v23.5 and may not be applicable to
other versions.

## Details

### Context

1. Saviynt relies on connections to external systems to do its work.
1. Connections are configured through HTML forms in the Saviynt UI.
1. Connection configuration is 'code' composed of plain text XML, SQL, JSON, Groovy.

### Problem areas

1. Configuration is not validated, so a missing comma, space, or a misplaced
   brace can only be found by visually 'parsing' the configuration.
1. Configuration is not formatted, nor syntax highlighted making it difficult
   to read and therefore, making it very time-consuming to debug.
1. Configuration is versioned, but the versioning UI is not sophisticated
   enough to provide a user-friendly experience for anything other than the
   most trivial values.

![Saviynt config ui](/img/sav-config-ui.png "Saviynt config UI")
![Saviynt history](/img/sav-config-history.png "Saviynt config history")

### This solution features

1. **Language Identification** - Isolates each configuration field and
   heuristically determines the programming language (e.g., Groovy, SQL) or
   structural format (e.g., XML, JSON).
   1. **Including embedded code blocks** - Most of the non-trivial
      configuration fields accept JSON or XML which may include embedded blocks
      of SQL, Groovy. These are extracted during a recursive traversal of the
      outer structure and presented as standalone code blocks in the Markdown
      output.
1. **Formatting** - With 'language' determined, 'code'  is reformatted
   according to its particular convention and output as language-hinted code
   blocks in a Markdown file.
1. **Industry-standard version control** - Generates Markdown files that can be
   committed to a git repository and pushed to a repository hosting service
   (e.g., GitHub, GitLab, BitBucket, etc).
1. **Syntax Highlighting** - Repository hosting services like GitHub render
   Markdown files as HTML, using the language hints to provide syntax
   highlighting.

![Formatted, highlighted code](/img/formatted-code-block.png "Formatted, highlighted code")
![Embedded code](/img/embedded-code-block.png "Embedded code block")
![Diff](/img/git-diff.png "Rich diff")


## Use

There are two ways to get configuration out of Saviynt, 'save HTML' and 'export
.zip'. 

### Save HTML
1. Navigate to the Saviynt connections list
1. Choose one, and when its configuration page loads FULLY (wait a beat for the JavaScript to
   load), Ctrl-s to open the save dialog (tested in Chromium)
   1. Choose 'web page, complete' from the bottom-left corner drop-down in the
      Save.. dialog.
1. Run the tool against the downloaded .html file (the companion folder is
   not used, and other download methods don't work).
   ```shell
   $ python wrangle.py --output-dir /tmp/connections PROD ~/Downloads/Add_Update\ Connection.html
   2023-07-31 15:41:09,348 WARNING wrangle:151 Problem parsing JSON, message was: Invalid \escape: line 1 column 270 (char 269)
   2023-07-31 15:41:09,400 INFO wrangle:228 Done writing details for 'GYBONID DB' to file /tmp/connections/connector-config-prod-gybonid-db.md
   ```
1. Go back to your browser and then back to the connections list to pick the
   next one.

### Export .zip
1. In each Saviynt environment, navigate to Admin -> Transport -> Export
1. Choose 'Connection' from the drop-down list
1. 'Add All' and proceed to 'View Summary'
1. Choose 'Export' (download icon)
1. Run the tool against the .zip file
   ```shell
   $ python wrangle.py --output-dir /tmp/connections PROD ~/Downloads/transport_sasaviyntpeakja_2023-07-31_22-38-19\(UTC\).zip
   2023-07-31 15:39:00,275 INFO wrangle:228 Done writing details for 'Privileged_Application' to file /tmp/connections/connector-config-prod-privileged_application.md
   2023-07-31 15:39:00,275 INFO wrangle:228 Done writing details for 'SAVIYNT_EXCHANGE' to file /tmp/connections/connector-config-prod-saviynt_exchange.md
   2023-07-31 15:39:00,275 WARNING wrangle:151 Problem parsing JSON, message was: Invalid \escape: line 1 column 271 (char 270)
   2023-07-31 15:39:00,329 INFO wrangle:228 Done writing details for 'GYBONID DB' to file /tmp/connections/connector-config-prod-gybonid-db.md
   2023-07-31 15:39:00,330 INFO wrangle:228 Done writing details for 'Active Directory ' to file /tmp/connections/connector-config-prod-active-directory.md
   2023-07-31 15:39:00,331 INFO wrangle:228 Done writing details for 'OSU Azure AD - REST' to file /tmp/connections/connector-config-prod-osu-azure-ad-rest.md
   2023-07-31 15:39:00,334 INFO wrangle:228 Done writing details for 'OSU ONID LDAP' to file /tmp/connections/connector-config-prod-osu-onid-ldap.md
   2023-07-31 15:39:00,334 INFO wrangle:228 Done writing details for 'OSU GOOGLE' to file /tmp/connections/connector-config-prod-osu-google.md
   2023-07-31 15:39:00,334 INFO wrangle:228 Done writing details for 'Unix-Pwdless' to file /tmp/connections/connector-config-prod-unix-pwdless.md
   2023-07-31 15:39:00,335 INFO wrangle:228 Done writing details for 'OSU Exchange-REST' to file /tmp/connections/connector-config-prod-osu-exchange-rest.md
   2023-07-31 15:39:00,336 INFO wrangle:228 Done writing details for 'OSU GOOGLE - REST' to file /tmp/connections/connector-config-prod-osu-google-rest.md
   ```

## Room for Improvement
1. Format groovy(-ish) strings like those used in `CREATEACCOUNTJSON` and
   `UPDATEACCOUNTJSON` (see
   [tests/groovy_samples.py](./tests/groovy_samples.py)) in the LDAP connector,
   e.g.,

   ```groovy
   ${
    Map map1 = new HashMap();
    if (! user?.customproperty30?.equalsIgnoreCase('R')) map1.put("objectClass",["top", "person","organizationalPerson","inetOrgPerson","posixAccount","shadowAccount", "googlePerson","osuPerson","lpSghePerson","eduPerson"]);
   ...
   }
   ```
   These strings _seem_ to be groovy template strings (a la Python's Jinja),
   based on a casual reading of Groovy docs' [Template
   engines](https://docs.groovy-lang.org/docs/next/html/documentation/template-engines.html#_simpletemplateengine)
   page.

   1. Linting/formatting with [npm-groovy-lint](https://github.com/nvuillam/npm-groovy-lint) fails with

      ```shell
      error    Unexpected input: '{' @ line 1, column 2.  NglParseError`.
      ```

      Removing the opening `${` and closing `}` doesn't help enough:

      ```shell
      error    Unexpected input: '(' @ line 1, column 35.  NglParseError
      ```
      It's quite possible (untested) that when used as a component of VSCode,
      npm-groovy-lint _just works_ for these strings, meaning that it _may_ be
      possible to configure npm-groovy-lint for them.

   1. Other possible paths forward:
      1. Write/configure a lexer and parser generator with one of the following;
         1. [Python Shlex](https://docs.python.org/3/library/shlex.html) - see
            [StackOverflow](https://stackoverflow.com/a/32217053) for an
            incomplete, non-working example
            1. Unrelated [SO thread](https://stackoverflow.com/q/14354165)
               points to Groovy internals, and the OP characterizes this
               problem well: _"Since groovy is good at parsing nearly anything,
               a search on how to parse groovy code will not reveal any good
               results"_.
         1. The venerable [ANTLR](https://www.antlr.org/), which has a Python entry point,
            [antlr4-tools](https://github.com/antlr/antlr4-tools), and [a large library of
            off-the-shelf grammars](https://github.com/antlr/grammars-v4), but nothing for Groovy!
         1. [PLY (Python Lex-Yacc)](http://www.dabeaz.com/ply/ply.html#ply_nn9)
      1. Try more formal means of language recognition such as is done in
         [guesslang](https://pypi.org/project/guesslang/).
      1. For users in a more Java-/Groovy- centric environment,
         [CodeNarc](https://codenarc.org/) "Static Analysis for Groovy", will
         likely recognize these snippets perfectly.

1. Parse and format unparse-able JSON such as that found in `UPDATEUSERJSON` of
   the GYBONID connector.
   1. Preprocessing may help for a class of issues, such as the presence if
      control characters (like `\n`).
   1. It's possible, though probably not helpful, to extend [Python's
      `json.JSONDecoder`](https://docs.python.org/3.10/library/json.html?highlight=json#json.JSONDecoder).

1. Real XML parsing - current XML is fairly well-formatted, though it would not
   take much to parse it with Python's
   [`xml.etree.ElementTree`](https://docs.python.org/3.10/library/xml.etree.elementtree.html?highlight=etree).
   Then walk the tree looking for `CDATA` sections containing other language
   snippets.
