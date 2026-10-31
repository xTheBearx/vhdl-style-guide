
package sine_lut_pkg is

  constant sine_lut : lut_type_t :=
  (
    to_unsigned(0, c_AMPL_WIDTH),
    to_unsigned(3, c_AMPL_WIDTH),
    std_logic_vector(resize(x, 8)), to_unsigned(6, c_AMPL_WIDTH)
  );

end package sine_lut_pkg;
