
architecture rtl of e is

begin

  output <= '1' when input = "0000" or (input = "1111" and
                                         -- comment_one
                                         input2) = "0101" else
            sig_a or sig_b when input = "0001" and
                                input = "1001" else
            -- comment_two
            sig_c and sig_d when input = "0010" else
            '0';

end architecture rtl;
