library ieee;
use ieee.std_logic_1164.all;

architecture rtl of myentity is

begin

	Pfoo: process (all)
		procedure foooooooo (a : natural; b : std_logic_vector(31 downto 0); c : boolean) is
		begin
		end procedure;
	begin
		if toto = '1' then
			foooooooo(
				a => 5,
				b => (others => '0'),
				c => true
			);
		end if;
	end process;

end architecture;
