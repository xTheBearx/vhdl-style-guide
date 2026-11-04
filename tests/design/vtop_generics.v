// A Verilog top that sets the generics of VHDL entities: by name, by position, in a generate block, with an
// expression, in a module with parameters of its own, and in a generate loop, whose instances would need values of
// their own and are analyzed with the defaults
module vtop_generics (
    input  wire        clk,
    input  wire [7:0]  a,
    output wire [7:0]  y,
    input  wire [15:0] b,
    output wire [15:0] z,
    input  wire [3:0]  c,
    output wire [3:0]  w,
    input  wire [7:0]  e,
    output wire [7:0]  v,
    input  wire [5:0]  f,
    output wire [5:0]  u
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
    vtop_mid #(.Bits(3)) u_mid (.clk(clk), .d(f), .q(u));
    genvar i;
    generate
        for (i = 1; i < 3; i = i + 1) begin : g_loop
            vtop_reg #(.WIDTH(i)) u_loop (.clk(clk), .d(f[i-1:0]), .q());
        end
    endgenerate
endmodule

// A module with a parameter of its own, which sets the width of the VHDL register
module vtop_mid #(
    parameter integer Bits = 2
) (
    input  wire                clk,
    input  wire [2*Bits-1:0]   d,
    output wire [2*Bits-1:0]   q
);
    vtop_reg #(.WIDTH(Bits * 2)) u_inner (.clk(clk), .d(d), .q(q));
endmodule
