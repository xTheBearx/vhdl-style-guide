
entity fifo is
  generic (
    -- Widths
    G_WIDTH      : integer := 8;
    G_DEPTH      : integer := 16;

    -- Derived
    G_ADDR_WIDTH : integer := G_DEPTH / 4;
    G_DEBUG      : boolean := false
  );
end entity fifo;
