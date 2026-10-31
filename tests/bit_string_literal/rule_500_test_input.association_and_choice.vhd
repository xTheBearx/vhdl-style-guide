library ieee;
  use ieee.std_logic_1164.all;

entity b is
  port (
    a : in    std_logic_vector(7 downto 0);
    b : out   std_logic_vector(7 downto 0)
  );
end entity b;

architecture a of b is

  procedure foo (
    a : std_logic_vector;
    b : boolean
  ) is
  begin

  end procedure foo;

  procedure bar (
    signal a : std_logic_vector
  ) is
  begin

    foo(X"5a", a = X"5a");  -- 1

  end procedure bar;

  component my_component is
    port (
      c : in    std_logic_vector(7 downto 0)
    );
  end component my_component;

begin

  inst : component my_component
    port map (
      c => X"5a"  -- 2
    );

  proc : process is
  begin

    case a is

      when X"5a" =>  -- 3

        null;

      when others =>

        null;

    end case;

  end process proc;

end architecture a;
