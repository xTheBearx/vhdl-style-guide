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
    TYPE t_private is PRIVATE;
    TYPE t_scalar is <>;
    TYPE t_discrete is (<>);
    TYPE t_integer is RANGE <>;
    TYPE t_physical is UNITS <>;
    TYPE t_floating is RANGE <> . <>;
    TYPE t_array is ARRAY (type IS RANGE <>) OF TYPE IS PRIVATE;
    TYPE t_array2 is ARRAY (natural RANGE <>) OF std_logic_vector;
    TYPE t_access is ACCESS TYPE IS PRIVATE;
    TYPE t_access2 is ACCESS integer;
    TYPE t_file is FILE OF TYPE IS PRIVATE;
    TYPE t_file2 is FILE OF string;
    TYPE t_plain
  );

end package p;
