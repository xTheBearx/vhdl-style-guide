module dimensions (
    input  logic [31:0] a_i,
    input  logic [4:0]  b_i,
    output logic        c_o
);
    logic [15:0] x;
    logic [7:0]  y;
    logic        z;
    logic [1:0]  w;
endmodule

module dimensions_flush;
    // A width written with a parameter needs more than 2 spaces before the others: they stay flush left
    wire [Width-1:0] p;
    wire [3:0] q;
endmodule
