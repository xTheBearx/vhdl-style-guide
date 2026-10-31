
entity ex_nty is
  generic (
    g_A : boolean := true; -- Generic map alignment, not aligned with last comment
    g_B : boolean := true; /* Generic map alignment
                              Second line
                           */
    g_C : boolean := true; /* Generic map alignment
                              Second line
                           */
    g_D : boolean := true; -- REMOVE ME
    g_E : boolean := true);
  port (
    rst_i : in    std_logic; /* Reset
                                Can reset something
                             */
    en_i  : in    std_logic; /* Enable
                                Can enable something
                             */
    clk_i : in    std_logic; -- REMOVE ME
    sig_i : in    std_logic);
end ex_nty;

architecture rtl of ex_nty is

  signal   signal1 : std_logic; -- C1
  signal   signal2 : std_logic; /* C2a
                                   C2b
*/

  signal   signal3 : std_logic; -- REMOVE ME
  signal   signal4 : std_logic; /* C4a
                                   C4b
                                   C4c
                                */

begin

end rtl;
