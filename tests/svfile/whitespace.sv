module ws #(parameter int W=8) (
    input logic clk_i , // clock
    input logic [W-1:0] a_i,b_i,
    output logic [W-1:0] y_o
);
    data_t [1:0] mem;
    logic [W-1:0] sum;
    always_ff@ (posedge clk_i) begin: proc_sum
        if(a_i [0]) sum <= a_i+b_i ;
        else sum <= ~ b_i;
    end:proc_sum
    always_comb begin
        case (sum)
            0 : y_o = sum ? a_i:b_i;
            1: ;
            default : y_o = '0;
        endcase
        for (int i = 0;i < W;i ++) $display ("%d", i, , W);
    end
    always @(a_i , b_i) y_o = a_i[W-1:0];
    sub # (.W(W)) u_sub (.clk_i(clk_i));
    `ASSERT(a_check , a_i,clk_i)
endmodule


