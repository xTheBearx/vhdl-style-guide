// Module: starc_more8
// Function: examples
// Author: A. Designer
// Date: 2026-11-04
module starc_more8 (
    input  logic       sample,
    input  logic       init_n,
    input  logic       srst_n,
    input  logic [3:0] sel_i,
    input  logic [7:0] a_i,
    output logic [7:0] y_o,
    output logic [7:0] Y_O
);
    `define LOCAL 3
    logic signed [7:0] s;
    logic [2:0] grant;
    logic [7:0] q, r, t;
    always_ff @(posedge sample or negedge init_n)
        if (!init_n) q <= '0;
        else q <= a_i;
    always_ff @(posedge sample)
        if (!srst_n) r <= '0;
        else r <= a_i;
    sub u_sub (.y(t), .a(a_i));
    assign y_o = q & r;
    always_comb begin
        grant = '0;
        for (int i = 0; i < 8; i++)
            if (a_i[i]) grant = 3'(i);
        for (int j = 0; j < 12; j++)
            if (a_i == 8'd5) t = s + a_i;
        casez (sel_i)
            4'b1?0?: t = a_i * q - r;
            default: t = '0;
        endcase
        if (sel_i[0]) t = (q & r) | a_i;
        else t = (q & r) ^ a_i;
    end
endmodule

module sub (
    input  logic [7:0] a,
    output logic [7:0] y
);
    assign y = a;
endmodule

module starc_more8_tb;
    logic clk, d;
    initial begin
        @(posedge clk);
        d = 1'b1;
    end
endmodule
