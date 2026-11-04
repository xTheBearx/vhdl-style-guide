library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library vendorlib;
use vendorlib.components.all;

-- Vendor components without declarations: the stub package of vendorlib takes their ports and generics from the
-- instances

entity stub_top is
  generic (
    WIDTH : integer := 8
  );
  port (
    clk  : in  std_logic;
    d    : in  std_logic_vector(WIDTH - 1 downto 0);
    q    : out std_logic_vector(3 downto 0);
    flag : out std_logic
  );
end entity stub_top;

architecture rtl of stub_top is

  constant LATENCY : natural := 2;

  signal data  : std_logic_vector(WIDTH - 1 downto 0);
  signal count : unsigned(3 downto 0);
  signal link  : std_logic;
  signal r     : std_logic;

begin

  proc_r : process (clk) is
  begin
    if rising_edge(clk) then
      data  <= d;
      count <= count + 1;
    end if;
  end process proc_r;

  u_first : SHIFTER
    generic map (
      INIT    => x"00",
      DEPTH   => LATENCY,
      SCALE   => 1.5,
      ENABLED => true,
      MODE    => "fast",
      DELAY   => 1 ns
    )
    port map (
      CLK   => clk,
      DIN   => data(3 downto 0),
      SEL   => count(0),
      LOAD  => '0',
      PRESET => (others => '0'),
      COUNT => std_logic_vector(count),
      DOUT  => q,
      LAST  => link,
      SPARE => open
    );

  u_second : SHIFTER
    port map (
      CLK   => clk,
      DIN   => data(7 downto 4),
      SEL   => link,
      LOAD  => r,
      PRESET => "0000",
      COUNT => "0000",
      DOUT  => open,
      LAST  => flag,
      SPARE => open
    );

  r <= link and d(0);

end architecture rtl;
