.. include:: includes.rst

SystemVerilog Whitespace Rules
------------------------------

sv_whitespace_001
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_before_comma`

This rule checks for no space before a comma, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   foo(a , b);

**Fix**

.. code-block:: systemverilog

   foo(a, b);

sv_whitespace_002
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_after_comma`

This rule checks for at least one space after a comma, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   foo(a,b);

**Fix**

.. code-block:: systemverilog

   foo(a, b);

sv_whitespace_003
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_before_semicolon`

This rule checks for no space before a semicolon, except one after the colon of an empty case item (default:
;), as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   assign a = b ;

**Fix**

.. code-block:: systemverilog

   assign a = b;

sv_whitespace_004
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_after_semicolon`

This rule checks for at least one space after a semicolon followed by more code on the line, as in a for
loop, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   for (int i = 0;i < 4;i++) begin

**Fix**

.. code-block:: systemverilog

   for (int i = 0; i < 4; i++) begin

sv_whitespace_005
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_control_keyword`

This rule checks for one space between if, for, foreach, while, repeat, wait or case and its opening
parenthesis, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   if(valid) begin

**Fix**

.. code-block:: systemverilog

   if (valid) begin

sv_whitespace_006
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_event_control`

This rule checks for no space between @ and its parenthesis or :code:`*`, and one space between an always keyword
and @, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   always_ff@ (posedge clk_i) begin

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i) begin

sv_whitespace_007
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_hash`

This rule checks for no space after # in parameter lists and delays, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   fifo # (.Depth(4)) u_fifo (

**Fix**

.. code-block:: systemverilog

   fifo #(.Depth(4)) u_fifo (

sv_whitespace_008
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_binary_operator`

This rule checks for at least one space around binary and assignment operators and the ? and : of a
conditional expression, except in the brackets of a select or a dimension, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   assign sum=a+b;

**Fix**

.. code-block:: systemverilog

   assign sum = a + b;

sv_whitespace_009
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_unary_operator`

This rule checks for no space between a unary operator and its operand, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   assign ready = ~ busy;

**Fix**

.. code-block:: systemverilog

   assign ready = ~busy;

sv_whitespace_010
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_increment`

This rule checks for no space between ++ or -- and its operand, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   count ++;

**Fix**

.. code-block:: systemverilog

   count++;

sv_whitespace_011
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_call`

This rule checks for no space between the name of a function, task or system task and its argument list, as
Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   $display ("done");

**Fix**

.. code-block:: systemverilog

   $display("done");

sv_whitespace_012
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_select`

This rule checks for no space between a name and the bracket of a select, such as data[0]; the packed
dimensions of a type, as in data_t [1:0], keep their space, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   assign first = data [0];

**Fix**

.. code-block:: systemverilog

   assign first = data[0];

sv_whitespace_013
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_label_colon`

This rule checks for one space on each side of the colon of a block label, such as begin : name and end :
name, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   end: gen_stage

**Fix**

.. code-block:: systemverilog

   end : gen_stage

sv_whitespace_014
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_case_item_colon`

This rule checks for no space before the colon of a case item and at least one after it, as Verible's
formatter does.

**Violation**

.. code-block:: systemverilog

   Idle : state_d = Busy;

**Fix**

.. code-block:: systemverilog

   Idle: state_d = Busy;

sv_whitespace_015
#################

|phase_2| |error| |whitespace|

Alias: :code:`sv_whitespace_trailing_comment`

This rule checks for at least **spaces** spaces, 2 by default, between code and a comment at the end of its
line, as Verible's formatter does.

**Violation**

.. code-block:: systemverilog

   logic valid; // the data is valid

**Fix**

.. code-block:: systemverilog

   logic valid;  // the data is valid
