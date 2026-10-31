package p is

  generic (
    type t_private IS private;
    type t_scalar IS <>;
    type t_discrete IS (<>);
    type t_integer IS range <>;
    type t_physical IS units <>;
    type t_floating IS range <> . <>;
    type t_array IS array (type is range <>) of type is private;
    type t_array2 IS array (natural range <>) of std_logic_vector;
    type t_access IS access type is private;
    type t_access2 IS access integer;
    type t_file IS file of type is private;
    type t_file2 IS file of string;
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
