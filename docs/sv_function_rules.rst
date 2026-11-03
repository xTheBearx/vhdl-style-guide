.. include:: includes.rst

SystemVerilog Function Rules
----------------------------

sv_function_001
###############

|phase_1| |error| |structure|

Alias: :code:`sv_function_explicit_function_lifetime`

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
