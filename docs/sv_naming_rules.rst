.. include:: includes.rst

Verilog and SystemVerilog Naming Rules
--------------------------------------

sv_naming_001
#############

|phase_7| |error| |unfixable| |naming|

Alias: :code:`sv_naming_parameter_name_style`

This rule checks that parameter names match **parameter_pattern** and localparam names match
**localparam_pattern**, regular expressions, by default UpperCamelCase or ALL_CAPS for parameters and
UpperCamelCase for localparams, as Verible's parameter-name-style rule does.

**Violation**

.. code-block:: systemverilog

   parameter int data_width = 8;

**Fix**

.. code-block:: systemverilog

   parameter int DataWidth = 8;

sv_naming_002
#############

|phase_7| |error| |unfixable| |naming|

Alias: :code:`sv_naming_enum_name_style`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks that the names of enum types match **pattern**, a regular expression, by default
[a-z_0-9]+(_t|_e), as Verible's enum-name-style rule does.

**Violation**

.. code-block:: systemverilog

   typedef enum logic {Idle, Busy} State;

**Fix**

.. code-block:: systemverilog

   typedef enum logic {Idle, Busy} state_e;

sv_naming_003
#############

|phase_7| |error| |unfixable| |naming|

Alias: :code:`sv_naming_struct_union_name_style`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks that the names of struct and union types match **pattern**, a regular expression, by
default [a-z_0-9]+_t, as Verible's struct-union-name-style rule does.

**Violation**

.. code-block:: systemverilog

   typedef struct packed {logic a;} Beat;

**Fix**

.. code-block:: systemverilog

   typedef struct packed {logic a;} beat_t;

sv_naming_004
#############

|phase_7| |error| |unfixable| |naming|

Alias: :code:`sv_naming_interface_name_style`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks that interface names match **pattern**, a regular expression, by default [a-z_0-9]+_if, as
Verible's interface-name-style rule does.

**Violation**

.. code-block:: systemverilog

   interface Bus;

**Fix**

.. code-block:: systemverilog

   interface bus_if;

sv_naming_005
#############

|phase_7| |error| |unfixable| |naming|

Alias: :code:`sv_naming_macro_name_style`

This rule checks that macro names match **pattern**, a regular expression, by default [A-Z_0-9]+, as
Verible's macro-name-style rule does; macros whose names start with :code:`uvm_` or :code:`UVM_` may be
lower case.

**Violation**

.. code-block:: systemverilog

   `define data_width 8

**Fix**

.. code-block:: systemverilog

   `define DATA_WIDTH 8

sv_naming_006
#############

|phase_7| |error| |unfixable| |naming|

Alias: :code:`sv_naming_constraint_name_style`

SystemVerilog only: this rule is not applied to Verilog files, see :ref:`verilog_2005`.

This rule checks that constraint names match **pattern**, a regular expression, by default ([a-z0-9]+_)+c,
as Verible's constraint-name-style rule does.

**Violation**

.. code-block:: systemverilog

   constraint Length { length < 64; }

**Fix**

.. code-block:: systemverilog

   constraint length_c { length < 64; }

sv_naming_007
#############

|phase_7| |error| |unfixable| |naming|

Alias: :code:`sv_naming_positive_meaning_parameter_name`

This rule checks that no parameter name starts with disable; name it after what it enables, as Verible's
positive-meaning-parameter-name rule does.

**Violation**

.. code-block:: systemverilog

   parameter bit DisableParity = 1'b0;

**Fix**

.. code-block:: systemverilog

   parameter bit EnableParity = 1'b1;

sv_naming_008
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_signal_name_style`

This rule checks that the names of signals and ports match **pattern**, a regular expression, by default
lower_snake_case [a-z_0-9]+, as Verible's signal-name-style rule does. It is disabled by default, as in
Verible.

**Violation**

.. code-block:: systemverilog

   logic DataValid;

**Fix**

.. code-block:: systemverilog

   logic data_valid;

sv_naming_009
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_identifier_characters`

This rule checks that names use only letters, digits and underscores and start with a letter, as the STARC
guide asks (1.1.1.2): no escaped identifiers and no leading underscore. It is disabled by default; the starc
rule set enables it.

**Violation**

.. code-block:: systemverilog

   logic _valid;

**Fix**

.. code-block:: systemverilog

   logic valid;

sv_naming_010
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_vhdl_keywords`

This rule checks that no name is a VHDL keyword, in any case, as the STARC guide asks (1.1.1.3), so the
design can be translated or mixed with VHDL. The keywords of the language of the file cannot be names. It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   logic signal;

**Fix**

.. code-block:: systemverilog

   logic valid;

sv_naming_011
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_power_names`

This rule checks that no name starts with VDD, VSS, VCC, GND or VREF, in any case, as the STARC guide asks
(1.1.1.4). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   logic vdd_ok;

**Fix**

.. code-block:: systemverilog

   logic supply_ok;

sv_naming_012
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_case_only_difference`

This rule checks that no two names of a file differ only in case, as the STARC guide asks (1.1.1.5). It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   logic data;
   logic Data;

**Fix**

.. code-block:: systemverilog

   logic data;
   logic data_q;

sv_naming_013
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_name_length`

This rule checks the length of names, as the STARC guide asks: modules and instances **module_minimum** to
**module_maximum** characters, 2 to 32 by default (1.1.2.1); other names **minimum** to **maximum**, 2 to 40
by default (1.1.3.3). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   logic v;

**Fix**

.. code-block:: systemverilog

   logic valid;

sv_naming_014
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_underscores`

This rule checks that the names of modules and ports do not end with an underscore, and that no name has two
underscores in a row, as the STARC guide asks (1.1.1.6). It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module fifo_ (input logic clk__i);

**Fix**

.. code-block:: systemverilog

   module fifo (input logic clk_i);

sv_naming_015
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_instance_after_module`

This rule checks that an instance is named after the module it instantiates, or after it and a number for
several instances, such as fifo or fifo_1, as the STARC guide recommends (1.1.1.8). It is disabled by default; the
starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   fifo buffer (.clk_i(clk_i));

**Fix**

.. code-block:: systemverilog

   fifo fifo (.clk_i(clk_i));

sv_naming_016
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_ports_and_signals`

This rule checks that port names match **port_pattern**, a regular expression, by default names ending in _i, _o
or _io, with an n before it for active low ports, and that the other signals of the module do not, so ports and
internal signals can be told apart, as the STARC guide asks (1.1.2.5, 1.1.3.1). It is disabled by default; the
starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module fifo (input logic clk, output logic full);
       logic count_o;

**Fix**

.. code-block:: systemverilog

   module fifo (input logic clk_i, output logic full_o);
       logic count;

sv_naming_017
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_active_low_resets`

This rule checks that asynchronous resets that are active low, tested on negedge or with !, have names marking
them so, matching **active_low_pattern**, a regular expression matched ignoring case, by default names ending in
_n, _x, _b or _l, with i or o after it for ports, or such as rstn, as the STARC guide recommends (1.1.1.7). It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_i)
       if (!rst_i) q <= 1'b0;

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_i or negedge rst_ni)
       if (!rst_ni) q <= 1'b0;

sv_naming_018
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_top_names`

This rule checks that the names of modules and ports are at most **maximum_name_length** characters long, 16 by
default, and that no two names of a file differ only in case, as the STARC guide recommends (1.1.1.9) for the top
level of a design, whose names other tools must handle. It checks every module, as a file does not tell which is
the top. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module serial_receiver_with_fifo (input logic Clk, input logic clk);

**Fix**

.. code-block:: systemverilog

   module uart_rx (input logic clk_i);

sv_naming_019
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_no_cell_names`

This rule checks that modules and instances are not named after the cells of the target library, listed in
**cell_names**, compared ignoring case, as the STARC guide asks (1.1.1.10). The list is empty by default: give
the cells of your library. It is disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   module AND2 (input logic a, b, output logic y);

**Fix**

.. code-block:: systemverilog

   module and_gate (input logic a, b, output logic y);

sv_naming_020
#############

|phase_7| |disabled| |error| |unfixable| |naming|

Alias: :code:`sv_naming_clock_reset_words`

This rule checks the base names of clocks and resets, as the STARC guide recommends (1.1.5.2): the clocks of edge
triggered always blocks are named with a clock word, such as clk, and their asynchronous resets with a reset
word, such as rst, as port_028 tells them: **clock_words**, **reset_words** and **qualifier_words**. It is
disabled by default; the starc rule set enables it.

**Violation**

.. code-block:: systemverilog

   always_ff @(posedge sample or negedge init_n) ...

**Fix**

.. code-block:: systemverilog

   always_ff @(posedge clk_sample or negedge rst_n) ...
