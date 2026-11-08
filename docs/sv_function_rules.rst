.. include:: includes.rst

Verilog and SystemVerilog Function Rules
----------------------------------------

sv_function_001
###############

|phase_1| |error| |structure|

Alias: :code:`sv_function_explicit_function_lifetime`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks that functions outside classes are declared automatic or static, as Verible's
explicit-function-lifetime rule does; the fix adds automatic.

**Violation**

.. code-block:: systemverilog

   function logic parity(input logic [7:0] data);

**Fix**

.. code-block:: systemverilog

   function automatic logic parity(input logic [7:0] data);

sv_function_002
###############

|phase_1| |error| |structure|

Alias: :code:`sv_function_explicit_task_lifetime`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks that tasks outside classes are declared automatic or static, as Verible's
explicit-task-lifetime rule does; the fix adds automatic.

**Violation**

.. code-block:: systemverilog

   task wait_cycles(input int n);

**Fix**

.. code-block:: systemverilog

   task automatic wait_cycles(input int n);

sv_function_003
###############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_function_explicit_function_task_parameter_type`

This rule checks that the arguments of functions and tasks are declared with a type, as Verible's
explicit-function-task-parameter-type rule does.

**Violation**

.. code-block:: systemverilog

   function automatic logic parity(input data);

**Fix**

.. code-block:: systemverilog

   function automatic logic parity(input logic [7:0] data);

sv_function_004
###############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`sv_function_nonblocking_assignment`

This rule checks for nonblocking assignments (<=) in functions, as the STARC guide asks (2.1.2.2). Methods
of classes, such as the drivers of a testbench writing to a virtual interface, are not checked.

**Violation**

.. code-block:: systemverilog

   function automatic logic f(input logic a);
       f <= a;

**Fix**

.. code-block:: systemverilog

   function automatic logic f(input logic a);
       f = a;

sv_function_005
###############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_function_no_tasks`

This rule checks for tasks in design code, as the STARC guide asks (2.1.2.4): use functions. It is disabled
by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   task automatic load(input int value);

**Fix**

.. code-block:: systemverilog

   function automatic int load(input int value);

sv_function_006
###############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_function_reads_arguments`

This rule checks that a function reads only its arguments, its own variables and constants, not the signals of
the module, as the STARC guide asks (2.1.2.3). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   function automatic logic gate(input logic x);
       gate = x & enable;
   endfunction

**Fix**

.. code-block:: systemverilog

   function automatic logic gate(input logic x, input logic en);
       gate = x & en;
   endfunction

sv_function_007
###############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_function_assigns_no_signals`

This rule checks that a function assigns only its own variables and its result, not the signals of the module, as
the STARC guide asks (2.1.3.5). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   function automatic logic gate(input logic x);
       flag = x;
       gate = x;
   endfunction

**Fix**

Return the value and assign it where the function is called.

sv_function_008
###############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_function_no_clock_in_task`

This rule checks for edge event controls, such as @(posedge clk), in tasks, as the STARC guide asks (2.1.2.5). It
is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   task automatic send(input logic [7:0] d);
       @(posedge clk);
       data = d;
   endtask

**Fix**

Move the timing to the always block that calls the task, or use a function.

sv_function_009
###############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_function_ends_with_result`

This rule checks that a function ends by assigning its result, with a return statement or an assignment to its
name, as the STARC guide recommends (2.1.3.4). Functions returning void and methods of classes are not checked.
It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   function automatic logic parity(input logic [7:0] data);
       parity = ^data;
       $display("parity");
   endfunction

**Fix**

.. code-block:: systemverilog

   function automatic logic parity(input logic [7:0] data);
       $display("parity");
       parity = ^data;
   endfunction

sv_function_010
###############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_function_task_outputs`

This rule checks for output and inout arguments of tasks, as the STARC guide recommends (4.2.3.2) for the tasks
that drive test stimulus. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   task automatic send(input logic [7:0] data, output logic done);

**Fix**

.. code-block:: systemverilog

   task automatic send(input logic [7:0] data);

sv_function_011
###############

|phase_1| |disabled| |error| |unfixable| |structure|

Alias: :code:`sv_function_complete_branches`

This rule checks that the if and case statements of a function cover every condition, with an else or a default,
as the STARC guide asks (2.1.1.2). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   function automatic logic f(input logic a);
       if (a) f = 1'b1;
   endfunction

**Fix**

.. code-block:: systemverilog

   function automatic logic f(input logic a);
       if (a) f = 1'b1;
       else f = 1'b0;
   endfunction
