
architecture rtl of e is

  constant c_width : integer := (8);

begin

  process (clk) is
  begin

    if (rst) then
    end if;

    while (busy) loop
    end loop;

    a <= f(d) and x(0) and std_logic_vector(k);
    b <= t'(x);
    c <= (others => '0');
    d <= and(e) or xor (g);
    q <= (a and b) or c;

    -- Violations below

    if (sync_reset) = '1' then
      a <= (b);
      a <= (b) and (c);
      a <= not(b);
      a <= ('1') & ("0101");
    end if;

    case sel is
      when (idle) =>
        null;
    end case;

  end process;

  u1 : entity work.x
    port map (
      WEA(0) => (wea)
    );

  y <= (z) when sel = '1' else w;

end architecture rtl;
