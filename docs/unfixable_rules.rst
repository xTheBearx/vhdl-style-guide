
.. include:: includes.rst

Unfixable Rules
===============

MHSG is capable of fixing a wide range of formatting issues.
However, there are a class of issues which can be checked but can not be fixed.
These issues require the user to make the required changes.
In the documentation, these rules are marked with the following icon:  |unfixable|


Comments
--------

The existence and formatting of comments is left to the user as MHSG can not have an opinion.

* `block_comment_001 <block_comment_rules.html#block-001>`_
* `block_comment_002 <block_comment_rules.html#block-002>`_
* `block_comment_003 <block_comment_rules.html#block-003>`_
* `comment_012 <comment_rules.html#comment-012>`_
* `comment_013 <comment_rules.html#comment-013>`_
* `generic_023 <generic_rules.html#generic-023>`_
* `port_029 <port_rules.html#port-029>`_
* `sequential_006 <sequential_rules.html#sequential-006>`_
* `variable_assignment_006 <variable_assignment_rules.html#variable-assignment-006>`_

Configuration
-------------

Issues in configuration files can not be fixed.

* `source_file_001 <source_file_rules.html#source-file-001>`_

Default Assignments
-------------------

Default assignments are not preferred, but removing them may affect the design.

* `port_012 <port_rules.html#port-012>`_
* `signal_007 <signal_rules.html#signal-007>`_
* `variable_007 <variable_rules.html#variable-007>`_

Formatting Options
------------------

There are some formatting decisions that are best left to the user.

* `instantiation_034 <instantiation_rules.html#instantiation-034>`_
* `port_023 <port_rules.html#port-023>`_
* `process_030 <process_rules.html#process-030>`_
* `reserved_001 <reserved_rules.html#reserved-001>`_

Identifier Restrictions
-----------------------

With multiple options available, the user is required to make the decision.

* `architecture_025 <architecture_rules.html#architecture-025>`_
* `instantiation_036 <instantiation_rules.html#instantiation-036>`_
* `library_012 <../library_rules.html#library-012>`_
* `use_clause_001 <../use_clause_rules.html#use-clause-001>`_

Lengths
-------

Addressing length issues requires the user to address.

* `length_001 <length_rules.html#length-001>`_
* `length_002 <length_rules.html#length-002>`_
* `length_003 <length_rules.html#length-003>`_
* `length_004 <length_rules.html#length-004>`_

Missing Labels
--------------

The name of the label must be chosen by the user.

* `loop_statement_006 <loop_statement_rules.html#loop-statement-006>`_
* `process_016 <process_rules.html#process-016>`_

Positional Assignments
----------------------

Mapping positional assignments to formal parts is left to the user.

* `generic_map_008 <generic_map_rules.html#generic-map-008>`_
* `port_map_008 <port_map_rules.html#port-map-008>`_

Prefix and Suffix
-----------------

With multiple options available, the user is required to make the decision.

* `alias_declaration_600 <alias_declaration_rules.html#alias-declaration-600>`_
* `alias_declaration_601 <alias_declaration_rules.html#alias-declaration-601>`_
* `block_600 <block_rules.html#block-600>`_
* `block_601 <block_rules.html#block-601>`_
* `case_022 <case_rules.html#case-022>`_
* `case_023 <case_rules.html#case-023>`_
* `concurrent_013 <concurrent_rules.html#concurrent-013>`_
* `constant_015 <constant_rules.html#constant-015>`_
* `constant_600 <constant_rules.html#constant-600>`_
* `constant_601 <constant_rules.html#constant-601>`_
* `constant_602 <constant_rules.html#constant-602>`_
* `design_001 <design_rules.html#design-001>`_
* `design_002 <design_rules.html#design-002>`_
* `design_003 <design_rules.html#design-003>`_
* `design_004 <design_rules.html#design-004>`_
* `design_005 <design_rules.html#design-005>`_
* `design_006 <design_rules.html#design-006>`_
* `design_007 <design_rules.html#design-007>`_
* `design_008 <design_rules.html#design-008>`_
* `design_009 <design_rules.html#design-009>`_
* `design_010 <design_rules.html#design-010>`_
* `design_011 <design_rules.html#design-011>`_
* `design_012 <design_rules.html#design-012>`_
* `design_013 <design_rules.html#design-013>`_
* `design_014 <design_rules.html#design-014>`_
* `design_015 <design_rules.html#design-015>`_
* `design_016 <design_rules.html#design-016>`_
* `design_017 <design_rules.html#design-017>`_
* `design_018 <design_rules.html#design-018>`_
* `function_600 <function_rules.html#function-600>`_
* `function_601 <function_rules.html#function-601>`_
* `generate_017 <generate_rules.html#generate-017>`_
* `generate_600 <generate_rules.html#generate-600>`_
* `generate_601 <generate_rules.html#generate-601>`_
* `generate_602 <generate_rules.html#generate-602>`_
* `generic_020 <generic_rules.html#generic-020>`_
* `generic_600 <generic_rules.html#generic-600>`_
* `generic_map_600 <generic_map_rules.html#generic-map-600>`_
* `generic_map_601 <generic_map_rules.html#generic-map-601>`_
* `instantiation_600 <instantiation_rules.html#instantiation-600>`_
* `instantiation_601 <instantiation_rules.html#instantiation-601>`_
* `interface_incomplete_type_declaration_600 <../interface_incomplete_type_declaration_rules.html#interface-incomplete-type-declaration-600>`_
* `interface_incomplete_type_declaration_601 <../interface_incomplete_type_declaration_rules.html#interface-incomplete-type-declaration-601>`_
* `lint_001 <lint_rules.html#lint-001>`_
* `lint_002 <lint_rules.html#lint-002>`_
* `lint_003 <lint_rules.html#lint-003>`_
* `lint_004 <lint_rules.html#lint-004>`_
* `lint_005 <lint_rules.html#lint-005>`_
* `lint_006 <lint_rules.html#lint-006>`_
* `lint_007 <lint_rules.html#lint-007>`_
* `lint_008 <lint_rules.html#lint-008>`_
* `lint_009 <lint_rules.html#lint-009>`_
* `lint_010 <lint_rules.html#lint-010>`_
* `lint_011 <lint_rules.html#lint-011>`_
* `lint_012 <lint_rules.html#lint-012>`_
* `lint_013 <lint_rules.html#lint-013>`_
* `lint_014 <lint_rules.html#lint-014>`_
* `lint_015 <lint_rules.html#lint-015>`_
* `lint_016 <lint_rules.html#lint-016>`_
* `lint_017 <lint_rules.html#lint-017>`_
* `lint_018 <lint_rules.html#lint-018>`_
* `lint_019 <lint_rules.html#lint-019>`_
* `lint_020 <lint_rules.html#lint-020>`_
* `lint_021 <lint_rules.html#lint-021>`_
* `lint_022 <lint_rules.html#lint-022>`_
* `lint_023 <lint_rules.html#lint-023>`_
* `lint_024 <lint_rules.html#lint-024>`_
* `lint_025 <lint_rules.html#lint-025>`_
* `lint_026 <lint_rules.html#lint-026>`_
* `lint_027 <lint_rules.html#lint-027>`_
* `lint_028 <lint_rules.html#lint-028>`_
* `lint_029 <lint_rules.html#lint-029>`_
* `lint_030 <lint_rules.html#lint-030>`_
* `lint_031 <lint_rules.html#lint-031>`_
* `lint_032 <lint_rules.html#lint-032>`_
* `lint_033 <lint_rules.html#lint-033>`_
* `lint_034 <lint_rules.html#lint-034>`_
* `lint_035 <lint_rules.html#lint-035>`_
* `lint_036 <lint_rules.html#lint-036>`_
* `lint_037 <lint_rules.html#lint-037>`_
* `lint_038 <lint_rules.html#lint-038>`_
* `lint_039 <lint_rules.html#lint-039>`_
* `lint_040 <lint_rules.html#lint-040>`_
* `lint_041 <lint_rules.html#lint-041>`_
* `lint_042 <lint_rules.html#lint-042>`_
* `loop_statement_600 <loop_statement_rules.html#loop-statement-600>`_
* `loop_statement_601 <loop_statement_rules.html#loop-statement-601>`_
* `loop_statement_602 <loop_statement_rules.html#loop-statement-602>`_
* `loop_statement_603 <loop_statement_rules.html#loop-statement-603>`_
* `package_016 <package_rules.html#package-016>`_
* `package_017 <package_rules.html#package-017>`_
* `package_body_600 <package_body_rules.html#package-body-600>`_
* `package_body_601 <package_body_rules.html#package-body-601>`_
* `package_instantiation_600 <package_instantiation_rules.html#package-instantiation-600>`_
* `package_instantiation_601 <package_instantiation_rules.html#package-instantiation-601>`_
* `port_011 <port_rules.html#port-011>`_
* `port_025 <port_rules.html#port-025>`_
* `port_600 <port_rules.html#port-600>`_
* `port_601 <port_rules.html#port-601>`_
* `port_602 <port_rules.html#port-602>`_
* `port_603 <port_rules.html#port-603>`_
* `port_604 <port_rules.html#port-604>`_
* `port_605 <port_rules.html#port-605>`_
* `port_606 <port_rules.html#port-606>`_
* `port_607 <port_rules.html#port-607>`_
* `port_608 <port_rules.html#port-608>`_
* `port_609 <port_rules.html#port-609>`_
* `process_036 <process_rules.html#process-036>`_
* `process_600 <process_rules.html#process-600>`_
* `signal_008 <signal_rules.html#signal-008>`_
* `signal_600 <signal_rules.html#signal-600>`_
* `subtype_004 <subtype_rules.html#subtype-004>`_
* `subtype_600 <subtype_rules.html#subtype-600>`_
* `subtype_601 <subtype_rules.html#subtype-601>`_
* `subtype_602 <subtype_rules.html#subtype-602>`_
* `type_015 <type_rules.html#type-015>`_
* `type_600 <type_rules.html#type-600>`_
* `type_601 <type_rules.html#type-601>`_
* `type_602 <type_rules.html#type-602>`_
* `variable_012 <variable_rules.html#variable-012>`_
* `variable_600 <variable_rules.html#variable-600>`_

SystemVerilog Rules
-------------------

Rules on the design of SystemVerilog and Verilog code that only the designer can change.

* `sv_always_003 <sv_always_rules.html#sv-always-003>`_
* `sv_always_004 <sv_always_rules.html#sv-always-004>`_
* `sv_always_005 <sv_always_rules.html#sv-always-005>`_
* `sv_always_006 <sv_always_rules.html#sv-always-006>`_
* `sv_always_007 <sv_always_rules.html#sv-always-007>`_
* `sv_always_008 <sv_always_rules.html#sv-always-008>`_
* `sv_always_009 <sv_always_rules.html#sv-always-009>`_
* `sv_always_010 <sv_always_rules.html#sv-always-010>`_
* `sv_always_011 <sv_always_rules.html#sv-always-011>`_
* `sv_always_012 <sv_always_rules.html#sv-always-012>`_
* `sv_always_013 <sv_always_rules.html#sv-always-013>`_
* `sv_always_014 <sv_always_rules.html#sv-always-014>`_
* `sv_always_015 <sv_always_rules.html#sv-always-015>`_
* `sv_always_016 <sv_always_rules.html#sv-always-016>`_
* `sv_always_017 <sv_always_rules.html#sv-always-017>`_
* `sv_always_018 <sv_always_rules.html#sv-always-018>`_
* `sv_always_019 <sv_always_rules.html#sv-always-019>`_
* `sv_always_020 <sv_always_rules.html#sv-always-020>`_
* `sv_always_021 <sv_always_rules.html#sv-always-021>`_
* `sv_always_022 <sv_always_rules.html#sv-always-022>`_
* `sv_always_023 <sv_always_rules.html#sv-always-023>`_
* `sv_always_024 <sv_always_rules.html#sv-always-024>`_
* `sv_always_025 <sv_always_rules.html#sv-always-025>`_
* `sv_case_001 <sv_case_rules.html#sv-case-001>`_
* `sv_case_002 <sv_case_rules.html#sv-case-002>`_
* `sv_case_003 <sv_case_rules.html#sv-case-003>`_
* `sv_case_004 <sv_case_rules.html#sv-case-004>`_
* `sv_case_005 <sv_case_rules.html#sv-case-005>`_
* `sv_case_006 <sv_case_rules.html#sv-case-006>`_
* `sv_case_007 <sv_case_rules.html#sv-case-007>`_
* `sv_case_008 <sv_case_rules.html#sv-case-008>`_
* `sv_case_009 <sv_case_rules.html#sv-case-009>`_
* `sv_case_010 <sv_case_rules.html#sv-case-010>`_
* `sv_comment_001 <sv_comment_rules.html#sv-comment-001>`_
* `sv_comment_002 <sv_comment_rules.html#sv-comment-002>`_
* `sv_comment_003 <sv_comment_rules.html#sv-comment-003>`_
* `sv_comment_004 <sv_comment_rules.html#sv-comment-004>`_
* `sv_comment_005 <sv_comment_rules.html#sv-comment-005>`_
* `sv_declaration_001 <sv_declaration_rules.html#sv-declaration-001>`_
* `sv_declaration_002 <sv_declaration_rules.html#sv-declaration-002>`_
* `sv_declaration_003 <sv_declaration_rules.html#sv-declaration-003>`_
* `sv_dimension_001 <sv_dimension_rules.html#sv-dimension-001>`_
* `sv_dimension_002 <sv_dimension_rules.html#sv-dimension-002>`_
* `sv_dimension_003 <sv_dimension_rules.html#sv-dimension-003>`_
* `sv_dimension_004 <sv_dimension_rules.html#sv-dimension-004>`_
* `sv_file_001 <sv_file_rules.html#sv-file-001>`_
* `sv_file_002 <sv_file_rules.html#sv-file-002>`_
* `sv_file_003 <sv_file_rules.html#sv-file-003>`_
* `sv_file_004 <sv_file_rules.html#sv-file-004>`_
* `sv_file_005 <sv_file_rules.html#sv-file-005>`_
* `sv_file_006 <sv_file_rules.html#sv-file-006>`_
* `sv_file_007 <sv_file_rules.html#sv-file-007>`_
* `sv_function_003 <sv_function_rules.html#sv-function-003>`_
* `sv_function_004 <sv_function_rules.html#sv-function-004>`_
* `sv_function_005 <sv_function_rules.html#sv-function-005>`_
* `sv_function_006 <sv_function_rules.html#sv-function-006>`_
* `sv_function_007 <sv_function_rules.html#sv-function-007>`_
* `sv_function_008 <sv_function_rules.html#sv-function-008>`_
* `sv_function_009 <sv_function_rules.html#sv-function-009>`_
* `sv_function_010 <sv_function_rules.html#sv-function-010>`_
* `sv_function_011 <sv_function_rules.html#sv-function-011>`_
* `sv_generate_001 <sv_generate_rules.html#sv-generate-001>`_
* `sv_generate_002 <sv_generate_rules.html#sv-generate-002>`_
* `sv_generate_003 <sv_generate_rules.html#sv-generate-003>`_
* `sv_generate_005 <sv_generate_rules.html#sv-generate-005>`_
* `sv_lint_001 <sv_lint_rules.html#sv-lint-001>`_
* `sv_lint_002 <sv_lint_rules.html#sv-lint-002>`_
* `sv_lint_003 <sv_lint_rules.html#sv-lint-003>`_
* `sv_lint_004 <sv_lint_rules.html#sv-lint-004>`_
* `sv_lint_005 <sv_lint_rules.html#sv-lint-005>`_
* `sv_lint_006 <sv_lint_rules.html#sv-lint-006>`_
* `sv_lint_007 <sv_lint_rules.html#sv-lint-007>`_
* `sv_lint_008 <sv_lint_rules.html#sv-lint-008>`_
* `sv_lint_009 <sv_lint_rules.html#sv-lint-009>`_
* `sv_lint_010 <sv_lint_rules.html#sv-lint-010>`_
* `sv_lint_011 <sv_lint_rules.html#sv-lint-011>`_
* `sv_lint_012 <sv_lint_rules.html#sv-lint-012>`_
* `sv_lint_013 <sv_lint_rules.html#sv-lint-013>`_
* `sv_literal_002 <sv_literal_rules.html#sv-literal-002>`_
* `sv_literal_003 <sv_literal_rules.html#sv-literal-003>`_
* `sv_literal_004 <sv_literal_rules.html#sv-literal-004>`_
* `sv_literal_005 <sv_literal_rules.html#sv-literal-005>`_
* `sv_literal_006 <sv_literal_rules.html#sv-literal-006>`_
* `sv_literal_007 <sv_literal_rules.html#sv-literal-007>`_
* `sv_literal_008 <sv_literal_rules.html#sv-literal-008>`_
* `sv_literal_009 <sv_literal_rules.html#sv-literal-009>`_
* `sv_module_001 <sv_module_rules.html#sv-module-001>`_
* `sv_module_002 <sv_module_rules.html#sv-module-002>`_
* `sv_module_003 <sv_module_rules.html#sv-module-003>`_
* `sv_module_004 <sv_module_rules.html#sv-module-004>`_
* `sv_module_005 <sv_module_rules.html#sv-module-005>`_
* `sv_module_006 <sv_module_rules.html#sv-module-006>`_
* `sv_module_007 <sv_module_rules.html#sv-module-007>`_
* `sv_module_008 <sv_module_rules.html#sv-module-008>`_
* `sv_module_009 <sv_module_rules.html#sv-module-009>`_
* `sv_module_010 <sv_module_rules.html#sv-module-010>`_
* `sv_module_011 <sv_module_rules.html#sv-module-011>`_
* `sv_module_012 <sv_module_rules.html#sv-module-012>`_
* `sv_naming_001 <sv_naming_rules.html#sv-naming-001>`_
* `sv_naming_002 <sv_naming_rules.html#sv-naming-002>`_
* `sv_naming_003 <sv_naming_rules.html#sv-naming-003>`_
* `sv_naming_004 <sv_naming_rules.html#sv-naming-004>`_
* `sv_naming_005 <sv_naming_rules.html#sv-naming-005>`_
* `sv_naming_006 <sv_naming_rules.html#sv-naming-006>`_
* `sv_naming_007 <sv_naming_rules.html#sv-naming-007>`_
* `sv_naming_008 <sv_naming_rules.html#sv-naming-008>`_
* `sv_naming_009 <sv_naming_rules.html#sv-naming-009>`_
* `sv_naming_010 <sv_naming_rules.html#sv-naming-010>`_
* `sv_naming_011 <sv_naming_rules.html#sv-naming-011>`_
* `sv_naming_012 <sv_naming_rules.html#sv-naming-012>`_
* `sv_naming_013 <sv_naming_rules.html#sv-naming-013>`_
* `sv_naming_014 <sv_naming_rules.html#sv-naming-014>`_
* `sv_naming_015 <sv_naming_rules.html#sv-naming-015>`_
* `sv_naming_016 <sv_naming_rules.html#sv-naming-016>`_
* `sv_naming_017 <sv_naming_rules.html#sv-naming-017>`_
* `sv_statement_001 <sv_statement_rules.html#sv-statement-001>`_
* `sv_statement_004 <sv_statement_rules.html#sv-statement-004>`_
* `sv_statement_005 <sv_statement_rules.html#sv-statement-005>`_
* `sv_statement_006 <sv_statement_rules.html#sv-statement-006>`_
* `sv_statement_007 <sv_statement_rules.html#sv-statement-007>`_
* `sv_statement_008 <sv_statement_rules.html#sv-statement-008>`_
* `sv_statement_009 <sv_statement_rules.html#sv-statement-009>`_
* `sv_statement_010 <sv_statement_rules.html#sv-statement-010>`_
* `sv_statement_011 <sv_statement_rules.html#sv-statement-011>`_
* `sv_statement_012 <sv_statement_rules.html#sv-statement-012>`_
* `sv_statement_013 <sv_statement_rules.html#sv-statement-013>`_
* `sv_statement_014 <sv_statement_rules.html#sv-statement-014>`_
* `sv_statement_015 <sv_statement_rules.html#sv-statement-015>`_
* `sv_statement_016 <sv_statement_rules.html#sv-statement-016>`_
* `sv_statement_017 <sv_statement_rules.html#sv-statement-017>`_
* `sv_statement_018 <sv_statement_rules.html#sv-statement-018>`_
* `sv_statement_019 <sv_statement_rules.html#sv-statement-019>`_
* `sv_statement_020 <sv_statement_rules.html#sv-statement-020>`_
* `sv_statement_021 <sv_statement_rules.html#sv-statement-021>`_
* `sv_statement_022 <sv_statement_rules.html#sv-statement-022>`_
* `sv_statement_023 <sv_statement_rules.html#sv-statement-023>`_
* `sv_statement_024 <sv_statement_rules.html#sv-statement-024>`_
* `sv_statement_025 <sv_statement_rules.html#sv-statement-025>`_
* `sv_statement_026 <sv_statement_rules.html#sv-statement-026>`_
* `sv_statement_027 <sv_statement_rules.html#sv-statement-027>`_
* `sv_statement_028 <sv_statement_rules.html#sv-statement-028>`_
* `sv_statement_029 <sv_statement_rules.html#sv-statement-029>`_
* `sv_statement_030 <sv_statement_rules.html#sv-statement-030>`_
* `sv_statement_031 <sv_statement_rules.html#sv-statement-031>`_
* `sv_statement_032 <sv_statement_rules.html#sv-statement-032>`_
* `sv_statement_033 <sv_statement_rules.html#sv-statement-033>`_
* `sv_statement_034 <sv_statement_rules.html#sv-statement-034>`_
* `sv_syntax_001 <sv_syntax_rules.html#sv-syntax-001>`_
* `sv_typedef_001 <sv_typedef_rules.html#sv-typedef-001>`_
* `sv_typedef_002 <sv_typedef_rules.html#sv-typedef-002>`_
