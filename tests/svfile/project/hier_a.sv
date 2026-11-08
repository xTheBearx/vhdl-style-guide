module hier_a (
    input  logic clk_i,
    input  logic a_i,
    output logic a_o
);
    // hier_b instantiates hier_sync too, so in a run with hier_b.sv its ports are not checked
    hier_sync u_sync (
        .clk_i(clk_i),
        .d_i  (a_i),
        .q_o  (a_o)
    );
endmodule
