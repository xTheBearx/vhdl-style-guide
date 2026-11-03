
architecture rtl of fifo is

  signal sbi_if         : t_sbi_if(addr(C_ADDR_WIDTH - 1 downto 0),
                                   wdata(C_DATA_WIDTH - 1 downto 0),
                                   rdata(C_DATA_WIDTH - 1 downto 0)) := init_sbi_if_signals(C_ADDR_WIDTH);
  signal terminate_loop : std_logic                       := '0';

begin

  proc_test : process is

    variable data_inputs : integer_array_vec_t(input_valid'range) := (
      others => null_integer_array
    );
    variable data_result : integer_array_t := new_1d(
      length=>num_words,
      bit_width=>8
    );

  begin

    wait;

  end process proc_test;

end architecture rtl;
