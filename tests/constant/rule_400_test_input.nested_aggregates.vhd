
architecture rtl of e is
        constant c_reg_desc : t_reg_descriptor_array(c_reg_count - 1 downto 0) :=
        (
            c_core_id_and_rev_reg_idx => (
                                             addr_offset => c_core_id_and_rev_reg_idx * 4,
                                             size_words  => 1,
                                             writable    => false,
                                             readable    => true,
                                             reset_val   => (others => '0')
                                         ),
            c_control_reg_idx         => (
                                             addr_offset => c_control_reg_idx * 4,
                                             size_words  => 1,
                                             writable    => true,
                                             readable    => true,
                                             reset_val   => (others => '0')
                                         )
        );
begin
end architecture rtl;
