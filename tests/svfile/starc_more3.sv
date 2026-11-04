// Violations of the STARC checks of sv_file_005, sv_naming_016, sv_module_004 to 006 and sv_dimension_004
`define WIDTH 8
`include "definitions.v"
module starc_more3 (
    input  logic       clk,
    input  logic [7:0] data_i,
    output logic       ready_o,
    output logic       q_o
);
    logic count_o;

    and g_and (q_o, clk, count_o);
    assign ready_o = 1'b1;
endmodule
