
architecture ARCH of ENTITY1 is

begin

  U_INST1 : INST1

    generic map (
      G_GEN_1 => 3
    )
    port map (
      PORT_1 => w_port_1
    );

  U_INST1 : INST1
    generic map (
      G_GEN_1 => 3
    )
    -- comment
    port map (
      PORT_1 => w_port_1
    );

  -- Violations below

  U_INST1 : INST1
    generic map (
      G_GEN_1 => 3
    )

    port map (
      PORT_1 => w_port_1
    );

  U_INST1 : INST1


    port map (
      PORT_1 => w_port_1
    );

end architecture ARCH;
