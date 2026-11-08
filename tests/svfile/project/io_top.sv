// The top level of a design: pad_io is a pin of the device
module io_top (
    input logic clk_i,
    inout wire  pad_io
);
    io_sub u_sub (
        .clk_i (clk_i),
        .bus_io(pad_io)
    );
endmodule
