
architecture arch of minimal is

  procedure calc_out_procedure is

    procedure nested_procedure_procedure is
    begin
      null;
    end procedure;

  begin
    nested_procedure_procedure;
  end procedure;

begin

end architecture arch;
