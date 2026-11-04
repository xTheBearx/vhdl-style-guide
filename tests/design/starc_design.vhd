library ieee;
use ieee.std_logic_1164.all;

entity starc_driver is
  port (
    oe : in    std_logic;
    d  : in    std_logic;
    y  : inout std_logic
  );
end entity starc_driver;

architecture rtl of starc_driver is
begin

  y <= d when oe = '1' else 'Z';

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity starc_design_top is
  port (
    clk     : in    std_logic;
    reset   : in    std_logic;
    oe      : in    std_logic_vector(5 downto 0);
    a       : in    std_logic;
    we      : in    std_logic;
    address : in    unsigned(3 downto 0);
    din     : in    std_logic_vector(1 downto 0);
    pins    : inout std_logic;
    pin_six : inout std_logic;
    q       : out   std_logic_vector(3 downto 0)
  );
end entity starc_design_top;

architecture rtl of starc_design_top is

  type ram_t is array (0 to 15) of std_logic_vector(1 downto 0);

  signal ram    : ram_t;
  signal data_r : std_logic_vector(1 downto 0);

begin

  -- Five tri-state drivers are allowed, six are not
  gen_five : for i in 0 to 4 generate
    u_driver : entity work.starc_driver
      port map (
        oe => oe(i),
        d  => a,
        y  => pins
      );
  end generate gen_five;

  gen_six : for i in 0 to 5 generate
    u_driver : entity work.starc_driver
      port map (
        oe => oe(i),
        d  => a,
        y  => pin_six
      );
  end generate gen_six;

  -- An asynchronous reset
  process (clk, reset) is
  begin
    if reset = '1' then
      q(0) <= '0';
    elsif rising_edge(clk) then
      q(0) <= a;
    end if;
  end process;

  -- The same reset as a synchronous reset
  process (clk) is
  begin
    if rising_edge(clk) then
      if reset = '1' then
        q(1) <= '0';
      else
        q(1) <= a;
      end if;
    end if;
  end process;

  process (clk) is
  begin
    if rising_edge(clk) then
      if we = '1' then
        ram(to_integer(address)) <= din;
      end if;
      data_r <= ram(to_integer(address));
      -- The memory output decides a condition
      if data_r(0) = '1' then
        q(2) <= a;
      else
        q(2) <= not a;
      end if;
      -- A case statement that assigns unknown values in its others choice is not reported
      case data_r is
        when "00" => q(3) <= a;
        when "01" => q(3) <= not a;
        when others => q(3) <= 'X';
      end case;
    end if;
  end process;

end architecture rtl;
