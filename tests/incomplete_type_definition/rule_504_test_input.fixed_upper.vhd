package p is

  generic (
    type t_private is private;
    type t_scalar is <>;
    type t_discrete is (<>);
    type t_integer is range <>;
    type t_physical is units <>;
    type t_floating is range <> . <>;
    type t_array is array (type is range <>) OF type is private;
    type t_array2 is array (natural range <>) OF std_logic_vector;
    type t_access is access type is private;
    type t_access2 is access integer;
    type t_file is file OF type is private;
    type t_file2 is file OF string;
    type t_plain
  );

end package p;

package p is

  generic (
    TYPE t_private IS PRIVATE;
    TYPE t_scalar IS <>;
    TYPE t_discrete IS (<>);
    TYPE t_integer IS RANGE <>;
    TYPE t_physical IS UNITS <>;
    TYPE t_floating IS RANGE <> . <>;
    TYPE t_array IS ARRAY (type IS RANGE <>) OF TYPE IS PRIVATE;
    TYPE t_array2 IS ARRAY (natural RANGE <>) OF std_logic_vector;
    TYPE t_access IS ACCESS TYPE IS PRIVATE;
    TYPE t_access2 IS ACCESS integer;
    TYPE t_file IS FILE OF TYPE IS PRIVATE;
    TYPE t_file2 IS FILE OF string;
    TYPE t_plain
  );

end package p;
