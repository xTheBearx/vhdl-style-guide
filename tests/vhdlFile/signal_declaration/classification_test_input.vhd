
architecture RTL of FIFO is

  signal fifo_wr : std_logic;

  signal fifo_wr : std_logic_vector(3 downto 0);

  signal fifo_wr : std_logic_vector(3 downto 0) := "000";

  signal fifo_wr, fifo_rd, fifo_empty : std_logic := '1';

  signal fifo_rd : fifo_wr'subtype;

  signal slv : std_logic_vector(integer_range_subtype);

  signal slv : std_logic_vector(open);

  signal slv : std_logic_vector(open) bus;

  signal slv : std_logic_vector(open) register;

  signal sig_inst : record_array_type(index).record_element'subtype;

  signal sig_inst : array_type(1)(2)'subtype;

  signal sig_inst : record_array_type(index).record_element(3)'element;

begin

end architecture RTL;
