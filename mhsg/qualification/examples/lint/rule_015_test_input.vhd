
architecture rtl of top is

begin

  -- synthesis translate_off
  assert width > 0 report "width must be positive";
  -- synthesis translate_on

  process (all) is
  begin
    case sel is
      when '0' => a <= b;
      -- coverage off
      when others => null;
      -- coverage on
    end case;
  end process;

end architecture rtl;
