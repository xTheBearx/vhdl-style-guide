-- File: counter.vhd
-- Function: counts enabled clock cycles and reports when the count wraps
-- Author: mhsg tests
-- Date: 2026-11-08
-- REQ: HWR-200

library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

-- REQ: HWR-201
entity counter is
  generic (
    WIDTH : positive := 8   -- Width of the count
  );
  port (
    clk_i   : in    std_logic;           -- Clock
    rst_i   : in    std_logic;           -- Sync reset
    en_i    : in    std_logic;           -- Count enable
    count_o : out   std_logic_vector(WIDTH - 1 downto 0) -- Count
  );
end entity counter;

architecture rtl of counter is

  type state_t is (IDLE, RUN);

  constant MAX_COUNT : unsigned(WIDTH - 1 downto 0) := (others => '1');

  signal count_r : unsigned(WIDTH - 1 downto 0);
  signal state_r : state_t;

  -- Stops the elaboration of a counter too narrow to wrap
  procedure check_width (constant W : in positive) is
  begin
    assert W > 1 report "WIDTH must be more than 1" severity failure;
  end procedure check_width;

begin

  -- REQ: HWR-202
  proc_count : process (clk_i) is
  begin
    if rising_edge(clk_i) then
      if rst_i = '1' then
        count_r <= (others => '0');
        state_r <= IDLE;
      else
        -- Counts while running, and waits for an enable when idle
        case_state : case state_r is
          when IDLE =>
            if en_i = '1' then
              state_r <= RUN;
            end if;
          when RUN =>
            if count_r = MAX_COUNT then
              state_r <= IDLE;
            end if;
            count_r <= count_r + 1;
          when others =>
            state_r <= IDLE;
        end case case_state;
      end if;
    end if;
  end process proc_count;

  -- Checks the width once, when the design is elaborated
  call_check : check_width(WIDTH);

  -- The count as a vector
  assign_count : count_o <= std_logic_vector(count_r);

end architecture rtl;
