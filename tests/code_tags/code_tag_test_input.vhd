
-- mhsg_off library_008 process_012
library ieee;
use ieee.std_logic_arith.all;
-- mhsg_on library_008 process_012

library ieee;
  use ieee.std_logic.all;

-- mhsg_off : comment
entity FIFO is
  port (
    WRITE_EN : in std_logic;
    READ_EN  : in std_logic
  );
end entity;
-- mhsg_on : comment

-- mhsg_off library_002 : comment
library  ieee;
-- mhsg_on library_002 : comment
library  ieee;
-- mhsg_off : comment
library  ieee;
-- mhsg_on : comment
library  ieee;

-- mhsg_off library_001 process_001


-- mhsg_on library_001


-- mhsg_off case_001

-- mhsg_on  process_001

-- mhsg_off library_001

-- mhsg_on case_001 library_001

architecture rtl of fifo is

begin

-- mhsg_off comment_010
-- Comment
-- Comment
-- mhsg_on comment_010

  a <= b;

end architecture rtl;

-- mhsg_off

architecture rtl of fifo is

  constant CONST : t_rec_vector :=
  (
    (val1 => 1, val2 => 2), -- Despite the tag mhsg_off, MHSG reports missing carriage return here
    (val1 => 3, val2 => 4), -- Despite the tag mhsg_off, MHSG reports missing carriage return here
    (val1 => 5, val2 => 6)  -- Despite the tag mhsg_off, MHSG reports missing carriage return here
  );
-- mhsg_on

begin

  -- mhsg_off length_003 length_001 : comment

  p_length_003_passing : process is
  begin

    a <= b;
    a <= b;
    a <= b;

  end process p_length_003;

  -- mhsg_on length_003

  p_length_003_failing : process is
  begin

    a <= b;
    a <= b;
    a <= b;

  end process p_length_003;

end architecture rtl;

-- mhsg_on comment_010
