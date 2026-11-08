module hier_sync (
    input  logic clk_i,
    input  logic d_i,
    output logic q_o
);
    always_ff @(posedge clk_i) q_o <= d_i;
endmodule
