library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity fsm_top is
  port (
    clk   : in  std_logic;
    rst   : in  std_logic;
    start : in  std_logic;
    ack   : in  std_logic;
    nack  : in  std_logic;
    busy  : out std_logic
  );
end entity fsm_top;

architecture rtl of fsm_top is
  type state_t is (IDLE, RUN, DONE, WAIT_ACK, HOLD, SPIN, ERROR);
  signal state : state_t;
  signal count : unsigned(2 downto 0);
begin
  process (clk, rst) is
  begin
    if rst = '1' then
      state <= IDLE;
      count <= (others => '0');
    elsif rising_edge(clk) then
      case state is
        when IDLE =>
          if start = '1' then
            state <= RUN;
          end if;
        when RUN =>
          count <= count + 1;
          if count = 5 then
            state <= DONE;
          elsif count = 7 then
            -- count is reset on leaving RUN: never 7 here
            state <= ERROR;
          end if;
        when DONE =>
          count <= (others => '0');
          state <= WAIT_ACK;
        when WAIT_ACK =>
          if ack = '1' then
            state <= IDLE;
          elsif nack = '1' then
            state <= HOLD;
          end if;
        when HOLD =>
          state <= SPIN;
        when SPIN =>
          -- never goes back to IDLE: HOLD and SPIN lock up
          state <= HOLD;
        when ERROR =>
          state <= IDLE;
      end case;
    end if;
  end process;
  busy <= '0' when state = IDLE else '1';
end architecture rtl;
