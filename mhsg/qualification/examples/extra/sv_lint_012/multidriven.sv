// Qualification example of sv_lint_012: busy is assigned in always blocks of two clocks; done_q in one
module multidriven (
    input  logic clk,
    input  logic clk_b,
    input  logic start,
    input  logic done,
    output logic busy,
    output logic done_q
);

    always @(posedge clk) begin
        if (start) busy <= 1'b1;
    end

    always @(posedge clk_b) begin
        if (done) busy <= 1'b0;
    end

    always @(posedge clk) begin
        done_q <= done;
    end

endmodule
