
architecture rtl of fifo is

  type t_record is record
    a : std_logic;
    b : std_logic;
  end record t_record;

  type t_record is record
    a : std_logic;
    b : std_logic;
  end record t_record;

  type t_record is record a : std_logic; b : std_logic; end record;

  type my_array1 is array (natural range 0 to 3) of std_logic ;   -- white space before semicolon here

begin

end architecture rtl;

package body pkg is

  type t_protected is protected body

    type t_record_a is record
      a : std_logic;
    end record t_record_a;

    type t_record_b is record
      b : std_logic;
    end record t_record_b;

  end protected body t_protected ;

end package body pkg;
