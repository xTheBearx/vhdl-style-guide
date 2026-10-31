-- The end keyword and designator of a subprogram declared inside another
-- subprogram must be added to its own end, not to the enclosing one (issue #76).

package body p is

  function outer return integer is
    function inner return integer is
    begin
      return 1;
    end;
  begin
    return inner;
  end;

  procedure outer_proc is
    procedure inner_proc is
    begin
      null;
    end;
  begin
    inner_proc;
  end;

end package body p;
