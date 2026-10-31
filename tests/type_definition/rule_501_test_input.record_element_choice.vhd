
architecture rtl of example is

  type t_state is (BIT_LENGTH, MUL, DATA_STREAM_LENGTH);

  type t_reg is record
    state              : t_state;
    data_stream_length : std_logic_vector(21 downto 0);
  end record;

  constant C_REG_T_INIT : t_reg := (
    state              => BIT_LENGTH,
    data_stream_length => (others => '0')
  );

begin

  process is
  begin
    case state is
      when data_stream_length =>
        null;
      when others =>
        null;
    end case;
  end process;

end architecture rtl;
