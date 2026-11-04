// A Verilog top that sets the generics of VHDL entities: by name, by position, in a generate block and with an
// expression, which cannot be passed on
module vtop_generics (
    input  wire        clk,
    input  wire [7:0]  a,
    output wire [7:0]  y,
    input  wire [15:0] b,
    output wire [15:0] z,
    input  wire [3:0]  c,
    output wire [3:0]  w,
    input  wire [7:0]  e,
    output wire [7:0]  v
);
    localparam integer Half = 4;

    vtop_reg #(.WIDTH(8), .INVERT(1)) u_named (.clk(clk), .d(a), .q(y));
    vtop_reg #(16) u_position (.clk(clk), .d(b), .q(z));
    generate
        if (1) begin : g_reg
            vtop_reg #(.WIDTH(4)) u_generate (.clk(clk), .d(c), .q(w));
        end
    endgenerate
    vtop_reg #(.WIDTH(2 * Half)) u_expression (.clk(clk), .d(e), .q(v));
endmodule
