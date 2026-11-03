Code Tags
=========

MHSG supports inline tags embedded into code to enable or disable rules.
This can be useful in fine tuning rule exceptions within a file.
The code tags are embedded in comments similar to pragmas, and must be on its own line.

In SystemVerilog and Verilog files the code tags are written in a :code:`//` comment, such as :code:`// mhsg_off`.
A block comment on one line can hold a code tag too, in either language: :code:`/* mhsg_off */` is read as
:code:`// mhsg_off`. A block comment over several lines is not a code tag.

.. NOTE:: The code tags used by VSG, **vsg_off**, **vsg_on** and **vsg_disable_next_line**, are also recognized and behave the same as the **mhsg_** tags.

Full rule exclusion
-------------------

Entire portions of a file can be ignored using the **mhsg_off** and **mhsg_on** tags.

.. code-block:: vhdl

    -- mhsg_off
    process (write, read, full) is
    begin
      a <= write;
      b <= read;
    end process;
    -- mhsg_on

The **mhsg_off** tag disables all rule checking.
The **mhsg_on** tag enables all rule checking, except those disabled by a configuration.

If MHSG cannot parse a file, but the code it cannot parse is between a bare **mhsg_off** and **mhsg_on** tag,
the file is parsed again with that code hidden, so the rest of the file is still checked.
This can be used to exclude code which uses a construct MHSG does not support yet.
Tags which name rules, such as :code:`-- mhsg_off process_016`, do not hide code from the parser.

Individual Rule Exclusions
--------------------------

Individual rules can be disabled by adding the rule identifier to the **mhsg_off** and **mhsg_on** tags.
Multiple identifiers can be added.

.. code-block:: vhdl

   -- mhsg_off process_016 process_018
   process (write, read, full) is
   begin
     a <= write;
     b <= read;
   end process;
   -- mhsg_on

The bare **mhsg_on** enables all rules not disabled by a configuration.

Each rule can be independently enabled or disabled:

.. code-block:: vhdl

   -- mhsg_off process_016 process_018
   process (write, read, full) is
   begin
     a <= write;
     b <= read;
   end process;

   -- mhsg_on process_016
   FIFO_PROC : process (write, read, full) is
   begin
     a <= write;
     b <= read;
   end process;

   -- mhsg_on process_018
   FIFO_PROC : process (write, read, full) is
   begin
     a <= write;
     b <= read;
   end process FIFO_PROC;

In the previous example, the *process_016* and *process_018* are disabled for the first process.
*Process_018* is disabled for the second process.
No rules are disabled for the third process.

A rule can also be named by its alias, see :ref:`configuring-rule-aliases`.
A rule disabled by its alias can be enabled again by its identifier, and the other way around.

.. code-block:: vhdl

   -- mhsg_off process_label_exists process_end_label_exists
   process (write, read, full) is
   begin
     a <= write;
   end process;
   -- mhsg_on process_016 process_018

Next Line Rule Exclusions
-------------------------

Rules can be disabled for a single line using the **mhsg_disable_next_line** tag.
Multiple identifiers or aliases can be added to a single tag.

.. code-block:: vhdl

   -- mhsg_disable_next_line process_016
   process (write, read, full) is
   begin
     a <= write;
     b <= read;
     -- mhsg_disable_next_line process_018
   end process;

In the above example, process_016 will only be disabled for the line with the **process** keyword.
Successive processes without labels will be flagged by process_016.

Sequential next line exclusions will also be honored:

.. code-block:: vhdl

   -- mhsg_disable_next_line process_002
   -- mhsg_disable_next_line process_016
   process(write, read, full) is
   begin
     a <= write;
     b <= read;
     -- mhsg_disable_next_line process_018
   end process;

In the above example, both process_002 and process_016 will be disabled for the line starting with the **process** keyword.

Comments in code tags
---------------------

Code tags themselves are comments, however there is a method to allow commenting of the code tag on the same line.
The colon character, :, can be used to document why the code tag exists.

.. code-block:: vhdl

   -- mhsg_off process_016 process_018 : MHSG errors out on the following code
   process (write, read, full) is
   begin
     a <= write;
     b <= read;
   end process;
   -- mhsg_on process_016 process_018 : Done with exclusion until MHSG is fixed
