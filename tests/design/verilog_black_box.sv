// A design with black boxes: BUFGCE, which Yosys has a model of, and vendor_ip, which no file defines
module vbb_top (
    input  logic clk_a,
    input  logic clk_b,
    input  logic d_a,
    output logic q_b,
    output logic irq_q
);
    logic clk_g;
    logic d_r;
    logic q_r;
    logic irq;

    BUFGCE u_bufg (.I(clk_b), .CE(1'b1), .O(clk_g));

    always_ff @(posedge clk_a) d_r <= d_a;
    always_ff @(posedge clk_g) q_r <= d_r;
    assign q_b = q_r;

    vendor_ip #(.WIDTH(8)) u_ip (.aclk(clk_a), .data_i(d_r), .irq(irq));
    always_ff @(posedge clk_a) irq_q <= irq;
endmodule
