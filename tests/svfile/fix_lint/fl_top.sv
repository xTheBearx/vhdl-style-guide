module fl_top (
    input  logic a_i,
    output logic y_o,
    output logic z_o
);

  fl_sub u_sub (
        .a_i(a_i),
        .y_o(y_o)
    );

endmodule
