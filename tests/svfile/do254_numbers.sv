// Module: do254_numbers
// Function: numbers that DO-254 CP3 (sv_literal_010) reports, and those it does not
// Author: mhsg tests
// Date: 2026-11-08
module do254_numbers (
    input  logic       clk_i,
    input  logic       rst_i,
    input  logic [2:0] idx_i,
    output logic [7:0] char_o,
    output logic       tick_o
);

    logic [7:0] char;

    // The values of the case items are not reported; the statements of every item are, default included
    always_comb begin
        case (idx_i)
            3'd5:    char = 8'h0d;
            default: char = 8'h0a;
        endcase
    end

    // A number in an ordinary statement
    assign char_o = char + 8'd3;

    // Parameter values given to an instance, by name and in order
    baud_gen #(.CLK_HZ(100_000_000), .WIDTH(12)) u_named (.clk_i(clk_i), .rst_i(rst_i), .tick_o(tick_o));
    baud_gen #(100_000_000, 12) u_ordered (.clk_i(clk_i), .rst_i(rst_i), .tick_o());

endmodule
