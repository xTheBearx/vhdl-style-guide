-- procedure_call_400 indents the lines of a nested function call again after
-- procedure_call_401 aligns => and moves the parenthesis (issue #83).

architecture rtl of foo is

begin

  process
  begin

    set(
      arr=>data_result,
      value=>get(
        arr=>data_inputs(input_idx),
        idx=>word_idx
      )
    );

  end process;

end architecture rtl;
