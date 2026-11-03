// The top of a design of two files: lint of the run checks the instance against sub.sv
`include "widths.svh"

module top (
    input  logic                clk_i,
    input  logic [`WIDTH - 1:0] a_i,
    output logic [`WIDTH - 1:0] y_o
);
    logic spare;

    sub u_sub (
        .clk_i(clk_i),
        .d_i  (a_i),
        .q_o  (y_o)
    );

`ifdef EXTRA
    logic extra;
`endif
endmodule
