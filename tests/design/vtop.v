// A Verilog top that uses the VHDL synchronizer of vtop_sync.vhd for one crossing and none for another
module vtop (
    input  wire clk_a,
    input  wire clk_b,
    input  wire d,
    output wire q,
    output reg  raw
);
    reg flag_a;
    always @(posedge clk_a) begin
        flag_a <= d;
    end

    vtop_sync u_sync (
        .clk(clk_b),
        .d(flag_a),
        .q(q)
    );

    always @(posedge clk_b) begin
        raw <= flag_a;
    end
endmodule
