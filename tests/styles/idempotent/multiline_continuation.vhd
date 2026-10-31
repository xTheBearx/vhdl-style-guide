-- The continuation lines must be aligned after the assignment operators
-- have been aligned, so a second fix does not move them again (issue #74).

package body p is

  procedure proc is
    constant c_proc_name : string := "gmii_read";
    constant c_proc_call : string := c_proc_name & "(" -- First part
                                     & ", " & ")";
    variable v_normalised_addr : unsigned(7 downto 0) := (others => '0');
  begin
  end procedure proc;

end package body p;

architecture rtl of e is
begin

  process is
    constant BIN_LENS : integer_vector :=
        BinLengths(
           Bin1, Bin2,
           Bin3, Bin4
         ) ;
    variable BinIndex : integer_vector(1 to BIN_LENS'length) := (others => 1) ;
  begin
  end process;

end architecture rtl;
