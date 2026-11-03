
architecture rtl of top is

  type state_t is (IDLE, START, STOP);
  signal state  : state_t;
  signal state2 : state_t;
  signal sel    : std_logic_vector(1 downto 0);

  attribute fsm_safe_state : string;
  attribute fsm_safe_state of state2 : signal is "reset_state";

begin

  process (clk) is
  begin
    if rising_edge(clk) then
      case state is
        when IDLE => state <= START;
        when START => state <= STOP;
        when others => null;
      end case;
      case state2 is
        when IDLE => state2 <= START;
        when others => state2 <= IDLE;
      end case;
      case sel is
        when "00" => q <= '1';
        when others => null;
      end case;
    end if;
  end process;

end architecture rtl;
