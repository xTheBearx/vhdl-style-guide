.. include:: includes.rst

If Rules
--------

if_001
######

|phase_4| |error| |indent|

Alias: :code:`if_keyword_indent`

This rule checks the indent of the **if** keyword.

**Violation**

.. code-block:: vhdl

    if (a = '1') then
    b <= '0'
  elsif (c = '1') then
    d <= '1';
  else
    e <= '0';
  end if;

**Fix**

.. code-block:: vhdl

  if (a = '1') then
    b <= '0'
  elsif (c = '1') then
    d <= '1';
  else
    e <= '0';
  end if;

if_002
######

|phase_1| |error| |structure|

Alias: :code:`if_condition_in_parentheses`

This rule checks the boolean expression is enclosed in ().

.. NOTE:: There is a configuration option **parenthesis** which will either insert or remove the parenthesis.

parenthesis set to 'insert' (Default)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Violation**

.. code-block:: vhdl

  if a = '1' then

**Fix**

.. code-block:: vhdl

  if (a = '1') then

parenthesis set to 'remove'
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Violation**

.. code-block:: vhdl

  if (a = '1') then

**Fix**

.. code-block:: vhdl

  if a = '1' then

if_003
######

|phase_2| |error| |whitespace|

Alias: :code:`if_space_before_open_parenthesis`

This rule checks for a single space between the **if** keyword and the (.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

  if(a = '1') then

  if   (a = '1') then

**Fix**

.. code-block:: vhdl

  if (a = '1') then

  if (a = '1') then

if_004
######

|phase_2| |error| |whitespace|

Alias: :code:`if_space_before_then_keyword`

This rule checks for a single space between the ) and the **then** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

  if (a = '1')then

  if (a = '1')    then

**Fix**

.. code-block:: vhdl

  if (a = '1') then

  if (a = '1') then

if_005
######

|phase_2| |error| |whitespace|

Alias: :code:`if_space_after_elsif_keyword`

This rule checks for a single space after the **elsif** keyword.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

  elsif(c = '1') then

  elsif   (c = '1') then

  elsif    b = '0' then

**Fix**

.. code-block:: vhdl

  elsif (c = '1') then

  elsif (c = '1') then

  elsif b = '0' then

if_006
######

This rule has been replaced by :ref:`if_200`, which supports the **style** option.

if_007
######

This rule has been replaced by :ref:`if_201`, which supports the **style** option.

if_008
######

This rule has been replaced by :ref:`if_204`, which supports the **style** option.

if_009
######

|phase_4| |error| |alignment|

Alias: :code:`if_multiline_condition_alignment`

This rule checks the alignment of multiline boolean expressions.

|configuring_multiline_indent_rules_link|

**Violation**

.. code-block:: vhdl

   if (a = '0' and b = '1' and
         c = '0') then

**Fix**

.. code-block:: vhdl

   if (a = '0' and b = '1' and
       c = '0') then

if_010
######

This rule has been replaced by :ref:`if_202`, which supports the **style** option.

if_011
######

This rule has been replaced by :ref:`if_203`, which supports the **style** option.

if_012
######

|phase_4| |error| |indent|

Alias: :code:`if_elsif_keyword_indent`

This rule checks the indent of the **elsif** keyword.

**Violation**

.. code-block:: vhdl

  if (a = '1') then
    b <= '0'
    elsif (c = '1') then
    d <= '1';
  else
    e <= '0';
  end if;

**Fix**

.. code-block:: vhdl

  if (a = '1') then
    b <= '0'
  elsif (c = '1') then
    d <= '1';
  else
    e <= '0';
  end if;

if_013
######

|phase_4| |error| |indent|

Alias: :code:`if_else_keyword_indent`

This rule checks the indent of the **else** keyword.

**Violation**

.. code-block:: vhdl

  if (a = '1') then
    b <= '0'
  elsif (c = '1') then
    d <= '1';
    else
    e <= '0';
  end if;

**Fix**

.. code-block:: vhdl

  if (a = '1') then
    b <= '0'
  elsif (c = '1') then
    d <= '1';
  else
    e <= '0';
  end if;

if_014
######

|phase_4| |error| |indent|

Alias: :code:`if_end_if_keyword_indent`

This rule checks the indent of the **end if** keyword.

**Violation**

.. code-block:: vhdl

  if (a = '1') then
    b <= '0'
  elsif (c = '1') then
    d <= '1';
  else
    e <= '0';
    end if;

**Fix**

.. code-block:: vhdl

  if (a = '1') then
    b <= '0'
  elsif (c = '1') then
    d <= '1';
  else
    e <= '0';
  end if;

if_015
######

|phase_2| |error| |whitespace|

Alias: :code:`if_space_between_end_and_if`

This rule checks for a single space between the **end if** keywords.

|configuring_whitespace_rules_link|

**Violation**

.. code-block:: vhdl

   end    if;

**Fix**

.. code-block:: vhdl

   end if;

if_020
######

|phase_1| |error| |structure|

Alias: :code:`if_end_if_keyword_on_own_line`

This rule checks the **end if** keyword is on its own line.

**Violation**

.. code-block:: vhdl

   if (a = '1') then c <= '1'; else c <= '0'; end if;

**Fix**

.. code-block:: vhdl

   if (a = '1') then c <= '1'; else c <= '0';
   end if;

if_021
######

|phase_1| |error| |structure|

Alias: :code:`if_else_keyword_on_own_line`

This rule checks the **else** keyword is on its own line.

**Violation**

.. code-block:: vhdl

   if (a = '1') then c <= '1'; else c <= '0'; end if;

**Fix**

.. code-block:: vhdl

   if (a = '1') then c <= '0';
   else c <= '1'; end if;

if_022
######

|phase_1| |error| |structure|

Alias: :code:`if_no_code_after_else_keyword`

This rule checks for code after the **else** keyword.

**Violation**

.. code-block:: vhdl

   if (a = '1') then c <= '1'; else c <= '0'; end if;

**Fix**

.. code-block:: vhdl

   if (a = '1') then c <= '1'; else
     c <= '0'; end if;

if_023
######

|phase_1| |error| |structure|

Alias: :code:`if_elsif_keyword_on_own_line`

This rule checks the **elsif** keyword is on its own line.

**Violation**

.. code-block:: vhdl

   if (a = '1') then c <= '1'; else c <= '0'; elsif (b = '0') then d <= '0'; end if;

**Fix**

.. code-block:: vhdl

   if (a = '1') then c <= '1'; else c <= '0';
   elsif (b = '0') then d <= '0'; end if;

if_024
######

|phase_1| |error| |structure|

Alias: :code:`if_no_code_after_then_keyword`

This rule checks for code after the **then** keyword.

**Violation**

.. code-block:: vhdl

   if (a = '1') then c <= '1';

**Fix**

.. code-block:: vhdl

   if (a = '1') then
     c <= '1';

if_025
######

|phase_6| |error| |case| |case_keyword|

Alias: :code:`if_keyword_case`

This rule checks the **if** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   IF (a = '1') then

**Fix**

.. code-block:: vhdl

   if (a = '1') then

if_026
######

|phase_6| |error| |case| |case_keyword|

Alias: :code:`if_elsif_keyword_case`

This rule checks the **elsif** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   ELSIF (a = '1') then

**Fix**

.. code-block:: vhdl

   elsif (a = '1') then

if_027
######

|phase_6| |error| |case| |case_keyword|

Alias: :code:`if_else_keyword_case`

This rule checks the **else** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   ELSE

**Fix**

.. code-block:: vhdl

   else

if_028
######

|phase_6| |error| |case| |case_keyword|

Alias: :code:`if_end_keyword_case`

This rule checks the **end** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   END if;

   End if;

**Fix**

.. code-block:: vhdl

   end if;

   end if;

if_029
######

|phase_6| |error| |case| |case_keyword|

Alias: :code:`if_then_keyword_case`

This rule checks the **then** keyword has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   if (a = '1') THEN

**Fix**

.. code-block:: vhdl

   if (a = '1') then

if_030
######

|phase_3| |error| |blank_line|

Alias: :code:`if_blank_line_below_end_if`

This rule checks a single blank line after the **end if**.
In the case of nested **if** statements, the rule will be enforced on the last **end if**.

|configuring_blank_lines_link|

**Violation**

.. code-block:: vhdl

   if (A = '1') then
     B <= '0';
   end if;
   C <= '1';

**Fix**

.. code-block:: vhdl

   if (A = '1') then
     B <= '0';
   end if;

   C <= '1';

if_031
######

|phase_3| |error| |blank_line|

Alias: :code:`if_lines_above_if_keyword`

This rule checks for blank lines or comments above the **if** keyword.
In the case of nested **if** statements, the rule will be enforced on the first **if**.

|configuring_previous_line_rules_link|

The default style is :code:`no_code`.

**Violation**

.. code-block:: vhdl

   C <= '1';
   if (A = '1') then
     B <= '0';
   end if;

   -- This is a comment
   if (A = '1') then
     B <= '0';
   end if;

**Fix**

.. code-block:: vhdl

   C <= '1';

   if (A = '1') then
     B <= '0';
   end if;

   -- This is a comment
   if (A = '1') then
     B <= '0';
   end if;

if_032
######

The function of this rule has been superseded with comment indent updates and is handled by rule comment_010.

if_033
######

The function of this rule has been superseded with comment indent updates and is handled by rule comment_010.

if_034
######

|phase_6| |error| |case| |case_keyword|

Alias: :code:`if_end_if_keyword_case`

This rule checks the **if** keyword in the **end if** has proper case.

|configuring_uppercase_and_lowercase_rules_link|

**Violation**

.. code-block:: vhdl

   end If;

   end IF;

**Fix**

.. code-block:: vhdl

   end if;

   end if;

if_035
######

|phase_1| |error| |structure|

Alias: :code:`if_condition_on_same_line_as_keyword`

This rule checks the expression after the **if** or **elsif** keyword starts on the same line.

**Violation**

.. code-block:: vhdl

   if
     a = '1' then

   elsif
     b = '1' then

**Fix**

.. code-block:: vhdl

   if a = '1' then

   elsif b = '1' then

if_036
######

|phase_1| |error| |structure|

Alias: :code:`if_then_keyword_not_on_own_line`

This rule checks the **then** keyword is not on a line by itself.

**Violation**

.. code-block:: vhdl

   if a = '1'
     then

**Fix**

.. code-block:: vhdl

   if a = '1' then

if_200
######

|phase_3| |error| |blank_line|

Alias: :code:`if_blank_line_below_then_keyword`

This rule checks for blank lines below the **then** keyword.

|configuring_blank_lines_link|

The default style is :code:`no_blank_line`.
With this style, one blank line is allowed if the next line starts a **case** or **loop** statement.

**Violation**

.. code-block:: vhdl

   if (a = '1') then


     b <= '0';

**Fix**

.. code-block:: vhdl

   if (a = '1') then
     b <= '0';

if_201
######

|phase_3| |error| |blank_line|

Alias: :code:`if_lines_above_elsif_keyword`

This rule checks for blank lines or comments above the **elsif** keyword.

|configuring_previous_line_rules_link|

The default style is :code:`no_blank_line`.
With this style, one blank line is allowed if the previous line ends a **case** or **loop** statement.

**Violation**

.. code-block:: vhdl

     b <= '0';


   elsif (c = '1') then

**Fix**

.. code-block:: vhdl

     b <= '0';
   elsif (c = '1') then

if_202
######

|phase_3| |error| |blank_line|

Alias: :code:`if_lines_above_else_keyword`

This rule checks for blank lines or comments above the **else** keyword.

|configuring_previous_line_rules_link|

The default style is :code:`no_blank_line`.
With this style, one blank line is allowed if the previous line ends a **case** or **loop** statement.

**Violation**

.. code-block:: vhdl

     b <= '0';


   else

**Fix**

.. code-block:: vhdl

     b <= '0';
   else

if_203
######

|phase_3| |error| |blank_line|

Alias: :code:`if_blank_line_below_else_keyword`

This rule checks for blank lines below the **else** keyword.

|configuring_blank_lines_link|

The default style is :code:`no_blank_line`.
With this style, one blank line is allowed if the next line starts a **case** or **loop** statement.

**Violation**

.. code-block:: vhdl

   else


     e <= '0';

**Fix**

.. code-block:: vhdl

   else
     e <= '0';

if_204
######

|phase_3| |error| |blank_line|

Alias: :code:`if_lines_above_end_if_keyword`

This rule checks for blank lines or comments above the **end if** keywords.

|configuring_previous_line_rules_link|

The default style is :code:`no_blank_line`.
With this style, one blank line is allowed if the previous line ends a **case** or **loop** statement.

**Violation**

.. code-block:: vhdl

     e <= '0';


   end if;

**Fix**

.. code-block:: vhdl

     e <= '0';
   end if;
