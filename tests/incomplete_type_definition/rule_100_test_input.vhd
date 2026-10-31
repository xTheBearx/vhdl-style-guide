package p is

  generic (
    type t_private is private;
    type t_scalar is <>;
    type t_discrete is (<>);
    type t_integer is range <>;
    type t_physical is units <>;
    type t_floating is range <> . <>;
    type t_array is array (type is range <>) of type is private;
    type t_array2 is array (natural range <>) of std_logic_vector;
    type t_access is access type is private;
    type t_access2 is access integer;
    type t_file is file of type is private;
    type t_file2 is file of string;
    type t_plain
  );

end package p;

package p is

  generic (
    type t_data is array (type is range <>)    of type is private;
    type t_data is array (type is range <>)    of type is private
  );

end package p;
