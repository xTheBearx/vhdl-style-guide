Localizing
==========

MHSG supports customization to your coding style standards by allowing localized rules.
These rules are stored in a directory with an __init__.py file and one or more python files.

The localized rules will be used when the **--local_rules** command line argument is given or using the **local_rules** option in a configuration file.
More than one directory can be given, which allows rules to be organized in groups.

Prepare local rules directory
-----------------------------

Create a directory with an empty __init__.py file:

.. code-block:: bash

  $ mkdir ~/local_rules
  $ touch ~/local_rules/__init__.py

Each rule is a class in a python file in this directory.

.. NOTE::
  The file name and class name must start with **rule_**.
  Otherwise MHSG will not recognize it as a rule.

The class name gives the rule's number, for example **rule_001** is number **001**.
Local rules must set their name, which is the first part of the rule identifier.
The rules below use the name **localized**, so their identifiers are **localized_001** and **localized_002**.
Rule identifiers must be unique across all rule directories.

How rules work
--------------

MHSG reads a VHDL file into a list of tokens, and every token is classified, for example as an entity keyword or a port mode.
A rule finds the tokens it is interested in, checks them and reports violations.
If the rule is fixable, it can also change the tokens.

Every rule inherits from the **Rule** class in **mhsg/rule.py**.
These attributes control how a rule runs:

+---------------+-------------------------------------------------------------------+
| Attribute     | Description                                                       |
+===============+===================================================================+
| name          | The first part of the rule identifier, for example **localized**. |
+---------------+-------------------------------------------------------------------+
| phase         | The phase the rule runs in, see :doc:`phases`.                    |
+---------------+-------------------------------------------------------------------+
| solution      | The message reported with each violation.                         |
+---------------+-------------------------------------------------------------------+
| fixable       | Whether the rule can fix its violations.                          |
+---------------+-------------------------------------------------------------------+
| disable       | Whether the rule is disabled by default.                          |
+---------------+-------------------------------------------------------------------+
| configuration | The attributes which can be set in a configuration file.          |
+---------------+-------------------------------------------------------------------+

And these methods do the work:

+-------------------------------------+------------------------------------------------------------------+
| Method                              | Description                                                      |
+=====================================+==================================================================+
| analyze(oFile)                      | Calls **_get_tokens_of_interest** and passes the result to       |
|                                     | **_analyze**. Override it to work with the whole file directly.  |
+-------------------------------------+------------------------------------------------------------------+
| _get_tokens_of_interest(oFile)      | Returns the tokens to check, using methods of the file such as   |
|                                     | **get_tokens_matching** and **get_tokens_bounded_by**.           |
+-------------------------------------+------------------------------------------------------------------+
| _analyze(lToi)                      | Checks the tokens and calls **add_violation** for each problem.  |
+-------------------------------------+------------------------------------------------------------------+
| add_violation(oViolation)           | Records a violation, unless a code tag disables the rule there.  |
+-------------------------------------+------------------------------------------------------------------+
| _fix_violation(oViolation)          | Fixes one violation by changing its tokens.                      |
+-------------------------------------+------------------------------------------------------------------+

The **mhsg/rules** directory contains base classes for common checks, such as tokens which should not occur, the case of words, whitespace and alignment.
Extending one of them is the quickest way to write a rule, and fixes come with it where the base class supports them.

Example: Extend an existing base rule
-------------------------------------

Suppose ports must not use the **buffer** mode.
The **existence_of_tokens_which_should_not_occur** base rule reports every token of the given types, so the rule only needs to name the token and describe the solution.
Save this as **~/local_rules/rule_localized_002.py**:

.. code-block:: python

   from mhsg import token
   from mhsg.rules import existence_of_tokens_which_should_not_occur as Rule


   class rule_002(Rule):
       def __init__(self):
           super().__init__([token.mode.buffer_keyword])
           self.name = "localized"
           self.phase = 1
           self.solution = "Use out instead of buffer."

To find the token classes to use, run **bin/mhsg_parser** on an example file.
It prints the class of every token on every line.

Example: Write a rule from scratch
----------------------------------

Suppose the entity and architecture must be in separate files.
This rule overrides **analyze** to look at the whole file.
Save this as **~/local_rules/rule_localized_001.py**:

.. code-block:: python

   from mhsg import rule, token, violation


   class rule_001(rule.Rule):
       def __init__(self):
           super().__init__()
           self.name = "localized"
           self.phase = 1
           self.fixable = False  # User must split the file
           self.solution = "Split entity and architecture into separate files."

       def analyze(self, oFile):
           lToiEntity = oFile.get_tokens_matching([token.entity_declaration.entity_keyword])
           lToiArchitecture = oFile.get_tokens_matching([token.architecture_body.architecture_keyword])

           if len(lToiEntity) > 0 and len(lToiArchitecture) > 0:
               oViolation = violation.New(1, lToiEntity[0], self.solution)
               self.add_violation(oViolation)

**violation.New** takes the line number to report, the tokens the violation refers to and the solution.
Code tags such as :code:`-- mhsg_off localized_001` work with local rules, because **add_violation** checks the tokens of each violation.

Use the rules
-------------

Run MHSG with the **--local_rules** option:

.. code-block:: bash

   $ mhsg -f RAM.vhd --local_rules ~/local_rules -of syntastic
   ERROR: RAM.vhd(1)localized_001 -- Split entity and architecture into separate files.
   ERROR: RAM.vhd(3)localized_002 -- Use out instead of buffer.

Several directories can be given, for example **--local_rules ~/local_rules ~/team_rules**.

Configure the rules
-------------------

Local rules are configured like any other rule, for example to change the severity:

.. code-block:: yaml

   local_rules: ~/local_rules
   rule:
     localized_002:
       severity: Warning

To add an option of your own, set its default in **__init__** and append its name to **self.configuration**:

.. code-block:: python

   self.max_ports = 20
   self.configuration.append("max_ports")

The value from the configuration file is set on the rule before it runs.
Use **-rc** to see the configuration of a rule, for example :code:`mhsg -lr ~/local_rules -rc localized_002`.

Rule creation guidelines
------------------------

Keep these points in mind when creating new rules:

#. Start from an existing rule or base class in **mhsg/rules**.
#. Use **bin/mhsg_parser** to find the token classes to work with.
#. Report violations through **add_violation**, so code tags are respected.
#. Give every rule a unique identifier across all local rule directories.
