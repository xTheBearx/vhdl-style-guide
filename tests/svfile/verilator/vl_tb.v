// A Verilog-2005 testbench: an event control in an initial block, and logic, a name in Verilog
`timescale 1ns / 1ps
module vl_tb;
    reg clk = 1'b0;
    reg logic;
    always #5 clk = ~clk;
    initial begin
        logic = 1'b0;
        @(posedge clk);
        logic <= 1'b1;
        #20;
        $finish;
    end
endmodule
