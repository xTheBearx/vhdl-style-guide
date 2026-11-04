module starc_more6 (
    input  logic       clk_i,
    input  logic       rst_ni,
    input  logic       a_i,
    input  logic [1:0] state,
    input  logic [1:0] mode_state,
    output logic [3:0] y_o
);
    logic q, r, s, t, u, l, bus, en, sel, rst_n;
    assign rst_n = rst_ni & a_i;
    always_ff @(posedge clk_i)
        if (!rst_ni) q <= 1'b0;
        else q <= a_i;
    always_ff @(posedge clk_i or negedge rst_n)
        if (!rst_n) r <= init(1'b0);
        else r <= clk_i;
    always_latch
        if (!rst_ni) l <= 1'b0;
        else if (en) l <= a_i;
    assign bus = en ? a_i : 1'bz;
    BUFG u_bufg (.I(clk_i), .O());
    always_comb begin
        sel = 1'bx;
        if (a_i && !en) sel = 1'b0;
        if (sel) s = 1'b1;
        else s = 1'b0;
        if (a_i)
            if (en) t = 1'b1;
        for (int i = 0; i < 4; i++) y_o[i] = a_i + q;
        u = -1;
    end
    always_comb case (state) 2'd0: r = 1'b0; default: r = 1'b1; endcase
    always_comb case (mode_state) 2'd0: q = 1'b0; default: q = 1'b1; endcase
    function automatic logic f(input logic x);
        if (x) f = 1'b1;
    endfunction
    always_ff @(posedge clk_i) if (a_i) $display("a");
endmodule

module starc_more6_tb;
    logic clk_a, clk_b, done;
    always #(10 / 2) clk_a = ~clk_a;
    initial begin
        #5 clk_a = ~clk_a;
        #5 clk_b = ~clk_b;
        @(posedge done) $finish;
    end
endmodule
