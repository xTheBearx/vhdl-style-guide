
architecture rtl of fifo is

  signal sbi_if         : t_sbi_if(addr(C_ADDR_WIDTH - 1 downto 0),
                                   wdata(C_DATA_WIDTH - 1 downto 0),
                                   rdata(C_DATA_WIDTH - 1 downto 0)) := init_sbi_if_signals(C_ADDR_WIDTH);
  signal terminate_loop : std_logic                       := '0';

begin

end architecture rtl;
