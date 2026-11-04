`ifndef DIR_SV
  `define DIR_SV
`define WIDTH 8
`define MAX(a, b) \
    ((a) > (b) ? (a) : (b))
module dir (
    input  logic clk_i,
    input  logic d_i,
    output logic q_o
);
    logic a_q;
    always_ff @(posedge clk_i) begin
        `ifdef RESET_ALL
        a_q <= 1'b0;
        `else
        a_q <= d_i;
        `endif
          `ASSERT(a_known, !$isunknown(a_q))
    end
`include "x.svh"
    assign q_o = a_q;
  `undef WIDTH
endmodule
`endif
