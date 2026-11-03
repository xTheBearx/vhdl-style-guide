
architecture rtl of top is

  type state_t is (IDLE, START);
  signal state     : state_t;
  signal fsm_state : std_logic_vector(1 downto 0);
  signal sel       : std_logic_vector(1 downto 0);

begin

  process (clk) is
  begin
    if rising_edge(clk) then
      case state is
        when IDLE => state <= START;
        when others => state <= IDLE;
      end case;
      case fsm_state is
        when "00" => fsm_state <= "01";
        when others => fsm_state <= "00";
      end case;
      case sel is
        when "00" => q <= '1';
        when others => q <= '0';
      end case;
    end if;
  end process;

end architecture rtl;
