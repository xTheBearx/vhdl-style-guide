.. include:: includes.rst

Comment Rules
-------------

comment_004
###########

|phase_2| |error| |whitespace|

Alias: :code:`comment_space_before_inline_comments`

This rule checks for at least a single space before inline comments.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   wr_en <= '1';--Write data
   rd_en <= '1';   -- Read data

**Fix**

.. code-block:: vhdl

   wr_en <= '1'; --Write data
   rd_en <= '1';   -- Read data

comment_010
###########

|phase_4| |error| |indent|

Alias: :code:`comment_indent`

This rule checks the indent lines starting with comments.

Comments inside multiline conditional assignments are not checked by this rule.
They are aligned with the code around them by rules :ref:`concurrent_009`, :ref:`sequential_401` and :ref:`variable_assignment_400`.

|configuring_comment_indenting_link|

**Violation**

.. code-block:: vhdl

       -- Libraries
   library ieee;

    -- Define architecture
   architecture rtl of fifo is

   -- Define signals
     signal wr_en : std_logic;
     signal rd_en : std_Logic;

   begin

**Fix**

.. code-block:: vhdl

   -- Libraries
   library ieee;

   -- Define architecture
   architecture rtl of fifo is

     -- Define signals
     signal wr_en : std_logic;
     signal rd_en : std_Logic;

   begin

comment_011
###########

|phase_1| |disabled| |error| |structure|

Alias: :code:`comment_inline_comment_moved_above`

This rule checks for in-line comments and moves them to the line above.
The indent of the comment will be set to the indent of the current line.

.. NOTE:: This rule is disabled by default.

**Violation**

.. code-block:: vhdl

   a <= b; -- Assign signal

**Fix**

.. code-block:: vhdl

   -- Assign signal
   a <= b;

comment_012
###########

|phase_1| |disabled| |warning| |unfixable| |structure|

Alias: :code:`comment_keywords`

This rule checks for user defined keywords in comments.

.. NOTE:: This rule is disabled by default.

|configuring_comment_keywords_link|

**Violation**

.. code-block:: vhdl

   -- TODO:  Refactor the section below
   -- FIXME: Update

**Fix**

This is a reporting only rule.

comment_013
###########

|phase_1| |disabled| |warning| |unfixable| |structure|

Alias: :code:`comment_commented_out_code`

This rule checks for comments which contain commented out code.

A comment on a line of its own is reported if it ends like a statement or declaration, with a semicolon or one of the keywords **then**, **else**, **begin**, **is**, **loop** or **generate**, and its words are VHDL reserved words, common names from the standard and IEEE packages, or names used in the code of the file.
If the comment contains a symbol used in code, such as **<=**, **:=**, **=** or **(**, half of its words are enough, because commented out code can name things which were removed from the code.
Comments written as sentences are not reported, because they contain words which are not in the code.

.. NOTE:: This rule is disabled by default.
   It only reports the comments, because deciding whether to delete them is left to the user.

**Violation**

.. code-block:: vhdl

   -- use ieee.numeric_std.all;

   -- Wait for the FIFO to empty
   -- if rd_en = '1' then
   if empty = '1' then

**Fix**

.. code-block:: vhdl

   -- Wait for the FIFO to empty
   if empty = '1' then

comment_100
###########

|phase_2| |error| |whitespace|

Alias: :code:`comment_space_after_dashes`

This rule checks for a single space after the **--**.

|configuring_whitespace_after_comment_rules_link|

**Violation**

.. code-block:: vhdl

   --Comment 1
   --|Comment 2
   ---Comment
   ---------------------------

**Fix**

.. code-block:: vhdl

   -- Comment 1
   --|Comment 2
   ---Comment
   ---------------------------
