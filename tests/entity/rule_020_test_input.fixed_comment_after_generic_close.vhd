
entity ex_nty is
  generic (
    g_A : boolean := true;                     -- Generic map alignment, not aligned with last comment
    g_B : boolean := true;                     -- Generic map alignment
    g_C : positive range 16 to positive'high); -- Comment on line ending generic clause
  port (
    rst_i : in    std_logic;  -- Port comment
    clk_i : in    std_logic); -- Clk
end ex_nty;
