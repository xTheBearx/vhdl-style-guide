
library ieee;
    use ieee.std_logic_1164.all;

entity four_spaces is
    port (
        clk : in    std_logic;
        d   : in    std_logic;
        q   : out   std_logic
    );
end entity four_spaces;

architecture rtl of four_spaces is

begin

    proc_q : process (clk) is
    begin

        if rising_edge(clk) then
            q <= d;
        end if;

    end process proc_q;

end architecture rtl;
