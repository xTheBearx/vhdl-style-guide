
architecture rtl of fifo is

  type DECODER_STATE_T is (IDLE, RUN);

begin

  BLK : block is

    type   FIRST_BUNCH_POS_T is array (0 to 1) of integer;
    signal first_bunch_pos : FIRST_BUNCH_POS_T;
    signal state           : DECODER_STATE_T;
    signal other           : STD_LOGIC;

  begin

  end block BLK;

end architecture rtl;
