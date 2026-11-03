`default_nettype none
`define WIDTH 8

/* A block comment
   over two lines */
module sample #(
    parameter int Depth = 4
) (
    input  logic              clk_i,
    input  logic [`WIDTH-1:0] data_i,
    output logic [`WIDTH-1:0] data_o
);

    always_ff @(posedge clk_i) begin : proc_reg
        data_o <= data_i;  // a line comment
    end

`ifdef SIMULATION
    initial $display("simulation");
`endif

endmodule
