
library ieee;
  use ieee.std_logic_1164.all;

library work;
  use work.fsm_pkg.all;

entity fsm_user is
  port (
    clk_i   : in    std_logic;
    start_i : in    std_logic;
    last_i  : in    std_logic;
    busy_o  : out   std_logic
  );
end entity fsm_user;

architecture rtl of fsm_user is

  signal state_r : state_t;

begin

  proc_state : process (clk_i) is
  begin

    if rising_edge(clk_i) then

      case state_r is

        when IDLE =>

          if (start_i = '1') then
            state_r <= RUN;
          end if;

        when RUN =>

          if (last_i = '1') then
            state_r <= DONE;
          end if;

        when DONE =>

          null;

        when others =>

          null;

      end case;

    end if;

  end process proc_state;

  busy_o <= '1' when state_r = RUN else '0';

end architecture rtl;
