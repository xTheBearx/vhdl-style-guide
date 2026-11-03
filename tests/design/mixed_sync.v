// A two-register synchronizer in Verilog, used by the VHDL of mixed_top.vhd
module mixed_sync (
    input  wire clk,
    input  wire d,
    output reg  q
);
    reg meta;
    always @(posedge clk) begin
        meta <= d;
        q <= meta;
    end
endmodule
