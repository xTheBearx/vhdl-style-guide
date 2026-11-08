.. include:: includes.rst

Verilog and SystemVerilog Alignment Rules
-----------------------------------------

sv_alignment_001
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_port_declarations`

This rule aligns the names of the port declarations of a module, interface or program header in a column, as
Verible's formatter does. By default it infers whether the author meant them aligned or flush left;
**policy** set to align or flush_left forces one.

**Violation**

.. code-block:: systemverilog

   input logic clk_i,
   output logic [7:0] data_o

**Fix**

.. code-block:: systemverilog

   input  logic       clk_i,
   output logic [7:0] data_o

sv_alignment_002
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_named_ports`

This rule aligns the opening parentheses of the named port connections of an instance in a column, as
Verible's formatter does. By default it infers whether the author meant them aligned or flush left;
**policy** set to align or flush_left forces one.

**Violation**

.. code-block:: systemverilog

   .clk_i(clk_i),
   .data_i(data)

**Fix**

.. code-block:: systemverilog

   .clk_i (clk_i),
   .data_i(data)

sv_alignment_003
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_named_parameters`

This rule aligns the opening parentheses of the named parameter assignments of an instance in a column, as
Verible's formatter does. By default it infers whether the author meant them aligned or flush left;
**policy** set to align or flush_left forces one.

**Violation**

.. code-block:: systemverilog

   .Width(8),
   .Depth(16)

**Fix**

.. code-block:: systemverilog

   .Width(8),
   .Depth(16)

sv_alignment_004
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_declarations`

This rule aligns the names of consecutive variable and net declarations in a column, as Verible's formatter
does. By default it infers whether the author meant them aligned or flush left; **policy** set to align or
flush_left forces one.

**Violation**

.. code-block:: systemverilog

   logic valid;
   logic [7:0] data;

**Fix**

.. code-block:: systemverilog

   logic       valid;
   logic [7:0] data;

sv_alignment_005
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_assignments`

This rule aligns the assignment operators of consecutive continuous assignments and assignment statements in
a column, as Verible's formatter does. By default it infers whether the author meant them aligned or flush
left; **policy** set to align or flush_left forces one.

**Violation**

.. code-block:: systemverilog

   assign valid = valid_q;
   assign data_o = data_q;

**Fix**

.. code-block:: systemverilog

   assign valid  = valid_q;
   assign data_o = data_q;

sv_alignment_006
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_parameters`

This rule aligns the = of consecutive parameter and localparam declarations, and of the parameters of a
header in a column, as Verible's formatter does. By default it infers whether the author meant them aligned
or flush left; **policy** set to align or flush_left forces one.

**Violation**

.. code-block:: systemverilog

   localparam int Depth = 16;
   localparam int AddrWidth = 4;

**Fix**

.. code-block:: systemverilog

   localparam int Depth     = 16;
   localparam int AddrWidth = 4;

sv_alignment_007
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_case_items`

This rule aligns the statements of case items written on the line of their item in a column, as Verible's
formatter does. By default it infers whether the author meant them aligned or flush left; **policy** set to
align or flush_left forces one.

**Violation**

.. code-block:: systemverilog

   Idle: state_d = Busy;
   default: state_d = Idle;

**Fix**

.. code-block:: systemverilog

   Idle:    state_d = Busy;
   default: state_d = Idle;

sv_alignment_008
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_struct_members`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule aligns the names of the members of a struct or union in a column, as Verible's formatter does. By
default it infers whether the author meant them aligned or flush left; **policy** set to align or flush_left
forces one.

**Violation**

.. code-block:: systemverilog

   logic valid;
   logic [7:0] data;

**Fix**

.. code-block:: systemverilog

   logic       valid;
   logic [7:0] data;

sv_alignment_009
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_port_types`

This rule aligns the types of the port declarations of a module, interface or program header in a column after
their directions, as Verible's formatter does. Ports without a type after their direction, such as input clk, are
left out without ending the group. By default it infers whether the author meant them aligned or flush left;
**policy** set to align or flush_left forces one.

**Violation**

.. code-block:: systemverilog

   module fifo (
       input logic clk_i,
       output logic [7:0] data_o
   );

**Fix**

.. code-block:: systemverilog

   module fifo (
       input  logic clk_i,
       output logic [7:0] data_o
   );

sv_alignment_010
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_packed_dimensions`

This rule aligns the packed dimensions of the port declarations of a header, and of consecutive variable and net
declarations, in a column, as Verible's formatter does. Declarations without a packed dimension are left out
without ending the group. By default it infers whether the author meant them aligned or flush left; **policy**
set to align or flush_left forces one.

**Violation**

.. code-block:: systemverilog

   logic [7:0] data;
   wire [3:0] strobe;

**Fix**

.. code-block:: systemverilog

   logic [7:0] data;
   wire  [3:0] strobe;

sv_alignment_011
################

|phase_5| |error| |alignment|

Alias: :code:`sv_alignment_dimension_colons`

This rule aligns the packed dimensions of the declarations that sv_alignment_010 aligns, as Verible's formatter
does: the text inside the brackets of each dimension is aligned right, by spaces after the opening bracket, so
[ 4:0] goes under [31:0], and the brackets of the next dimension line up. Declarations without a dimension leave its
column alone. By default it infers whether the author meant them aligned, as for the other alignment rules;
**policy** set to align or flush_left forces one.

**Violation**

.. code-block:: systemverilog

   logic [31:0]       data;
   logic [4:0]        count;
   logic [7:0][3:0]   bytes;
   logic [15:0][31:0] words;

**Fix**

.. code-block:: systemverilog

   logic [31:0]       data;
   logic [ 4:0]       count;
   logic [ 7:0][ 3:0] bytes;
   logic [15:0][31:0] words;
