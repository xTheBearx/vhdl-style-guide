
entity top is
  port (
    -- Data
    clk    : in  std_logic; -- main clock
    a_i    : in  std_logic;
    data_o : out std_logic; -- result

    rst    : in std_logic;
    rst_n  : in std_logic
  );
end entity top;

architecture rtl of top is

  component comp is
    port (
      z : out std_logic;
      a : in  std_logic
    );
  end component comp;

begin

end architecture rtl;

entity multi_line is
  port (
    b_o : out std_logic;
    a_i : in
      std_logic
  );
end entity multi_line;

entity ordered is
  port (
    clk  : in  std_logic;
    rst  : in  std_logic;
    a_i  : in  std_logic;
    z_io : inout std_logic;
    b_o  : out std_logic
  );
end entity ordered;
