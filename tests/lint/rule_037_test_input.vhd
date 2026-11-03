
architecture rtl of e is
  type state_t is (IDLE, RUN, DONE, ERROR);
  signal state : state_t;
begin

  process (clk) is
  begin
    if rising_edge(clk) then
      case state is
        when IDLE =>
          if start = '1' then
            state <= RUN;
          end if;
        when RUN =>
          if last = '1' then
            state <= DONE;
          end if;
        when DONE =>
          null;
        when others =>
          state <= IDLE;
      end case;
    end if;
  end process;

end architecture rtl;
