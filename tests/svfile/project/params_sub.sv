// A module with two parameters, and a macro params_top.sv uses
`define PARAMS_DEPTH 2

module params_sub #(
    parameter int WIDTH = 8,
    parameter int DEPTH = 4
) (
    input  logic clk_i
);
endmodule
