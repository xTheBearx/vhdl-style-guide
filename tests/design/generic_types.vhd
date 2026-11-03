-- Generics of the types GHDL cannot set from the command line (real, time) or wants quoted (std_logic, character)
library ieee; use ieee.std_logic_1164.all;
entity generic_types_top is
  generic (
    T_g : time := 1 ns;
    E_g : std_logic := '0';
    B_g : boolean := false;
    S_g : string := "ab";
    V_g : std_logic_vector(3 downto 0) := "0000";
    N_g : natural := 0;
    C_g : character := 'a';
    R_g : real := 1.0
  );
  port (q : out std_logic);
end entity;
architecture a of generic_types_top is begin q <= E_g; end architecture;
