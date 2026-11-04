// A transceiver of the xilinx black box library: the data it sends is timed by TXUSRCLK2, the data it receives by
// RXUSRCLK2, and its clock outputs are clocks of their own
module gt_top (
    input  logic        clk_a,
    input  logic        refclk,
    input  logic [63:0] d_a,
    input  logic [7:0]  k_a,
    output logic [63:0] q
);
    logic        txoutclk;
    logic        rxoutclk;
    logic [63:0] d_r;
    logic [7:0]  k_tx;
    logic [63:0] rxdata;

    // d_r is in the domain of clk_a and crosses into the transceiver; k_tx is in the domain of TXUSRCLK2
    always_ff @(posedge clk_a) d_r <= d_a;
    always_ff @(posedge txoutclk) k_tx <= k_a;

    GTXE2_CHANNEL u_gt (
        .GTREFCLK0 (refclk),
        .TXUSRCLK  (txoutclk),
        .TXUSRCLK2 (txoutclk),
        .TXOUTCLK  (txoutclk),
        .TXDATA    (d_r),
        .TXCHARISK (k_tx),
        .RXUSRCLK  (rxoutclk),
        .RXUSRCLK2 (rxoutclk),
        .RXOUTCLK  (rxoutclk),
        .RXDATA    (rxdata)
    );

    // In the domain of RXUSRCLK2, as the received data
    always_ff @(posedge rxoutclk) q <= rxdata;
endmodule
