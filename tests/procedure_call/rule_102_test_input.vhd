
architecture rtl of fifo is

begin

  connect_ports(port_1 => data, port_2 => enable);
  connect_ports(port_1=> data, port_2=> enable);

  process is
  begin

    connect_ports(port_1 => data, port_2 => enable);
    connect_ports(port_1=> data, port_2=>enable);
    connect_ports(
      port_1   => data,
      port_2=> enable
    );

  end process;

end architecture rtl;
