
entity fifo is
  generic (
    G_ADDR_WIDTH : integer := 4;
    G_DEPTH      : integer := 2 ** G_ADDR_WIDTH; -- uses G_ADDR_WIDTH
    G_WIDTH      : integer := 8
  );
end entity fifo;

entity fifo2 is
  generic (
    G_DATA_WIDTH : integer := 8;
    G_ADDR_WIDTH : integer := G_DATA_WIDTH / 2 -- may stay after G_DATA_WIDTH
  );
end entity fifo2;

package pkg is
  generic (
    type t_data;
    a_default : t_data
  );
end package pkg;

-- Violations below

entity fifo3 is
  generic (
    G_WIDTH : integer := 8;
    G_DEPTH : integer := 16
  );
end entity fifo3;

architecture rtl of fifo3 is

  component ram is
    generic (
      G_WIDTH : integer := 8;
      G_ADDR_WIDTH : integer := 4;
      G_DEPTH : integer := 2 ** G_ADDR_WIDTH
    );
  end component ram;

begin
end architecture rtl;
