.. include:: includes.rst

SystemVerilog Naming Rules
--------------------------

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
design can be translated or mixed with VHDL. SystemVerilog keywords cannot be names. It is disabled by
default; the starc rule set enables it.

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
