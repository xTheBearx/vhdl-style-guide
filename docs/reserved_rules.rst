.. include:: includes.rst

Reserved Rules
--------------

reserved_001
############

|phase_1| |error| |unfixable| |structure|

Alias: :code:`reserved_words_not_used_as_names`

This rule checks for VHDL reserved words being used as identifiers and names.

|configuring_vhdl_reserved_words_link|

**Violation**

.. code-block:: vhdl

   entity null is
   end null;
