
architecture rtl of e is

begin

  process is
  begin

    if (e = '1') and
       (f = '1')
       then
      q <= '0';
    elsif (g = '1') and
          (h = '1')
          then
      q <= '1';
    end if;

    if (ip_rx_state /= IDLE) and
       ((etrx_fifo_err = '1') or
        (map_ipid_failed = '1') or
        ((etrx_frame_err = '1') and
         (etrx_data_valid = '1'))) then
      q <= '1';
    end if;

  end process;

end architecture rtl;
