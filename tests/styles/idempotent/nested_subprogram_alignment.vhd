-- Declarations in a subprogram declared inside another subprogram are aligned
-- on their own, not together with the enclosing subprogram (issue #77).

package body p is

  impure function get_id (name : string) return id_t is
    impure function validate_name (name : string) return boolean is
      function join (s1, s2 : string) return string is
        constant a : string := s1;
        variable longer_name : integer;
      begin
        return s1 & s2;
      end;
      variable x : integer;
      constant long_name_here : boolean := true;
      procedure helper;
      variable after_declaration : integer;
    begin
      return true;
    end;
    constant stripped_name : string := strip(name, ":");
    constant real_parent : id_t := get_real_parent(parent);
  begin
    return null_id;
  end;

end package body p;
