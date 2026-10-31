.. include:: includes.rst

Length Rules
------------

These rules cover the length of lines in the VHDL file.

length_001
##########

|phase_7| |warning| |unfixable| |length|

Alias: :code:`length_line`

This rule checks the length of the line.

|configuring_length_rules_link|

length_002
##########

|phase_7| |warning| |unfixable| |length|

Alias: :code:`length_file`

This rule checks the length of a file.

|configuring_length_rules_link|

length_003
##########

|phase_7| |warning| |unfixable| |length|

Alias: :code:`length_process`

This rule checks the length of a process statement.

|configuring_length_rules_link|

length_004
##########

|phase_7| |disabled| |error| |unfixable| |length|

Alias: :code:`length_line_second_limit`

This rule checks the length of the line against a second, usually longer, limit.

Together with :ref:`length_001` it allows staged line lengths.
For example, length_001 can report lines over 80 characters as warnings, while this rule reports lines over 120 characters as errors.

This rule is disabled by default.
Its default length is 120 and its default severity is Error.

|configuring_length_rules_link|
