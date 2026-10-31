
architecture RTL of FIFO is

begin

  process

  begin

    if a = '1' then
      b <= '0';
    elsif c = '1' then
      b <= '1';
    end if;

    -- Violations below
    if a = '1' then
      b <= '0';
    elsif c = '1' then
      b <= '1';
    end if;

    if a = '1' then
      b <= '0';
    elsif                      c = '1' then
      b <= '1';
    end if;

    if                   a = '1' then
      b <= '0';
    elsif                      c = '1' and
   d = '0' then
      b <= '1';
    end if;

    -- Comments between keyword and expression should not be merged (issue 1585)
    if a = '1' then
      b <= '0';
    elsif
      -- wait here until the sub-steps are
      -- complete and the data is consumed
      (b = '1') and
      (c = '1') then
      b <= '1';
    end if;

    if

      -- comment after blank line
      a = '1' then
      b <= '0';
    end if;

  end process;

end architecture RTL;
