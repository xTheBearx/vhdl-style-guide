// sv_lint_008: a variable written in both branches is computed by the block; one written in one branch is read
module branch (
    input  logic a_i,
    input  logic b_i,
    input  logic c_i,
    output logic y_o,
    output logic z_o
);
    logic t;
    logic u;

    always @(a_i or b_i) begin
        if (a_i) begin
            t = b_i;
        end else begin
            t = 1'b0;
        end
        y_o = t;
    end

    always @(a_i or b_i) begin
        if (a_i) begin
            u = b_i;
        end
        z_o = u | c_i;
    end
endmodule
