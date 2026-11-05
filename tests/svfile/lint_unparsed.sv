// Width truncations in an inactive branch and in the arguments of a macro use
`define ASSIGN(dst, src) assign dst = src;
module li (
    input  logic [7:0] a_i,
    output logic [3:0] y_o,
    output logic [3:0] z_o
);
`ifdef WIDE
    assign y_o = a_i;
`else
    assign y_o = a_i[3:0];
`endif
    `ASSIGN(z_o, a_i)
endmodule
