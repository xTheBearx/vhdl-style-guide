
library ieee;
    use ieee.std_logic_1164.all;

entity long_line is
    port (
        clk : in    std_logic;
        d   : in    std_logic;
        q   : out   std_logic
    );
end entity long_line;

architecture rtl of long_line is

begin

    proc_q : process (clk) is
    begin

        if rising_edge(clk) then
            q <= d; -- this comment makes the line longer than eighty characters!
        end if;

    end process proc_q;

end architecture rtl;
