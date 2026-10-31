
architecture rtl of e is

begin

  output <= '1' when input = "0000" or (input = "1111" and
                                         -- Aligned by concurrent_009
                                         input2) = "0101" else
            sig_a when input = "0001" else
            -- Aligned by concurrent_009
            '0';

  -- Violation
  output <= input;

  process is

    variable v : std_logic;

  begin

    sig <= a when b = '1' else
           -- Aligned by sequential_401
           c;
    v := a when b = '1' else
         -- Aligned by variable_assignment_400
         c;
    -- Violation
    sig <= a;

  end process;

end architecture rtl;
