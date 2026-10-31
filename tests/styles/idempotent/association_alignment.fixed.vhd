-- The alignment of => in multiline declarations must be measured from the
-- start of the line, and after the lines have been indented (issue #75).

package p is

  constant c_default_stop_limit : t_alert_counters :=
  (
    note to manual_check => 0,
    others               => 1
  );

end package p;

architecture a of e is

  shared variable rnd_stimuli, rnd_expected : randomptype;
  constant        memory                    : memory_t    := new_memory;
  constant        axi_slave                 : axi_slave_t := new_axi_slave(address_fifo_depth => 1,
                                                                           memory             => memory);
  signal          config                    : t_config    :=
  (
    mismatch_alert_level => ERROR,
    allow_lossy          => false
  );

begin

  process is

    variable v_config : t_config :=
    (
      mismatch_alert_level => ERROR,
      allow_lossy          => false
    );

  begin

  end process;

end architecture a;
