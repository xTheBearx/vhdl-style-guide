library ieee;
use ieee.std_logic_1164.all;

-- A handshake: the data of clk_a is held while its request crosses into clk_b through a chain of four registers,
-- and captured when stage ENABLE_STAGE of the chain allows it (issue 96)
entity handshake_stages is
  generic (
    ENABLE_STAGE : integer range 1 to 4 := 2
  );
  port (
    clk_a  : in  std_logic;
    clk_b  : in  std_logic;
    send_a : in  std_logic;
    data_i : in  std_logic_vector(7 downto 0);
    data_o : out std_logic_vector(7 downto 0);
    req_o  : out std_logic
  );
end entity handshake_stages;

architecture rtl of handshake_stages is

  signal req_a  : std_logic;
  signal data_a : std_logic_vector(7 downto 0);
  signal req_b  : std_logic_vector(1 to 4);
  signal data_b : std_logic_vector(7 downto 0);

begin

  proc_a : process (clk_a) is
  begin
    if rising_edge(clk_a) then
      if send_a = '1' then
        data_a <= data_i;
        req_a  <= not req_a;
      end if;
    end if;
  end process proc_a;

  proc_b : process (clk_b) is
  begin
    if rising_edge(clk_b) then
      req_b <= req_a & req_b(1 to 3);
      if req_b(ENABLE_STAGE) = '1' then
        data_b <= data_a;
      end if;
    end if;
  end process proc_b;

  data_o <= data_b;
  req_o  <= req_b(4);

end architecture rtl;
