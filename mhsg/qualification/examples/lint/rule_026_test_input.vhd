
entity fifo is
  port (
    d : in std_logic
  );
end entity fifo;

architecture rtl of top is

  component fifo is
    port (
      d : in std_logic
    );
  end component fifo;

begin

  u_fifo : fifo
    port map (
      d => a
    );

  u_direct : entity work.fifo
    port map (
      d => a
    );

  u_buf : bufg
    port map (
      i => clk_in,
      o => clk
    );

end architecture rtl;
