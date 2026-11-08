// A testbench of io_top
module io_tb;
    logic clk;
    wire  pad;

    io_top u_top (
        .clk_i (clk),
        .pad_io(pad)
    );
endmodule
