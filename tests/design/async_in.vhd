-- Asynchronous inputs of the top level, declared async in the design configuration: a synchronizer straight from a
-- port, one behind a gate, a single register, and a vector synchronized bit by bit

library ieee;
  use ieee.std_logic_1164.all;

entity async_in_top is
  port (
    clk    : in    std_logic;
    a_i    : in    std_logic;
    b_i    : in    std_logic;
    c_i    : in    std_logic;
    d_i    : in    std_logic;
    e_i    : in    std_logic_vector(1 downto 0);
    a_o    : out   std_logic;
    bc_o   : out   std_logic;
    d_o    : out   std_logic;
    e_o    : out   std_logic_vector(1 downto 0)
  );
end entity async_in_top;

architecture rtl of async_in_top is

  signal a_meta  : std_logic;
  signal a_sync  : std_logic;
  signal bc_meta : std_logic;
  signal bc_sync : std_logic;
  signal d_r     : std_logic;
  signal e_meta  : std_logic_vector(1 downto 0);
  signal e_sync  : std_logic_vector(1 downto 0);

begin

  proc_sync : process (clk) is
  begin
    if rising_edge(clk) then
      a_meta  <= a_i;
      a_sync  <= a_meta;
      bc_meta <= b_i and c_i;
      bc_sync <= bc_meta;
      d_r     <= d_i;
      e_meta  <= e_i;
      e_sync  <= e_meta;
    end if;
  end process proc_sync;

  a_o  <= a_sync;
  bc_o <= bc_sync;
  d_o  <= d_r;
  e_o  <= e_sync;

end architecture rtl;
