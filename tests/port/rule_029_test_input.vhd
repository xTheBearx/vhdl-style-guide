
entity top is
  port (
    -- Clocks and resets
    clk : in  std_logic;
    rst : in  std_logic;

    data_o : out std_logic;

    ----------------------------------------
    -- AXI interface
    ----------------------------------------
    axi_valid : in  std_logic;
    -- unformatted note
    axi_ready : out std_logic
  );
end entity top;
