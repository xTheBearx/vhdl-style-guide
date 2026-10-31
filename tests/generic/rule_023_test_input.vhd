
entity fifo is
  generic (
    -- Widths
    G_WIDTH : integer := 8;
    G_DEPTH : integer := 16;

    G_DEBUG : boolean := false;
    -- unformatted note
    G_SEED  : integer := 1
  );
end entity fifo;

architecture rtl of fifo is

  component ram is
    generic (
      G_SIZE : integer := 4
    );
  end component ram;

begin

end architecture rtl;
