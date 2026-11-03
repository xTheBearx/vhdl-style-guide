// Clock domain crossings in SystemVerilog
module cdc_sv (
    input  logic clk_a,
    input  logic clk_b,
    input  logic rst_ni,
    input  logic in_a,
    input  logic en_a,
    output logic out_b,
    output logic mixed_b,
    output logic sync_b,
    output logic gated_q
);
    logic flag_a, x_a, y_a;
    logic unsync_b, s1_b, s2_b, s1x_b, s2x_b;

    always_ff @(posedge clk_a or negedge rst_ni) begin
        if (!rst_ni) begin
            flag_a <= 1'b0;
            x_a <= 1'b0;
            y_a <= 1'b0;
        end else begin
            flag_a <= in_a;
            x_a <= in_a;
            y_a <= en_a;
        end
    end

    // flag_a is used in clock domain b without a synchronizer
    always_ff @(posedge clk_b) begin
        unsync_b <= flag_a;
        out_b <= unsync_b ^ s2_b;
    end

    // A two-register synchronizer
    always_ff @(posedge clk_b) begin
        s1_b <= x_a;
        s2_b <= s1_b;
    end
    assign sync_b = s2_b;

    // Logic before a synchronizer
    always_ff @(posedge clk_b) begin
        s1x_b <= x_a & y_a;
        s2x_b <= s1x_b;
        mixed_b <= s2x_b;
    end

    // A gated clock
    logic clk_gated;
    assign clk_gated = clk_a & en_a;
    always_ff @(posedge clk_gated) gated_q <= in_a;
endmodule
