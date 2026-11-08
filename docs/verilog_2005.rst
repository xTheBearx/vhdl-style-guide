.. _verilog_2005:

Verilog-2005 files
==================

Files whose names end in :code:`.v` or :code:`.vh` are read as Verilog-2005 (IEEE 1364-2005), and
:code:`.sv` and :code:`.svh` files as SystemVerilog, see :doc:`systemverilog`. In a Verilog file the names that are
keywords only in SystemVerilog, such as :code:`logic`, :code:`bit`, :code:`int` and :code:`byte`, are names, as in
Verilog-2005, and SystemVerilog constructs, such as always_comb, are syntax errors (:code:`sv_syntax_001`).

The rules for SystemVerilog check Verilog files too, but for those that need SystemVerilog constructs: a rule that
asks for always_comb, or checks enum types, end labels or packages, has nothing to ask of a Verilog file, or would
ask for code Verilog-2005 cannot have, and is not applied to it. A rule that applies to both gives a Verilog file
advice it can follow, such as always @* instead of always_comb, and its fix never puts SystemVerilog into a Verilog
file. The rule sets work the same way: a check that only a SystemVerilog only rule implements does not apply to
Verilog files, and the coverage tables of :doc:`lint` mark those rules. Verilator, when it lints the files of a run,
and the Yosys reader of design analysis read Verilog files as Verilog-2005 too.

A project that writes SystemVerilog in :code:`.v` files reads them as SystemVerilog, with all the rules:

.. code-block:: yaml

   systemverilog:
     v_files: systemverilog   # verilog, the default, reads .v and .vh files as Verilog-2005

Rules
-----

Each rule for SystemVerilog, :code:`sv_` in its name, applies to Verilog files as follows:

* **Both**: the rule checks Verilog and SystemVerilog files alike.
* **Both, Verilog advice**: the rule checks both, and gives Verilog files advice, or checks constructs, that
  Verilog-2005 has.
* **SystemVerilog only**: the rule is not applied to Verilog files; its documentation says so.

Of the 226 rules, 204 apply to both, 7 to both with Verilog advice and 15 to SystemVerilog only.

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Rule
     - Verilog files
     - Reason
   * - :code:`sv_alignment_001`
     - Both
     - Port declarations of ANSI headers, as Verilog-2005 writes them
   * - :code:`sv_alignment_002`
     - Both
     - Named port connections: the same in Verilog-2005
   * - :code:`sv_alignment_003`
     - Both
     - Named parameter assignments: the same in Verilog-2005
   * - :code:`sv_alignment_004`
     - Both
     - Reg, wire and integer declarations: the same in Verilog-2005
   * - :code:`sv_alignment_005`
     - Both
     - Continuous assignments and assignment statements: the same in Verilog-2005
   * - :code:`sv_alignment_006`
     - Both
     - Parameter and localparam declarations: the same in Verilog-2005
   * - :code:`sv_alignment_007`
     - Both
     - Case items: the same in Verilog-2005
   * - :code:`sv_alignment_008`
     - SystemVerilog only
     - Aligns the members of structs and unions, which Verilog-2005 does not have
   * - :code:`sv_alignment_009`
     - Both
     - The types of ports, such as reg or wire, after their directions: the same in Verilog-2005
   * - :code:`sv_alignment_010`
     - Both
     - Ranges of ports and declarations: the same in Verilog-2005
   * - :code:`sv_alignment_011`
     - Both
     - The inside of ranges: the same in Verilog-2005
   * - :code:`sv_always_001`
     - SystemVerilog only
     - Asks for always_comb, which Verilog-2005 does not have
   * - :code:`sv_always_002`
     - Both, Verilog advice
     - Checks the combinational always blocks of Verilog files, always @* and lists without edges, as they have no always_comb
   * - :code:`sv_always_003`
     - Both
     - Nonblocking assignments in always blocks clocked on an edge: the same in Verilog-2005
   * - :code:`sv_always_004`
     - Both
     - Mixed assignments in any always block: the same in Verilog-2005
   * - :code:`sv_always_005`
     - Both
     - Event controls of always blocks: the same in Verilog-2005
   * - :code:`sv_always_006`
     - Both
     - If and case statements of always blocks: the same in Verilog-2005
   * - :code:`sv_always_007`
     - Both
     - Edges of always blocks: the same in Verilog-2005
   * - :code:`sv_always_008`
     - Both
     - Assignments of always blocks: the same in Verilog-2005
   * - :code:`sv_always_009`
     - Both
     - Length of always blocks: the same in Verilog-2005
   * - :code:`sv_always_010`
     - Both
     - Sensitivity lists: the same in Verilog-2005
   * - :code:`sv_always_011`
     - Both
     - Sensitivity lists of combinational always blocks: the same in Verilog-2005
   * - :code:`sv_always_012`
     - Both
     - Clocks of edge triggered always blocks: the same in Verilog-2005
   * - :code:`sv_always_013`
     - Both
     - Edges of asynchronous resets: the same in Verilog-2005
   * - :code:`sv_always_014`
     - Both
     - Events of edge triggered always blocks: the same in Verilog-2005
   * - :code:`sv_always_015`
     - Both
     - Edges and tests of asynchronous resets: the same in Verilog-2005
   * - :code:`sv_always_016`
     - Both
     - Reset branches of always blocks: the same in Verilog-2005
   * - :code:`sv_always_017`
     - Both
     - Assignments in sequences of statements: the same in Verilog-2005
   * - :code:`sv_always_018`
     - Both
     - Assignments of always and initial blocks: the same in Verilog-2005
   * - :code:`sv_always_019`
     - Both
     - Constant assignments of edge triggered always blocks: the same in Verilog-2005
   * - :code:`sv_always_020`
     - Both
     - For loops of always blocks with a reset: the same in Verilog-2005
   * - :code:`sv_always_021`
     - Both
     - Synchronous resets of edge triggered always blocks: the same in Verilog-2005
   * - :code:`sv_always_022`
     - Both
     - Uses of clocks as data: the same in Verilog-2005
   * - :code:`sv_always_023`
     - Both, Verilog advice
     - Resets made by continuous assignments and combinational blocks: always_comb, or always @* and lists without edges in Verilog files
   * - :code:`sv_always_024`
     - Both
     - Function calls in reset branches: the same in Verilog-2005
   * - :code:`sv_always_025`
     - SystemVerilog only
     - Checks always_latch blocks, which Verilog-2005 does not have
   * - :code:`sv_always_026`
     - Both
     - Delays of nonblocking assignments, as q <= #1 d: the same in Verilog-2005
   * - :code:`sv_always_027`
     - Both
     - Registers of edge triggered always blocks: the same in Verilog-2005
   * - :code:`sv_always_028`
     - Both
     - Resets of edge triggered always blocks: the same in Verilog-2005
   * - :code:`sv_always_029`
     - Both
     - Named begin-end blocks: the same in Verilog-2005
   * - :code:`sv_blank_line_001`
     - Both
     - Blank lines only: the same in Verilog-2005
   * - :code:`sv_case_001`
     - Both
     - Default items; the exemption of unique case never applies to Verilog
   * - :code:`sv_case_002`
     - Both
     - Place of the default item: the same in Verilog-2005
   * - :code:`sv_case_003`
     - Both
     - Case selectors: the same in Verilog-2005
   * - :code:`sv_case_004`
     - Both
     - Number of case items: the same in Verilog-2005
   * - :code:`sv_case_005`
     - Both
     - Casex and casez, which Verilog-2005 has
   * - :code:`sv_case_006`
     - Both
     - Case labels: the same in Verilog-2005
   * - :code:`sv_case_007`
     - Both
     - Case selectors: the same in Verilog-2005
   * - :code:`sv_case_008`
     - Both
     - State encodings, named with parameters in Verilog
   * - :code:`sv_case_009`
     - Both
     - Number of states: the same in Verilog-2005
   * - :code:`sv_case_010`
     - Both
     - State machines of a module: the same in Verilog-2005
   * - :code:`sv_case_011`
     - Both
     - Widths of case tables, from slang's elaboration: the same in Verilog-2005
   * - :code:`sv_case_012`
     - Both
     - Wildcards of casex and casez items: the same in Verilog-2005
   * - :code:`sv_comment_001`
     - Both
     - Comments only: the same in Verilog-2005
   * - :code:`sv_comment_002`
     - Both
     - Comments only: the same in Verilog-2005
   * - :code:`sv_comment_003`
     - Both
     - Comments only: the same in Verilog-2005
   * - :code:`sv_comment_004`
     - Both
     - Comments of ports and signals: the same in Verilog-2005
   * - :code:`sv_comment_005`
     - Both
     - Comments only: the same in Verilog-2005
   * - :code:`sv_comment_006`
     - Both
     - Comments only: the same in Verilog-2005
   * - :code:`sv_comment_007`
     - Both
     - Comments only: the same in Verilog-2005
   * - :code:`sv_comment_008`
     - Both
     - Comments, read as SystemVerilog, which holds Verilog-2005: the same in Verilog-2005
   * - :code:`sv_declaration_001`
     - Both, Verilog advice
     - Verilog-2005 can type a parameter only as integer, real, realtime or time: a range or signed counts as a type, and the advice names integer or a range
   * - :code:`sv_declaration_002`
     - Both
     - Default values of parameters: the same in Verilog-2005
   * - :code:`sv_declaration_003`
     - Both
     - Declarations of several signals: the same in Verilog-2005
   * - :code:`sv_declaration_004`
     - Both
     - Initial values of variables, such as reg q = 0: the same in Verilog-2005
   * - :code:`sv_dimension_001`
     - Both
     - Ranges of vectors: the same in Verilog-2005
   * - :code:`sv_dimension_002`
     - Both, Verilog advice
     - Verilog-2005 cannot write [N]: the advice is [0:N-1]
   * - :code:`sv_dimension_003`
     - Both
     - Ranges of vectors: the same in Verilog-2005
   * - :code:`sv_dimension_004`
     - Both
     - Ranges of ports: the same in Verilog-2005
   * - :code:`sv_file_001`
     - Both
     - File names of modules: the same in Verilog-2005
   * - :code:`sv_file_002`
     - SystemVerilog only
     - Checks packages, which Verilog-2005 does not have
   * - :code:`sv_file_003`
     - Both
     - Modules of a file: the same in Verilog-2005
   * - :code:`sv_file_004`
     - Both
     - Include directives: the same in Verilog-2005
   * - :code:`sv_file_005`
     - Both
     - Include directives: the same in Verilog-2005
   * - :code:`sv_file_006`
     - Both, Verilog advice
     - Verilog-2005 has no timeunit: the advice is a timescale directive
   * - :code:`sv_file_007`
     - Both
     - File names of testbenches: the same in Verilog-2005
   * - :code:`sv_function_001`
     - SystemVerilog only
     - Verilog-2005 cannot declare a function static, and one without automatic is static, so its lifetime is never unclear; the fix would add automatic
   * - :code:`sv_function_002`
     - SystemVerilog only
     - As sv_function_001, for tasks
   * - :code:`sv_function_003`
     - Both
     - Types of ANSI function and task arguments, such as reg [7:0] or integer: the same in Verilog-2005
   * - :code:`sv_function_004`
     - Both
     - Nonblocking assignments in functions: the same in Verilog-2005
   * - :code:`sv_function_005`
     - Both
     - Tasks in design code: the same in Verilog-2005
   * - :code:`sv_function_006`
     - Both
     - What functions read: the same in Verilog-2005
   * - :code:`sv_function_007`
     - Both
     - What functions assign: the same in Verilog-2005
   * - :code:`sv_function_008`
     - Both
     - Edges in tasks: the same in Verilog-2005
   * - :code:`sv_function_009`
     - Both
     - The last statement of functions, an assignment to their name in Verilog
   * - :code:`sv_function_010`
     - Both
     - Output arguments of tasks: the same in Verilog-2005
   * - :code:`sv_function_011`
     - Both
     - If and case statements of functions: the same in Verilog-2005
   * - :code:`sv_generate_001`
     - Both
     - Labels of generate blocks, which Verilog-2005 has
   * - :code:`sv_generate_002`
     - Both
     - Labels of generate blocks: the same in Verilog-2005
   * - :code:`sv_generate_003`
     - Both
     - Begin-end blocks directly in generate regions, which Verilog-2005 no longer allows
   * - :code:`sv_generate_004`
     - Both
     - Generate and endgenerate, optional in Verilog-2005: the fix keeps Verilog-2005
   * - :code:`sv_generate_005`
     - SystemVerilog only
     - Verilog-2005 cannot declare a genvar in its for loop
   * - :code:`sv_indent_001`
     - Both
     - Indentation only: the same in Verilog-2005
   * - :code:`sv_indent_002`
     - Both
     - Indentation only: the same in Verilog-2005
   * - :code:`sv_indent_003`
     - Both
     - Indentation of directives: the same in Verilog-2005
   * - :code:`sv_indent_004`
     - Both
     - Indentation of call arguments; assignment patterns and constraints do not occur in Verilog
   * - :code:`sv_label_001`
     - SystemVerilog only
     - Checks end labels, which Verilog-2005 does not have
   * - :code:`sv_lint_001`
     - Both
     - Slang's warnings, from the file read as Verilog-2005
   * - :code:`sv_lint_002`
     - Both
     - Slang's warnings: the same in Verilog-2005
   * - :code:`sv_lint_003`
     - Both
     - Slang's warnings: the same in Verilog-2005
   * - :code:`sv_lint_004`
     - Both
     - Slang's warnings: the same in Verilog-2005
   * - :code:`sv_lint_005`
     - Both
     - Slang's warnings: the same in Verilog-2005
   * - :code:`sv_lint_006`
     - Both
     - Slang's warnings: the same in Verilog-2005
   * - :code:`sv_lint_007`
     - Both
     - Slang's warnings: the same in Verilog-2005
   * - :code:`sv_lint_008`
     - Both, Verilog advice
     - The advice of a Verilog file is always @* instead of always_comb
   * - :code:`sv_lint_009`
     - Both
     - Slang's warnings: the same in Verilog-2005
   * - :code:`sv_lint_010`
     - Both
     - Slang's warnings: the same in Verilog-2005
   * - :code:`sv_lint_011`
     - Both
     - Verilator's warnings, with the file read as Verilog-2005
   * - :code:`sv_lint_012`
     - Both
     - Verilator's warnings: the same in Verilog-2005
   * - :code:`sv_lint_013`
     - Both
     - Verilator's warnings: the same in Verilog-2005
   * - :code:`sv_lint_014`
     - Both
     - Parameters of instances: the same in Verilog-2005
   * - :code:`sv_lint_015`
     - Both
     - Parameter names of modules: the same in Verilog-2005
   * - :code:`sv_lint_016`
     - Both
     - Macros of a run: the same in Verilog-2005
   * - :code:`sv_literal_001`
     - Both
     - Binary literals: the same in Verilog-2005
   * - :code:`sv_literal_002`
     - Both
     - Sized literals: the same in Verilog-2005
   * - :code:`sv_literal_003`
     - Both
     - Bases of parameter values: the same in Verilog-2005
   * - :code:`sv_literal_004`
     - Both
     - Widths of literals: the same in Verilog-2005
   * - :code:`sv_literal_005`
     - Both
     - Comparisons with x or z: the same in Verilog-2005
   * - :code:`sv_literal_006`
     - Both
     - X and z in literals: the same in Verilog-2005
   * - :code:`sv_literal_007`
     - Both
     - Widths of constants in conditions: the same in Verilog-2005
   * - :code:`sv_literal_008`
     - Both
     - Bases of numbers: the same in Verilog-2005
   * - :code:`sv_literal_009`
     - Both
     - Negative constants: the same in Verilog-2005
   * - :code:`sv_literal_010`
     - Both
     - Numbers in the code: the same in Verilog-2005
   * - :code:`sv_module_001`
     - Both
     - Begin-end blocks directly in modules: the same in Verilog-2005
   * - :code:`sv_module_002`
     - Both
     - Defparam, which Verilog-2005 has
   * - :code:`sv_module_003`
     - Both
     - Port connections by position: the same in Verilog-2005
   * - :code:`sv_module_004`
     - Both
     - Outputs driven by constants: the same in Verilog-2005
   * - :code:`sv_module_005`
     - Both
     - Gate primitives: the same in Verilog-2005
   * - :code:`sv_module_006`
     - Both
     - Text macros of constants: the same in Verilog-2005
   * - :code:`sv_module_007`
     - Both
     - Order of ports: the same in Verilog-2005
   * - :code:`sv_module_008`
     - Both
     - Text macros in text macros: the same in Verilog-2005
   * - :code:`sv_module_009`
     - Both
     - Number of ports: the same in Verilog-2005
   * - :code:`sv_module_010`
     - SystemVerilog only
     - Checks always_latch blocks, which Verilog-2005 does not have
   * - :code:`sv_module_011`
     - Both
     - Tri-state buffers: the same in Verilog-2005
   * - :code:`sv_module_012`
     - Both
     - Vendor primitives: the same in Verilog-2005
   * - :code:`sv_module_013`
     - Both
     - Text macros of modules: the same in Verilog-2005
   * - :code:`sv_module_014`
     - Both
     - Synchronous resets: the same in Verilog-2005
   * - :code:`sv_module_015`
     - Both
     - Logic in modules that connect instances: the same in Verilog-2005
   * - :code:`sv_module_016`
     - Both
     - Order of port connections: the same in Verilog-2005
   * - :code:`sv_module_017`
     - Both, Verilog advice
     - Outputs driven by continuous assignments and combinational blocks: always_comb, or always @* and lists without edges in Verilog files
   * - :code:`sv_naming_001`
     - Both
     - Parameter names: the same in Verilog-2005
   * - :code:`sv_naming_002`
     - SystemVerilog only
     - Checks enum types, which Verilog-2005 does not have
   * - :code:`sv_naming_003`
     - SystemVerilog only
     - Checks struct and union types, which Verilog-2005 does not have
   * - :code:`sv_naming_004`
     - SystemVerilog only
     - Checks interfaces, which Verilog-2005 does not have
   * - :code:`sv_naming_005`
     - Both
     - Macro names: the same in Verilog-2005
   * - :code:`sv_naming_006`
     - SystemVerilog only
     - Checks constraints, which Verilog-2005 does not have
   * - :code:`sv_naming_007`
     - Both
     - Parameter names: the same in Verilog-2005
   * - :code:`sv_naming_008`
     - Both
     - Signal and port names: the same in Verilog-2005
   * - :code:`sv_naming_009`
     - Both
     - Characters of names: the same in Verilog-2005
   * - :code:`sv_naming_010`
     - Both
     - VHDL keywords as names: the same in Verilog-2005
   * - :code:`sv_naming_011`
     - Both
     - Power net prefixes: the same in Verilog-2005
   * - :code:`sv_naming_012`
     - Both
     - Names differing in case: the same in Verilog-2005
   * - :code:`sv_naming_013`
     - Both
     - Lengths of names: the same in Verilog-2005
   * - :code:`sv_naming_014`
     - Both
     - Underscores in names: the same in Verilog-2005
   * - :code:`sv_naming_015`
     - Both
     - Instance names: the same in Verilog-2005
   * - :code:`sv_naming_016`
     - Both
     - Port and signal names: the same in Verilog-2005
   * - :code:`sv_naming_017`
     - Both
     - Names of active low resets: the same in Verilog-2005
   * - :code:`sv_naming_018`
     - Both
     - Names of modules and ports: the same in Verilog-2005
   * - :code:`sv_naming_019`
     - Both
     - Names of library cells: the same in Verilog-2005
   * - :code:`sv_naming_020`
     - Both
     - Names of clocks and resets: the same in Verilog-2005
   * - :code:`sv_statement_001`
     - Both
     - Begin-end blocks: the same in Verilog-2005
   * - :code:`sv_statement_002`
     - Both
     - Null statements: the same in Verilog-2005
   * - :code:`sv_statement_003`
     - Both
     - Statements per line: the same in Verilog-2005
   * - :code:`sv_statement_004`
     - Both
     - Initial blocks: the same in Verilog-2005
   * - :code:`sv_statement_005`
     - Both
     - Fork-join, which Verilog-2005 has
   * - :code:`sv_statement_006`
     - Both
     - Empty branches: the same in Verilog-2005
   * - :code:`sv_statement_007`
     - Both
     - Nested conditional operators: the same in Verilog-2005
   * - :code:`sv_statement_008`
     - Both
     - Nesting of if statements: the same in Verilog-2005
   * - :code:`sv_statement_009`
     - Both
     - Loop variables: the same in Verilog-2005
   * - :code:`sv_statement_010`
     - Both
     - If chains of combinational always blocks: the same in Verilog-2005
   * - :code:`sv_statement_011`
     - Both
     - Arithmetic in if conditions: the same in Verilog-2005
   * - :code:`sv_statement_012`
     - Both
     - Mixed && and ||: the same in Verilog-2005
   * - :code:`sv_statement_013`
     - Both
     - Operands of / and %: the same in Verilog-2005
   * - :code:`sv_statement_014`
     - Both
     - Length of fork-join blocks: the same in Verilog-2005
   * - :code:`sv_statement_015`
     - Both
     - Delays: the same in Verilog-2005
   * - :code:`sv_statement_016`
     - Both
     - Delays of continuous assignments and nets: the same in Verilog-2005
   * - :code:`sv_statement_017`
     - Both
     - Enables of tri-state buffers: the same in Verilog-2005
   * - :code:`sv_statement_018`
     - Both
     - Tests of tri-state signals: the same in Verilog-2005
   * - :code:`sv_statement_019`
     - Both
     - Repeated branches of if chains: the same in Verilog-2005
   * - :code:`sv_statement_020`
     - Both
     - Repeated conditions of if chains: the same in Verilog-2005
   * - :code:`sv_statement_021`
     - Both
     - Parentheses of arithmetic: the same in Verilog-2005
   * - :code:`sv_statement_022`
     - Both
     - Arithmetic in conditional operators: the same in Verilog-2005
   * - :code:`sv_statement_023`
     - Both
     - Indexes: the same in Verilog-2005
   * - :code:`sv_statement_024`
     - Both
     - Nonblocking assignments in initial blocks: the same in Verilog-2005
   * - :code:`sv_statement_025`
     - Both
     - $fdisplay: the same in Verilog-2005
   * - :code:`sv_statement_026`
     - Both
     - Logical operators: the same in Verilog-2005
   * - :code:`sv_statement_027`
     - Both
     - Nested ifs: the same in Verilog-2005
   * - :code:`sv_statement_028`
     - Both
     - Tests of signals that may be x: the same in Verilog-2005
   * - :code:`sv_statement_029`
     - Both
     - Computation in for loops: the same in Verilog-2005
   * - :code:`sv_statement_030`
     - Both
     - Delays computed in always blocks: the same in Verilog-2005
   * - :code:`sv_statement_031`
     - Both
     - Clocks toggled in procedural blocks: the same in Verilog-2005
   * - :code:`sv_statement_032`
     - Both
     - Edge events in initial blocks and tasks: the same in Verilog-2005
   * - :code:`sv_statement_033`
     - Both
     - Simulation tasks in modules with ports: the same in Verilog-2005
   * - :code:`sv_statement_034`
     - Both
     - Delays in testbenches: the same in Verilog-2005
   * - :code:`sv_statement_035`
     - Both
     - Widths of logical operands, from slang's elaboration: the same in Verilog-2005
   * - :code:`sv_statement_036`
     - Both
     - Widths of conditions: the same in Verilog-2005
   * - :code:`sv_statement_037`
     - Both
     - Widths of compared operands: the same in Verilog-2005
   * - :code:`sv_statement_038`
     - Both
     - Widths of assigned values: the same in Verilog-2005
   * - :code:`sv_statement_039`
     - Both
     - Widths of sums and products: the same in Verilog-2005
   * - :code:`sv_statement_040`
     - Both
     - Widths of dividers: the same in Verilog-2005
   * - :code:`sv_statement_041`
     - Both
     - Widths of multipliers: the same in Verilog-2005
   * - :code:`sv_statement_042`
     - Both
     - Reductions in wider contexts: the same in Verilog-2005
   * - :code:`sv_statement_043`
     - Both
     - Comparisons of integers with vectors: the same in Verilog-2005
   * - :code:`sv_statement_044`
     - Both
     - Priority logic in loops: the same in Verilog-2005
   * - :code:`sv_statement_045`
     - Both
     - Iterations of loops: the same in Verilog-2005
   * - :code:`sv_statement_046`
     - Both
     - Mixed signedness: the same in Verilog-2005
   * - :code:`sv_statement_047`
     - Both
     - Arithmetic operators per line: the same in Verilog-2005
   * - :code:`sv_statement_048`
     - Both
     - Expressions of both branches of an if: the same in Verilog-2005
   * - :code:`sv_statement_049`
     - Both
     - Stimulus at clock edges: the same in Verilog-2005
   * - :code:`sv_statement_050`
     - Both
     - Repeated expressions: the same in Verilog-2005
   * - :code:`sv_statement_051`
     - Both
     - Continuous assignments: the same in Verilog-2005
   * - :code:`sv_syntax_001`
     - Both
     - Syntax errors of the file in its language: in a Verilog file, SystemVerilog constructs are errors
   * - :code:`sv_typedef_001`
     - SystemVerilog only
     - Checks enum types, which Verilog-2005 does not have
   * - :code:`sv_typedef_002`
     - SystemVerilog only
     - Checks struct and union types, which Verilog-2005 does not have
   * - :code:`sv_whitespace_001`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_002`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_003`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_004`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_005`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_006`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_007`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_008`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_009`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_010`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_011`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_012`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_013`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_014`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_015`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_016`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_017`
     - Both
     - Whitespace only: the same in Verilog-2005
   * - :code:`sv_whitespace_018`
     - Both
     - Whitespace only: the same in Verilog-2005
