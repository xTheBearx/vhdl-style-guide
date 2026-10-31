
architecture arch of minimal is

  procedure calc_out_procedure is

    procedure nested_procedure_procedure is
    begin
      null;
    end procedure nested_procedure_procedure;

  begin
    nested_procedure_procedure;
  end procedure calc_out_procedure;

begin

end architecture arch;
