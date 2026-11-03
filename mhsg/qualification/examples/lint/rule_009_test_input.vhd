
architecture rtl of fifo is

begin

  process (in1, in2, in3, in4) is
  begin
    if in4 = '0' then
      out1 <= in1;
      out2(3) <= in1;
      out2(0) <= in2;
    else
      out2 <= (others => in3);
    end if;
    out3 <= '0';
    if in4 = '1' then
      out3 <= in2;
    end if;
    case in1 is
      when '0' =>
        out4 <= in2;
        out5 <= in2;
      when others =>
        out4 <= in3;
    end case;
    if in2 = '1' then
      out6 <= in1;
    elsif in3 = '1' then
      out6 <= in2;
    else
      out6 <= '0';
    end if;
  end process;

end architecture rtl;
