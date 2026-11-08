module hier_b (
    input  logic clk_i,
    input  logic b_i,
    output logic b_o
);
    hier_sync u_sync (
        .clk_i(clk_i),
        .d_i  (b_i),
        .q_o  (b_o)
    );
endmodule
