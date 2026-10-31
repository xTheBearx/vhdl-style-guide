.. include:: includes.rst

Expression Rules
----------------

expression_001
##############

|phase_1| |disabled| |error| |structure|

Alias: :code:`expression_redundant_parentheses`

This rule checks for parentheses which enclose a single name or literal in an expression.
Such parentheses do not change the meaning of the expression.

Parentheses are not reported when they:

* belong to a function call, an index, a type conversion or a qualified expression
* follow a unary reduction operator, as in **and(a)**
* enclose an entire **if**, **elsif** or **while** condition. Rule :ref:`if_002` controls the parentheses around **if** conditions.

.. NOTE:: This rule is disabled by default.

**Violation**

.. code-block:: vhdl

   if (sync_reset) = '1' then
     a <= (b) and c;

**Fix**

.. code-block:: vhdl

   if sync_reset = '1' then
     a <= b and c;
