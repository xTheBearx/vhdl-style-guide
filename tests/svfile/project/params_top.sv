// One instance sets one of the two parameters of params_sub, the other both; WIDTH is a parameter of both modules
module params_top #(
    parameter int WIDTH = 16
) (
    input  logic clk_i
);
    params_sub #(.WIDTH(WIDTH)) u_partial (.clk_i(clk_i));

    params_sub #(.WIDTH(WIDTH), .DEPTH(2)) u_full (.clk_i(clk_i));
endmodule
