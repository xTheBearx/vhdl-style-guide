`define WIDTH_M 8
`define DEPTH_M (`WIDTH_M * 2)
module starc_more4 (
    input  logic       data_i,
    input  logic       clk_i,
    output logic       full_o,
    input  logic       rst_ni,
    input  logic [3:0] count_i
);
    logic q, r, s;
    always_ff @(posedge clk_i or posedge rst_ni)
        if (!rst_ni) q <= 1'b0;
        else q <= data_i;
    always_ff @(posedge clk_i or negedge rst_ni)
        if (rst_ni == 1'b0) r <= 1'b0;
        else begin
            r <= data_i;
            s <= r;
        end
    always_comb full_o = (count_i == 3) ? 1'b1 : (count_i > 'd4);
    assign t = 5;
    function automatic logic parity(input logic [7:0] data);
        parity = ^data;
        if (data[0]) $display("odd");
    endfunction
    initial begin
        fork
            #1 q = 1'b1;
            #2 q = 1'b0;
            #3 q = 1'b1;
            #4 q = 1'b0;
        join
    end
endmodule
