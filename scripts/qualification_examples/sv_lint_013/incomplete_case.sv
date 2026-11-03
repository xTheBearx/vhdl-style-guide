// Qualification example of sv_lint_013: the first case statement does not cover every value of sel, the second does
module incomplete_case (
    input  logic [1:0] sel,
    input  logic       a,
    input  logic       b,
    output logic       y,
    output logic       z
);

    always_comb begin
        y = 1'b0;
        case (sel)
            2'b00: y = a;
            2'b01: y = b;
        endcase
    end

    always_comb begin
        case (sel)
            2'b00:   z = a;
            2'b01:   z = b;
            default: z = 1'b0;
        endcase
    end

endmodule
