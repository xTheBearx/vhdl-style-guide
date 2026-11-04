library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- A gray coded pointer crosses bit by bit through synchronizer black boxes, and the data it points at is captured
-- only when the synchronized pointer allows it, as in a FIFO
entity box_gray_top is
  port (
    clk_a  : in    std_logic;
    clk_b  : in    std_logic;
    rst_n  : in    std_logic;
    push   : in    std_logic;
    din    : in    std_logic_vector(7 downto 0);
    dout   : out   std_logic_vector(7 downto 0);
    valid  : out   std_logic
  );
end entity box_gray_top;

architecture rtl of box_gray_top is

  component sync_cell is
    port (
      clk_i    : in    std_logic;
      rst_ni   : in    std_logic;
      serial_i : in    std_logic;
      serial_o : out   std_logic
    );
  end component;

  signal wptr_bin  : unsigned(3 downto 0);
  signal wptr_gray : unsigned(3 downto 0);
  signal wptr_sync : std_logic_vector(3 downto 0);
  signal rptr_gray : std_logic_vector(3 downto 0);
  signal data_a    : std_logic_vector(7 downto 0);
  signal data_b    : std_logic_vector(7 downto 0);

begin

  process (clk_a, rst_n) is
  begin
    if rst_n = '0' then
      wptr_bin  <= (others => '0');
      wptr_gray <= (others => '0');
      data_a    <= (others => '0');
    elsif rising_edge(clk_a) then
      if push = '1' then
        wptr_bin  <= wptr_bin + 1;
        wptr_gray <= (wptr_bin + 1) xor shift_right(wptr_bin + 1, 1);
        data_a    <= din;
      end if;
    end if;
  end process;

  gen_sync : for i in 0 to 3 generate
    u_sync : component sync_cell
      port map (
        clk_i    => clk_b,
        rst_ni   => rst_n,
        serial_i => wptr_gray(i),
        serial_o => wptr_sync(i)
      );
  end generate gen_sync;

  process (clk_b, rst_n) is
  begin
    if rst_n = '0' then
      rptr_gray <= (others => '0');
      data_b    <= (others => '0');
    elsif rising_edge(clk_b) then
      if wptr_sync /= rptr_gray then
        rptr_gray <= wptr_sync;
        data_b    <= data_a;
      end if;
    end if;
  end process;

  dout  <= data_b;
  valid <= '1' when wptr_sync /= rptr_gray else '0';

end architecture rtl;
