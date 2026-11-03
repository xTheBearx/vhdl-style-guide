// Qualification example of sv_statement_005: a fork-join block, then the same statements in a begin-end block
module fork_join (
    input  logic clk,
    input  logic d,
    output logic a,
    output logic b
);

    always @(posedge clk) begin
        fork
            a <= d;
        join
    end

    always @(posedge clk) begin
        b <= d;
    end

endmodule
