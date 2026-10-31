
library ieee;
  use ieee.std_logic_1164.all;
  use work.pkg.slv_data;

architecture rtl of example is

  type t_rec is record
    sl_Valid : std_logic;
    slv_Data : std_logic_vector(7 downto 0);
  end record t_rec;

  -- Declared with two capitalizations, so not checked
  type t_rec_a is record
    Mode : std_logic;
  end record t_rec_a;

  type t_rec_b is record
    MODE : std_logic;
  end record t_rec_b;

  signal rec   : t_rec;
  signal rec_a : t_rec_a;

  constant c_good : t_rec := (sl_Valid => '0', slv_Data => (others => '0'));

  -- Violations below

  constant c_rec : t_rec := (sl_valid => '0', SLV_DATA => (others => '0'));

begin

  rec.sl_Valid <= '1';
  rec_a.mode   <= '1';

  -- Violations below

  rec.SL_VALID <= c_rec.slv_data(0);

end architecture rtl;
