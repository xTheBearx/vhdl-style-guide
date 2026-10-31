
entity fifo is
  generic (
    type generic_data_type
  );
  port (
    data_in : generic_data_type
  );
end entity fifo;

architecture rtl of fifo is

  component buffer is
    generic (
        type generic_data_type
    );
    port (
        data_in : generic_data_type
    );
  end component buffer;

begin

  buf1 : buffer
    generic map (
        generic_data_type => std_logic
    )
    port map (
        data_in => '0'
    );

end architecture rtl;

-- VHDL-2019 incomplete type definitions

package p is
  generic (
    type t_private is private;
    type t_scalar is <>;
    type t_discrete is (<>);
    type t_integer is range <>;
    type t_physical is units <>;
    type t_floating is range <> . <>;
    type t_array is array (type is range <>) of type is private;
    type t_array2 is array (natural range <>, type is (<>)) of std_logic_vector;
    type t_array3 is array (natural range 0 to 7) of integer;
    type t_access is access type is private;
    type t_access2 is access integer;
    type t_file is file of type is private;
    type t_file2 is file of string;
    type t_plain
  );
end package p;
