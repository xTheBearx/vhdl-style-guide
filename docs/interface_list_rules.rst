.. include:: includes.rst

Interface List Rules
--------------------

interface_list_001
##################

|phase_1| |disabled| |error| |structure| |structure_optional|

Alias: :code:`interface_list_trailing_semicolon`

This rule checks for the optional semicolon after the last element of a generic, port or parameter list.
VHDL-2019 allows this semicolon; earlier versions of VHDL do not.

|configuring_optional_items_link|

.. NOTE:: This rule is disabled by default.
   Its default action is :code:`remove`, which keeps the code valid for tools that do not support VHDL-2019.

**Violation**

.. code-block:: vhdl

   port (
     a : in    std_logic;
     b : out   std_logic;
   );

**Fix**

.. code-block:: vhdl

   port (
     a : in    std_logic;
     b : out   std_logic
   );
