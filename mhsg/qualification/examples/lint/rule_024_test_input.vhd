
architecture rtl of top is

begin

  process (all) is
  begin
    tx_valid <= '0';
    case state is
      when IDLE =>
        state_next <= START;
        tx_valid   <= '1';
      when others =>
        state_next <= IDLE;
    end case;
  end process;

end architecture rtl;
