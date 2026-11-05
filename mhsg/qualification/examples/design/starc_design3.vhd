library ieee;
use ieee.std_logic_1164.all;

-- A reset synchronizer in a block of its own: where resets are made
entity starc3_rstgen is
  port (
    clk     : in    std_logic;
    rst_n_i : in    std_logic;
    rst_n_o : out   std_logic
  );
end entity starc3_rstgen;

architecture rtl of starc3_rstgen is

  signal s1 : std_logic;
  signal s2 : std_logic;

begin

  process (clk, rst_n_i) is
  begin
    if rst_n_i = '0' then
      s1 <= '0';
      s2 <= '0';
    elsif rising_edge(clk) then
      s1 <= '1';
      s2 <= s1;
    end if;
  end process;

  rst_n_o <= s2;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

-- A block of I/O cells only
entity starc3_io is
  port (
    pad : in    std_logic;
    o   : out   std_logic
  );
end entity starc3_io;

architecture rtl of starc3_io is

  component IBUF is
    port (
      I : in    std_logic;
      O : out   std_logic
    );
  end component;

begin

  u_ibuf : component IBUF
    port map (
      I => pad,
      O => o
    );

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

-- A block with an I/O cell, and a clock divider next to the registers it clocks
entity starc3_core is
  port (
    clk   : in    std_logic;
    rst_n : in    std_logic;
    pad2  : in    std_logic;
    d     : in    std_logic;
    q     : out   std_logic
  );
end entity starc3_core;

architecture rtl of starc3_core is

  component IBUF is
    port (
      I : in    std_logic;
      O : out   std_logic
    );
  end component;

  signal din2   : std_logic;
  signal div_q  : std_logic;
  signal slow_r : std_logic;

begin

  u_ibuf2 : component IBUF
    port map (
      I => pad2,
      O => din2
    );

  process (clk, rst_n) is
  begin
    if rst_n = '0' then
      div_q <= '0';
    elsif rising_edge(clk) then
      div_q <= not div_q;
    end if;
  end process;

  process (div_q) is
  begin
    if rising_edge(div_q) then
      slow_r <= din2 xor d;
    end if;
  end process;

  q <= slow_r;

end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity starc3_top is
  port (
    clk_a  : in    std_logic;
    clk_b  : in    std_logic;
    rst_n  : in    std_logic;
    pad    : in    std_logic;
    pad2   : in    std_logic;
    d      : in    std_logic;
    q_a    : out   std_logic;
    q_b    : out   std_logic;
    q_n    : out   std_logic;
    q_core : out   std_logic;
    q_ip   : out   std_logic
  );
end entity starc3_top;

architecture rtl of starc3_top is

  component vendor_ip is
    port (
      clk_i   : in    std_logic;
      d_i     : in    std_logic;
      ready_o : out   std_logic
    );
  end component;

  signal rst_sync_n : std_logic;
  signal pad_d      : std_logic;
  signal ready      : std_logic;
  signal a_r        : std_logic;
  signal b_r        : std_logic;
  signal n_r        : std_logic;
  signal ip_r       : std_logic;

begin

  u_rst : entity work.starc3_rstgen
    port map (
      clk     => clk_a,
      rst_n_i => rst_n,
      rst_n_o => rst_sync_n
    );

  u_io : entity work.starc3_io
    port map (
      pad => pad,
      o   => pad_d
    );

  u_core : entity work.starc3_core
    port map (
      clk   => clk_a,
      rst_n => rst_sync_n,
      pad2  => pad2,
      d     => pad_d,
      q     => q_core
    );

  -- A clock into a data input of a black box, and its asynchronous output used as a clock
  u_ip : component vendor_ip
    port map (
      clk_i   => clk_a,
      d_i     => clk_b,
      ready_o => ready
    );

  -- Registers in the top level
  process (clk_a, rst_sync_n) is
  begin
    if rst_sync_n = '0' then
      a_r <= '0';
    elsif rising_edge(clk_a) then
      a_r <= d;
    end if;
  end process;

  -- A crossing from clk_a to clk_b without a latch
  process (clk_b) is
  begin
    if rising_edge(clk_b) then
      b_r <= a_r;
    end if;
  end process;

  -- The other edge of clk_a
  process (clk_a) is
  begin
    if falling_edge(clk_a) then
      n_r <= a_r;
    end if;
  end process;

  process (ready) is
  begin
    if rising_edge(ready) then
      ip_r <= d;
    end if;
  end process;

  q_a    <= a_r;
  q_b    <= b_r;
  q_n    <= n_r;
  q_ip   <= ip_r;

end architecture rtl;
